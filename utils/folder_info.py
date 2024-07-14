import logging
import re

class IMAPFolderInfo:

  ''' IMAP info'''
  @property
  def name(self) -> str:
    return self._name

  @property
  def delimiter(self) -> str:
    return self._delimiter

  @property
  def flags(self) -> tuple[str]:
    return self._flags

  ''' local OS info '''
  @property
  def mboxFolderName(self) -> str:
    return self._mboxFolderName

  @property
  def mboxFileName(self) -> str:
    return self._mboxFileName

  @property
  def cfgFileName(self) -> str:
    return self._cfgFileName

  def __init__(self, folderItem: bytes):
    ''' ex.: b'(\\HasChildren) "/" "folder_name"' '''
    folderItemRe = re.compile(r'\((?P<flags>[\S ]*)\) (?P<delim>[\S]+) (?P<name>.+)')
    folderMatch = re.search(folderItemRe, folderItem.decode("utf-8"))
    if not folderMatch:
      self.valid = False
      logging.warn(f"Unknown folder info: {folderItem}")
    folderDict = folderMatch.groupdict()
    self.valid = True
    self._name = self._trimQuote(folderDict["name"])
    self._delimiter = self._trimQuote(folderDict["delim"])
    self._flags = tuple(folderDict["flags"].split())

  def _trimQuote(self, name: str) -> str:
    if name.startswith('"') and name.endswith('"'):
      name = name[1:-1]
    return name

  def setFileNames(self, mboxFolderName: str, mboxFileName: str, cfgFileName: str):
    self._mboxFolderName = mboxFolderName
    self._mboxFileName = mboxFileName
    self._cfgFileName = cfgFileName
