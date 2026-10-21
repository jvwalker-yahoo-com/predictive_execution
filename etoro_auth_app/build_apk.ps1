# PowerShell wrapper for building the eToro ReAuth Standalone APK
$PSScriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
python "$PSScriptRoot\build_apk.py"
