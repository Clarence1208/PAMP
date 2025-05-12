import os
from aws_cdk import (
    Duration,
    aws_lambda as lambda_,
    aws_sqs as sqs,
    aws_dynamodb as dynamodb,
    aws_lambda_event_sources as lambda_event_sources,
    aws_iam as iam,
    aws_ses as ses,
    aws_logs as logs,
    CfnOutput,
)
from constructs import Construct


class MailingComponent(Construct):
    """SES mailing component for notification service"""

    def __init__(self, scope: Construct, id: str, notification_queue: sqs.Queue, notification_table: dynamodb.Table, **kwargs) -> None:
        super().__init__(scope, id)
        
        # Lambda function to process messages from SQS and send emails via SES
        self.lambda_function = lambda_.Function(
            self, "MailingHandler",
            runtime=lambda_.Runtime.PYTHON_3_9,
            code=lambda_.Code.from_asset(os.path.join(os.path.dirname(__file__), "runtime")),
            handler="lambda_function.handler",
            environment={
                "NOTIFICATION_TABLE": notification_table.table_name,
            },
            timeout=Duration.seconds(30),
            memory_size=256,
            log_retention=logs.RetentionDays.ONE_WEEK,
        )
        
        # Grant permissions to the Lambda function
        notification_table.grant_read_write_data(self.lambda_function)
        
        # Add SQS event source to Lambda
        self.lambda_function.add_event_source(lambda_event_sources.SqsEventSource(
            notification_queue,
            batch_size=5,  # Process up to 5 messages at a time
            max_batching_window=Duration.seconds(30),  # Wait up to 30 seconds to gather batch
            report_batch_item_failures=True,  # Enable partial batch responses
        ))
        
        # Grant SES permissions to Lambda
        self.lambda_function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "ses:SendEmail",
                    "ses:SendRawEmail"
                ],
                resources=["*"]  # In production, scope this to specific resources
            )
        )
        
        # Output lambda ARN
        CfnOutput(self, "MailingLambdaArn", value=self.lambda_function.function_arn)
