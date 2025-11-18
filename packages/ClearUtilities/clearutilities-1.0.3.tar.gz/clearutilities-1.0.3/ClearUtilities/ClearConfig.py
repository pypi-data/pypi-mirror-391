from pathlib import Path
import sys
import json
from munch import Munch
import socket
from urllib.parse import urlparse
import git
import git.exc
from .ClearHelpers import ClearHelpers

class ClearConfig:
	@staticmethod
	def AppendScriptConfig(config:dict, filePath:Path, overwrite:bool = False) -> None:
		if (filePath.exists()):
			scriptConfig:dict  = json.loads(filePath.read_text())
			for key in scriptConfig.keys():
				if (key in config and overwrite):
					config[key] = scriptConfig[key]
				else:
					config.update({ key: scriptConfig[key] })

	@staticmethod
	def GetFilesInTree(beginPath:Path, endPath:Path) -> list:
		"""Returns all .env files found in the directories between beginPath and endPath.
		Note that begin path should be the top path and end path lowest path.
		The paths are search in reverse order starting at endPath going up to beginPath.
		However, the found .env files are returned in top to bottom order.

		Keyword arguments:
			beginPath -- the top path to search to
			endPath -- the bottom path to search from
		"""
		returnValue:list = []
		currentPath:Path = endPath
		if (currentPath.is_file()):
			currentPath = currentPath.parent
		while (currentPath != beginPath.parent):
			envFilePath:Path = currentPath.joinpath(".env")
			if (envFilePath.exists()):
				returnValue.append(envFilePath)
			currentPath = currentPath.parent
		returnValue.sort()
		return returnValue

	@staticmethod
	def Parse(contents:str) -> dict:
		"""Returns a dict containing any name=value pairs found in the string.
		Comment (#) lines are ignored.
		Comments should not be included inline with name=value pairs.

		Keyword arguments:
			contents -- the string to parse
		"""
		if (contents is not None):
			lines:list = contents.splitlines()
			if (len(lines) > 0):
				returnValue = {}
				for line in lines:
					line = line.strip()
					if (not line.startswith("#") and len(line) > 0):
						#Find first eqaul sign
						firstEqual:int = line.find("=")

						#Split into name/value
						name = line[:firstEqual].strip()
						value = line[firstEqual+1:].strip()

						#Strip leading and trailing double quotes from name
						if name.startswith('"') and name.endswith('"'):
							name = name[1:-1]

						#Strip leading and trailing single quotes from name
						if name.startswith("'") and name.endswith("'"):
							name = name[1:-1]

						#Strip leading and trailing double quotes from value
						if value.startswith('"') and value.endswith('"'):
							value = value[1:-1]

						#Strip leading and trailing single quotes from value
						if value.startswith("'") and value.endswith("'"):
							value = value[1:-1]

						#Attempt to resolve boolean values
						if (value in ["True", "TRUE", "true"]):
							returnValue.update({name: True})
						elif (value in ["False", "FALSE", "false"]):
							returnValue.update({name: False})
						#If not boolean, then
						else:
							returnValue.update({name: value})
		return returnValue

	@staticmethod
	def OpenFilePath(filePath:Path, resolveSmartSettings:bool = False) -> dict:
		"""Returns a dict containing any name=value pairs found in the specified file.
		Comment (#) lines are ignored.
		Comments should not be included inline with name=value pairs.

		Keyword arguments:
			filePath -- the path to the file to parse
			resolveSmartSettings -- Alters settings as follows and returns appropriate type
				If key begins with PATH_, converts relative paths to absolute paths
				If key begins with SQLCONSTRING_, appends application name and workstation name to connection strings
				If key begins with POSTGRECONSTRING_, appends application name to connection strings
				If key begins with LIST_, converts value to a list, splitting on the pipe (|) character
		"""
		returnValue:dict = None
		fileContents:str = None
		with open(filePath, "r") as file:
			fileContents = file.read()
		if (fileContents is not None):
			returnValue = ClearConfig.Parse(fileContents)
			for key in returnValue:
				if (resolveSmartSettings):
					if (key.startswith("PATH_")):
						returnValue.update({key: ClearHelpers.ResolveSibling(Path(returnValue[key]), filePath)})
					if (key.startswith("SQLCONSTRING_")):
						returnValue.update({key: 
							ClearHelpers.AddAppToSQLServerConnectionString(
								ClearHelpers.AddHostNameToSQLServerConnectionString(
									str(returnValue[key])
						))})
					if (key.startswith("POSTGRECONSTRING_")):
						returnValue.update({key: ClearHelpers.AddAppToPostgreSQLConnectionString(str(returnValue[key]))})
					if (key.startswith("LIST_")):
						returnValue.update({key: str(returnValue[key]).split("|")})
		return returnValue

	@staticmethod
	def OpenFilesInTree(beginPath:Path, endPath:Path, resolveSmartSettings:bool = False) -> dict:
		"""Returns a dict containing any name=value pairs found in any .env files located in the directories between beginPath and endPath.
		Note that begin path should be the top path and end path lowest path.
		The paths are search in reverse order starting at endPath going up to beginPath.
		However, the found .env files are processed in top to bottom order.
		Duplicate key names found are overriden by the value in the lower level .env.

		Keyword arguments:
			beginPath -- the top path to search to
			endPath -- the bottom path to search from
			resolveSmartSettings -- Alters settings as follows and returns appropriate type
				If key begins with PATH_, converts relative paths to absolute paths
				If key begins with SQLCONSTRING_, appends application name and workstation name to connection strings
				If key begins with POSTGRECONSTRING_, appends application name to connection strings
				If key begins with LIST_, converts value to a list, splitting on the pipe (|) character
		"""
		returnValue:dict = {}
		if (beginPath is None or endPath is None):
			raise ValueError("Paths cannot be None")
		envFilePathList:list = ClearConfig.GetFilesInTree(beginPath, endPath)
		for envFilePath in envFilePathList:
			returnValue.update(ClearConfig.OpenFilePath(envFilePath, resolveSmartSettings))
		return dict(sorted(returnValue.items()))

	@staticmethod
	def OpenRepoEnv(resolveSmartSettings:bool = False, jsonScriptConfigPath:Path|str|None=None) -> dict:
		"""Returns a dict containing any name=value pairs found in any .env files located in the directories between the first found git repo directory and sys.argv[0] file.
		The paths are search in reverse order starting at sys.argv[0] path going up to repo path.
		However, the found .env files are processed in top to bottom order.
		Duplicate key names found are overriden by the value in the lower level .env.

		Keyword arguments:
			resolveSmartSettings -- Alters settings as follows and returns appropriate type
				If key begins with PATH_, converts relative paths to absolute paths
				If key begins with SQLCONSTRING_, appends application name and workstation name to connection strings
				If key begins with POSTGRECONSTRING_, appends application name to connection strings
				If key begins with LIST_, converts value to a list, splitting on the pipe (|) character
			jsonScriptConfigPath -- If specified, adds data from JSON file to config.
		"""
		returnValue:dict = None
		returnValue = ClearConfig.OpenFilesInTree(ClearHelpers.GetRepoPath(), Path(sys.argv[0]), resolveSmartSettings)
		if (jsonScriptConfigPath is not None):
			if (isinstance(jsonScriptConfigPath, str)):
				scriptConfigPath = Path(jsonScriptConfigPath)
				if (jsonScriptConfigPath.exists()):
					if (returnValue is None):
						returnValue = dict()
					ClearConfig.AppendScriptConfig(returnValue, jsonScriptConfigPath, True)
		return returnValue

	@staticmethod
	def OpenFile(filePath:str = None) -> dict:
		returnValue:dict = None
		fileContents:str = None
		if (not filePath):
			filePath = str(Path(sys.argv[0]).parent.joinpath(".env"))
		if (not Path(filePath).is_file()):
			raise FileNotFoundError(filePath)
		else:
			with open(filePath, "r") as file:
				fileContents = file.read()
		if (fileContents is not None):
			returnValue = ClearConfig.Parse(fileContents)
		return returnValue

__all__ = ["ClearConfig"]
