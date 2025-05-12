import os
from aws_cdk import (
    Duration,
    aws_apigateway as apigw,
    aws_lambda as lambda_,
    aws_sqs as sqs,
    aws_iam as iam,
    aws_logs as logs,
    CfnOutput,
)
from constructs import Construct


class ApiComponent(Construct):
    """API Gateway component for notification service"""

    def __init__(self, scope: Construct, id: str, notification_queue: sqs.Queue, **kwargs) -> None:
        super().__init__(scope, id)
        
        # Lambda function to send messages to SQS
        self.lambda_function = lambda_.Function(
            self, "ApiHandler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset(os.path.join(os.path.dirname(__file__), "runtime")),
            handler="lambda_function.handler",
            environment={
                "QUEUE_URL": notification_queue.queue_url,
            },
            timeout=Duration.seconds(10),
            memory_size=128,
            log_retention=logs.RetentionDays.ONE_WEEK,
        )
        
        # Grant permission to send messages to SQS
        notification_queue.grant_send_messages(self.lambda_function)
        
        # Create REST API
        self.api = apigw.RestApi(
            self, "NotificationApi",
            rest_api_name="NotificationService",
            description="API for sending notifications",
            deploy_options=apigw.StageOptions(
                stage_name="prod",
                throttling_rate_limit=10,    # 10 requests per second
                throttling_burst_limit=20,   # 20 concurrent requests
                logging_level=apigw.MethodLoggingLevel.INFO,
                metrics_enabled=True,
            ),
            default_cors_preflight_options=apigw.CorsOptions(
                allow_origins=apigw.Cors.ALL_ORIGINS,
                allow_methods=apigw.Cors.ALL_METHODS,
                allow_headers=["Content-Type", "X-Api-Key"]
            )
        )
        
        # Create API usage plan
        usage_plan = self.api.add_usage_plan("NotificationUsagePlan",
            name="BasicUsagePlan",
            description="Basic usage plan for notification service",
            throttle=apigw.ThrottleSettings(
                rate_limit=10,    # 10 requests per second
                burst_limit=20,   # 20 concurrent requests
            ),
            quota=apigw.QuotaSettings(
                limit=3000,       # Matches SES free tier
                period=apigw.Period.MONTH
            )
        )
        
        # Create API key
        self.api_key = self.api.add_api_key("NotificationApiKey",
            api_key_name="NotificationApiKey",
            description="API key for notification service"
        )
        
        # Associate API key with usage plan
        usage_plan.add_api_key(self.api_key)
        
        # Add API resources and methods
        notifications_resource = self.api.root.add_resource("notify")
        email_resource = notifications_resource.add_resource("email")
        
        # POST method to send an email notification
        email_resource.add_method(
            "POST", 
            apigw.LambdaIntegration(self.lambda_function),
            api_key_required=True,
            method_responses=[
                apigw.MethodResponse(
                    status_code="200",
                    response_models={
                        "application/json": apigw.Model.EMPTY_MODEL
                    }
                ),
                apigw.MethodResponse(
                    status_code="400",
                    response_models={
                        "application/json": apigw.Model.ERROR_MODEL
                    }
                ),
                apigw.MethodResponse(
                    status_code="500",
                    response_models={
                        "application/json": apigw.Model.ERROR_MODEL
                    }
                )
            ]
        )
        
        # Store the API endpoint for reference
        self.api_endpoint = self.api.url_for_path("/notify/email")
        
        # Outputs
        CfnOutput(self, "ApiEndpoint", value=self.api_endpoint)
        CfnOutput(self, "ApiKeyId", value=self.api_key.key_id)
