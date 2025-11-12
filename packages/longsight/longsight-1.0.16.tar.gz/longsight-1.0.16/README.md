# Longsight: Best Practice Logging Library
A range of common logging functions for the observability of Python AWS cloud applications


![license](https://img.shields.io/gitlab/license/crossref/labs/longsight) ![activity](https://img.shields.io/gitlab/last-commit/crossref/labs/longsight)

![AWS](https://img.shields.io/badge/AWS-%23FF9900.svg?style=for-the-badge&logo=amazon-aws&logoColor=white) ![Linux](https://img.shields.io/badge/Linux-FCC624?style=for-the-badge&logo=linux&logoColor=black) ![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)

This library implements a range of best-practice logging techniques for Python AWS cloud applications. This includes [FastAPI Lambda contexts](https://www.eliasbrange.dev/posts/observability-with-fastapi-aws-lambda-powertools/). 

This is a prototype Crossref Labs system. It is not guaranteed to be stable and the metadata schema and behaviour may be subject to change at any time.

# longsight.instrumentation
The longsight.instrumentation module provides functionality for instrumenting a FastAPI application with AWS CloudWatch Metrics and Logs. It includes middleware to handle correlation IDs, filters for attaching correlation IDs to logs, and context managers for instrumenting routes with metrics and logging.

## Installation
To install the longsight.instrumentation module, run the following command:

    pip install longsight

## Usage
To use the longsight.instrumentation module, import the necessary components and add them to your FastAPI application.

## Decorators
Using the longsight decorators are the easiest way to start logging locally (or in Lambda contexts) quickly.

    from longsight.instrumentation import instrument

    router = APIRouter()
    
    @router.get("/path")
    @instrument()
    async def a_route(request: Request, instrumentation=None):
        instrumentation.logger.info("Hello, World!")
        return {"message": "Hello, World!"}

Note that, in FastAPI contexts, you must specify "instrumentation=None" to avoid FastAPI thinking this is an unfilled parameter.

Alternatively, you can also log to CloudWatch instead of locally from any function (note also that the decorator works on both async and synchronous functions and is _not_ limited to FastAPI functions):

    from longsight.instrumentation import instrument

    @instrumentation.instrument(
    cloudwatch_push=True,
    log_stream_name="martin-test-stream-name",
    log_group_name="martin-test-group-name",
    namespace="martin-test-namespace",
    )
    def a_function(instrumentation):
        instrumentation.logger.info("Hello, World!")
        instrumentation.logger.info("A second log line")
        instrumentation.add_metric_point(
            metric_name="test_metric",
            dimensions=[{"Name": "Environment", "Value": "Production"}],
            metric_value=1,
            unit="Count",
            time_stamp=datetime.now(),
        )

Longsight can also create AWS objects for you to reuse throughout your project, centralizing AWS code:

    from longsight.instrumentation import instrument

    @instrument(create_aws=True, bucket="my-bucket")
    def a_function(instrumentation):
        instrumentation.logger.info("Hello, World!")
        s3_client = instrumentation.aws_connector.s3_client
        return

By default, the AWS interaction is anonymous. To write to S3 buckets or access protected buckets, pass sign_aws_requests=True. 

## Easy counters
The instrumentation class also provides a simple counter function to increment a counter in CloudWatch:

    from longsight.instrumentation import instrument

    @instrumentation.instrument(
    cloudwatch_push=True,
    log_stream_name="martin-test-stream-name",
    log_group_name="martin-test-group-name",
    namespace="martin-test-namespace",
    )
    def a_function(instrumentation):
        instrumentation.add_counter(
            metric_name="test_counter", status_code=200, member_id=None, 
            additional_dimensions=[{"Name": "Environment", "Value": "Production"}]
        )

## Correlation ID Middleware
The AWSCorrelationIdMiddleware middleware automatically generates or loads a correlation ID for each incoming request, and attaches it to the request headers and logs. To use the middleware, create an instance of the AWSCorrelationIdMiddleware class and add it to your FastAPI application:

    from fastapi import FastAPI
    from longsight.instrumentation import AWSCorrelationIdMiddleware
    
    app = FastAPI()
    app.add_middleware(AWSCorrelationIdMiddleware)

By default, the middleware looks for the X-Request-ID header in the incoming request headers, or in the mangum handlers aws.context, and generates a new UUID if the header is not present.

## Using Mangum and logging default Lambda stats

To configure Mangum to handle requests in an AWS Lambda context and to inject instrumentation, use:

    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
    handler = instrumentation.logger.inject_lambda_context(
        lambda_handler=handler, clear_state=True
    )
    handler = instrumentation.metrics.log_metrics(
        handler, capture_cold_start_metric=True
    )

## Logging Filters
The CorrelationIdFilter filter attaches the correlation ID to log records. To use the filter, create an instance of the CorrelationIdFilter class and add it to your logger:

    import logging
    from longsight.instrumentation import CorrelationIdFilter
    
    logger = logging.getLogger(__name__)
    logger.addFilter(CorrelationIdFilter())

This setup is done automatically if you use the decorators.

## Context Managers
The Instrumentation context manager provides functionality for instrumenting routes with metrics and logging. To use the context manager, create an instance of the Instrumentation class and use it as a context manager:

    from fastapi import FastAPI
    from longsight.instrumentation import Instrumentation
    
    app = FastAPI()
    
    @app.get("/")
    async def root(request: Request):
        with Instrumentation(
                        aws_connector=aws_connector,
                        fastapi_app=fastapi_app,
                        request=request) as instrumentation:
            instrumentation.logger.info("Handling request")
            return {"message": "Hello, World!"}

The Instrumentation context manager automatically logs the start and end of the request, and provides an instance of the Logger classes for logging and metrics. The Logger classes are provided by the aws_lambda_powertools package.

# Credits
* [.gitignore](https://github.com/github/gitignore) from Github.
* [AWS Lambda Powertools](https://awslabs.github.io/aws-lambda-powertools-python/2.10.0/) by Amazon.

&copy; Crossref 2023