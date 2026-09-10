# Gmail client

Send one UTF-8 text file as an email through Gmail from an explicit Python command.
The client uses Python's standard library and runs locally.

## Setup

Use Python 3.12 or newer. No third-party packages are required.

Set `GMAIL_ADDRESS` and `GMAIL_APP_PASSWORD` in the environment of the terminal
that will run the command. This client uses SMTP app-password authentication;
it does not implement Google's browser sign-in flow. Google requires 2-Step
Verification for app passwords, and some account policies make them unavailable.
See [Google's app-password instructions](https://support.google.com/accounts/answer/185833)
for account eligibility and setup.

Example in PowerShell 7:

```powershell
$env:GMAIL_ADDRESS = 'you@example.com'
$env:GMAIL_APP_PASSWORD = Read-Host 'Gmail app password' -MaskInput
```

Keep the credential out of source files and command arguments. An `.env` file is
not loaded automatically.

## Usage

Create a UTF-8 text file containing the message, then run:

```powershell
python gmail_client.py --to recipient@example.com --message message.txt --subject 'Hello'
```

`--to` is required. The body defaults to `message.txt` in the current directory;
the subject defaults to `Message`. Each successful command submits one message.
It uses TLS with certificate verification on `smtp.gmail.com:465`, a 30-second
socket timeout, and closes the connection on success or failure.

Exit status is `0` when Gmail accepts the message, `1` for a connection or SMTP
failure, and `2` for invalid arguments, configuration or local input. Acceptance
does not guarantee that the recipient has received or read the message.

```powershell
python gmail_client.py --help
```

Help and module import do not read message files or connect to Gmail. The entry
point is named `gmail_client.py` because `email.py` masks Python's standard
`email` package and prevents SMTP imports from working.

## Checks

```powershell
python -B -m unittest discover -s tests -v
```

Tests use temporary synthetic messages and a fake SMTP server. They check import
behavior, configuration/input errors, Unicode content, TLS settings, cleanup and
failure exit codes. They do not verify a real account or send a test email.

## License

Apache-2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE).
