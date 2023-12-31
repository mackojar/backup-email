import imaplib
import mailbox
import getpass
import os
import re
from dotenv import load_dotenv

class BackupException(Exception):
  pass

class FolderInfo:
  def __init__(self, folderItem: bytes):
    folderItemRe = re.compile(r'\((?P<flags>[\S ]*)\) (?P<delim>[\S]+) (?P<name>.+)')
    folderMatch = re.search(folderItemRe, folderItem.decode("utf-8"))
    if not folderMatch:
      self.valid = False
      print(f"Unknown folder info: {folderItem}")
    folderDict = folderMatch.groupdict()
    self.valid = True
    self.name = self.trimQuote(folderDict["name"])
    self.delim = self.trimQuote(folderDict["delim"])
    self.flags = tuple(folderDict["flags"].split())

  def trimQuote(self, name: str) -> str:
    if name.startswith('"') and name.endswith('"'):
      name = name[1:-1]
    return name

def checkResponse(status: str, commandName: str):
  if status != "OK":
    raise BackupException(f"Error calling {commandName}")

def retrieveMessageIds(mail: imaplib.IMAP4_SSL) -> list[bytes]:
  status, messages = mail.search(None, "ALL")
  checkResponse(status, "retrieve mails")
  messageIds = messages[0].split()
  print(f"Found {len(messageIds)} messages")
  return messageIds

def saveMailbox(mail: imaplib.IMAP4_SSL, mboxFileName: str, messageIds: list[bytes]):
  mbox = mailbox.mbox(mboxFileName)
  mbox.clear()
  for messageId in messageIds:
    print(f"Reading mail {messageId.decode()}...", end="\r")
    status, msgData = mail.fetch(messageId, "(RFC822)")
    checkResponse(status, "retrieve message")
    rawEmail = msgData[0][1]
    msg = mailbox.mboxMessage(rawEmail)
    mbox.add(msg)
  print(" " * 70, end="\r")
  mbox.close()

def saveFolder(mail: imaplib.IMAP4_SSL, folderInfo: FolderInfo):
  LOCAL_MBOX_FOLDER = os.getenv("LOCAL_MBOX_FOLDER")
  folderFileName = folderInfo.name.replace(folderInfo.delim, '_')
  mboxFileName = f"{LOCAL_MBOX_FOLDER}/{folderFileName}.mbox"

  print(f"Saving folder {folderInfo.name} into {mboxFileName}...")
  mail.select(folderInfo.name, readonly=True)
  messageIds = retrieveMessageIds(mail)
  saveMailbox(mail, mboxFileName, messageIds)
  mail.close()
  print(f"All emails from {folderInfo.name} saved into {mboxFileName}")

def processFolder(mail: imaplib.IMAP4_SSL, folder: bytes):
  EXCLUDED_MAILBOXES = ["\\Archive", "\\Junk", "\\Trash", "\\Sent", "\\Drafts"]
  folderInfo = FolderInfo(folder)
  if not folderInfo.valid:
    return
  if any(item in EXCLUDED_MAILBOXES for item in folderInfo.flags):
    print(f"Ignoring folder: {folderInfo.name}")
    return
  saveFolder(mail, folderInfo)

def main():
  load_dotenv()
  EMAIL = os.getenv("EMAIL")
  IMAP_SERVER = os.getenv("IMAP_SERVER")
  PASSWORD = getpass.getpass(f"Password for {EMAIL} account:")

  LOCAL_MBOX_FOLDER = os.getenv("LOCAL_MBOX_FOLDER")
  os.makedirs(LOCAL_MBOX_FOLDER, exist_ok=True)

  mail = imaplib.IMAP4_SSL(IMAP_SERVER)
  mail.login(EMAIL, PASSWORD)

  status, folders = mail.list()
  checkResponse(status, "list folders")
  for folder in folders:
    processFolder(mail, folder)

  mail.logout()

if __name__ == "__main__":
  main()
