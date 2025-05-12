from aws_cdk import (
    Stack,
    aws_dynamodb as dynamodb,
    RemovalPolicy,
    CfnOutput,
)
from constructs import Construct
from .api.infrastructure import ApiComponent
from .queue.infrastructure import QueueComponent
from .mailing.infrastructure import MailingComponent
from .monitoring.infrastructure import MonitoringComponent


class NotificationServiceComponent(Construct):
    """Main component for the notification service"""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id)
        
        # Create the notification tracking table
        self.notification_table = dynamodb.Table(
            self, "NotificationTable",
            partition_key=dynamodb.Attribute(
                name="id",
                type=dynamodb.AttributeType.STRING
            ),
            sort_key=dynamodb.Attribute(
                name="timestamp",
                type=dynamodb.AttributeType.STRING
            ),
            billing_mode=dynamodb.BillingMode.PAY_PER_REQUEST,  # Stays within free tier for small volumes
            removal_policy=RemovalPolicy.DESTROY,  # Use RETAIN in production
        )
        
        # Create the queue component first (other components depend on it)
        self.queue_component = QueueComponent(
            self, 
            "QueueComponent",
        )
        
        # Create the API component
        self.api_component = ApiComponent(
            self, 
            "ApiComponent", 
            notification_queue=self.queue_component.notification_queue
        )
        
        # Create the mailing component
        self.mailing_component = MailingComponent(
            self, 
            "MailingComponent", 
            notification_queue=self.queue_component.notification_queue,
            notification_table=self.notification_table
        )
        
        # Create the monitoring component
        self.monitoring_component = MonitoringComponent(
            self, 
            "MonitoringComponent",
            api_component=self.api_component,
            queue_component=self.queue_component,
            mailing_component=self.mailing_component,
            notification_table=self.notification_table
        )
        
        # Output important resources
        CfnOutput(self, "ApiEndpoint", value=self.api_component.api_endpoint)
        CfnOutput(self, "ApiKey", value=self.api_component.api_key.key_id)
        

class NotificationServiceStack(Stack):
    """Main stack for the notification service"""

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)
        
        # Create the notification service component
        self.notification_service = NotificationServiceComponent(
            self, 
            "NotificationService"
        )
