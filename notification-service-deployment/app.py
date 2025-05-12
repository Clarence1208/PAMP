#!/usr/bin/env python3
import os
from aws_cdk import App, Environment
import aws_cdk as cdk
from notification_service.component import NotificationServiceStack

# Define environment
account = os.environ.get('CDK_DEFAULT_ACCOUNT', '123456789012')  # Default placeholder account
region = os.environ.get('CDK_DEFAULT_REGION', 'eu-west-1')

app = App()

# Create the notification service stack
notification_service_stack = NotificationServiceStack(
    app, 
    "NotificationServiceStack",
    env=Environment(
        account=account,
        region=region
    ),
    description="Serverless email notification service that stays within AWS free tier"
)

# Add tags to all resources in the stack
cdk.Tags.of(notification_service_stack).add('Environment', 'dev')
cdk.Tags.of(notification_service_stack).add('Project', 'NotificationService')

app.synth()
