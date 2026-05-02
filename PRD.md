# PRD: gmailclient

## Overview
A minimal Python script that reads the content of a `message.txt` file and sends it as an email via Gmail SMTP SSL (port 465). Designed as a simple command-line email sender for automation — e.g., sending log files or daily reports to yourself. Intended to be modified with real credentials before use.

## Goals
- Read email body from `message.txt`
- Authenticate to Gmail SMTP using provided credentials
- Send email to a specified recipient with a timestamped subject line
- Handle send failure gracefully (print exception)

## Non-Goals
- HTML email or rich formatting
- Multiple recipients
- Attachments
- Email scheduling
- OAuth (uses app password / less-secure access)

## User Stories
- As a developer, I want a simple script to email myself log output from a Python process.
- As a sysadmin, I want to automate sending daily reports via Gmail without a full email library.

## Tech Stack
- **Language**: Python 3.x
- **Libraries**: `smtplib` (stdlib), `ssl` (stdlib), `email.mime.*` (stdlib), `os`, `datetime`

## Architecture
```
gmailclient/
├── email.py       # Main send script
├── message.txt    # Email body content (user-created)
└── requirements.txt
```

**Flow:**
1. Read `message.txt` content
2. Create SSL context via `ssl.create_default_context()`
3. Connect to `smtp.gmail.com:465` via `smtplib.SMTP_SSL`
4. Login with hardcoded (replaced) email + password
5. Build `MIMEMultipart` message with from/to/subject/body
6. Subject format: `MM/DD/YYYY, HH:MM:SS logs`
7. `sendmail()` and `quit()`
8. Print exception on failure

## Data / Config
| Item | Description |
|------|-------------|
| `message.txt` | Email body text — created by user |
| Sender email | Hardcoded in script (replace before running) |
| Sender password | Hardcoded in script (use Gmail App Password) |
| Recipient email | Hardcoded in script (replace before running) |

**Replace these 4 values in `email.py` before running:**
- `server.login('email', 'password')` — your Gmail + App Password
- `msg['From'] = "from who name"`
- `msg['To'] = "send to email"`
- `server.sendmail('from who email', 'send to email', text)`

## Deployment / Run
```bash
# Create message.txt with email body content
echo "Hello from the script" > message.txt
python email.py
```

## Constraints & Notes
- **Gmail App Password required**: Google disabled "less secure app access" — you must use a 2FA-enabled Google account with an App Password
- **Hardcoded credentials**: script requires manual credential insertion — do not commit with real credentials
- **No attachment support**: sends plain text body only
- **Port 465 (SSL)**: uses SMTP_SSL, not STARTTLS
- **Subject**: auto-stamped with current datetime — useful for identifying when the message was sent
