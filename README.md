# Backup emails
Saves all your mailboxes from IMAP account into mbox files.
It saves each mailbox into separate .mbox file in the given folder.
It uses SSL connection to connect to your IMAP server.

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
LOCAL_MBOX_FOLDER = "<folder name to store all emails>"
IMAP_SERVER = "<imap server>"
```

# Run your backup
```
python backup-email.py
```
Script will ask for the password for your email account.
Enjoy!
