import logging
import os
import imaplib
from .folder_info import IMAPFolderInfo
from .config import Config
from .sync import syncMailbox
from .imap import checkResponse

_LOCAL_MBOX_FOLDER = os.getenv("LOCAL_MBOX_FOLDER")

def _setFileFoldersNames(folderInfo: IMAPFolderInfo):
  splitNames = folderInfo.name.split(folderInfo.delimiter)
  mboxFolderName = os.path.join(_LOCAL_MBOX_FOLDER, *splitNames[0:-1])
  mboxFileName = f"{splitNames[-1]}.mbox"
  cfgFileName = f"{splitNames[-1]}.config"
  folderInfo.setFileNames(mboxFolderName, mboxFileName, cfgFileName)

def _selectFolder(mail: imaplib.IMAP4, folderInfo: IMAPFolderInfo, config: Config) -> bool:
  status, _ = mail.select(folderInfo.name, readonly=True)
  checkResponse(status, 'select folder')
  _, uidValidityBytes = mail.response('UIDVALIDITY')
  _, uidNextBytes = mail.response('UIDNEXT')
  uidValidity = uidValidityBytes[0].decode()
  uidNext = uidNextBytes[0].decode()
  if uidNext != config.config.uidNext or uidValidity != config.config.uidValidity:
    logging.info("Folder has changed: to be synchronized")
    config.updateUIDs(uidValidity, uidNext)
    return True
  logging.info("Folder has not changed: no further action")
  return False

def _syncFolder(mail: imaplib.IMAP4, folderInfo: IMAPFolderInfo):
  mboxFileName = os.path.join(folderInfo.mboxFolderName, folderInfo.mboxFileName)
  logging.info(f"-> Syncing IMAP folder {folderInfo.name} into {mboxFileName}...")
  config = Config(folderInfo)
  if _selectFolder(mail, folderInfo, config):
    syncMailbox(mail, mboxFileName)
    config.write()
  mail.close()  
  logging.info(f"<- Emails from {folderInfo.name} synced with {mboxFileName}")

def processFolder(mail: imaplib.IMAP4, folder: bytes):
  EXCLUDED_MAILBOXES = ["\\Archive", "\\Junk", "\\Trash", "\\Sent", "\\Drafts"]
  folderInfo = IMAPFolderInfo(folder)
  if not folderInfo.valid:
    logging.warn(f"Ignoring folder (not valid): {folderInfo.name}")
    return
  if any(item in EXCLUDED_MAILBOXES for item in folderInfo.flags):
    logging.info(f"Ignoring folder: {folderInfo.name}")
    return
  _setFileFoldersNames(folderInfo)
  _syncFolder(mail, folderInfo)
