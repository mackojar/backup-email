# Backup emails
Saves all your mailboxes from IMAP account into .mbox files.
It saves each mailbox into separate .mbox file in the given folder.
It uses SSL connection to connect to your IMAP server.
It ignores some special mailboxes: Archive, Junk, Trash, Sent, and Drafts.

During backup process emails are synced from IMAP (mail server) to MBOX (local file).

# Prerequisites
1. Create Python virtual env:
```
python -m venv env
```
2. Activate virtual environment
```
. ./env/bin/activate
```
3. Install dependencies
```
pip install -r requirements.txt
```
4. Create .env file with the following content:
```
EMAIL = "<your email>"
IMAP_SERVER = "<your imap server hostname>"
LOCAL_MBOX_FOLDER = "<local folder name to store all emails/mailboxes>"
```

# Run your backup
```
python backup_email.py
```
Script will ask for the password for your email account.

Enjoy!
