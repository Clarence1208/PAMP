import json
import os
import boto3
import logging
from datetime import datetime
import uuid

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize SQS client
sqs_client = boto3.client('sqs')
QUEUE_URL = os.environ['QUEUE_URL']

def handler(event, context):
    """Lambda handler function for processing API requests"""
    try:
        logger.info("Received event: %s", json.dumps(event))
        
        # Parse request body
        if not event.get('body'):
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': 'Missing request body'
                })
            }
        
        # Handle different content types
        body = event.get('body')
        if isinstance(body, str):
            try:
                body = json.loads(body)
            except json.JSONDecodeError:
                return {
                    'statusCode': 400,
                    'body': json.dumps({
                        'message': 'Invalid JSON in request body'
                    })
                }
        
        # Validate required fields
        required_fields = ['to', 'subject', 'message']
        missing_fields = [field for field in required_fields if field not in body]
        if missing_fields:
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'message': f'Missing required fields: {", ".join(missing_fields)}'
                })
            }
        
        # Create notification message payload
        notification_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        payload = {
            'id': notification_id,
            'timestamp': timestamp,
            'type': 'email',
            'to': body['to'],
            'subject': body['subject'],
            'message': body['message'],
            'from': body.get('from'),  # Optional field
            'status': 'QUEUED'
        }
        
        # Send message to SQS
        response = sqs_client.send_message(
            QueueUrl=QUEUE_URL,
            MessageBody=json.dumps(payload),
            MessageAttributes={
                'NotificationType': {
                    'DataType': 'String',
                    'StringValue': 'email'
                }
            }
        )
        
        logger.info("Successfully sent message to SQS: %s", response['MessageId'])
        
        # Return success response
        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Notification queued successfully',
                'notificationId': notification_id,
                'messageId': response['MessageId']
            })
        }
        
    except Exception as e:
        logger.error("Error processing notification request: %s", str(e))
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error processing notification request: {str(e)}'
            })
        }
