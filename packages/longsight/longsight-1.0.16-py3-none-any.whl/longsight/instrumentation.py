import functools
import inspect
import logging
import os
from contextlib import AbstractContextManager, contextmanager
from contextvars import ContextVar
from datetime import datetime
from logging import LogRecord
from types import TracebackType
from typing import Callable
from typing import Optional
from typing import Type
from uuid import uuid4

from aws_lambda_powertools import Logger, Tracer
from aws_lambda_powertools.logging.formatter import LambdaPowertoolsFormatter
from claws import aws_utils
from fastapi import Request
from fastapi.routing import APIRoute
from starlette.datastructures import MutableHeaders
from starlette.responses import Response
from starlette.types import ASGIApp, Message, Receive, Scope, Send


correlation_id: ContextVar[Optional[str]] = ContextVar(
    "correlation_id", default=None
)

logger: Logger = Logger()


class LoggerRouteHandler(APIRoute):
    def get_route_handler(self) -> Callable:
        original_route_handler = super().get_route_handler()

        async def route_handler(request: Request) -> Response:
            """
            Note: this returns the WRONG route for most requests, saying
            that they have come from the /heartbeat route. This is because
            the path is not set on the request object until after the route
            handler is called. This is apparently a known issue with FastAPI.

            ctx = {
                "path": request.url.path,
                "route": self.path,
                "method": request.method,
            }
            logger.append_keys(fastapi=ctx)
            """

            return await original_route_handler(request)

        return route_handler


class CorrelationIdFilter(logging.Filter):
    """Logging filter to attach correlation IDs to log records"""

    def __init__(
        self,
        name: str = "",
        uuid_length: Optional[int] = None,
        default_value: Optional[str] = None,
    ):
        super().__init__(name=name)
        self.uuid_length = uuid_length
        self.default_value = default_value

    def filter(self, record: "LogRecord") -> bool:
        """
        Attach a correlation ID to the log record.
        """
        record.correlation_id = correlation_id.get(self.default_value)
        return True


class AWSCorrelationIdMiddleware:
    def __init__(
        self,
        app: "ASGIApp",
        header_name: str = "X-Request-ID",
    ):
        self.app = app
        self.header_name = header_name

    async def __call__(
        self, scope: "Scope", receive: "Receive", send: "Send"
    ) -> None:
        """
        Load request ID from headers if present. Generate one otherwise.
        """
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        aws_context = scope.get("aws.context")
        id_value = None

        if hasattr(aws_context, "aws_request_id"):
            id_value = aws_context.aws_request_id

        headers = MutableHeaders(scope=scope)

        if not id_value:
            # Load request ID from the request headers
            header_value = headers.get(self.header_name.lower())

            if not header_value:
                id_value = uuid4().hex
            else:
                id_value = header_value

        headers[self.header_name] = id_value

        correlation_id.set(id_value)

        async def handle_outgoing_request(message: "Message") -> None:
            if (
                message["type"] == "http.response.start"
                and correlation_id.get()
            ):
                headers = MutableHeaders(scope=message)
                headers.append(self.header_name, correlation_id.get())

            await send(message)

        await self.app(scope, receive, handle_outgoing_request)
        return


def instrument(
    bucket: str = "",
    create_aws=False,
    cloudwatch_push=False,
    log_group_name: str = "",
    log_stream_name: str = "",
    namespace: str = "namespace",
    sign_aws_requests: bool = False,
):
    """
    This is a decorator that will instrument a method and provide AWS access
    if desired.
    :param bucket: the bucket for the AWSClient to use.
    :param create_aws: whether to create an AWSClient
    :param cloudwatch_push: whether to push metrics to CloudWatch. Note that
    setting this to true will create an AWSClient
    :param log_group_name: the log group name to use for the logger
    :param log_stream_name: the log stream name to use for the logger
    :param namespace: the namespace to use for the metrics
    :param sign_aws_requests: whether to sign AWS requests
    :return: the wrapped function
    """

    def wrap(f):
        @contextmanager
        def wrapping_logic(*args, **kwargs):
            from claws import aws_utils

            if create_aws or cloudwatch_push:
                # create the boto3 objects
                aws_access_key_id = os.environ.get("AWS_ACCESS_KEY_ID")
                aws_secret_access_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
                aws_session_token = os.environ.get("AWS_SESSION_TOKEN")

                aws_connector = aws_utils.AWSConnector(
                    bucket=bucket,
                    aws_access_key_id=aws_access_key_id,
                    aws_secret_access_key=aws_secret_access_key,
                    aws_session_token=aws_session_token,
                    unsigned=not sign_aws_requests,
                )
            else:
                aws_connector = None

            fastapi_request = kwargs.get("request", None)
            fastapi_app = fastapi_request.app if fastapi_request else None

            aws_context = (
                fastapi_request.scope.get("aws.context", {})
                if fastapi_request
                else {}
            )

            with Instrumentation(
                aws_connector=aws_connector,
                fastapi_app=fastapi_app,
                request=fastapi_request,
                cloudwatch_push=cloudwatch_push,
                log_group_name=log_group_name,
                log_stream_name=log_stream_name,
                namespace=namespace,
            ) as metric_logger:
                if hasattr(aws_context, "aws_request_id"):
                    metric_logger.logger.info(
                        f"Set correlation ID to AWS "
                        f"requestId: {aws_context.aws_request_id}"
                    )

                yield metric_logger

        def decorate_sync_async(func):
            func_sig = inspect.signature(func)

            if inspect.iscoroutinefunction(func):

                async def decorated(*args, **kwargs):
                    if "instrumentation" in func_sig.parameters:
                        with wrapping_logic(*args, **kwargs) as wl:
                            if (
                                "instrumentation" not in kwargs
                                or kwargs["instrumentation"] is None
                            ):
                                kwargs["instrumentation"] = wl
                            return await func(*args, **kwargs)
                    else:
                        return await func(*args, **kwargs)

            else:

                def decorated(*args, **kwargs):
                    if "instrumentation" in func_sig.parameters:
                        with wrapping_logic(*args, **kwargs) as wl:
                            if (
                                "instrumentation" not in kwargs
                                or kwargs["instrumentation"] is None
                            ):
                                kwargs["instrumentation"] = wl
                            return func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)

            return functools.wraps(func)(decorated)

        return decorate_sync_async(f)

    return wrap


class Instrumentation(AbstractContextManager):
    """
    A context manager that provides instrumentation on AWS CloudWatch.
    """

    def __exit__(
        self,
        __exc_type: Type[BaseException],
        __exc_value: BaseException,
        __traceback: TracebackType,
    ) -> bool:
        try:
            if len(self._metrics) > 0 and self._cloudwatch_push:
                self._aws_connector.cloudwatch_client.put_metric_data(
                    Namespace=self._namespace, MetricData=self._metrics
                )
                self.logger.info(
                    f"Pushed {len(self._metrics)} custom "
                    f"metrics to CloudWatch"
                )
            elif not self._cloudwatch_push:
                self.logger.info("Not pushing metrics to CloudWatch")
            else:
                self.logger.info("No metrics to push to CloudWatch")
        except Exception as e:
            self.logger.warning(
                f"Failed to send metrics to CloudWatch ({e}): {self._metrics}"
            )

        if __exc_value is not None:
            if hasattr(__exc_value, "detail"):
                self.logger.error(
                    f"Request shutdown with error: " f"{__exc_value.detail}."
                )
            else:
                self.logger.error(
                    f"Request shutdown with error: " f"{__exc_value}."
                )
            raise __exc_value

        return True

    def add_metric_point(
        self,
        metric_name: str,
        dimensions: list[dict],
        time_stamp: datetime,
        metric_value: int,
        unit: str,
    ):
        """
        Add a metric point to the list of metrics to send to CloudWatch.
        :param metric_name: the name of the metric
        :param dimensions: associated dimensions
        :param time_stamp: the timestamp of the metric point
        :param metric_value: the value of the metric point
        :param unit: the unit of the metric point
        :return: None
        """

        # documentation for how we build this can be found at:
        # https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/cloudwatch/client/put_metric_data.html
        MetricData = {
            "MetricName": metric_name,
            "Timestamp": time_stamp,
            "Value": metric_value,
            "Unit": unit,
            "StorageResolution": 60,  # one or 60
        }

        if dimensions:
            MetricData["Dimensions"] = dimensions

        self._metrics.append(MetricData)

    def add_counter(
        self,
        metric_name: str,
        status_code: int = None,
        member_id: str = None,
        additional_dimensions: list[dict] = None,
        date_time: datetime = None,
    ):
        """
        Add a counter to the list of metrics to send to CloudWatch.
        :param metric_name: the name of the metric
        :param status_code: the status code of the request
        :param member_id: the member id of the request
        :param additional_dimensions: additional dimensions to add. A list of dictionaries in the form {"Name": "DimensionName", "Value": "DimensionValue"}.
        :param date_time: the date time of the metric point if you wish to override
        :return: None
        """
        if additional_dimensions is None:
            additional_dimensions = []

        dimensions = additional_dimensions

        if status_code:
            dimensions.append({"Name": "StatusCode", "Value": str(status_code)})

        if member_id:
            dimensions.append({"Name": "MemberId", "Value": str(member_id)})

        self.add_metric_point(
            metric_name=metric_name,
            dimensions=dimensions,
            time_stamp=date_time if date_time else datetime.utcnow(),
            metric_value=1,
            unit="Count",
        )

    def __init__(
        self,
        aws_connector: aws_utils.AWSConnector = None,
        namespace: str = "LabsAPI",
        fastapi_app=None,
        request: Request = None,
        cloudwatch_push: bool = False,
        log_group_name: str = "",
        log_stream_name: str = "",
    ):
        self._metrics = []
        self._aws_connector = aws_connector
        self._namespace = namespace
        self._app = fastapi_app
        self._log_group_name = log_group_name
        self._log_stream_name = log_stream_name
        self._cloudwatch_push = cloudwatch_push

        self._logger: Logger = logger
        self._tracer: Tracer = Tracer()

        self._logger.addFilter(CorrelationIdFilter())

        if self._aws_connector:
            self._aws_connector.instrumentation = self

        self.request_id = None
        self._request = request

        import watchtower
        from watchtower import DEFAULT_LOG_STREAM_NAME

        # if we are in Cloudwatch push mode, use the watchtower library
        # to push logs to Cloudwatch
        if cloudwatch_push:
            lsn = self._log_stream_name if self._log_stream_name else __name__
            lsg = (
                self._log_group_name
                if self._log_group_name
                else DEFAULT_LOG_STREAM_NAME
            )

            handler = watchtower.CloudWatchLogHandler(
                boto3_client=self._aws_connector.log_client
                if self._aws_connector
                else None,
                log_stream_name=lsn,
                log_group_name=lsg,
            )

            handler.setFormatter(LambdaPowertoolsFormatter())
            self._logger.addHandler(handler)

        else:
            # check there isn't an existing instrumentation with a
            # CloudWatchLogHandler
            to_remove = []

            for handler in self._logger.handlers:
                if isinstance(handler, watchtower.CloudWatchLogHandler):
                    to_remove.append(handler)

            for handler in to_remove:
                self._logger.removeHandler(handler)

    @property
    def logger(self):
        return self._logger

    @property
    def aws_connector(self) -> aws_utils.AWSConnector:
        return self._aws_connector

    @aws_connector.setter
    def aws_connector(self, value):
        self._aws_connector = value
        self._aws_connector.instrumentation = self

    @property
    def metrics(self):
        return self._metrics

    @property
    def namespace(self):
        return self._namespace


class CorrelationIDFilter(logging.Filter):
    """
    This class acts as a context filter for logs. This adds the Correlation ID
    to log entries.
    """

    def __init__(self, request: Request):
        super().__init__()
        self._request = request

    def filter(self, record):
        try:
            record.correlation_id = self._request.state.correlation_id
        except:
            record.correlation_id = None
        return True
