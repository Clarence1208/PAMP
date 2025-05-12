from aws_cdk import (
    Duration,
    aws_sqs as sqs,
    CfnOutput,
)
from constructs import Construct


class QueueComponent(Construct):
    """SQS queue component for notification service"""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)
        
        # Create a dead letter queue for failed messages
        self.dlq = sqs.Queue(
            self, "NotificationDLQ",
            retention_period=Duration.days(14),  # Keep failed messages for 14 days
            encryption=sqs.QueueEncryption.SQS_MANAGED,  # Enable encryption
        )
        
        # Create the main notification queue
        self.notification_queue = sqs.Queue(
            self, "NotificationQueue",
            visibility_timeout=Duration.seconds(300),  # 5 minutes timeout for processing
            retention_period=Duration.days(4),        # Keep messages for 4 days
            encryption=sqs.QueueEncryption.SQS_MANAGED,  # Enable encryption
            dead_letter_queue=sqs.DeadLetterQueue(
                max_receive_count=3,  # After 3 failed attempts, send to DLQ
                queue=self.dlq
            )
        )
        
        # Outputs
        CfnOutput(self, "NotificationQueueUrl", value=self.notification_queue.queue_url)
        CfnOutput(self, "NotificationQueueDlqUrl", value=self.dlq.queue_url)
