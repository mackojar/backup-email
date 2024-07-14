import logging
import imaplib
import getpass
import os
from dotenv import load_dotenv
import utils.folder as folderProcessor
import utils.imap as imap

logging.basicConfig(format='%(asctime)s - %(message)s', level=logging.INFO)

def main():
  logging.info("Sync emails started...")
  load_dotenv()
  EMAIL = os.getenv("EMAIL")
  IMAP_SERVER = os.getenv("IMAP_SERVER")
  PASSWORD = os.getenv('PASSWORD')
  if PASSWORD == None:
    PASSWORD = getpass.getpass(f"Password for {EMAIL} account:")

  LOCAL_MBOX_FOLDER = os.getenv("LOCAL_MBOX_FOLDER")
  os.makedirs(LOCAL_MBOX_FOLDER, exist_ok=True)

  mail = imaplib.IMAP4_SSL(IMAP_SERVER)
  mail.login(EMAIL, PASSWORD)

  status, folders = mail.list()
  imap.checkResponse(status, "list folders")
  logging.info(f"Found {len(folders)} folders")
  for folder in folders:
    folderProcessor.processFolder(mail, folder)

  mail.logout()
  logging.info("Sync emails finished")

if __name__ == "__main__":
  main()
