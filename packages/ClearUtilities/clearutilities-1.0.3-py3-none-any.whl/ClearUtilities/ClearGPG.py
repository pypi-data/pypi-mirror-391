from enum import Enum
import tempfile
import uuid
from pathlib import Path
import platform
import subprocess
import shutil
import errno
import os
from datetime import datetime, timezone

class ClearGPGKeyType(Enum):
	Private = 1
	Public = 2
	Unknown = 3

class ClearGPGLookups:
	@staticmethod
	def GetKeyCapabilities(flags:str) -> dict:
		returnValue:dict = dict()
		flags = flags.lower()
		if ("d" in flags.lower()):
			returnValue.update({"D": "Disabled"})
		if ("e" in flags.lower()):
			returnValue.update({"e": "Encrypt"})
		if ("s" in flags.lower()):
			returnValue.update({"s": "Sign"})
		if ("c" in flags.lower()):
			returnValue.update({"c": "Certify"})
		if ("a" in flags.lower()):
			returnValue.update({"a": "Authentication"})
		if ("r" in flags.lower()):
			returnValue.update({"r": "Restricted Encryption (subkey only use)"})
		if ("t" in flags.lower()):
			returnValue.update({"t": "Timestamping"})
		if ("g" in flags.lower()):
			returnValue.update({"g": "Group Key"})
		if ("?" in flags.lower()):
			returnValue.update({"?": "Unknown"})
		return returnValue

	@staticmethod
	def GetAlgorithm(algorithm:int) -> str:
		returnValue:str = None
		algorithms:dict = {
			1: "RSA",
			16: "ELG",
			17: "DSA",
			18: "ECDH",
			19: "ECDSA",
			22: "EDDSA"}
		if (algorithm in algorithms):
			returnValue = algorithms[algorithm]
		return returnValue
		#cfg:pubkey:1;16;17;18;19;22
		#cfg:pubkeyname:RSA;ELG;DSA;ECDH;ECDSA;EDDSA

class ClearGPGommandListEntry:
	CommandSequence:int|None = None
	Method:str|None = None
	Timestamp:datetime|None = None
	ScriptFilePath:Path|None = None
	Script:str|None = None
	StandardOutput:str|None = None
	StandardError:str|None = None
	SensitiveData:list[str]|None = None
	SensitiveDataReplacement:str|None = None

	def __init__(self, commandSequence:int, method:str, sensitiveData:list[str]|None=None):
		self.CommandSequence = commandSequence
		self.Method = method
		self.Timestamp = datetime.now(tz=timezone.utc)
		self.ScriptFilePath:Path|None = None
		self.Script:str|None = None
		self.StandardOutput = None
		self.StandardError = None
		self.SensitiveData = list[str]()
		if (sensitiveData is not None):
			self.SensitiveData = sensitiveData
		self.SensitiveDataReplacement = "•••SENSITIVE•••"

	def __str__(self) -> str:
		scriptClean:str|None = None
		if (self.Script is not None):
			scriptClean = self.Script
			if (self.SensitiveData is not None
				and len(self.SensitiveData) > 0):
				for sensitiveData in self.SensitiveData:
					if (sensitiveData is not None):
						scriptClean = scriptClean.replace(sensitiveData, self.SensitiveDataReplacement)
		return "\n".join([
			"-"*80,
			"{} - {} - Command Sequence {}".format(self.Timestamp.strftime("%Y-%m-%d %H:%M:%S"), self.Method, str(self.CommandSequence)),
			"-"*80,
			"" if self.ScriptFilePath is None else str(self.ScriptFilePath),
			"" if scriptClean is None else scriptClean,
			"-"*80,
			"STANDARD OUT"+"-"*68,
			"" if self.StandardOutput is None else self.StandardOutput,
			"-"*80,
			"STANDARD ERROR"+"-"*66,
			"" if self.StandardError is None else self.StandardError,
			"-"*80
		])

class ClearGPGKeyInfo:
	KeyID:str|None = None
	KeyType:ClearGPGKeyType = ClearGPGKeyType.Unknown
	Fingerprint:str|None = None
	UserID:str|None = None
	Name:str|None = None
	EmailAddress:str|None = None
	KeyCapabilities:dict|None = None
	KeyLength:int|None = None
	Algorithm:str|None = None
	CreationDate:datetime|None = None
	ExpirationDate:datetime|None = None
	CurveName:str|None = None

	def __init__(self, elements:dict):
		if (elements is not None):
			for key, value in elements.items():
				match (key):
					case "KeyID":
						self.KeyID = value
					case "KeyType":
						self.KeyType = value
					case "Fingerprint":
						self.Fingerprint = value
					case "UserID":
						self.UserID = value
					case "Name":
						self.Name = value
					case "EmailAddress":
						self.EmailAddress = value
					case "KeyCapabilities":
						self.KeyCapabilities = ClearGPGLookups.GetKeyCapabilities(value)
					case "KeyLength":
						self.KeyLength = value
					case "Algorithm":
						self.Algorithm = ClearGPGLookups.GetAlgorithm(value)
					case "CreationDate":
						self.CreationDate = value
					case "ExpirationDate":
						self.ExpirationDate = value
					case "CurveName":
						self.CurveName = value

	def __str__(self):
		returnValue:str = f"KeyID: {"None" if self.KeyID is None else self.KeyID}\n"
		returnValue += f"KeyType: {"None" if self.KeyType is None else self.KeyType.name}\n"
		returnValue += f"Fingerprint: {"None" if self.Fingerprint is None else self.Fingerprint}\n"
		returnValue += f"UserID: {"None" if self.UserID is None else self.UserID}\n"
		returnValue += f"Name: {"None" if self.Name is None else self.Name}\n"
		returnValue += f"EmailAddress: {"None" if self.EmailAddress is None else self.EmailAddress}\n"
		returnValue += f"KeyCapabilities: {"None" if self.KeyCapabilities is None else self.KeyCapabilities}\n"
		returnValue += f"KeyLength: {"None" if self.KeyLength is None else self.KeyLength}\n"
		returnValue += f"Algorithm: {"None" if self.Algorithm is None else self.Algorithm}\n"
		returnValue += f"CreationDate: {"None" if self.CreationDate is None else self.CreationDate.strftime("%Y%m%dT%H%M%S")}\n"
		returnValue += f"ExpirationDate: {"None" if self.ExpirationDate is None else self.ExpirationDate.strftime("%Y%m%dT%H%M%S")}\n"
		returnValue += f"CurveName: {"None" if self.CurveName is None else self.CurveName}"
		return returnValue

class ClearGPG:
	System:str = platform.system()
	KeyCapabilities:dict = {
		"D": "Disabled (D)",
		"e": "Encrypt (e)",
		"s": "Sign (s)",
		"c": "Certify (c)",
		"a": "Authentication (a)",
		"r": "Restricted Encryption (subkey only use) (r)",
		"t": "Timestamping (t)",
		"g": "Group Key (g)",
		"?": "Unknown capability (?)"
	}
	PublicKeyAlgorithm:dict = {
		1: "RSA Encrypt or Sign (1)",
		2: "RSA Encrypt Only (2)",
		3: "RSA Sign Only (3)",
		16: "Elgamal Encrypt Only (16)",
		17: "DSA (17)",
		18: "ECDH Public Key Algorithm (18)",
		19: "ECDSA Public Key Algorithm (19)",
		20: "Reserved (20)",
		21: "Reserved for Diffie-Hellman (21)",
		22: "EdDSA (22)",
		23: "Reserved for AEDH (23)",
		24: "Reserved for AEDSA (24)",
		25: "X25519 (25)",
		26: "X448 (26)",
		27: "Ed25519 (27)",
		28: "Ed448 (28)",
		100: "Private/Experimental algorithm (100)",
		101: "Private/Experimental algorithm (101)",
		102: "Private/Experimental algorithm (102)",
		103: "Private/Experimental algorithm (103)",
		104: "Private/Experimental algorithm (104)",
		105: "Private/Experimental algorithm (105)",
		106: "Private/Experimental algorithm (106)",
		107: "Private/Experimental algorithm (107)",
		108: "Private/Experimental algorithm (108)",
		109: "Private/Experimental algorithm (109)",
		110: "Private/Experimental algorithm (110)",
	}
	Validity:dict = {
		"o": "Unknown New (o)",
		"i": "Invalid (i)",
		"d": "Disabled (d)",
		"r": "Revoked (r)",
		"e": "Expired (e)",
		"-": "Unknown Validity (-)",
		"q": "Undefined Validity (q)",
		"n": "Not Valid (n)",
		"m": "Marginal Valid (m)",
		"f": "Fully Valid (f)",
		"u": "Ultimately Valid (u)",
		"w": "Has Well Known Private Part (w)",
		"s": "Special Validity (s)",
		"!": "Signature Is Good (!)",
		"-": "Signature Is Bad (-)",
		"?": "No Usable Public Key (?)",
		"%": "Other Error (%)"
	}
	RecordType:dict = {
		"pub": "Public Key (pub)",
		"crt": "X.509 Certificate (crt)",
		"crs": "X.509 Certificate and Private Key Available (crs)",
		"sub": "Subkey (sub)",
		"sec": "Secret Key (sec)",
		"ssb": "Secret Subkey (ssb)",
		"uid": "User ID (uid)",
		"uat": "User Attribute (uat)",
		"sig": "Signature (sig)",
		"rev": "Revocation Signature (rev)",
		"rvs": "Standalone Revocation Signature (rvs)",
		"fpr": "Fingerprint (fpr)",
		"fp2": "SHA-256 Fingerprint (fp2)",
		"pkd": "Public Key Data (pkd)",
		"grp": "Keygrip (grp)",
		"rvk": "Revocation Key (rvk)",
		"tfs": "TOFU Statistics (tfs)",
		"tru": "Trust Database Information (tru)",
		"spk": "Signature Subpacket (spk)",
		"cfg": "Configuration Data (cfg)"
	}
	ClearGPGExecPath:Path|None = None
	HomeDirectoryPath:Path|None = None

	Commands:list[ClearGPGommandListEntry]|None = None
	LastCommandSequence:int|None = None

	def __init__(self, execPath:Path|None = None, homeDirectoryPath:Path|str|None = None) -> None:
		self.__SetClearGPGExecPath__(execPath)
		self.HomeDirectoryPath = Path.home()
		if (homeDirectoryPath is not None):
			if (isinstance(homeDirectoryPath, str)):
				self.HomeDirectoryPath = Path(homeDirectoryPath)
			else:
				self.HomeDirectoryPath = homeDirectoryPath
		if (not self.HomeDirectoryPath.exists()):
			self.HomeDirectoryPath.mkdir(parents=True, exist_ok=True)
		self.Commands = list[ClearGPGommandListEntry]()
		self.LastCommandSequence = (-1)

	def __BuildScript__(self, args:list, commandSequence:int) -> None:
		tempFileName:str = str(uuid.uuid4()).replace("-", "")
		tempFileName = f"ClearGPG.script.{tempFileName}"
		lineContinuationCharacter:str = "^"
		newLine:str = "\n"
		if (self.System == "Linux"):
			tempFileName += ".sh"
			lineContinuationCharacter = "\\"
		if (self.System == "Windows"):
			tempFileName += ".bat"
			lineContinuationCharacter = "^"
		self.Commands[commandSequence].ScriptFilePath = Path(str(tempfile.gettempdir())).joinpath(tempFileName)
		scriptFileContent:str = ""
		if (self.System == "Linux"):
			scriptFileContent = f"#!/bin/sh{newLine}{newLine}"
			scriptFileContent += f"export ClearGPGHOME={self.HomeDirectoryPath}{newLine}"
		if (self.System == "Windows"):
			scriptFileContent = f"@ECHO OFF\nSET ClearGPGHOME={self.HomeDirectoryPath}{newLine}"
		if (len(args) == 0):
			raise IndexError("args empty")
		if (args[0] != self.ClearGPGExecPath):
			args.insert(0, self.ClearGPGExecPath)
		for index, arg in enumerate(args):
			if (index > 0):
				scriptFileContent += "\t"
			if (str(arg).startswith("\"") and str(arg).endswith("\"")):
				scriptFileContent += f"{arg} "
			elif (" " in str(arg)):
				scriptFileContent += f"\"{arg}\" "
			else:
				scriptFileContent += f"{arg} "
			scriptFileContent += f"{lineContinuationCharacter}\n"
		scriptFileContent = scriptFileContent[:-3]
		scriptFileContent += newLine
		#print(scriptFileContent)
		self.Commands[commandSequence].ScriptFilePath.write_text(scriptFileContent)
		self.Commands[commandSequence].Script = scriptFileContent

	def __ExecScript__(self, args:list, callingMethod:str, sensitiveData:list[str]|None=None) -> int:
		self.LastCommandSequence += 1
		self.Commands.append(ClearGPGommandListEntry(self.LastCommandSequence, callingMethod, sensitiveData))
		self.__BuildScript__(args, self.LastCommandSequence)
		if (self.Commands[self.LastCommandSequence].ScriptFilePath is None):
			raise FileNotFoundError(self.Commands[self.LastCommandSequence].ScriptFilePath)
		result = subprocess.run(str(self.Commands[self.LastCommandSequence].ScriptFilePath),
			capture_output=True,
			text=True)
		self.Commands[self.LastCommandSequence].StandardOutput = result.stdout
		self.Commands[self.LastCommandSequence].StandardError = result.stderr
		self.Commands[self.LastCommandSequence].ScriptFilePath.unlink(True)
		return self.LastCommandSequence

	def __SetClearGPGExecPath__(self, execPath:Path|None = None):
		if (execPath is not None):
			if (not execPath.exists()):
				raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), str(execPath))
			self.ClearGPGExecPath = execPath
		else:
			try:
				execPath = Path(shutil.which("gpg.exe"))
			except:
				execPath = None
			if (execPath is None):
				raise  Exception("ClearGPG Not Found")
			if (not execPath.exists()):
				raise  Exception("ClearGPG Not Found")
			self.ClearGPGExecPath = execPath

	def KeyExists(self, keyID:str) -> bool:
		returnValue:bool = False
		commandSequenceListSecrectKeys:int = self.__ExecScript__([
			"--list-secret-keys",
			"--keyid-format=long",
			"--with-colons",
			"--with-fingerprint",
			keyID], "ClearGPG.KeyExists", None)
		if (
			"gpg: error reading key: No secret key" not in self.Commands[commandSequenceListSecrectKeys].StandardError
			and "sec:" in self.Commands[commandSequenceListSecrectKeys].StandardOutput
			and keyID in self.Commands[commandSequenceListSecrectKeys].StandardOutput):
			returnValue = True
		else:
			commandSequenceListKeys:int = self.__ExecScript__([
				"--list-keys",
				"--keyid-format=long",
				"--with-colons",
				"--with-fingerprint",
				keyID], "ClearGPG.KeyExists", None)
			if (
				"gpg: error reading key: No public key" not in self.Commands[commandSequenceListKeys].StandardError
				and "pub:" in self.Commands[commandSequenceListKeys].StandardOutput
				and keyID in self.Commands[commandSequenceListKeys].StandardOutput):
				returnValue = True
		return returnValue

	def GetKeyType(self, keyID:str) -> ClearGPGKeyType:
		returnValue:ClearGPGKeyType = ClearGPGKeyType.Unknown
		commandSequenceListSecrectKeys:int = self.__ExecScript__([
			"--list-secret-keys",
			"--keyid-format=long",
			"--with-colons",
			"--with-fingerprint",
			keyID], "ClearGPG.GetKeyType", None)
		if (
			"gpg: error reading key: No secret key" not in self.Commands[commandSequenceListSecrectKeys].StandardError
			and "sec:" in self.Commands[commandSequenceListSecrectKeys].StandardOutput
			and keyID in self.Commands[commandSequenceListSecrectKeys].StandardOutput):
			returnValue = ClearGPGKeyType.Private
		else:
			commandSequenceListKeys:int = self.__ExecScript__([
				"--list-keys",
				"--keyid-format=long",
				"--with-colons",
				"--with-fingerprint",
				keyID], "ClearGPG.GetKeyType", None)
			if (
				"gpg: error reading key: No public key" not in self.Commands[commandSequenceListKeys].StandardError
				and "pub:" in self.Commands[commandSequenceListKeys].StandardOutput
				and keyID in self.Commands[commandSequenceListKeys].StandardOutput):
				returnValue = ClearGPGKeyType.Public
		return returnValue

	def GetKeyInfo(self, keyID:str, keyType:ClearGPGKeyType = ClearGPGKeyType.Unknown) -> ClearGPGKeyInfo | None:
		returnValue:ClearGPGKeyInfo|None = None
		if (keyType == ClearGPGKeyType.Unknown):
			keyType = self.GetKeyType(keyID)
		keyData:dict|None = None
		commandSequence:int = self.__ExecScript__([
			"--list-secret-keys" if keyType == ClearGPGKeyType.Private else "--list-keys",
			"--keyid-format=long",
			"--with-colons",
			"--with-fingerprint",
			keyID], "ClearGPG.GetKeyInfo", None)
		outputText:str = None
		if ("gpg: error reading key: No secret key" not in self.Commands[commandSequence].StandardError
	  		and "gpg: error reading key: No public key" not in self.Commands[commandSequence].StandardError):
			outputText = self.Commands[commandSequence].StandardOutput
		if (outputText is not None):
			keyData = dict()
			keyData.update({ "KeyID": keyID, "KeyType": keyType })
			for line in outputText.splitlines():
				lineElements:list[str] = line.split(":")
				match (lineElements[0].lower()):
					case "sec":
						keyType = ClearGPGKeyType.Private
					case "pub":
						keyType = ClearGPGKeyType.Public
				if (line.startswith("sec:")
					or line.startswith("pub:")):
					if (lineElements[2] != ""
		 				and lineElements[2].isdigit()
						and "KeyLength" not in keyData):
						keyData.update({ "KeyLength": int(lineElements[2]) })
					if (lineElements[3] != ""
		 				and lineElements[3].isdigit()
						and "Algorithm" not in keyData):
						keyData.update({ "Algorithm": int(lineElements[3]) })
					if (lineElements[5] != ""
		 				and "CreationDate" not in keyData):
						if ("T" in lineElements[5]):
							keyData.update({ "CreationDate": datetime.strptime(lineElements[5], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc) })
						elif (lineElements[5].isdigit()):
							keyData.update({ "CreationDate": datetime.fromtimestamp(int(lineElements[5]), timezone.utc) })
					if (lineElements[6] != ""
		 				and "ExpirationDate" not in keyData):
						if ("T" in lineElements[6]):
							keyData.update({ "ExpirationDate": datetime.strptime(lineElements[6], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc) })
						elif (lineElements[5].isdigit()):
							keyData.update({ "ExpirationDate": datetime.fromtimestamp(int(lineElements[6]), timezone.utc) })
					if (lineElements[11] != ""
		 				and "KeyCapabilities" not in keyData):
						keyData.update({ "KeyCapabilities": lineElements[11] })
					if (lineElements[16] != ""
		 				and "CurveName" not in keyData):
						keyData.update({ "CurveName": lineElements[16] })
				if (line.startswith("fpr:") and "Fingerprint" not in keyData):
					keyData.update({ "Fingerprint": lineElements[9] })
				if (line.startswith("uid:") and "UserID" not in keyData):
					keyData.update({ "UserID": lineElements[9] })
					if ("<" in keyData["UserID"]):
						userIDElements:list[str] = keyData["UserID"].split("<")
						if (len(userIDElements) == 1):
							keyData.update({ "Name": userIDElements[0].strip() })
						elif (len(userIDElements) == 2):
							keyData.update({ "Name": userIDElements[0].strip() })
							keyData.update({ "EmailAddress": userIDElements[1][:-1].strip() })
		if (keyData is not None):
			returnValue = ClearGPGKeyInfo(keyData)
		return returnValue

	def AddPrivateKey(self, filePath:Path|str, passphrase:str) -> ClearGPGKeyInfo:
		returnValue:ClearGPGKeyInfo|None = None
		if (isinstance(filePath, str)):
			filePath = Path(filePath)
		if (not filePath.exists()):
			raise FileNotFoundError(filePath)
		commandSequence:int = self.__ExecScript__([
			"--allow-secret-key-import",
			"--pinentry-mode=loopback",
			"--passphrase", f"\"{passphrase}\"",
			"--import", str(filePath)], "ClearGPG.AddPrivateKey", [passphrase])
		if (not "gpg: Total number processed: 1" in self.Commands[commandSequence].StandardError
			and not "gpg: Total number processed: 1" in self.Commands[commandSequence].StandardError):
			raise ValueError(self.Commands[commandSequence].StandardError)
		outputText:str = None
		if (len(self.Commands[commandSequence].StandardOutput) > 0):
			outputText = self.Commands[commandSequence].StandardOutput
		else:
			outputText = self.Commands[commandSequence].StandardError
		keyID:str = None
		for line in outputText.splitlines():
			if (line.startswith("gpg: key ")):
				keyID = line[9:line.index(":", (line.index(":")+1))]
			if (keyID is not None):
				break
		if (keyID is not None):
			returnValue = self.GetKeyInfo(keyID, ClearGPGKeyType.Private)
		return returnValue
		
	def AddPublicKey(self, filePath:Path|str) -> ClearGPGKeyInfo:
		returnValue:ClearGPGKeyInfo|None = None
		if (isinstance(filePath, str)):
			filePath = Path(filePath)
		if (not filePath.exists()):
			raise FileNotFoundError(filePath)
		commandSequence:int = self.__ExecScript__([
			"--import", str(filePath)], "ClearGPG.AddPublicKey", None)
		if (not "gpg: Total number processed: 1" in self.Commands[commandSequence].StandardError
			and not "gpg: Total number processed: 1" in self.Commands[commandSequence].StandardError):
			raise ValueError(self.Commands[commandSequence].StandardError)
		outputText:str = None
		if (len(self.Commands[commandSequence].StandardOutput) > 0):
			outputText = self.Commands[commandSequence].StandardOutput
		else:
			outputText = self.Commands[commandSequence].StandardError
		keyID:str = None
		for line in outputText.splitlines():
			if (line.startswith("gpg: key ")):
				keyID = line[9:line.index(":", (line.index(":")+1))]
			if (keyID is not None):
				break
		if (keyID is not None):
			returnValue = self.GetKeyInfo(keyID, ClearGPGKeyType.Public)
		return returnValue
		
	def DeletePrivateKey(self, fingerprint:str, deletePublic:bool = True) -> None:
		commandSequence:int = self.__ExecScript__([
			"--batch",
			"--yes",
			"--delete-secret-key",
			fingerprint], "ClearGPG.DeletePrivateKey", None)
		if (len(self.Commands[commandSequence].StandardError) > 0):
			raise ValueError(self.Commands[commandSequence].StandardError)
		else:
			if (deletePublic):
				keyType = self.GetKeyType(fingerprint)
				if (keyType == ClearGPGKeyType.Public):
					self.DeletePublicKey(fingerprint)

	def DeletePublicKey(self, fingerprint:str) -> None:
		commandSequence:int = self.__ExecScript__([
			"--batch",
			"--yes",
			"--delete-key",
			fingerprint], "ClearGPG.DeletePublicKey", None)
		if (len(self.Commands[commandSequence].StandardError) > 0):
			raise ValueError(self.Commands[commandSequence].StandardError)

	def Sign(self, inputFilePath:Path|str, outputFilePath:Path|str, signer:str|None = None, passphrase:str|None = None, clearSign:bool|None = None, forceBinaryMode:bool|None = None) -> None:
		if (isinstance(inputFilePath, str)):
			inputFilePath = Path(inputFilePath)
		if (not inputFilePath.exists()):
			raise FileNotFoundError()
		if (isinstance(outputFilePath, str)):
			outputFilePath = Path(outputFilePath)
		if (outputFilePath.exists()):
			outputFilePath.unlink()
		args:list = [
			"--output", str(outputFilePath),
			"--verbose", "--verbose"]
		if (signer is not None):
			args.append("--local-user")
			args.append(signer)
		if (passphrase is not None):
			args.append("--pinentry-mode=loopback")
			args.append("--passphrase")
			args.append(f"\"{passphrase}\"")
		args.append("--trust-model")
		args.append("always")
		if (clearSign):
			args.append("--clearsign")
		if (forceBinaryMode):
			args.append("--no-textmode")
		#else:
		args.append("--sign")
		args.append(str(inputFilePath))
		commandSequence:int = self.__ExecScript__(args, "ClearGPG.Sign", [passphrase])
		if (not outputFilePath.exists()):
			if (len(self.Commands[commandSequence].StandardError) > 0):
				raise ValueError(self.Commands[commandSequence].StandardError)
			else:
				raise FileNotFoundError(outputFilePath)

	def Verify(self, inputFilePath:Path|str, outputFilePath:Path|str) -> None:
		if (isinstance(inputFilePath, str)):
			inputFilePath = Path(inputFilePath)
		if (not inputFilePath.exists()):
			raise FileNotFoundError()
		if (isinstance(outputFilePath, str)):
			outputFilePath = Path(outputFilePath)
		if (outputFilePath.exists()):
			outputFilePath.unlink()
		args:list = [
			"--output", str(outputFilePath),
			"--verbose", "--verbose"]
		args.append("--verify")
		args.append(str(inputFilePath))
		commandSequence:int = self.__ExecScript__(args, "ClearGPG.Verify", None)
		if (not outputFilePath.exists()):
			if (len(self.Commands[commandSequence].StandardError) > 0):
				raise ValueError(self.Commands[commandSequence].StandardError)
			else:
				raise FileNotFoundError(outputFilePath)

	def Encrypt(self, inputFilePath:Path|str, outputFilePath:Path|str, recipient:str|None = None, passphrase:str|None = None, sign:bool = False) -> None:
		if (isinstance(inputFilePath, str)):
			inputFilePath = Path(inputFilePath)
		if (not inputFilePath.exists()):
			raise FileNotFoundError()
		if (isinstance(outputFilePath, str)):
			outputFilePath = Path(outputFilePath)
		if (outputFilePath.exists()):
			outputFilePath.unlink()
		args:list = ["--output", str(outputFilePath)]
		if (recipient is not None):
			args.append("--recipient")
			args.append(recipient)
		if (passphrase is not None):
			args.append("--pinentry-mode=loopback")
			args.append("--passphrase")
			args.append(f"\"{passphrase}\"")
		args.append("--trust-model")
		args.append("always")
		if (sign):
			args.append("--sign")
		args.append("--encrypt")
		args.append(str(inputFilePath))
		commandSequence:int = self.__ExecScript__(args, "ClearGPG.Encrypt", [passphrase])
		if (not outputFilePath.exists()):
			if (len(self.Commands[commandSequence].StandardError) > 0):
				raise ValueError(self.Commands[commandSequence].StandardError)
			else:
				raise FileNotFoundError(outputFilePath)

	def Decrypt(self, inputFilePath:Path, outputFilePath:Path, recipient:str|None = None, passphrase:str|None = None) -> None:
		if (isinstance(inputFilePath, str)):
			inputFilePath = Path(inputFilePath)
		if (not inputFilePath.exists()):
			raise FileNotFoundError()
		if (isinstance(outputFilePath, str)):
			outputFilePath = Path(outputFilePath)
		if (outputFilePath.exists()):
			outputFilePath.unlink()
		args:list = ["--output", str(outputFilePath)]
		if (recipient is not None):
			args.append("--recipient")
			args.append(recipient)
		if (passphrase is not None):
			args.append("--pinentry-mode=loopback")
			args.append("--passphrase")
			args.append(f"\"{passphrase}\"")
		args.append("--decrypt")
		args.append(str(inputFilePath))
		commandSequence:int = self.__ExecScript__(args, "ClearGPG.Decrypt", [passphrase])
		if (not outputFilePath.exists()):
			if (len(self.Commands[commandSequence].StandardError) > 0):
				raise ValueError(self.Commands[commandSequence].StandardError)
			else:
				raise FileNotFoundError(outputFilePath)
	
	def __str__(self) -> str:
		return "\n********************************************************************************\n".join([str(entry) for entry in self.Commands])

__all__ = ["ClearGPGKeyType", "ClearGPGLookups", "ClearGPGommandListEntry", "ClearGPGKeyInfo", "ClearGPG"]
