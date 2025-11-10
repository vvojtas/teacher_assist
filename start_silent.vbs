' Teacher Assist - Silent Startup Script (Windows)
' This VBScript launches start.bat without showing console windows
' Perfect for creating a desktop shortcut

Set WshShell = CreateObject("WScript.Shell")

' Get the directory where this script is located
ScriptDir = CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName)

' Run start.bat in hidden window
WshShell.Run """" & ScriptDir & "\start.bat""", 0, False

' Show notification (requires Windows 10+)
WshShell.Run "powershell -WindowStyle Hidden -Command ""& {Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('Teacher Assist is starting...`n`nThe application will open in your browser shortly.', 'Teacher Assist', 0, [System.Windows.Forms.MessageBoxIcon]::Information)}""", 0, False

Set WshShell = Nothing
