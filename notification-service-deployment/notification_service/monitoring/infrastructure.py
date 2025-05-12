from aws_cdk import (
    Duration,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
    aws_sns as sns,
    aws_dynamodb as dynamodb,
    CfnOutput,
)
from constructs import Construct
from ..api.infrastructure import ApiComponent
from ..queue.infrastructure import QueueComponent
from ..mailing.infrastructure import MailingComponent


class MonitoringComponent(Construct):
    """CloudWatch monitoring component for notification service"""

    def __init__(
        self, 
        scope: Construct, 
        id: str, 
        api_component: ApiComponent,
        queue_component: QueueComponent,
        mailing_component: MailingComponent,
        notification_table: dynamodb.Table,
        **kwargs
    ) -> None:
        super().__init__(scope, id)
        
        # Create an SNS topic for alarms
        self.alarm_topic = sns.Topic(
            self, "NotificationServiceAlarmTopic",
            display_name="NotificationServiceAlarms",
            topic_name="notification-service-alarms"
        )
        
        # Output the SNS topic ARN
        CfnOutput(self, "AlarmTopicArn", value=self.alarm_topic.topic_arn)
        
        # Create CloudWatch dashboards for monitoring
        self.dashboard = cloudwatch.Dashboard(
            self, "NotificationServiceDashboard",
            dashboard_name="NotificationService"
        )
        
        # Monitor SQS Queue - ApproximateNumberOfMessagesVisible
        queue_depth_metric = queue_component.notification_queue.metric_approximate_number_of_messages_visible(
            statistic="Maximum",
            period=Duration.minutes(1)
        )
        
        # Queue depth alarm - Alert if more than 100 messages in queue for 5 minutes
        queue_depth_alarm = cloudwatch.Alarm(
            self, "QueueDepthAlarm",
            metric=queue_depth_metric,
            threshold=100,
            evaluation_periods=5,
            alarm_description="Queue depth exceeding threshold",
            alarm_name="NotificationQueueDepthAlarm",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )
        queue_depth_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alarm_topic))
        
        # Monitor DLQ - ApproximateNumberOfMessagesVisible
        dlq_depth_metric = queue_component.dlq.metric_approximate_number_of_messages_visible(
            statistic="Maximum",
            period=Duration.minutes(1)
        )
        
        # DLQ alarm - Alert if any messages in DLQ for 5 minutes
        dlq_alarm = cloudwatch.Alarm(
            self, "DLQAlarm",
            metric=dlq_depth_metric,
            threshold=0,
            evaluation_periods=5,
            alarm_description="Messages detected in Dead Letter Queue",
            alarm_name="NotificationDLQAlarm",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )
        dlq_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alarm_topic))
        
        # Monitor API Gateway 4XX errors - Fix: use correct metric method
        api_4xx_metric = api_component.api.metric_client_error(
            statistic="Sum",
            period=Duration.minutes(1)
        )
        
        # API 4XX alarm - Alert if more than 10 4XX errors in 5 minutes
        api_4xx_alarm = cloudwatch.Alarm(
            self, "Api4xxAlarm",
            metric=api_4xx_metric,
            threshold=10,
            evaluation_periods=5,
            alarm_description="High rate of 4XX errors from API Gateway",
            alarm_name="NotificationApi4xxAlarm",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )
        api_4xx_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alarm_topic))
        
        # Monitor Lambda errors
        lambda_errors_metric = mailing_component.lambda_function.metric_errors(
            statistic="Sum",
            period=Duration.minutes(1)
        )
        
        # Lambda errors alarm - Alert if more than 5 errors in 5 minutes
        lambda_errors_alarm = cloudwatch.Alarm(
            self, "LambdaErrorsAlarm",
            metric=lambda_errors_metric,
            threshold=5,
            evaluation_periods=5,
            alarm_description="High rate of errors from mailing Lambda",
            alarm_name="NotificationLambdaErrorsAlarm",
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING
        )
        lambda_errors_alarm.add_alarm_action(cloudwatch_actions.SnsAction(self.alarm_topic))
        
        # Add widgets to the dashboard
        self.dashboard.add_widgets(
            # Queue monitoring
            cloudwatch.GraphWidget(
                title="SQS Queue Metrics",
                left=[
                    queue_depth_metric,
                    queue_component.notification_queue.metric_approximate_number_of_messages_not_visible(),
                    queue_component.notification_queue.metric_approximate_age_of_oldest_message(),
                    dlq_depth_metric
                ]
            ),
            # API Gateway metrics - Fix: use correct metric methods
            cloudwatch.GraphWidget(
                title="API Gateway Metrics",
                left=[
                    api_component.api.metric_count(),
                    api_component.api.metric_client_error(),
                    api_component.api.metric_server_error(),
                    api_component.api.metric_latency()
                ]
            ),
            # Lambda metrics
            cloudwatch.GraphWidget(
                title="Lambda Metrics",
                left=[
                    mailing_component.lambda_function.metric_invocations(),
                    mailing_component.lambda_function.metric_errors(),
                    mailing_component.lambda_function.metric_duration(),
                    mailing_component.lambda_function.metric_throttles()
                ]
            )
        )
