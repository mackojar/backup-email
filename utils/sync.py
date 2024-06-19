import mailbox
import imaplib
from .imap import checkResponse

class MailSyncInfo:
  def __init__(self, mboxId: str, existsInIMAP: bool):
    self.mboxId = mboxId
    self.existsInMBox = True
    self.existsInIMAP = existsInIMAP


def _getMessageID(mail: imaplib.IMAP4_SSL, messageId) -> str:
  status, message = mail.fetch(messageId, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
  checkResponse(status, "retrieve mail Message-Id")
  msgId = message[0][1]   # b'Message-ID: <xxxxx@mail.gmail.com>\r\n\r\n'
  l = msgId.find(b'<')
  r = msgId.find(b'>')
  return msgId[l:r+1].decode()   # <xxxxx@mail.gmail.com>

def _createMsgsInfo(mbox: mailbox.mbox) -> dict[str, MailSyncInfo]:
  msgIdMap = {}
  for (id, email) in mbox.items():
    msgIdMap[email.get('Message-Id')] = MailSyncInfo(id, False)
  return msgIdMap

def _addMissingIMAPEmails(mail: imaplib.IMAP4_SSL, imapIds: list[bytes], mbox: mailbox.mbox, mboxMsgsInfo: dict[str, MailSyncInfo]):
  for imapId in imapIds:
    messageId = _getMessageID(mail, imapId)
    if messageId in mboxMsgsInfo:
      mboxMsgsInfo[messageId].existsInIMAP = True
    else:
      print(f"Reading IMAP email {imapId}:{messageId}...", end="\r")
      status, msgData = mail.fetch(imapId, "(RFC822)")
      checkResponse(status, "retrieve message")
      rawEmail = msgData[0][1]
      msg = mailbox.mboxMessage(rawEmail)
      mboxId = mbox.add(msg)
      mboxMsgsInfo[messageId] = MailSyncInfo(mboxId, True)
  print(" " * 70, end="\r")

def _removeUnwantedMBoxEmails(mbox: mailbox.mbox, mboxMsgsInfo: dict[str, MailSyncInfo]):
  for mailSyncInfo in mboxMsgsInfo.values():
    if mailSyncInfo.existsInIMAP == False:
      print(f"Remove mbox email {mailSyncInfo.mboxId}...", end="\r")
      mbox.remove(mailSyncInfo.mboxId)
  print(" " * 70, end="\r")

def _getIMAPIds(mail: imaplib.IMAP4_SSL) -> list[bytes]:
  status, messages = mail.search(None, "ALL")
  checkResponse(status, "retrieve mail IDs")
  imapMessageIds = messages[0].split()
  print(f"Found {len(imapMessageIds)} messages")
  return imapMessageIds

def syncMailbox(mail: imaplib.IMAP4_SSL, mboxFileName: str):
  imapIds = _getIMAPIds(mail)
  mbox = mailbox.mbox(mboxFileName)
  mboxMsgsInfo = _createMsgsInfo(mbox)
  _addMissingIMAPEmails(mail, imapIds, mbox, mboxMsgsInfo)
  _removeUnwantedMBoxEmails(mbox, mboxMsgsInfo)
  mbox.flush()
  mbox.close()
