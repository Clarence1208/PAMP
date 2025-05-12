import json
import os
import boto3
import logging
from datetime import datetime
import traceback

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ses_client = boto3.client('ses')
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['NOTIFICATION_TABLE']
notification_table = dynamodb.Table(table_name)

def handler(event, context):
    """Lambda handler function for processing email notifications"""
    # List to collect failed message IDs for SQS batch processing
    failed_message_ids = []
    
    # Process each message in the batch
    for record in event.get('Records', []):
        message_id = record['messageId']
        
        try:
            # Parse SQS message
            body = json.loads(record['body'])
            logger.info(f"Processing notification {body.get('id')}")
            
            # Validate required fields
            required_fields = ['id', 'timestamp', 'to', 'subject', 'message']
            missing_fields = [field for field in required_fields if field not in body]
            if missing_fields:
                logger.error(f"Missing required fields: {', '.join(missing_fields)}")
                failed_message_ids.append({'itemIdentifier': record['messageId']})
                continue
            
            # Extract email parameters
            to_email = body['to']
            subject = body['subject']
            message = body['message']
            from_email = body.get('from')
            
            if not from_email:
                # Use a default verified sender email address
                # In production, this should be configurable
                from_email = 'noreply@edulor.fr'  # Replace with your verified email
            
            # Update notification status to PROCESSING
            notification_table.update_item(
                Key={
                    'id': body['id'],
                    'timestamp': body['timestamp']
                },
                UpdateExpression="SET #status = :status, updatedAt = :updatedAt",
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'PROCESSING',
                    ':updatedAt': datetime.utcnow().isoformat()
                }
            )
            
            # Send email via SES
            response = ses_client.send_email(
                Source=from_email,
                Destination={
                    'ToAddresses': [to_email]
                },
                Message={
                    'Subject': {
                        'Data': subject
                    },
                    'Body': {
                        'Text': {
                            'Data': message
                        }
                    }
                }
            )
            
            # Log success
            logger.info(f"Successfully sent email: {response['MessageId']}")
            
            # Update notification status to SENT
            notification_table.update_item(
                Key={
                    'id': body['id'],
                    'timestamp': body['timestamp']
                },
                UpdateExpression="SET #status = :status, updatedAt = :updatedAt, messageId = :messageId",
                ExpressionAttributeNames={
                    '#status': 'status'
                },
                ExpressionAttributeValues={
                    ':status': 'SENT',
                    ':updatedAt': datetime.utcnow().isoformat(),
                    ':messageId': response['MessageId']
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing message {message_id}: {str(e)}")
            logger.error(traceback.format_exc())
            
            # Try to update notification status to ERROR if we have the necessary info
            try:
                if 'body' in locals() and isinstance(body, dict) and 'id' in body and 'timestamp' in body:
                    notification_table.update_item(
                        Key={
                            'id': body['id'],
                            'timestamp': body['timestamp']
                        },
                        UpdateExpression="SET #status = :status, updatedAt = :updatedAt, errorMessage = :errorMessage",
                        ExpressionAttributeNames={
                            '#status': 'status'
                        },
                        ExpressionAttributeValues={
                            ':status': 'ERROR',
                            ':updatedAt': datetime.utcnow().isoformat(),
                            ':errorMessage': str(e)
                        }
                    )
            except Exception as inner_e:
                logger.error(f"Error updating notification status: {str(inner_e)}")
            
            # Add to failed messages for SQS batch processing
            failed_message_ids.append({'itemIdentifier': message_id})
    
    # Return failed message IDs for SQS batch processing
    return {
        'batchItemFailures': failed_message_ids
    }
