from dataclasses import dataclass, asdict
import json
import os
from .folder_info import IMAPFolderInfo

@dataclass
class ConfigData:
  uidNext: str
  uidValidity: str


class Config:

  @property
  def config(self) -> ConfigData:
    return self._config

  _cfgFileName: str

  def __init__(self, imapFolderInfo: IMAPFolderInfo):
    self._checkFolder(imapFolderInfo)
    self._cfgFileName = os.path.join(imapFolderInfo.mboxFolderName, imapFolderInfo.cfgFileName)
    if os.path.isfile(self._cfgFileName):
      with open(self._cfgFileName) as dataFile:
        configFile = json.load(dataFile)
        self._config = ConfigData(configFile['uidNext'], configFile['uidValidity'])
    else:
      self._config = ConfigData('', '')
      

  def _checkFolder(self, imapFolderInfo: IMAPFolderInfo):
    if not os.path.isdir(imapFolderInfo.mboxFolderName):
      os.makedirs(imapFolderInfo.mboxFolderName)

  def write(self):
    with open(self._cfgFileName, 'w') as outFile:
      json.dump(asdict(self._config), outFile, indent = 2, ensure_ascii = False)

  def updateUIDs(self, uidValidity, uidNext):
    self._config.uidValidity = uidValidity
    self._config.uidNext = uidNext

