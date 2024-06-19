from exceptions.exceptions import BackupException

def checkResponse(status: str, commandName: str):
  if status != "OK":
    raise BackupException(f"Error calling {commandName}")
