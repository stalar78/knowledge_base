Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

projectDir = fso.GetParentFolderName(WScript.ScriptFullName)
venvPythonw = projectDir & "\.venv\Scripts\pythonw.exe"

If fso.FileExists(venvPythonw) Then
    cmd = """" & venvPythonw & """ -m src.gui_app"
Else
    cmd = "pythonw.exe -m src.gui_app"
End If

shell.CurrentDirectory = projectDir
shell.Run cmd, 0, False
