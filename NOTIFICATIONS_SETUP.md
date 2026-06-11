# Notification Providers Setup Guide

This guide covers setting up all four notification channels for OneTapGOV.

## Architecture

The notification system supports four channels:
- **Email** - SMTP-based
- **SMS** - Twilio
- **WhatsApp** - Twilio WhatsApp API
- **Push Notifications** - Firebase Cloud Messaging

Each provider is independently configurable. If a provider is not configured, notifications gracefully fail with a descriptive error.

---

## 1. Email Notifications (SMTP)

### Setup

Email notifications use standard SMTP. You can use any SMTP provider:
- Gmail (with app password)
- AWS SES
- SendGrid
- Mailgun
- Your own mail server

### Gmail Example (Development)

1. **Enable 2-Step Verification** on your Google account
2. **Create an App Password:**
   - Go to https://myaccount.google.com/apppasswords
   - Select Mail and Windows Computer
   - Copy the 16-character password

3. **Update `.env`:**
```bash
SMTP_ENABLED=true
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=xxxx xxxx xxxx xxxx
SMTP_FROM_EMAIL=your-email@gmail.com
```

### AWS SES Example (Production)

```bash
SMTP_ENABLED=true
SMTP_HOST=email-smtp.us-east-1.amazonaws.com
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=your-ses-username
SMTP_PASSWORD=your-ses-password
SMTP_FROM_EMAIL=verified-email@yourdomain.com
```

### SendGrid Example

```bash
SMTP_ENABLED=true
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USE_TLS=true
SMTP_USERNAME=apikey
SMTP_PASSWORD=SG.your_api_key_here
SMTP_FROM_EMAIL=verified-sender@yourdomain.com
```

### Email Payload Format

When queuing an email notification, use this payload:

```json
{
  "subject": "Your Scheme Eligibility",
  "body_text": "You are eligible for Post Matric Scholarship.",
  "body_html": "<p>You are eligible for <strong>Post Matric Scholarship</strong>.</p>"
}
```

---

## 2. SMS Notifications (Twilio)

### Prerequisites

1. **Create a Twilio Account:** https://www.twilio.com/console
2. **Verify your phone number** (for sandbox mode during development)
3. **Get your credentials from Dashboard:**
   - Account SID
   - Auth Token
   - SMS-capable phone number (or rent one)

### Setup

```bash
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
```

### SMS Payload Format

```json
{
  "body": "You are eligible for Post Matric Scholarship. Visit https://onetapgov.in to apply."
}
```

### Cost
- **Sandbox (Free):** Limited to verified numbers (development only)
- **Production:** ~$0.01-0.10 per SMS depending on country

---

## 3. WhatsApp Notifications (Twilio)

WhatsApp uses the same Twilio credentials as SMS but with a WhatsApp-enabled phone number.

### Prerequisites

1. **Have Twilio SMS setup** (above)
2. **Activate WhatsApp on Twilio:**
   - Go to https://www.twilio.com/console/sms/whatsapp/learn
   - Click "Get Started" and follow setup
   - Request approval for WhatsApp-enabled phone number

### Setup

```bash
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcdef
TWILIO_AUTH_TOKEN=your_auth_token_here
TWILIO_PHONE_NUMBER=+1234567890
TWILIO_WHATSAPP_NUMBER=+1234567890
```

### WhatsApp Payload Format

```json
{
  "body": "🎓 You are eligible for Post Matric Scholarship!\n\nVisit https://onetapgov.in to apply."
}
```

### Cost
- Similar to SMS (~$0.01-0.10 per message)
- Supports emoji and formatted text

### Usage Notes
- Recipient must opt-in to receive messages
- Messages are limited to 1600 characters
- Delivery is generally faster than SMS

---

## 4. Push Notifications (Firebase)

### Prerequisites

1. **Create a Firebase Project:**
   - Go to https://console.firebase.google.com
   - Create a new project
   - Enable Cloud Messaging

2. **Generate Service Account Key:**
   - Go to Project Settings → Service Accounts
   - Click "Generate New Private Key"
   - Save the JSON file securely

3. **Get your access token:**
   - The service account JSON contains the private key
   - A tool or Firebase Admin SDK generates short-lived access tokens from it

### Setup

For development, you can use a service account key:

```bash
FIREBASE_ENABLED=true
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_ACCESS_TOKEN=generated-access-token
```

### Generating an Access Token (Python)

```python
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

credentials = Credentials.from_service_account_file(
    'path/to/serviceAccountKey.json',
    scopes=['https://www.googleapis.com/auth/cloud-platform']
)
credentials.refresh(Request())
print(credentials.token)
```

Or use gcloud CLI:

```bash
gcloud auth application-default print-access-token
```

### Push Payload Format

```json
{
  "title": "Scheme Eligibility Update",
  "body": "You are eligible for Post Matric Scholarship",
  "data": {
    "scheme_id": "uuid-123",
    "eligibility_status": "eligible",
    "match_score": "92"
  }
}
```

### Client Setup

On the frontend (React/Flutter), you need to:

1. Register the device for push notifications
2. Store the Firebase device token
3. Send the device token to your backend via API

Example (React):

```javascript
import { getMessaging, getToken } from "firebase/messaging";

const messaging = getMessaging();
getToken(messaging, { vapidKey: 'YOUR_PUBLIC_KEY' })
  .then(token => {
    // Send token to backend
    fetch('/api/v1/notifications/register-device', {
      method: 'POST',
      body: JSON.stringify({ device_token: token })
    })
  });
```

---

## Testing Notifications Locally

### Option 1: Use Twilio Sandbox (No Setup)

```bash
# Set SMS to a verified test number
TWILIO_ENABLED=true
TWILIO_ACCOUNT_SID=AC1234...
TWILIO_AUTH_TOKEN=xxx...
TWILIO_PHONE_NUMBER=+1555010100  # Twilio sandbox number
```

Send test SMS:
```bash
curl -X POST http://localhost:8000/api/v1/notifications \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "sms",
    "recipient": "+1234567890",
    "template_code": "eligibility_update",
    "payload": {
      "body": "Test message"
    }
  }'
```

### Option 2: Use MailHog (Email, Local)

MailHog is a local email testing tool:

```bash
# Install MailHog
go install github.com/mailhog/MailHog@latest

# Run it
MailHog

# In .env:
SMTP_ENABLED=true
SMTP_HOST=localhost
SMTP_PORT=1025
SMTP_USE_TLS=false
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM_EMAIL=test@onetapgov.in

# View emails at http://localhost:8025
```

### Option 3: Mock Providers in Tests

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_notification_dispatch():
    with patch('app.services.notification_providers.SmtpEmailProvider.send') as mock_send:
        mock_send.return_value = DeliveryResult(
            provider_message_id='msg_123',
            accepted=True
        )
        # Your test here
        assert mock_send.called
```

---

## API Examples

### Queue an Email Notification

```bash
curl -X POST http://localhost:8000/api/v1/notifications \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "channel": "email",
    "recipient": "user@example.com",
    "template_code": "eligibility_update",
    "payload": {
      "subject": "Your Scheme Eligibility",
      "body_html": "<p>Congratulations! You are eligible for Post Matric Scholarship.</p>"
    }
  }'
```

### List User Notifications

```bash
curl -X GET http://localhost:8000/api/v1/notifications \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### Dispatch a Queued Notification (Celery Task)

```python
from app.workers.celery_app import celery_app

# In your service:
dispatch_notification.delay(str(notification.id))
```

---

## Monitoring & Troubleshooting

### View Notification Logs

All notifications are logged structurally:

```bash
# Watch logs:
tail -f app.log | grep notification
```

Log events include:
- `email_sent` - Email successfully sent
- `email_send_failed` - Email send failure with error
- `sms_sent` - SMS successfully sent
- `sms_send_failed` - SMS send failure
- `whatsapp_sent` - WhatsApp successfully sent
- `whatsapp_send_failed` - WhatsApp send failure
- `push_sent` - Push notification successfully sent
- `push_send_failed` - Push notification send failure

### Database Queries

Check notification history:

```sql
-- All notifications for a user
SELECT * FROM notifications WHERE user_id = 'user-uuid' ORDER BY created_at DESC;

-- Failed notifications
SELECT * FROM notifications WHERE status = 'failed' ORDER BY created_at DESC;

-- Notifications by channel
SELECT channel, COUNT(*), COUNT(CASE WHEN status = 'sent' THEN 1 END) as sent
FROM notifications
GROUP BY channel;
```

### Common Issues

| Issue | Solution |
|-------|----------|
| "Provider not configured" | Set `SMTP_ENABLED=true` (or TWILIO/FIREBASE) in `.env` |
| SMTP connection refused | Check `SMTP_HOST` and `SMTP_PORT`; ensure firewall allows outbound |
| Twilio 401 Unauthorized | Verify `TWILIO_ACCOUNT_SID` and `TWILIO_AUTH_TOKEN` |
| Firebase invalid token | Regenerate access token; tokens expire after 1 hour |
| Email goes to spam | Add SPF/DKIM records for your sender domain |

---

## Production Checklist

- [ ] Use production SMTP provider (AWS SES, SendGrid, etc.)
- [ ] Enable all required providers (`SMTP_ENABLED`, `TWILIO_ENABLED`, `FIREBASE_ENABLED`)
- [ ] Set production API credentials in secrets manager
- [ ] Configure CORS for frontend push notification URLs
- [ ] Set up alerting on notification failures
- [ ] Test sender domain reputation (for email)
- [ ] Configure rate limiting per recipient (anti-spam)
- [ ] Set up audit logging for sensitive notifications
- [ ] Monitor provider costs (Twilio/Firebase) daily
- [ ] Implement retry logic for failed notifications (already in Celery task)
- [ ] Set up log aggregation (ELK, DataDog, etc.)
- [ ] Test disaster recovery (provider outage)

---

## Extending with New Providers

To add a new provider (e.g., AWS SNS for SMS):

1. **Implement the interface:**

```python
from app.services.notification_providers import NotificationProvider

class AwsSnsProvider(NotificationProvider):
    channel = NotificationChannel.SMS
    
    async def send(self, recipient: str, payload: dict[str, Any]) -> DeliveryResult:
        # Implement SNS logic
        pass
```

2. **Add settings to config:**

```python
# app/core/config.py
aws_sns_enabled: bool = False
aws_sns_region: str = "us-east-1"
aws_sns_access_key: str | None = None
aws_sns_secret_key: str | None = None
```

3. **Register in NotificationService:**

```python
# app/services/notifications.py
if settings.aws_sns_enabled:
    providers[NotificationChannel.SMS] = AwsSnsProvider()
```

4. **Add to `.env.example` and deploy.**

---

## Questions?

- **Twilio Docs:** https://www.twilio.com/docs
- **Firebase Docs:** https://firebase.google.com/docs/cloud-messaging
- **SMTP Standards:** RFC 5321
- **OneTapGOV Issues:** Check GitHub issues or contact the team
