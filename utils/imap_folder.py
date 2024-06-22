import logging
import os
import re
import imaplib
from .sync import syncMailbox

class FolderInfo:
  def __init__(self, folderItem: bytes):
    folderItemRe = re.compile(r'\((?P<flags>[\S ]*)\) (?P<delim>[\S]+) (?P<name>.+)')
    folderMatch = re.search(folderItemRe, folderItem.decode("utf-8"))
    if not folderMatch:
      self.valid = False
      logging.warn(f"Unknown folder info: {folderItem}")
    folderDict = folderMatch.groupdict()
    self.valid = True
    self.name = self._trimQuote(folderDict["name"])
    self.delim = self._trimQuote(folderDict["delim"])
    self.flags = tuple(folderDict["flags"].split())

  def _trimQuote(self, name: str) -> str:
    if name.startswith('"') and name.endswith('"'):
      name = name[1:-1]
    return name


def _syncFolder(mail: imaplib.IMAP4_SSL, folderInfo: FolderInfo):
  LOCAL_MBOX_FOLDER = os.getenv("LOCAL_MBOX_FOLDER")
  folderFileName = folderInfo.name.replace(folderInfo.delim, '_')
  mboxFileName = f"{LOCAL_MBOX_FOLDER}/{folderFileName}.mbox"
  logging.info(f"-> Syncing IMAP folder {folderInfo.name} into {mboxFileName}...")
  
  mail.select(folderInfo.name, readonly=True)
  syncMailbox(mail, mboxFileName)
  mail.close()
  
  logging.info(f"<- Emails from {folderInfo.name} synced with {mboxFileName}")


def processFolder(mail: imaplib.IMAP4_SSL, folder: bytes):
  EXCLUDED_MAILBOXES = ["\\Archive", "\\Junk", "\\Trash", "\\Sent", "\\Drafts"]
  folderInfo = FolderInfo(folder)
  if not folderInfo.valid:
    logging.warn(f"Ignoring folder (not valid): {folderInfo.name}")
    return
  if any(item in EXCLUDED_MAILBOXES for item in folderInfo.flags):
    logging.info(f"Ignoring folder: {folderInfo.name}")
    return
  _syncFolder(mail, folderInfo)
