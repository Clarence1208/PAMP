import json
import os
import boto3
import logging
from datetime import datetime
import traceback
import re

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Initialize AWS clients
ses_client = boto3.client('ses')
dynamodb = boto3.resource('dynamodb')
table_name = os.environ['NOTIFICATION_TABLE']
notification_table = dynamodb.Table(table_name)

# Email styling constants
YELLOW_ACCENT = "#F0B100"
TEXT_COLOR = "#2C2C33"
PURPLE_ACCENT = "#6751E3"

# Logo URL - replace with your actual logo URL
LOGO_URL = "https://pamp-clm.s3.eu-west-1.amazonaws.com/PAMP-logo%400%2C3x.png"

def create_html_email(subject, message, logo_url=LOGO_URL, button_text=None):
    """Create HTML email with styling"""
    
    # Check if the message contains any URLs to convert to buttons
    button_html = ""
    url_pattern = r'https?://[^\s<>"]+|www\.[^\s<>"]+|http?://[^\s<>"]+'
    urls = re.findall(url_pattern, message)
    
    # Replace URLs in the message with placeholders
    message_without_urls = message
    for i, url in enumerate(urls):
        placeholder = f"[LINK_{i}]"
        message_without_urls = message_without_urls.replace(url, placeholder)
    
    # Create button HTML for each URL
    buttons_html = ""
    for i, url in enumerate(urls):
        if i == 0 and button_text:
            button_label = button_text
        else:
            button_label = f"Click here" if i == 0 else f"Link {i+1}"
        buttons_html += f"""
        <tr>
            <td align="center" style="padding: 20px 0;">
                <a href="{url}" target="_blank" style="background-color: {PURPLE_ACCENT}; 
                   color: white; padding: 12px 30px; text-decoration: none; 
                   border-radius: 4px; font-weight: bold; display: inline-block;">
                    {button_label}
                </a>
            </td>
        </tr>
        """
    
    # Replace placeholders with empty strings
    for i in range(len(urls)):
        message_without_urls = message_without_urls.replace(f"[LINK_{i}]", "")
    
    # Create paragraphs from the message text
    paragraphs = ""
    for paragraph in message_without_urls.split('\n'):
        if paragraph.strip():
            paragraphs += f"<p style=\"color: {TEXT_COLOR}; margin: 0 0 15px 0;\">{paragraph}</p>"
    
    # Create the HTML email template
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{subject}</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: Arial, sans-serif; background-color: #f9f9f9;">
        <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
            <tr>
                <td style="padding: 20px 0; text-align: center; background-color: {TEXT_COLOR};">
                    <img src="{logo_url}" alt="Logo" width="150" style="max-width: 100%; height: auto;">
                </td>
            </tr>
            <tr>
                <td style="padding: 30px 20px; background-color: white;">
                    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" border="0">
                        <tr>
                            <td>
                                <h1 style="color: {YELLOW_ACCENT}; margin: 0 0 20px 0;">{subject}</h1>
                                {paragraphs}
                            </td>
                        </tr>
                        {buttons_html}
                    </table>
                </td>
            </tr>
            <tr>
                <td style="padding: 20px; text-align: center; background-color: #f0f0f0; color: {TEXT_COLOR}; font-size: 12px;">
                    <p>&copy; 2025 PAMP. All rights reserved.</p>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return html_template

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
            button_text = body.get('buttonText')
            
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
            
            # Generate HTML content
            html_content = create_html_email(subject, message, button_text=button_text)
            
            # Send email via SES with both HTML and plain text
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
                        },
                        'Html': {
                            'Data': html_content
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
