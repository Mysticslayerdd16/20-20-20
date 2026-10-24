!define APP_NAME "EyeGuard"
Name "${APP_NAME}"
OutFile "EyeGuard-Setup.exe"
InstallDir "$LOCALAPPDATA\Programs\EyeGuard"
RequestExecutionLevel user
Page directory
Page instfiles
Section "Install"
  SetOutPath "$INSTDIR"
  File "20-20-20-application\Windows\dist\EyeGuard.exe"
  CreateShortcut "$DESKTOP\EyeGuard.lnk" "$INSTDIR\EyeGuard.exe"
  CreateShortcut "$SMPROGRAMS\EyeGuard.lnk" "$INSTDIR\EyeGuard.exe"
  WriteUninstaller "$INSTDIR\Uninstall.exe"
SectionEnd
Section "Uninstall"
  Delete "$INSTDIR\EyeGuard.exe"
  Delete "$INSTDIR\Uninstall.exe"
  Delete "$DESKTOP\EyeGuard.lnk"
  Delete "$SMPROGRAMS\EyeGuard.lnk"
  DeleteRegValue HKCU "Software\Microsoft\Windows\CurrentVersion\Run" "EyeGuard"
  RMDir "$INSTDIR"
SectionEnd
