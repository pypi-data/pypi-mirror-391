from pathlib import Path
import smtplib, ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.message import EmailMessage
from email import encoders

class ClearEmail:
	ServerHost:str|None = None
	ServerPort:int|None = None
	ServerUseTLS:bool|None = None
	ServerUseSSL:bool|None = None
	ServerUserName:str|None = None
	ServerPassword:str|None = None
	FromAddress:str|None = None
	ToAddresses:list[str]|None = None
	Subject:str|None = None
	HTMLBody:str|None = None
	PlainTextBody:str|None = None

	_multipartMessage:MIMEMultipart|None = None

	def __init__(self,
		serverHost:str|None=None,
		serverPort:int|None=None,
		serverUseTLS:bool|None=None,
		serverUseSSL:bool|None=None,
		serverUserName:str|None=None,
		serverPassword:str|None=None,
		fromAddress:str|None=None,
		toAddresses:list[str]|None=None,
		subject:str|None=None,
		htmlBody:str|None=None,
		plainTextBody:str|None=None) -> None:
		self.ServerHost = serverHost
		self.ServerPort = serverPort
		self.ServerUseTLS = serverUseTLS
		self.ServerUseSSL = serverUseSSL
		self.ServerUserName = serverUserName
		self.ServerPassword = serverPassword
		self.FromAddress = fromAddress
		self.ToAddresses = toAddresses
		self.Subject = subject
		self.HTMLBody = htmlBody
		self.PlainTextBody = plainTextBody
		self._multipartMessage = None

	def AttachFile(self, filePath:Path|str) -> None:
		if (isinstance(filePath, str)):
			filePath = Path(filePath)
		if (not filePath.exists()):
			raise FileNotFoundError(filePath)
		if (self._multipartMessage is None):
			self._multipartMessage = MIMEMultipart("alternative")
		mimeBase:MIMEBase = MIMEBase('application', 'octet-stream')
		mimeBase.set_payload(filePath.read_bytes())
		encoders.encode_base64(mimeBase)
		mimeBase.add_header(
			"Content-Disposition",
			"attachment; filename={}".format(filePath.name),
		)
		self._multipartMessage.attach(mimeBase)

	def Send(self) -> None:
		exception:Exception|None = None
		smtp:smtplib.SMTP|smtplib.SMTP_SSL|None = None
		try:
			if (self._multipartMessage is None):
				self._multipartMessage = MIMEMultipart("alternative")
			self._multipartMessage["Subject"] = self.Subject
			self._multipartMessage["From"] = self.FromAddress
			self._multipartMessage["To"] = ", ".join(self.ToAddresses)
			if (self.PlainTextBody is not None):
				self._multipartMessage.attach(MIMEText(self.PlainTextBody, 'plain'))
			if (self.HTMLBody is not None):
				self._multipartMessage.attach(MIMEText(self.HTMLBody, 'html'))

			if (self.ServerUseSSL):
				smtp = smtplib.SMTP_SSL(self.ServerHost, self.ServerPort)
			else:
				smtp = smtplib.SMTP(self.ServerHost, self.ServerPort)
			if (smtp is None):
				raise RuntimeError("Failed to connect to SMTP server.")
			if (self.ServerUseTLS):
				context = ssl.create_default_context()
				smtp.ehlo()
				smtp.starttls(context=context)
			smtp.ehlo()
			smtp.login(self.ServerUserName, self.ServerPassword)
			smtp.sendmail(self.FromAddress, self.ToAddresses, self._multipartMessage.as_string())
		except Exception as e:
			exception = e
		finally:
			if (smtp is not None):
				smtp.close()
		if (exception is not None):
			raise exception

__all__ = ["ClearEmail"]