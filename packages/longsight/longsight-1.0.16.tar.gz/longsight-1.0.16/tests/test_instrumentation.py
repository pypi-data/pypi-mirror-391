import asyncio
import sys
import unittest
from datetime import datetime
from unittest.mock import MagicMock, patch

import watchtower
from fastapi import FastAPI, Request
from moto import mock_logs, mock_cloudwatch
from starlette.datastructures import MutableHeaders
from starlette.responses import Response
from starlette.testclient import TestClient
from starlette.types import Receive, Scope, Send

sys.path.append("../../")
sys.path.append("../src")
sys.path.append("../src/longsight")

from instrumentation import (
    AWSCorrelationIdMiddleware,
    CorrelationIDFilter,
    Instrumentation,
    LoggerRouteHandler,
    instrument,
)

app = FastAPI()
app.add_middleware(AWSCorrelationIdMiddleware)
app.router.route_class = LoggerRouteHandler


@app.get("/dummy_route")
@instrument()
async def dummy_route(request: Request, instrumentation=None):
    return {"success": True}


class TestAWSCorrelationIdMiddleware(unittest.TestCase):
    def setUp(self) -> None:
        self.scope = {"type": "http", "headers": {}}
        self.receive: Receive = MagicMock()
        self.send: Send = MagicMock()

    async def mock_app(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        pass

    def test_aws_correlation_id_middleware(self):
        aws_middleware = AWSCorrelationIdMiddleware(self.mock_app)

        async def run_test():
            await aws_middleware(self.scope, self.receive, self.send)

        asyncio.run(run_test())

        headers = MutableHeaders(scope=self.scope)
        self.assertIsNotNone(headers.get("X-Request-ID"))


class TestInstrumentation(unittest.TestCase):
    def test_instrumentation_context_manager(self):
        request = MagicMock()
        with Instrumentation(request=request) as instr:
            self.assertIsNotNone(instr.logger)
            self.assertIsNotNone(instr.metrics)

    def test_instrumentation_error_handling(self):
        request = MagicMock()
        with self.assertRaises(ValueError):
            with self.assertLogs(level="ERROR") as log_cm:
                with Instrumentation(request=request) as instr:
                    raise ValueError("Test error")

        self.assertIn(
            "Request shutdown with error: Test error", log_cm.output[0]
        )


class TestInstrumentDecorator(unittest.TestCase):
    def test_non_async(self):
        @app.get("/test_not_async")
        @instrument(bucket="", create_aws=False, cloudwatch_push=False)
        def test_non_async_route(request: Request, instrumentation=None):
            self.assertIsNotNone(instrumentation)

            return {"success": True}

        with TestClient(app) as client:
            response = client.get("/test_not_async")
            self.assertEqual(response.status_code, 200)

            self.assertEqual(response.json(), {"success": True})

    def test_instrument_decorator(self):
        @instrument(bucket="", create_aws=False, cloudwatch_push=False)
        def test_non_async_route_again(request: Request, instrumentation=None):
            self.assertIsNotNone(instrumentation)

            return True

        test_non_async_route_again(request=None, instrumentation=None)

        with TestClient(app) as client:
            response = client.get("/dummy_route")
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json(), {"success": True})


@mock_logs
@mock_cloudwatch
class TestAddCounter(unittest.TestCase):
    def test_add_counter(self):
        with Instrumentation(request=MagicMock()) as instance:
            instance.add_metric_point = MagicMock()

            metric_name = "TestMetric"
            status_code = 200
            member_id = "12345"
            additional_dimensions = [{"Name": "Extra", "Value": "Test"}]
            date_time = datetime.utcnow()

            instance.add_counter(
                metric_name,
                status_code,
                member_id,
                additional_dimensions,
                date_time,
            )

            expected_dimensions = [
                {"Name": "Extra", "Value": "Test"},
                {"Name": "StatusCode", "Value": str(status_code)},
                {"Name": "MemberId", "Value": str(member_id)},
            ]

            instance.add_metric_point.assert_called_once_with(
                metric_name=metric_name,
                dimensions=expected_dimensions,
                time_stamp=date_time,
                metric_value=1,
                unit="Count",
            )


@mock_logs
class TestInstrumentWithAWSDecorator(unittest.TestCase):
    def test_instrument_with_aws(self):
        @app.get("/test_aws")
        @instrument(bucket="test_bucket", create_aws=True)
        async def test_route(request: Request, instrumentation=None):
            self.assertIsNotNone(instrumentation)
            self.assertIsNotNone(instrumentation.aws_connector)

            return Response(status_code=200)

        @app.get("/test_aws_cloudwatch")
        @instrument(
            bucket="test_bucket", create_aws=False, cloudwatch_push=True
        )
        async def test_route_two(request: Request, instrumentation=None):
            self.assertIsNotNone(instrumentation)
            self.assertIsNotNone(instrumentation.aws_connector)

            return Response(status_code=200)

        with TestClient(app) as client:
            # Make a request to the test route
            response = client.get("/test_aws")

            # Assert that the response status code is 200
            self.assertEqual(response.status_code, 200)

            # Make a request to the second CloudWatch test route
            response = client.get("/test_aws_cloudwatch")

            # Assert that the response status code is 200
            self.assertEqual(response.status_code, 200)

    def test_remote_logging(self):
        @app.get("/test_aws_cloudwatch_logs")
        @instrument(
            bucket="test_bucket", create_aws=False, cloudwatch_push=True
        )
        async def test_route_three(request: Request, instrumentation=None):
            self.assertIsNotNone(instrumentation)
            self.assertIsNotNone(instrumentation.aws_connector)

            self.assertTrue(
                any(
                    isinstance(e, watchtower.CloudWatchLogHandler)
                    for e in instrumentation.logger.handlers
                )
            )

            instrumentation.logger.info("Remote CloudWatch line")

            return Response(status_code=200)

        @app.get("/test_aws_cloudwatch_logs_two")
        @instrument(
            bucket="test_bucket", create_aws=False, cloudwatch_push=False
        )
        async def test_route_four(request: Request, instrumentation=None):
            self.assertIsNotNone(instrumentation)

            self.assertFalse(
                any(
                    isinstance(e, watchtower.CloudWatchLogHandler)
                    for e in instrumentation.logger.handlers
                )
            )

            instrumentation.logger.info("Remote CloudWatch line")

            return Response(status_code=200)

        with TestClient(app) as client:
            # Make a request to the second CloudWatch test route
            response = client.get("/test_aws_cloudwatch_logs")

            # Assert that the response status code is 200
            self.assertEqual(response.status_code, 200)

            # Make a request to the second CloudWatch test route
            response = client.get("/test_aws_cloudwatch_logs_two")

            # Assert that the response status code is 200
            self.assertEqual(response.status_code, 200)


class TestCorrelationIDFilter(unittest.TestCase):
    def setUp(self):
        self.request = MagicMock()
        self.request.state = MagicMock()
        self.request.state.correlation_id = "test_correlation_id"

    def test_correlation_id_filter(self):
        correlation_id_filter = CorrelationIDFilter(self.request)
        log_record = MagicMock()

        result = correlation_id_filter.filter(log_record)

        self.assertEqual(log_record.correlation_id, "test_correlation_id")
        self.assertTrue(result)
