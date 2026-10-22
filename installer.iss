#define AppVersion "0.3.0"
[Setup]
AppId={{ED0ED89C-2987-4774-940D-9D8BBD086009}
AppName=sg0hann Skin Changer
AppVersion={#AppVersion}
AppPublisher=sg0hann
DefaultDirName={localappdata}\Programs\sg0hann Skin Changer
DefaultGroupName=sg0hann Skin Changer
OutputDir=dist
OutputBaseFilename=sg0hann-SkinChanger-v{#AppVersion}-setup
Compression=lzma2
SolidCompression=yes
PrivilegesRequired=lowest
CloseApplications=yes
RestartApplications=yes
UninstallDisplayIcon={app}\sg0hann-SkinChanger.exe
[Files]
Source: "dist\sg0hann-SkinChanger.exe"; DestDir: "{app}"; Flags: ignoreversion
[Icons]
Name: "{group}\sg0hann Skin Changer"; Filename: "{app}\sg0hann-SkinChanger.exe"
Name: "{autodesktop}\sg0hann Skin Changer"; Filename: "{app}\sg0hann-SkinChanger.exe"; Tasks: desktopicon
[Tasks]
Name: desktopicon; Description: "Create desktop shortcut"; GroupDescription: "Additional shortcuts:"
[Run]
Filename: "{app}\sg0hann-SkinChanger.exe"; Description: "Launch sg0hann Skin Changer"; Flags: nowait postinstall
