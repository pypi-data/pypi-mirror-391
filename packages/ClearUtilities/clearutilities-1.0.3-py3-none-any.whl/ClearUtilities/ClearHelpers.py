from pathlib import Path
from datetime import datetime, timezone
import pytz
import inspect
from slugify import slugify
import sys
import json
import socket
from urllib.parse import urlparse
import git

class ClearHelpers:
	@staticmethod
	#pattern:str = "FOXCAR.ARP.POSPAY1.{DT:EST:%Y%m%d_%H%M%S}.DATAFILE"
	def ReplaceTimestamp(pattern:str) -> str:
		returnValue:str = ""
		if ("{DT" in pattern):
			beginIndex:int = pattern.find("{DT")
			endIndex:int = pattern.find("}", beginIndex)
			if (beginIndex != (-1) and endIndex != (-1)):
				prefix:str = pattern[:beginIndex]
				suffix:str = pattern[endIndex+1:]
				dtStatement:str = pattern[beginIndex+1:endIndex]
				dtElements:list[str] = dtStatement.split(":")
				timeFormat:str = "%Y%m%d%H%M%S"
				useTimezone:timezone = datetime.now().astimezone().tzinfo
				if (len(dtElements) == 2):
					timeFormat = dtElements[1]
				elif (len(dtElements) == 3):
					match (dtElements[1]):
						case "L" | "l":
							useTimezone:timezone = datetime.now().astimezone().tzinfo
						case "Z" | "z" | "UTC" | "utc":
							useTimezone:timezone = timezone.utc
						case _:
							useTimezone:timezone = pytz.timezone(dtElements[1])
					timeFormat = dtElements[2]
				timestamp:str  = datetime.now(useTimezone).strftime(timeFormat)
				returnValue = f"{prefix}{timestamp}{suffix}"
		return returnValue

	@staticmethod
	#pattern:str = "FOXCAR.ARP.POSPAY1.{DT:%Y%m%d_%H%M%S}.DATAFILE"
	def ReplaceTimestampWithDateTime(pattern:str, dt:datetime) -> str:
		returnValue:str = ""
		if ("{DT" in pattern):
			beginIndex:int = pattern.find("{DT")
			endIndex:int = pattern.find("}", beginIndex)
			if (beginIndex != (-1) and endIndex != (-1)):
				prefix:str = pattern[:beginIndex]
				suffix:str = pattern[endIndex+1:]
				dtStatement:str = pattern[beginIndex+1:endIndex]
				dtElements:list[str] = dtStatement.split(":")
				timeFormat:str = "%Y%m%d%H%M%S"
				useTimezone:timezone = dt.astimezone().tzinfo
				if (len(dtElements) == 2):
					timeFormat = dtElements[1]
				elif (len(dtElements) == 3):
					match (dtElements[1]):
						case "L" | "l":
							useTimezone:timezone = datetime.now().astimezone().tzinfo
						case "Z" | "z" | "UTC" | "utc":
							useTimezone:timezone = timezone.utc
						case _:
							useTimezone:timezone = pytz.timezone(dtElements[1])
					timeFormat = dtElements[2]
				if (useTimezone != dt.astimezone().tzinfo):
					timestamp:str  = dt.astimezone(useTimezone).strftime(timeFormat)
				else:
					timestamp:str  = dt.strftime(timeFormat)
				returnValue = f"{prefix}{timestamp}{suffix}"
		return returnValue

	@staticmethod
	def ConvertToUTCEvenIfNaive(localized:datetime) -> datetime:
		returnValue:datetime = None
		if (localized.tzinfo == timezone.utc):
			returnValue = localized
		else:
			aware:datetime = None
			if (localized.tzinfo is not None):
				aware = localized
			else:
				aware = datetime(
					year=localized.year,
					month=localized.month,
					day=localized.day,
					hour=localized.hour,
					minute=localized.minute,
					second=localized.second,
					microsecond=localized.microsecond,
					tzinfo=datetime.now().astimezone().tzinfo
				)
			returnValue = aware.astimezone(timezone.utc)
		return returnValue

	@staticmethod
	def GetPathPartsFromRight(path:Path|str, numberOfElements:int, separator:str = "/", removeFileExtension:bool = False) -> str:
		returnValue:str = ""
		elementIndex:int = 0
		if (not isinstance(path, Path)):
			path = Path(path)
		if (removeFileExtension):
			path = path.with_suffix("")
		for element in Path(path).parts[::-1]:
			elementIndex += 1
			if (elementIndex == 1 and elementIndex <= numberOfElements):
				returnValue = element
			else:
				returnValue = f"{element}{separator}{returnValue}"
			if (elementIndex >= numberOfElements):
				break
		return returnValue

	@staticmethod
	def GetPathPartsFromLeft(path:str, numberOfElements:int, separator:str = "/") -> str:
		returnValue:str = ""
		elementIndex:int = 0
		for element in Path(path).parts:
			elementIndex += 1
			if (elementIndex == 1 and elementIndex <= numberOfElements):
				returnValue = element
			else:
				returnValue = f"{returnValue}{separator}{element}"
			if (elementIndex >= numberOfElements):
				break
		return returnValue

	@staticmethod
	def AddHostNameToSQLServerConnectionString(connectionString:str, hostName:str = None) -> str:
		if (hostName is None):
			hostName = Utilities.GetHostName()
		returnValue:str = connectionString
		returnValue += f"Workstation ID={hostName};"
		return returnValue

	@staticmethod
	def AddAppToSQLServerConnectionString(connectionString:str, appName:str= None) -> str:
		if (appName is None):
			appName = Utilities.GetPathPartsFromRight(sys.argv[0], 3, "/")
		returnValue:str = connectionString
		returnValue += f"Application Name={appName};"
		return returnValue

	@staticmethod
	def AddAppToPostgreSQLConnectionString(connectionString:str, appName:str= None) -> str:
		if (appName is None):
			appName = Utilities.GetPathPartsFromRight(sys.argv[0], 3, "/")
		returnValue:str = connectionString
		returnValue += f" application_name=\"{appName}\""
		returnValue += f" fallback_application_name=\"{appName}\""
		return returnValue

	@staticmethod
	def ParsePostgreSQLConnectionString(connectionString:str, removeSensitiveInfo:bool = False) -> dict:
		returnValue:dict = dict()
		for keyValue in connectionString.split(" "):
			keyValue = keyValue.strip()
			if (keyValue):
				keyValuePair:list = keyValue.split("=")
				key:str = ""
				value:str = ""
				if (len(keyValuePair) == 2):
					key = keyValuePair[0].strip()
					value = keyValuePair[1].strip()
					returnValue.update({key: value})
				elif (len(keyValuePair) == 1):
					key = keyValuePair[0].strip()
					value = ""
					returnValue.update({key: value})
		if (removeSensitiveInfo):
			returnValue.pop("password")
		return returnValue

	@staticmethod
	def ParseSQLServerConnectionString(connectionString:str, removeSensitiveInfo:bool = False) -> dict:
		returnValue:dict = dict()
		for keyValue in connectionString.split(";"):
			keyValue = keyValue.strip()
			if (keyValue):
				keyValuePair:list = keyValue.split("=")
				key:str = ""
				value:str = ""
				if (len(keyValuePair) == 2):
					key = keyValuePair[0].strip()
					value = keyValuePair[1].strip()
					returnValue.update({key: value})
				elif (len(keyValuePair) == 1):
					key = keyValuePair[0].strip()
					value = ""
					returnValue.update({key: value})
		if (removeSensitiveInfo):
			returnValue.pop("Password")
		return returnValue

	@staticmethod
	def ParseURIString(uriString:str, removeSensitiveInfo:bool = False) -> dict:
		returnValue:dict = dict()
		parsedSFTPURI = urlparse(uriString)
		returnValue.update({
			"hostname": parsedSFTPURI.hostname,
			"port": parsedSFTPURI.port,
			"username": parsedSFTPURI.username,
			"path": parsedSFTPURI.path
		})
		if (not removeSensitiveInfo):
			returnValue.update({ "password": parsedSFTPURI.password })
		return returnValue

	@staticmethod
	def GetRepoPath(filePath:Path = None) -> Path:
		"""Returns the first found repo path while traversing up the dir tree.
		The returned path is the parent of the first found ".git" directory.

		Keyword arguments:
		filePath -- the file (or directory) path to begin searching from. If None, then sys.argv[0] is used
		"""
		returnValue:Path = None
		if (not filePath):
			filePath = Path(sys.argv[0])
		try:
			gitDirPath = git.Repo(Path(filePath), search_parent_directories=True).git_dir
			if (gitDirPath and Path(gitDirPath).exists() and Path(gitDirPath).is_dir()):
				returnValue = Path(gitDirPath).parent
		except:
			returnValue = None
		return returnValue

	@staticmethod
	def ResolveSibling(relativePath:Path, absolutePath:Path = None) -> Path:
		"""Returns the absolute path of a relative path in relation to the absolute path.

		Keyword arguments:
		relativePath -- the path to resolve
		absolutePath -- the path to resolve by. If None, then sys.argv[0] is used
		"""
		if (absolutePath is None):
			absolutePath = Path(sys.argv[0]).absolute()
		if (absolutePath.is_file()):
			absolutePath = absolutePath.parent
		returnValue:Path = absolutePath.joinpath(relativePath).resolve()
		return returnValue

	@staticmethod
	def GetValidFileName(name:str):
		"""
		Normalizes string, converts to lowercase, removes non-alpha characters,
		and converts spaces to hyphens.
		"""
		return slugify(name)

	@staticmethod
	def GetHostName() -> str:
		return socket.gethostname().lower()

	@staticmethod
	def GetExecutingScript() -> str:
		return  str(Path(sys.argv[0]))

	@staticmethod
	def GetLineNumber() -> int:
		return inspect.currentframe().f_back.f_lineno

	@staticmethod
	def Debug(text:str, data:dict|None=None) -> None:
		"""
		Prints out the text provided, the current time in UTC, and a reference to the current file line.

		Parameters:
			text (str): The text to print to the console.
			data (dict) optional: Additional name/value paris to print to the console.

		Returns: None
		"""
		currentFrame = inspect.currentframe().f_back
		print("{0}\n  File: \"{1}\", line {2}\n  Time: {3}".format(
			text,
			currentFrame.f_code.co_filename,
			currentFrame.f_lineno,
			datetime.now(tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")))
		if (data is not None):
			if (len(data) > 0):
				print("  Data".ljust(20, "."))
				maxKeyLen:int = max([len(str(key)) for key in data.keys()])
				print("\n".join(["    {0}: {1}".format(
						"{0}".format(str(key)).ljust(maxKeyLen, " "),
						str(value)
					) for key, value in data.items()]))

__all__ = ["Helpers"]