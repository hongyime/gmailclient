"""Send one UTF-8 text message through Gmail when explicitly run from the CLI."""
import argparse
import os
from pathlib import Path
import smtplib
import ssl
import sys
from email.message import EmailMessage
from typing import List, Optional


def main(argv: Optional[List[str]] = None) -> int:
    """Validate local input, send one message, and return an honest exit status."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--message', type=Path, default=Path('message.txt'),
                        help='UTF-8 body file (default: message.txt)')
    parser.add_argument('--subject', default='Message', help='Message subject')
    args = parser.parse_args(argv)
    if not args.to.strip():
        print('Provide a recipient email address with --to.', file=sys.stderr)
        return 2
    sender = os.environ.get('GMAIL_ADDRESS', '').strip()
    password = os.environ.get('GMAIL_APP_PASSWORD', '').strip()
    if not sender or not password:
        print('Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD before sending.', file=sys.stderr)
        return 2

    try:
        body = args.message.read_text(encoding='utf-8')
        message = EmailMessage()
        message['From'] = sender
        message['To'] = args.to
        message['Subject'] = args.subject
        message.set_content(body)
    except (OSError, UnicodeError, ValueError):
        print('Check the UTF-8 message file and single-line message headers.', file=sys.stderr)
        return 2

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=30,
                              context=ssl.create_default_context()) as server:
            server.login(sender, password)
            server.send_message(message)
    except smtplib.SMTPAuthenticationError:
        print('Gmail authentication failed. Check the account and app password.', file=sys.stderr)
        return 1
    except (smtplib.SMTPException, OSError):
        print('Email delivery failed. Check the connection and recipient.', file=sys.stderr)
        return 1
    print('Message accepted by Gmail for delivery.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
