; by the hm NIS Edit Script Wizard.

; gaim	 From	 INSTALLER
;GLOBAL VARIABLES
Var name
Var GTK_FOLDER

; HM NIS Edit Wizard helper defines
!define GOURMET_NAME "Gourmet Recipe Manager"
!define GOURMET_VERSION "0.8.3.3"
!define GOURMET_PUBLISHER "Thomas M. Hinkle"
!define GOURMET_WEB_SITE "http://grecipe-manager.sourceforge.net"
!define GOURMET_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Gourmet.exe"
!define GOURMET_UNINST_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${GOURMET_NAME}"
!define GOURMET_UNINST_ROOT_KEY "HKLM"
!define GOURMET_STARTMENU_REGVAL "NSIS:StartMenuDir"
; GTK Stuff from gaim
!define GTK_VERSION				"2.6.4"
!define GTK_REG_KEY				"SOFTWARE\GTK\2.0"
!define GTK_DEFAULT_INSTALL_PATH		"$PROGRAMFILES\Common Files\GTK\2.0"
!define GTK_RUNTIME_INSTALLER			"..\..\gtk-win32-2.6.4-rc3.exe"
;!define GTK_THEME_DIR				"..\..\gtk_installer\gtk_themes"
;!define GTK_DEFAULT_THEME_GTKRC_DIR		"share\themes\Default\gtk-2.0"
;!define GTK_DEFAULT_THEME_ENGINE_DIR		"lib\gtk-2.0\2.4.0\engines"

;--------------------- from gaim-installer
;Configuration
!ifdef WITH_GTK
OutFile "gourmet-installer-${GOURMET_VERSION}.exe"
!else
!ifdef DEBUG
OutFile "gourmet-${GOURMET_VERSION}-debug.exe"
!else
OutFile "gourmet-${GOURMET_VERSION}-no-gtk.exe"
!endif
!endif

; 1 Mui	.67 compatible ------
!include "MUI.nsh"

; MUI Settings
!define MUI_ABORTWARNING
!define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
!define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

; Welcome page
!insertmacro MUI_PAGE_WELCOME
; License page

; Alter License section
!define MUI_LICENSEPAGE_BUTTON		"Ok"
!define MUI_LICENSEPAGE_TEXT_BOTTOM	"Gourmet is licensed under the GPL, a license designed to guarantee your continued freedom to use and modify this software. If you wish to modify and distribute this software, you will need to accept this license. You need not accept the license merely to use this program."
;LicenseText "Gourmet is licensed under the GPL, a license designed to guarantee your continued freedom to use and modify this software. If you wish to modify and distribute this software, you will need to accept this license. You need not accept the license merely to use this program."
;LicenseData "..\LICENSE"
!insertmacro MUI_PAGE_LICENSE "..\LICENSE"
; Components page
;!insertmacro MUI_PAGE_COMPONENTS

; Directory page
!insertmacro MUI_PAGE_DIRECTORY
; Start menu page
var ICONS_GROUP
!define MUI_STARTMENUPAGE_NODISABLE
!define MUI_STARTMENUPAGE_DEFAULTFOLDER "Gourmet Recipe Manager"
!define MUI_STARTMENUPAGE_REGISTRY_ROOT "${GOURMET_UNINST_ROOT_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_KEY "${GOURMET_UNINST_KEY}"
!define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${GOURMET_STARTMENU_REGVAL}"
!insertmacro MUI_PAGE_STARTMENU Application $ICONS_GROUP
; Instfiles page
!insertmacro MUI_PAGE_INSTFILES
; Finish page
!define MUI_FINISHPAGE_RUN "$INSTDIR\Gourmet.exe"
!define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\documentation\README"
!insertmacro MUI_PAGE_FINISH

; Uninstaller pages
!insertmacro MUI_UNPAGE_INSTFILES

; Language files
!insertmacro MUI_LANGUAGE "English"

; MUI end ------

Name "${GOURMET_NAME} ${GOURMET_VERSION}"
; OutFile "Setup.exe"
InstallDir "$PROGRAMFILES\Gourmet Recipe Manager"
InstallDirRegKey HKLM "${GOURMET_DIR_REGKEY}" ""
ShowInstDetails show
ShowUnInstDetails show

;--------------------------------
;GTK+ Runtime Install Section
; Taken from GAIM code more or less verbatem

!ifdef WITH_GTK
Section $(GTK_SECTION_TITLE) SecGtk
  SectionIn 1 RO

  Call CheckUserInstallRights
  Pop $R1

  SetOutPath $TEMP
  SetOverwrite on
  File /oname=gtk-runtime.exe ${GTK_RUNTIME_INSTALLER}
  SetOverwrite off

  ; This keeps track whether we install GTK+ or not..
  StrCpy $R5 "0"

  Call DoWeNeedGtk
  Pop $R0
  Pop $R6

  StrCmp $R0 "0" have_gtk
  StrCmp $R0 "1" upgrade_gtk
  StrCmp $R0 "2" no_gtk no_gtk

  no_gtk:
    StrCmp $R1 "NONE" gtk_no_install_rights
    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE $ISSILENT /D=$GTK_FOLDER'
    Goto gtk_install_cont

  upgrade_gtk:
    StrCpy $GTK_FOLDER $R6
    IfSilent skip_mb
    MessageBox MB_YESNO $(GTK_UPGRADE_PROMPT) IDNO done
    skip_mb:
    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE $ISSILENT'
    Goto gtk_install_cont

  gtk_install_cont:
    IfErrors gtk_install_error
      StrCpy $R5 "1"  ; marker that says we installed...
      Goto done

    gtk_install_error:
      Delete "$TEMP\gtk-runtime.exe"
      IfSilent skip_mb1
      MessageBox MB_OK $(GTK_INSTALL_ERROR) IDOK
      skip_mb1:
      Quit

  have_gtk:
    StrCpy $GTK_FOLDER $R6
    StrCmp $R1 "NONE" done ; If we have no rights.. can't re-install..
    ; Even if we have a sufficient version of GTK+, we give user choice to re-install.
    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE $ISSILENT'
    IfErrors gtk_install_error
    Goto done

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; end got_install rights

  gtk_no_install_rights:
    ; Install GTK+ to Gourmet install dir
    StrCpy $GTK_FOLDER $INSTDIR
    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE $ISSILENT /D=$GTK_FOLDER'
    IfErrors gtk_install_error
      SetOverwrite on
      ClearErrors
      CopyFiles /FILESONLY "$GTK_FOLDER\bin\*.dll" $GTK_FOLDER
      SetOverwrite off
      IfErrors gtk_install_error
        Delete "$GTK_FOLDER\bin\*.dll"
        Goto done
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; end gtk_no_install_rights

  done:
    Delete "$TEMP\gtk-runtime.exe"
SectionEnd ; end of GTK+ section
!endif

; --- GOURMET MAIN INSTALL

Section "MainSection" SEC01
  SetOutPath "$INSTDIR"
  SetOverwrite try
  File "C:\Python23\dist\Gourmet.exe"
  File "C:\Python23\dist\_sre.pyd"
  File "C:\Python23\dist\wx._windows_.pyd"
  File "C:\Python23\dist\pyexpat.pyd"
  File "C:\Python23\dist\unicodedata.pyd"
  File "C:\Python23\dist\_winreg.pyd"
  File "C:\Python23\dist\Mk4py.dll"
  File "C:\Python23\dist\wxmsw254uh_gl_vc.dll"
  File "C:\Python23\dist\_imaging.pyd"
  File "C:\Python23\dist\gtk.glade.pyd"
  File "C:\Python23\dist\_tkinter.pyd"
  File "C:\Python23\dist\python23.dll"
  File "C:\Python23\dist\gobject.pyd"
  File "C:\Python23\dist\wx._controls_.pyd"
  File "C:\Python23\dist\_ssl.pyd"
  File "C:\Python23\dist\wx._misc_.pyd"
  File "C:\Python23\dist\gtk._gtk.pyd"
  File "C:\Python23\dist\wx._gdi_.pyd"
  File "C:\Python23\dist\_socket.pyd"
  File "C:\Python23\dist\wxmsw254uh_vc.dll"
  File "C:\Python23\dist\wxmsw254uh_stc_vc.dll"
  File "C:\Python23\dist\tk84.dll"
  File "C:\Python23\dist\wx._html.pyd"
  File "C:\Python23\dist\tcl84.dll"
  File "C:\Python23\dist\atk.pyd"
  File "C:\Python23\dist\_imagingtk.pyd"
  File "C:\Python23\dist\wxmsw254uh_gizmos_vc.dll"
  File "C:\Python23\dist\pango.pyd"
  File "C:\Python23\dist\mmap.pyd"
  File "C:\Python23\dist\wx._core_.pyd"
  File "C:\Python23\dist\zlib.pyd"
  File "C:\Python23\dist\LICENSE"
  File "C:\Python23\dist\README"

; Shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  CreateDirectory "$SMPROGRAMS\$ICONS_GROUP"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Gourmet Recipe Manager.lnk" "$INSTDIR\Gourmet.exe"
  CreateShortCut "$DESKTOP\Gourmet Recipe Manager.lnk" "$INSTDIR\Gourmet.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "DataFiles" SEC02
  SetOutPath "$INSTDIR\data\"
  File "C:\Python23\gourmet\data\gourmet_logo.png"
  File "C:\Python23\gourmet\data\recbox.png"
  File "C:\Python23\gourmet\data\recbox_biggish.png"
  File "C:\Python23\gourmet\data\recbox_icon.png"
  File "C:\Python23\gourmet\data\splash.png"
  File "C:\Python23\gourmet\data\default.css"
  File "C:\Python23\gourmet\data\app.glade"
  File "C:\Python23\gourmet\data\app_backup.glade"
  File "C:\Python23\gourmet\data\converter.glade"
  File "C:\Python23\gourmet\data\converter_new.glade"
  File "C:\Python23\gourmet\data\converter_old.glade"
  File "C:\Python23\gourmet\data\databaseChooser.glade"
  File "C:\Python23\gourmet\data\keyeditor.glade"
  File "C:\Python23\gourmet\data\recCard.glade"
  File "C:\Python23\gourmet\data\recCard_backup9-19.glade"
  File "C:\Python23\gourmet\data\recCard_backup9-25.glade"
  File "C:\Python23\gourmet\data\recSelector.glade"
  File "C:\Python23\gourmet\data\rec_ref_window.glade"
  File "C:\Python23\gourmet\data\shopCatEditor.glade"
  File "C:\Python23\gourmet\data\shopList.glade"
  File "C:\Python23\gourmet\data\recipe.dtd"
  SetOutPath "$INSTDIR\data\i18n"
  File "C:\Python23\gourmet\data\i18n\gourmet.mo"
  SetOutPath "$INSTDIR\data\i18n\de_DE\LC_MESSAGES"
  File "C:\Python23\gourmet\data\i18n\de_DE\LC_MESSAGES\gourmet.mo"

; Shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section "Documentation" SEC03
  SetOutPath "$INSTDIR\documentation\"
  SetOverwrite ifnewer
  File "..\TODO"
  File "..\README"
  File "..\LICENSE"
  File "..\CHANGES"

; Shortcuts
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section -AdditionalIcons
  SetOutPath $INSTDIR
  !insertmacro MUI_STARTMENU_WRITE_BEGIN Application
  WriteIniStr "$INSTDIR\${GOURMET_NAME}.url" "InternetShortcut" "URL" "${GOURMET_WEB_SITE}"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Website.lnk" "$INSTDIR\${GOURMET_NAME}.url"
  CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Uninstall.lnk" "$INSTDIR\uninst.exe"
  !insertmacro MUI_STARTMENU_WRITE_END
SectionEnd

Section -Post
  WriteUninstaller "$INSTDIR\uninst.exe"
  WriteRegStr HKLM "${GOURMET_DIR_REGKEY}" "" "$INSTDIR\Gourmet.exe"
  WriteRegStr ${GOURMET_UNINST_ROOT_KEY} "${GOURMET_UNINST_KEY}" "DisplayName" "$(^Name)"
  WriteRegStr ${GOURMET_UNINST_ROOT_KEY} "${GOURMET_UNINST_KEY}" "UninstallString" "$INSTDIR\uninst.exe"
  WriteRegStr ${GOURMET_UNINST_ROOT_KEY} "${GOURMET_UNINST_KEY}" "DisplayIcon" "$INSTDIR\Gourmet.exe"
  WriteRegStr ${GOURMET_UNINST_ROOT_KEY} "${GOURMET_UNINST_KEY}" "DisplayVersion" "${GOURMET_VERSION}"
  WriteRegStr ${GOURMET_UNINST_ROOT_KEY} "${GOURMET_UNINST_KEY}" "URLInfoAbout" "${GOURMET_WEB_SITE}"
  WriteRegStr ${GOURMET_UNINST_ROOT_KEY} "${GOURMET_UNINST_KEY}" "Publisher" "${GOURMET_PUBLISHER}"
SectionEnd

; Section descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !ifdef WITH_GTK
    !insertmacro MUI_DESCRIPTION_TEXT $(SECGTK) ""
  !endif
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC01} ""
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC02} ""
  !insertmacro MUI_DESCRIPTION_TEXT ${SEC03} ""
!insertmacro MUI_FUNCTION_DESCRIPTION_END


Function un.onUninstSuccess
  HideWindow
  MessageBox MB_ICONINFORMATION|MB_OK "Gourmet Recipe Manager was successfully removed from your computer."
FunctionEnd

Function un.onInit
  MessageBox MB_ICONQUESTION|MB_YESNO|MB_DEFBUTTON2 "Are you sure you want to completely remove Gourmet Recipe Manager and all of its components?" IDYES +2
  Abort
FunctionEnd

Section Uninstall
  !insertmacro MUI_STARTMENU_GETFOLDER "Application" $ICONS_GROUP
  Delete "$INSTDIR\${GOURMET_NAME}.url"
  Delete "$INSTDIR\uninst.exe"
  Delete "$INSTDIR\documentation\CHANGES"
  Delete "$INSTDIR\documentation\LICENSE"
  Delete "$INSTDIR\documentation\README"
  Delete "$INSTDIR\documentation\TODO"
  Delete "$INSTDIR\data\i18n\de_DE\LC_MESSAGES\gourmet.mo"
  Delete "$INSTDIR\data\i18n\gourmet.mo"
  Delete "$INSTDIR\data\recipe.dtd"
  Delete "$INSTDIR\data\shopList.glade"
  Delete "$INSTDIR\data\shopCatEditor.glade"
  Delete "$INSTDIR\data\rec_ref_window.glade"
  Delete "$INSTDIR\data\recSelector.glade"
  Delete "$INSTDIR\data\recCard_backup9-25.glade"
  Delete "$INSTDIR\data\recCard_backup9-19.glade"
  Delete "$INSTDIR\data\recCard.glade"
  Delete "$INSTDIR\data\keyeditor.glade"
  Delete "$INSTDIR\data\databaseChooser.glade"
  Delete "$INSTDIR\data\converter_old.glade"
  Delete "$INSTDIR\data\converter_new.glade"
  Delete "$INSTDIR\data\converter.glade"
  Delete "$INSTDIR\data\app_backup.glade"
  Delete "$INSTDIR\data\app.glade"
  Delete "$INSTDIR\data\default.css"
  Delete "$INSTDIR\data\splash.png"
  Delete "$INSTDIR\data\recbox_icon.png"
  Delete "$INSTDIR\data\recbox_biggish.png"
  Delete "$INSTDIR\data\recbox.png"
  Delete "$INSTDIR\data\gourmet_logo.png"
  Delete "$INSTDIR\README"
  Delete "$INSTDIR\LICENSE"
  Delete "$INSTDIR\zlib.pyd"
  Delete "$INSTDIR\wx._core_.pyd"
  Delete "$INSTDIR\mmap.pyd"
  Delete "$INSTDIR\pango.pyd"
  Delete "$INSTDIR\wxmsw254uh_gizmos_vc.dll"
  Delete "$INSTDIR\_imagingtk.pyd"
  Delete "$INSTDIR\atk.pyd"
  Delete "$INSTDIR\tcl84.dll"
  Delete "$INSTDIR\wx._html.pyd"
  Delete "$INSTDIR\tk84.dll"
  Delete "$INSTDIR\wxmsw254uh_stc_vc.dll"
  Delete "$INSTDIR\wxmsw254uh_vc.dll"
  Delete "$INSTDIR\_socket.pyd"
  Delete "$INSTDIR\wx._gdi_.pyd"
  Delete "$INSTDIR\gtk._gtk.pyd"
  Delete "$INSTDIR\wx._misc_.pyd"
  Delete "$INSTDIR\_ssl.pyd"
  Delete "$INSTDIR\wx._controls_.pyd"
  Delete "$INSTDIR\gobject.pyd"
  Delete "$INSTDIR\python23.dll"
  Delete "$INSTDIR\_tkinter.pyd"
  Delete "$INSTDIR\gtk.glade.pyd"
  Delete "$INSTDIR\_imaging.pyd"
  Delete "$INSTDIR\wxmsw254uh_gl_vc.dll"
  Delete "$INSTDIR\Mk4py.dll"
  Delete "$INSTDIR\_winreg.pyd"
  Delete "$INSTDIR\unicodedata.pyd"
  Delete "$INSTDIR\pyexpat.pyd"
  Delete "$INSTDIR\wx._windows_.pyd"
  Delete "$INSTDIR\_sre.pyd"
  Delete "$INSTDIR\Gourmet.exe"

  Delete "$SMPROGRAMS\$ICONS_GROUP\Uninstall.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Website.lnk"
  Delete "$DESKTOP\Gourmet Recipe Manager.lnk"
  Delete "$SMPROGRAMS\$ICONS_GROUP\Gourmet Recipe Manager.lnk"

  RMDir "$SMPROGRAMS\$ICONS_GROUP"
  RMDir "$INSTDIR\documentation\"
  RMDir "$INSTDIR\data\i18n\de_DE\LC_MESSAGES"
  RMDir "$INSTDIR\data\i18n"
  RMDir "$INSTDIR\data\"
  RMDir "$INSTDIR"
  DeleteRegKey ${GOURMET_UNINST_ROOT_KEY} "${GOURMET_UNINST_KEY}"
  DeleteRegKey HKLM "${GOURMET_DIR_REGKEY}"
  SetAutoClose true
SectionEnd

; Functions from GAIM installer stuff (shamelessly stolen)
;--------------------------------
;Functions

;
; Usage:
;
; Call CanWeInstallATheme
; Pop $R0
;
; Return:
;   "" - If no
;   "root path of GTK+ installation" - if yes
;
Function CanWeInstallATheme
    Push $1
    Push $0

    ; Set default.. no rights
    StrCpy $1 ""

    Call CheckUserInstallRights
    Pop $0

    ; If no rights check if gtk was installed to gaim dir..
    StrCmp $0 "NONE" 0 themes_cont
      StrCmp $GTK_FOLDER $INSTDIR 0 no_rights
        StrCpy $1 $INSTDIR
	Goto done
    themes_cont:

    StrCmp $0 "HKCU" hkcu hklm

    hkcu:
      ReadRegStr $1 HKCU ${GTK_REG_KEY} "Path"
      StrCmp $1 "" no_rights done

    hklm:
      ReadRegStr $1 HKLM ${GTK_REG_KEY} "Path"
      Goto done

    no_rights:
      IfSilent skip_mb
      MessageBox MB_OK $(GTK_NO_THEME_INSTALL_RIGHTS) IDOK
      skip_mb:
      StrCpy $1 ""

    done:
      Pop $0
      Exch $1
FunctionEnd


Function CheckUserInstallRights
	ClearErrors
	UserInfo::GetName
	IfErrors Win9x
	Pop $0
	UserInfo::GetAccountType
	Pop $1

	StrCmp $1 "Admin" 0 +3
                StrCpy $1 "HKLM"
		Goto done
	StrCmp $1 "Power" 0 +3
                StrCpy $1 "HKLM"
		Goto done
	StrCmp $1 "User" 0 +3
		StrCpy $1 "HKCU"
		Goto done
	StrCmp $1 "Guest" 0 +3
		StrCpy $1 "NONE"
		Goto done
	; Unknown error
	StrCpy $1 "NONE"
        Goto done

	Win9x:
		StrCpy $1 "HKLM"

	done:
        Push $1
FunctionEnd

Function un.CheckUserInstallRights
	ClearErrors
	UserInfo::GetName
	IfErrors Win9x
	Pop $0
	UserInfo::GetAccountType
	Pop $1

	StrCmp $1 "Admin" 0 +3
                StrCpy $1 "HKLM"
		Goto done
	StrCmp $1 "Power" 0 +3
                StrCpy $1 "HKLM"
		Goto done
	StrCmp $1 "User" 0 +3
		StrCpy $1 "HKCU"
		Goto done
	StrCmp $1 "Guest" 0 +3
		StrCpy $1 "NONE"
		Goto done
	; Unknown error
	StrCpy $1 "NONE"
        Goto done

	Win9x:
		StrCpy $1 "HKLM"

	done:
        Push $1
FunctionEnd

;
; Usage:
;   Push $0 ; Path string
;   Call VerifyDir
;   Pop $0 ; 0 - Bad path  1 - Good path
;
Function VerifyDir
  Pop $0
  Loop:
    IfFileExists $0 dir_exists
    StrCpy $1 $0 ; save last
    Push $0
    Call GetParent
    Pop $0
    StrLen $2 $0
    ; IfFileExists "C:" on xp returns true and on win2k returns false
    ; So we're done in such a case..
    IntCmp $2 2 loop_done
    ; GetParent of "C:" returns ""
    IntCmp $2 0 loop_done
    Goto Loop

  loop_done:
    StrCpy $1 "$0\GaImFooB"
    ; Check if we can create dir on this drive..
    ClearErrors
    CreateDirectory $1
    IfErrors DirBad DirGood

  dir_exists:
    ClearErrors
    FileOpen $1 "$0\gaimfoo.bar" w
    IfErrors PathBad PathGood

    DirGood:
      RMDir $1
      Goto PathGood1

    DirBad:
      RMDir $1
      Goto PathBad1

    PathBad:
      FileClose $1
      Delete "$0\gaimfoo.bar"
      PathBad1:
      StrCpy $0 "0"
      Push $0
      Return

    PathGood:
      FileClose $1
      Delete "$0\gaimfoo.bar"
      PathGood1:
      StrCpy $0 "1"
      Push $0
FunctionEnd

Function .onVerifyInstDir
  Push $INSTDIR
  Call VerifyDir
  Pop $0
  StrCmp $0 "0" 0 dir_good
    Abort
  dir_good:
FunctionEnd

; GetParent
; input, top of stack  (e.g. C:\Program Files\Poop)
; output, top of stack (replaces, with e.g. C:\Program Files)
; modifies no other variables.
;
; Usage:
;   Push "C:\Program Files\Directory\Whatever"
;   Call GetParent
;   Pop $R0
;   ; at this point $R0 will equal "C:\Program Files\Directory"
Function GetParent
   Exch $0 ; old $0 is on top of stack
   Push $1
   Push $2
   StrCpy $1 -1
   loop:
     StrCpy $2 $0 1 $1
     StrCmp $2 "" exit
     StrCmp $2 "\" exit
     IntOp $1 $1 - 1
   Goto loop
   exit:
     StrCpy $0 $0 $1
     Pop $2
     Pop $1
     Exch $0 ; put $0 on top of stack, restore $0 to original value
FunctionEnd


; CheckGtkVersion
; inputs: Push 2 GTK+ version strings to check. The major value needs to
; be equal and the minor value needs to be greater or equal.
;
; Usage:
;   Push "2.1.0"  ; Refrence version
;   Push "2.2.1"  ; Version to check
;   Call CheckGtkVersion
;   Pop $R0
;   $R0 will now equal "1", because 2.2 is greater than 2.1
;
Function CheckGtkVersion
  ; Version we want to check
  Pop $6
  ; Reference version
  Pop $8

  ; Check that the string to check is at least 5 chars long (i.e. x.x.x)
  StrLen $7 $6
  IntCmp $7 5 0 bad_version

  ; Major version check
  StrCpy $7 $6 1
  StrCpy $9 $8 1
  IntCmp $7 $9 check_minor bad_version bad_version

  check_minor:
    StrCpy $7 $6 1 2
    StrCpy $9 $8 1 2
    IntCmp $7 $9 good_version bad_version good_version

  bad_version:
    StrCpy $6 "0"
    Push $6
    Goto done

  good_version:
    StrCpy $6 "1"
    Push $6
  done:
FunctionEnd

;
; Usage:
; Call DoWeNeedGtk
; First Pop:
;   0 - We have the correct version
;       Second Pop: Key where Version was found
;   1 - We have an old version that needs to be upgraded
;       Second Pop: HKLM or HKCU depending on where GTK was found.
;   2 - We don't have Gtk+ at all
;       Second Pop: "NONE, HKLM or HKCU" depending on our rights..
;
Function DoWeNeedGtk
  ; Logic should be:
  ; - Check what user rights we have (HKLM or HKCU)
  ;   - If HKLM rights..
  ;     - Only check HKLM key for GTK+
  ;       - If installed to HKLM, check it and return.
  ;   - If HKCU rights..
  ;     - First check HKCU key for GTK+
  ;       - if good or bad exists stop and ret.
  ;     - If no hkcu gtk+ install, check HKLM
  ;       - If HKLM ver exists but old, return as if no ver exits.
  ;   - If no rights
  ;     - Check HKLM

  Call CheckUserInstallRights
  Pop $3
  StrCmp $3 "HKLM" check_hklm
  StrCmp $3 "HKCU" check_hkcu check_hklm
    check_hkcu:
      ReadRegStr $0 HKCU ${GTK_REG_KEY} "Version"
      StrCpy $5 "HKCU"
      StrCmp $0 "" check_hklm have_gtk

    check_hklm:
      ReadRegStr $0 HKLM ${GTK_REG_KEY} "Version"
      StrCpy $5 "HKLM"
      StrCmp $0 "" no_gtk have_gtk


  have_gtk:
    ; GTK+ is already installed.. check version.
    StrCpy $1 ${GTK_VERSION} ; Minimum GTK+ version needed
    Push $1
    Push $0
    Call CheckGtkVersion
    Pop $2
    StrCmp $2 "1" good_version bad_version
    bad_version:
      ; Bad version. If hklm ver and we have hkcu or no rights.. return no gtk
      StrCmp $3 "NONE" no_gtk  ; if no rights.. can't upgrade
      StrCmp $3 "HKCU" 0 upgrade_gtk ; if HKLM can upgrade..
        StrCmp $5 "HKLM" no_gtk upgrade_gtk ; have hkcu rights.. if found hklm ver can't upgrade..

      upgrade_gtk:
        StrCpy $2 "1"
        Push $5
        Push $2
        Goto done

  good_version:
    StrCmp $5 "HKLM" have_hklm_gtk have_hkcu_gtk
      have_hkcu_gtk:
        ; Have HKCU version
        ReadRegStr $4 HKCU ${GTK_REG_KEY} "Path"
        Goto good_version_cont

      have_hklm_gtk:
        ReadRegStr $4 HKLM ${GTK_REG_KEY} "Path"
        Goto good_version_cont

    good_version_cont:
      StrCpy $2 "0"
      Push $4  ; The path to existing GTK+
      Push $2
      Goto done

  no_gtk:
    StrCpy $2 "2"
    Push $3 ; our rights
    Push $2
    Goto done

  done:
FunctionEnd

Function RunCheck
  System::Call 'kernel32::OpenMutex(i 2031617, b 0, t "gourmet_is_running") i .R0'
  IntCmp $R0 0 done
  MessageBox MB_OK|MB_ICONEXCLAMATION $(GAIM_IS_RUNNING) IDOK
    Abort
  done:
FunctionEnd

Function un.RunCheck
  System::Call 'kernel32::OpenMutex(i 2031617, b 0, t "gourmet_is_running") i .R0'
  IntCmp $R0 0 done
  MessageBox MB_OK|MB_ICONEXCLAMATION $(GOURMET_IS_RUNNING) IDOK
    Abort
  done:
FunctionEnd

;; Function .onInit
;;   System::Call 'kernel32::CreateMutexA(i 0, i 0, t "gourmet_installer_running") i .r1 ?e'
;;   Pop $R0
;;   StrCmp $R0 0 +3
;;     MessageBox MB_OK|MB_ICONEXCLAMATION $(INSTALLER_IS_RUNNING)
;;     Abort
;;   Call RunCheck
;;   StrCpy $name "Gourmet ${GOURMET_VERSION}"
;;   ;StrCpy $GTK_THEME_SEL ${SecGtkWimp}
;;   ;StrCpy $ISSILENT "/NOUI"

;;   ; GTK installer has two silent states.. one with Message boxes, one without
;;   ; If gaim installer was run silently, we want to supress gtk installer msg boxes.
;;   IfSilent 0 set_gtk_normal
;;       StrCpy $ISSILENT "/S"
;;   set_gtk_normal:

;;   Call ParseParameters

;;   ; Select Language
;;   ;IntCmp $LANG_IS_SET 1 skip_lang
;;   ;  ; Display Language selection dialog
;;   ;  !insertmacro MUI_LANGDLL_DISPLAY
;;   ;  skip_lang:

;;   ; If install path was set on the command, use it.
;;   StrCmp $INSTDIR "" 0 instdir_done

;;   ;  If gaim is currently intalled, we should default to where it is currently installed
;;   ClearErrors
;;   ReadRegStr $INSTDIR HKCU "${GOURMET_REG_KEY}" ""
;;   IfErrors +2
;;   StrCmp $INSTDIR "" 0 instdir_done
;;   ReadRegStr $INSTDIR HKLM "${GOURMET_REG_KEY}" ""
;;   IfErrors +2
;;   StrCmp $INSTDIR "" 0 instdir_done

;;   Call CheckUserInstallRights
;;   Pop $0

;;   StrCmp $0 "HKLM" 0 user_dir
;;     StrCpy $INSTDIR "$PROGRAMFILES\Gaim"
;;     Goto instdir_done
;;   user_dir:
;;     StrCpy $2 "$SMPROGRAMS"
;;     Push $2
;;     Call GetParent
;;     Call GetParent
;;     Pop $2
;;     StrCpy $INSTDIR "$2\Gaim"

;;   instdir_done:

;; FunctionEnd

;; Function un.onInit
;;   Call un.RunCheck
;;   StrCpy $name "Gourmet Recipe Manager ${GOURMET_VERSION}"

;;   ; Get stored language prefrence
;;   ReadRegStr $LANGUAGE HKCU ${GOURMET_REG_KEY} "${GOURMET_REG_LANG}"

;; FunctionEnd

;; Function .onSelChange
;;   Push $0
;;   Push $2

;;   StrCpy $2 ${SF_SELECTED}
;;   SectionGetFlags ${SecGtkNone} $0
;;   IntOp $2 $2 & $0
;;   ;SectionGetFlags ${SecGtkWimp} $0
;;   ;IntOp $2 $2 & $0
;;   ;SectionGetFlags ${SecGtkBluecurve} $0
;;   ;IntOp $2 $2 & $0
;;   ;SectionGetFlags ${SecGtkLighthouseblue} $0
;;   ;IntOp $2 $2 & $0
;;   StrCmp $2 0 skip
;;     SectionSetFlags ${SecGtkNone} 0
;;     ;SectionSetFlags ${SecGtkWimp} 0
;;     ;SectionSetFlags ${SecGtkBluecurve} 0
;;     ;SectionSetFlags ${SecGtkLighthouseblue} 0
;;   skip:

;;   !insertmacro UnselectSection $GTK_THEME_SEL

;;   ; Remember old selection
;;   StrCpy $2 $GTK_THEME_SEL

;;   ; Now go through and see who is checked..
;;   SectionGetFlags ${SecGtkNone} $0
;;   IntOp $0 $0 & ${SF_SELECTED}
;;   IntCmp $0 ${SF_SELECTED} 0 +2 +2
;;     StrCpy $GTK_THEME_SEL ${SecGtkNone}
;;   ;SectionGetFlags ${SecGtkWimp} $0
;;   ;IntOp $0 $0 & ${SF_SELECTED}
;;   ;IntCmp $0 ${SF_SELECTED} 0 +2 +2
;;     ;StrCpy $GTK_THEME_SEL ${SecGtkWimp}
;;   ;SectionGetFlags ${SecGtkBluecurve} $0
;;   ;IntOp $0 $0 & ${SF_SELECTED}
;;   ;IntCmp $0 ${SF_SELECTED} 0 +2 +2
;;   ;  StrCpy $GTK_THEME_SEL ${SecGtkBluecurve}
;;   ;SectionGetFlags ${SecGtkLighthouseblue} $0
;;   ;IntOp $0 $0 & ${SF_SELECTED}
;;   ;IntCmp $0 ${SF_SELECTED} 0 +2 +2
;;   ;  StrCpy $GTK_THEME_SEL ${SecGtkLighthouseblue}

;;   ;StrCmp $2 $GTK_THEME_SEL 0 +2 ; selection hasn't changed
;;   ;  !insertmacro SelectSection $GTK_THEME_SEL

;;   Pop $2
;;   Pop $0
;; FunctionEnd

;; ; Page enter and exit functions..

;; Function preWelcomePage
;;   ; If this installer dosn't have GTK, check whether we need it.
;;   ; We do this here an not in .onInit because language change in
;;   ; .onInit doesn't take effect until it is finished.
;;   !ifndef WITH_GTK
;;     Call DoWeNeedGtk
;;     Pop $0
;;     Pop $GTK_FOLDER

;;     StrCmp $0 "0" have_gtk need_gtk
;;     need_gtk:
;;       IfSilent skip_mb
;;       MessageBox MB_OK $(GTK_INSTALLER_NEEDED) IDOK
;;       skip_mb:
;;       Quit
;;     have_gtk:
;;   !endif
;; FunctionEnd

!ifdef WITH_GTK
Function preGtkDirPage
  Call DoWeNeedGtk
  Pop $0
  Pop $1

  StrCmp $0 "0" have_gtk
  StrCmp $0 "1" upgrade_gtk
  StrCmp $0 "2" no_gtk no_gtk

  ; Don't show dir selector.. Upgrades are done to existing path..
  have_gtk:
  upgrade_gtk:
    Abort

  no_gtk:
    StrCmp $1 "NONE" 0 no_gtk_cont
      ; Got no install rights..
      Abort
    no_gtk_cont:
      ; Suggest path..
      StrCmp $1 "HKCU" 0 hklm1
        StrCpy $2 "$SMPROGRAMS"
        Push $2
        Call GetParent
        Call GetParent
        Pop $2
        StrCpy $2 "$2\GTK\2.0"
        Goto got_path
      hklm1:
        StrCpy $2 "${GTK_DEFAULT_INSTALL_PATH}"

   got_path:
     StrCpy $name "GTK+ ${GTK_VERSION}"
     StrCpy $GTK_FOLDER $2
FunctionEnd

Function postGtkDirPage
  StrCpy $name "Gaim ${GAIM_VERSION}"
  Push $GTK_FOLDER
  Call VerifyDir
  Pop $0
  StrCmp $0 "0" 0 done
    IfSilent skip_mb
    MessageBox MB_OK $(GTK_BAD_INSTALL_PATH) IDOK
    skip_mb:
    Abort
  done:
FunctionEnd
!endif

; GetParameters
; input, none
; output, top of stack (replaces, with e.g. whatever)
; modifies no other variables.

Function GetParameters

   Push $R0
   Push $R1
   Push $R2
   Push $R3

   StrCpy $R2 1
   StrLen $R3 $CMDLINE

   ;Check for quote or space
   StrCpy $R0 $CMDLINE $R2
   StrCmp $R0 '"' 0 +3
     StrCpy $R1 '"'
     Goto loop
   StrCpy $R1 " "

   loop:
     IntOp $R2 $R2 + 1
     StrCpy $R0 $CMDLINE 1 $R2
     StrCmp $R0 $R1 get
     StrCmp $R2 $R3 get
     Goto loop

   get:
     IntOp $R2 $R2 + 1
     StrCpy $R0 $CMDLINE 1 $R2
     StrCmp $R0 " " get
     StrCpy $R0 $CMDLINE "" $R2

   Pop $R3
   Pop $R2
   Pop $R1
   Exch $R0

FunctionEnd

 ; StrStr
 ; input, top of stack = string to search for
 ;        top of stack-1 = string to search in
 ; output, top of stack (replaces with the portion of the string remaining)
 ; modifies no other variables.
 ;
 ; Usage:
 ;   Push "this is a long ass string"
 ;   Push "ass"
 ;   Call StrStr
 ;   Pop $R0
 ;  ($R0 at this point is "ass string")

Function StrStr
   Exch $R1 ; st=haystack,old$R1, $R1=needle
   Exch    ; st=old$R1,haystack
   Exch $R2 ; st=old$R1,old$R2, $R2=haystack
   Push $R3
   Push $R4
   Push $R5
   StrLen $R3 $R1
   StrCpy $R4 0
   ; $R1=needle
   ; $R2=haystack
   ; $R3=len(needle)
   ; $R4=cnt
   ; $R5=tmp
   loop:
     StrCpy $R5 $R2 $R3 $R4
     StrCmp $R5 $R1 done
     StrCmp $R5 "" done
     IntOp $R4 $R4 + 1
     Goto loop
   done:
   StrCpy $R1 $R2 "" $R4
   Pop $R5
   Pop $R4
   Pop $R3
   Pop $R2
   Exch $R1
FunctionEnd

;
; Parse the Command line
;
; Unattended install command line parameters
; /L=Language e.g.: /L=1033
;
;Function ParseParameters
;  IntOp $LANG_IS_SET 0 + 0
;  Call GetParameters
;  Pop $R0
;  Push $R0
;  Push "L="
;  Call StrStr
;  Pop $R1
;  StrCmp $R1 "" next
;  StrCpy $R1 $R1 4 2 ; Strip first 2 chars of string
;  StrCpy $LANGUAGE $R1
;  IntOp $LANG_IS_SET 0 + 1
;  next:
;FunctionEnd

; GetWindowsVersion
;
; Based on Yazno's function, http://yazno.tripod.com/powerpimpit/
; Updated by Joost Verburg
;
; Returns on top of stack
;
; Windows Version (95, 98, ME, NT x.x, 2000, XP, 2003)
; or
; '' (Unknown Windows Version)
;
; Usage:
;   Call GetWindowsVersion
;   Pop $R0
;
; at this point $R0 is "NT 4.0" or whatnot
Function GetWindowsVersion

  Push $R0
  Push $R1

  ReadRegStr $R0 HKLM \
  "SOFTWARE\Microsoft\Windows NT\CurrentVersion" CurrentVersion

  IfErrors 0 lbl_winnt

  ; we are not NT
  ReadRegStr $R0 HKLM \
  "SOFTWARE\Microsoft\Windows\CurrentVersion" VersionNumber

  StrCpy $R1 $R0 1
  StrCmp $R1 '4' 0 lbl_error

  StrCpy $R1 $R0 3

  StrCmp $R1 '4.0' lbl_win32_95
  StrCmp $R1 '4.9' lbl_win32_ME lbl_win32_98

  lbl_win32_95:
    StrCpy $R0 '95'
  Goto lbl_done

  lbl_win32_98:
    StrCpy $R0 '98'
  Goto lbl_done

  lbl_win32_ME:
    StrCpy $R0 'ME'
  Goto lbl_done

  lbl_winnt:
    StrCpy $R1 $R0 1

    StrCmp $R1 '3' lbl_winnt_x
    StrCmp $R1 '4' lbl_winnt_x

    StrCpy $R1 $R0 3

    StrCmp $R1 '5.0' lbl_winnt_2000
    StrCmp $R1 '5.1' lbl_winnt_XP
    StrCmp $R1 '5.2' lbl_winnt_2003 lbl_error

  lbl_winnt_x:
    StrCpy $R0 "NT $R0" 6
  Goto lbl_done

  lbl_winnt_2000:
    Strcpy $R0 '2000'
  Goto lbl_done

  lbl_winnt_XP:
    Strcpy $R0 'XP'
  Goto lbl_done

  lbl_winnt_2003:
    Strcpy $R0 '2003'
  Goto lbl_done

  lbl_error:
    Strcpy $R0 ''
  lbl_done:

  Pop $R1
  Exch $R0
FunctionEnd