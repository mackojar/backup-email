import logging
import mailbox
import imaplib
from typing import List, Tuple
from .imap import checkResponse

class MailSyncInfo:
  def __init__(self, mboxId: str, existsInIMAP: bool):
    self.mboxId = mboxId
    self.existsInMBox = True
    self.existsInIMAP = existsInIMAP


def _convertMsgId(imapMessageId: bytes): # b'Message-ID: <xxxxx@mail.gmail.com>\r\n\r\n'
  l = imapMessageId.find(b'<')
  r = imapMessageId.find(b'>')
  return imapMessageId[l:r+1].decode()   # <xxxxx@mail.gmail.com>

def _getMessageIDs(mail: imaplib.IMAP4, messageIds: list[bytes]) -> List[Tuple[bytes, str]]:
  logging.info("Retrieve IMAP message IDs...")
  criteria = messageIds[0] + b':' + messageIds[-1]
  status, messages = mail.fetch(criteria, '(BODY[HEADER.FIELDS (MESSAGE-ID)])')
  checkResponse(status, "retrieve mail Message-Ids")
  messagesOnly = filter(lambda m: isinstance(m, tuple), messages)
  result = []
  for message in messagesOnly:
    imapId = message[0].split(b' ')[0]
    result.append( (imapId, _convertMsgId(message[1])))
  return result

def _createMsgsInfo(mbox: mailbox.mbox) -> dict[str, MailSyncInfo]:
  msgIdMap = {}
  for (id, email) in mbox.items():
    msgIdMap[email.get('Message-Id')] = MailSyncInfo(id, False)
  return msgIdMap

def _addMissingIMAPEmails(mail: imaplib.IMAP4, imapIds: list[bytes], mbox: mailbox.mbox, mboxMsgsInfo: dict[str, MailSyncInfo]):
  if len(imapIds) == 0:
    return
  logging.info("Retrieve missing IMAP emails...")
  messageInfos = _getMessageIDs(mail, imapIds)
  for messageInfo in messageInfos:
    imapMsgId = messageInfo[0]
    messageId = messageInfo[1]
    logging.info(f"Check IMAP email {imapMsgId}...")
    if messageId in mboxMsgsInfo:
      mboxMsgsInfo[messageId].existsInIMAP = True
    else:
      logging.info(f"Retrieving IMAP email {imapMsgId}:{messageId}...")
      status, msgData = mail.fetch(imapMsgId, "(RFC822)")
      checkResponse(status, "retrieve message")
      rawEmail = msgData[0][1]
      msg = mailbox.mboxMessage(rawEmail)
      mboxId = mbox.add(msg)
      mboxMsgsInfo[messageId] = MailSyncInfo(mboxId, True)

def _removeUnwantedMBoxEmails(mbox: mailbox.mbox, mboxMsgsInfo: dict[str, MailSyncInfo]):
  logging.info("Remove unwanted MBOX emails...")
  for mailSyncInfo in mboxMsgsInfo.values():
    if mailSyncInfo.existsInIMAP == False:
      logging.info(f"Remove MBOX email {mailSyncInfo.mboxId}")
      mbox.remove(mailSyncInfo.mboxId)

def _getIMAPIds(mail: imaplib.IMAP4) -> list[bytes]:
  status, messages = mail.search(None, "ALL")
  checkResponse(status, "retrieve mail IDs")
  imapMessageIds = messages[0].split()
  logging.info(f"Found {len(imapMessageIds)} IMAP messages")
  return imapMessageIds

def syncMailbox(mail: imaplib.IMAP4, mboxFileName: str):
  imapIds = _getIMAPIds(mail)
  mbox = mailbox.mbox(mboxFileName)
  mboxMsgsInfo = _createMsgsInfo(mbox)
  _addMissingIMAPEmails(mail, imapIds, mbox, mboxMsgsInfo)
  _removeUnwantedMBoxEmails(mbox, mboxMsgsInfo)
  mbox.flush()
  mbox.close()
