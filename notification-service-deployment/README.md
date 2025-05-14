# Notification Service Deployment

A serverless email notification service that stays within AWS free tier limits. This service is designed to handle thousands of notifications per month without incurring costs.

## Architecture

The service is built using the following AWS services:

- **Amazon API Gateway**: Provides the REST API endpoint for submitting notifications
- **Amazon SQS**: Queues notifications for reliable processing
- **AWS Lambda**: Processes notifications and sends emails
- **Amazon SES**: Sends the actual email notifications
- **Amazon DynamoDB**: Tracks notification status and history
- **Amazon CloudWatch**: Monitors service health and performance

## Free Tier Coverage

This architecture is specifically designed to remain within the AWS free tier limits:

- **SES**: Uses the 3,000 emails per month free tier
- **Lambda**: Stays within 1M requests and 400K GB-seconds per month
- **API Gateway**: Uses the 1M API calls per month free tier
- **SQS**: Uses well below the 1M requests per month free tier
- **DynamoDB**: Uses on-demand capacity well below free tier limits
- **CloudWatch**: Stays within the basic monitoring free tier

## Key Features

- **Queuing and Resilience**: Uses SQS to decouple API requests from email sending
- **Automatic Retries**: Failed emails are automatically retried up to 3 times
- **Dead Letter Queue**: Persistently failed messages are captured for investigation
- **Status Tracking**: All notifications are tracked in DynamoDB
- **Monitoring**: CloudWatch dashboards and alarms for operational visibility
- **Rate Limiting**: API throttling to stay within SES sending limits

## Getting Started

### Prerequisites

- AWS CLI configured with appropriate credentials
- Python 3.9 or later
- AWS CDK v2 installed (`npm install -g aws-cdk`)

### Deployment

1. Prepare the environment:

```bash
# Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\\Scripts\\activate

# Install dependencies
pip install -r requirements.txt
```

2. Configure Amazon SES:
   - Verify your email domain or at least one email address in SES
   - If your account is in the SES sandbox, verify recipient email addresses as well
   - Update the sender email address in the mailing Lambda function

3. Deploy the service:

```bash
cdk deploy
```

4. After deployment, note the outputs:
   - `NotificationServiceStack.NotificationServiceApiEndpoint`: The API endpoint URL
   - `NotificationServiceStack.NotificationServiceApiKeyId`: The API key ID

5. Retrieve the API key value:

```bash
aws apigateway get-api-key --api-key YOUR_API_KEY_ID --include-value
```

### Usage

Send an email notification:

```bash
curl -X POST \
  https://your-api-endpoint/notify/email \
  -H 'Content-Type: application/json' \
  -H 'X-Api-Key: YOUR_API_KEY_VALUE' \
  -d '{
    "to": "recipient@example.com",
    "subject": "Test Notification",
    "message": "This is a test notification from the serverless notification service."
  }'
```

Send an email with a button link:

```bash
curl -X POST \
 https://b7ywphvnv6.execute-api.eu-west-1.amazonaws.com/prod/notify/email \
 -H 'Content-Type: application/json' -H 'X-Api-Key: 9HnDynqinT6mPcyiD766FanAnVS4RmPz1ggVxJZm' \
  -d '{
  "to": "hirsch.clarence@gmail.com",
   "subject": "Welcome to PAMP",
    "message": "Hello,\n\n
    Welcome to the PAMP platform! We are excited to have you on board.\n\n
    Please verify your account by clicking on this link: https://edulor.fr/verify\n\n
    Thank you,\n
    The PAMP Team",
    "from": "noreply@edulor.fr",
    "buttonText": "Verify Account"
}'
```


## Monitoring

The service includes a CloudWatch dashboard named "NotificationService" that displays:
- Queue metrics (message count, age)
- Dead letter queue metrics
- API Gateway metrics (requests, errors, latency)
- Lambda metrics (invocations, errors, duration)

CloudWatch alarms will trigger on:
- Queue depth exceeding 100 messages
- Any messages in the dead letter queue
- High rate of API 4XX errors
- High rate of Lambda errors

## Clean Up

To remove all deployed resources:

```bash
cdk destroy
```
