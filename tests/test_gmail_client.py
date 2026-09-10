"""Validate explicit email delivery with synthetic files and a fake SMTP server."""
import contextlib
import io
import os
from pathlib import Path
import smtplib
import ssl
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

with patch.object(smtplib, 'SMTP_SSL', side_effect=AssertionError('Import must not connect')):
    with patch('builtins.open', side_effect=AssertionError('Import must not read message files')):
        import gmail_client


class GmailClientTests(unittest.TestCase):
    """Exercise startup, validation, message encoding and connection cleanup."""

    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.message = Path(self.temporary.name) / 'synthetic.txt'
        self.message.write_text('A synthetic message with prawn 🦐.\n', encoding='utf-8')
        self.environment = patch.dict(os.environ, {
            'GMAIL_ADDRESS': 'sender@example.invalid', 'GMAIL_APP_PASSWORD': 'synthetic-secret',
        }, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.smtp_patch = patch.object(gmail_client.smtplib, 'SMTP_SSL')
        self.smtp = self.smtp_patch.start()
        self.addCleanup(self.smtp_patch.stop)
        self.output = io.StringIO()
        self.errors = io.StringIO()

    def run_client(self, extra=None):
        """Run a synthetic CLI request with stdout and stderr captured."""
        args = ['--to', 'recipient@example.invalid', '--message', str(self.message)]
        with contextlib.redirect_stdout(self.output), contextlib.redirect_stderr(self.errors):
            return gmail_client.main(args + (extra or []))

    def test_import_uses_standard_library_email_and_does_not_send(self):
        """Imports must work from the checkout without opening a network connection."""
        result = subprocess.run([
            sys.executable, '-B', '-c',
            "import socket, builtins; deny = lambda *a, **kw: (_ for _ in ()).throw("
            "RuntimeError('file/network access disabled')); socket.socket.connect = deny; "
            "builtins.open = deny; import smtplib, email.mime.text, gmail_client",
        ], cwd=Path(__file__).resolve().parents[1], text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_help_needs_no_credentials_or_connection(self):
        """Help remains usable before account configuration."""
        with patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(self.output):
            with self.assertRaises(SystemExit) as raised:
                gmail_client.main(['--help'])
        self.assertEqual(raised.exception.code, 0)
        self.smtp.assert_not_called()

    def test_missing_credentials_fail_before_connecting(self):
        """Incomplete configuration cannot trigger SMTP or report success."""
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(self.run_client(), 2)
        self.smtp.assert_not_called()

    def test_missing_message_fails_before_connecting(self):
        """A missing input file is reported before authentication."""
        self.assertEqual(self.run_client(['--message', str(self.message.parent / 'absent.txt')]), 2)
        self.smtp.assert_not_called()

    def test_blank_recipient_fails_before_reading_or_connecting(self):
        """An empty recipient must not read a message or contact Gmail."""
        with patch.object(Path, 'read_text', side_effect=AssertionError('No file read expected')):
            self.assertEqual(self.run_client(['--to', '  ']), 2)
        self.smtp.assert_not_called()

    def test_message_preserves_unicode_and_closes_tls_connection(self):
        """Delivery carries the chosen body/headers through a bounded TLS session."""
        self.assertEqual(self.run_client(['--subject', 'Synthetic subject']), 0)
        args, kwargs = self.smtp.call_args
        self.assertEqual(args, ('smtp.gmail.com', 465))
        self.assertEqual(kwargs['timeout'], 30)
        self.assertEqual(kwargs['context'].verify_mode, ssl.CERT_REQUIRED)
        client = self.smtp.return_value.__enter__.return_value
        client.login.assert_called_once_with('sender@example.invalid', 'synthetic-secret')
        message = client.send_message.call_args.args[0]
        self.assertEqual(message['From'], 'sender@example.invalid')
        self.assertEqual(message['To'], 'recipient@example.invalid')
        self.assertEqual(message['Subject'], 'Synthetic subject')
        self.assertEqual(message.get_content(), self.message.read_text(encoding='utf-8'))
        self.smtp.return_value.__exit__.assert_called_once()

    def test_auth_failure_returns_failure_without_printing_secrets(self):
        """Authentication failures close the session and keep provider details private."""
        client = self.smtp.return_value.__enter__.return_value
        client.login.side_effect = smtplib.SMTPAuthenticationError(535, b'synthetic-secret')
        self.assertEqual(self.run_client(), 1)
        client.send_message.assert_not_called()
        self.smtp.return_value.__exit__.assert_called_once()
        self.assertNotIn('synthetic-secret', self.errors.getvalue())
        self.assertNotIn('synthetic-secret', self.output.getvalue())

    def test_header_line_breaks_are_rejected_before_connecting(self):
        """A subject cannot introduce a second header."""
        self.assertEqual(self.run_client(['--subject', 'Subject\nBcc: extra@example.invalid']), 2)
        self.smtp.assert_not_called()


if __name__ == '__main__':
    unittest.main()
