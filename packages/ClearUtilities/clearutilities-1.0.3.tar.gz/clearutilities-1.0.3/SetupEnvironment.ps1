[String] $VEnvPath = [IO.Path]::Combine([IO.Path]::GetDirectoryName($PSCommandPath), ".venv")
[String] $SourcePath =  [IO.Path]::GetDirectoryName($PSCommandPath)
$SourcePath += "\."

& "C:/Program Files/Python312/python.exe" -m venv $VEnvPath

[String] $VEnvPythonPath = [IO.Path]::Combine([IO.Path]::GetDirectoryName($PSCommandPath), ".venv", "Scripts/python.exe")
#& $VEnvPythonPath -m pip install --upgrade pip
& $VEnvPythonPath -m pip install --upgrade slugify
#& $VEnvPythonPath -m pip install --upgrade python-dotenv
#& $VEnvPythonPath -m pip install --upgrade pytz
#& $VEnvPythonPath -m pip install --upgrade smbprotocol
#& $VEnvPythonPath -m pip install --upgrade pywin32
#& $VEnvPythonPath -m pip install --upgrade "paramiko<4.0"
#& $VEnvPythonPath -m pip install --upgrade boto3

& $VEnvPythonPath -m pip install $SourcePath
