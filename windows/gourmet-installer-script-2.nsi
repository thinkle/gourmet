; Installer script for win32 Gourmet
; First author: Thomas Hinkle (thomas_hinkle@users.sourceforge.net)
; Second author: Daniel Folkinshteyn (nanotube@users.sourceforge.net)
; Third author: Bernhard Reiter (ockham@raz.or.at)
;
; Heavily borrowed from Installer script for win32 Gaim
; Herman Bloggs <hermanator12002@yahoo.com>
;
; NOTE: this .NSI script is intended for NSIS 2.0 (final release).

;--------------------------------
;Global Variables
    Var name
    Var GTK_FOLDER
    Var GTK_THEME_SEL
    Var LANG_IS_SET
    Var ISSILENT
    ;Var ISSILENT_STATE
    ;Var STARTUP_RUN_KEY
    ;Var GOURMET_UNINST_ROOT_KEY
    Var GTK_VERSION_INSTALLED
    Var GTK_UPGRADE_MESSAGE_CONTENT
    Var GTK_INSTALL_ERROR_HELPFUL

;--------------------------------
;Defines

    !define GOURMET_NAME "Gourmet Recipe Manager"
    !define GOURMET_VERSION "0.15.3-2alpha"
    !define GOURMET_PUBLISHER "Thomas M. Hinkle"
    !define GOURMET_WEB_SITE "http://grecipe-manager.sourceforge.net"
    !define GOURMET_DOWNLOAD_SITE "http://sourceforge.net/project/showfiles.php?group_id=108118"
    !define GOURMET_DIR_REGKEY "Software\Microsoft\Windows\CurrentVersion\App Paths\Gourmet.exe"
    !define GOURMET_UNINSTALL_KEY "Software\Microsoft\Windows\CurrentVersion\Uninstall\${GOURMET_NAME}"
    !define GOURMET_UNINST_ROOT_KEY "HKLM"
    !define GOURMET_STARTMENU_REGVAL "NSIS:StartMenuDir"

    !define PYTHON_PATH "C:\Program Files\Python26"

    !define GOURMET_NSIS_INCLUDE_PATH           ".\nsis"


    !define GOURMET_REG_KEY             "SOFTWARE\gourmet"
    !define HKLM_APP_PATHS_KEY                  "${GOURMET_DIR_REGKEY}"
    !define GOURMET_STARTUP_RUN_KEY         "SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
    !define GOURMET_UNINST_EXE              "gourmet-uninst.exe"
    !define GOURMET_REG_LANG                "Installer Language"

    !define GTK_VERSION             "2.12.9"
    !define GTK_REG_KEY             "SOFTWARE\GTK\2.0"
    !define GTK_DEFAULT_INSTALL_PATH        "$COMMONFILES\GTK\2.0"
    !define GTK_RUNTIME_INSTALLER       "gtk-2.12.9-win32-2.exe"  ;"gtk-runtime*.exe"

    !define GTK_DEFAULT_THEME_GTKRC_DIR     "share\themes\Default\gtk-2.0"
    !define GTK_DEFAULT_THEME_ENGINE_DIR        "lib\gtk-2.0\2.4.0\engines"

    ; Uncomment this to make an installer with GTK installer integrated.
    !define WITH_GTK

    ;TODO (done, answer is no) do we need these?
    ;!define GTK_THEME_DIR              "..\gtk_installer\gtk_themes"
    ;!define GOURMET_INSTALLER_DEPS         "..\win32-dev\gourmet-inst-deps"


;--------------------------------
;Configuration

    ;The $name var is set in .onInit
    Name $name

    !ifdef WITH_GTK
        OutFile "gourmet-${GOURMET_VERSION}-full_gtkglade-${GTK_VERSION}.exe"
    !else
        !ifdef DEBUG
            OutFile "gourmet-${GOURMET_VERSION}-debug.exe"
        !else
            OutFile "gourmet-${GOURMET_VERSION}-no-gtkglade.exe"
        !endif
    !endif

    SetCompressor lzma
    ShowInstDetails show
    ShowUninstDetails show
    SetDateSave on

; $name and $INSTDIR are set in .onInit function..

    !include "MUI.nsh"
    !include "Sections.nsh"

;--------------------------------
;Modern UI Configuration

    !define MUI_ABORTWARNING
    !define MUI_ICON "${NSISDIR}\Contrib\Graphics\Icons\modern-install.ico"
    !define MUI_UNICON "${NSISDIR}\Contrib\Graphics\Icons\modern-uninstall.ico"

;;  we dont use components page.
;;  !define MUI_COMPONENTSPAGE_SMALLDESC

;--------------------------------
;Pages

    ; Welcome page
        ;we do the customfunctionpre thing so we can check if a gtk installer is needed,
        ;when we use a no-gtk installer exe. see comments in preWelcomePage function.
        !define MUI_PAGE_CUSTOMFUNCTION_PRE     preWelcomePage

        !insertmacro MUI_PAGE_WELCOME

    ; License page
        ; Alter License section
            !define MUI_LICENSEPAGE_BUTTON      "Ok"
            !define MUI_LICENSEPAGE_TEXT_BOTTOM "Gourmet is licensed under the GPL, a license designed to guarantee your continued freedom to use and modify this software. If you wish to modify and distribute this software, you will need to accept this license. You need not accept the license merely to use this program."
        !insertmacro MUI_PAGE_LICENSE "..\LICENSE"


    ; Components page
        ;probably dont need it for gourmet
        !insertmacro MUI_PAGE_COMPONENTS

    ; GTK+ install dir page, if needed
    ; TODO: check up on GTK_FOLDER var
        !ifdef WITH_GTK
          !define MUI_PAGE_CUSTOMFUNCTION_PRE       preGtkDirPage
          !define MUI_PAGE_CUSTOMFUNCTION_LEAVE     postGtkDirPage
          !define MUI_DIRECTORYPAGE_VARIABLE        $GTK_FOLDER
          !insertmacro MUI_PAGE_DIRECTORY
        !endif

    ; Install dir page
        !insertmacro MUI_PAGE_DIRECTORY

    ; Start menu page
        var ICONS_GROUP
        !define MUI_STARTMENUPAGE_NODISABLE
        !define MUI_STARTMENUPAGE_DEFAULTFOLDER "${GOURMET_NAME}"
        !define MUI_STARTMENUPAGE_REGISTRY_ROOT "${GOURMET_UNINST_ROOT_KEY}"
        !define MUI_STARTMENUPAGE_REGISTRY_KEY "${GOURMET_UNINSTALL_KEY}"
        !define MUI_STARTMENUPAGE_REGISTRY_VALUENAME "${GOURMET_STARTMENU_REGVAL}"
        !insertmacro MUI_PAGE_STARTMENU Application $ICONS_GROUP

section
    MessageBox MB_OK "Note that this is an alpha version! $\r $\r \
                      While the Windows version is basically identical to the Linux version, \ 
                      it has not been tested as thouroughly. Also, as some of the components Gourmet relies on \
                      are not available for Windows, some features (mainly plugins) are not (yet) available. Specifically, the $\r \
                      * Browse Recipes, $\r \
                      * Printing & PDF Export, $\r \
                      * Spell Checking, and $\r \
                      * Python Shell $\r \
                      plugins are currently not working. $\r $\r \
                      Furthermore, there seem to be some errors related to the $\r \
                      * Nutritional Information and $\r \ 
                      * Unit Display Preferences $\r \
                      plugins, in particular when deactivating them again. $\r $\r \
                      We're currently working on resolving these issues. $\r \
                      If you experience any other issues, please report them at Gourmet's bug tracking system \ 
                      at http://sourceforge.net/tracker/?group_id=108118&atid=649652 -- \ 
                      by doing so, you can help us improve Gourmet! $\r $\r \
                      (This information is also available in the README file)" /SD IDOK
sectionEnd

    ; Instfiles page
        !insertmacro MUI_PAGE_INSTFILES

    ; Finish page
        !define MUI_FINISHPAGE_NOAUTOCLOSE
        !define MUI_FINISHPAGE_RUN "$INSTDIR\Gourmet.exe"
        !define MUI_FINISHPAGE_RUN_NOTCHECKED
        !define MUI_FINISHPAGE_SHOWREADME "$INSTDIR\documentation\README"
        !define MUI_FINISHPAGE_TEXT_REBOOT "If you just installed GTK+ for the first time, you have to reboot before running Gourmet."
        !define MUI_FINISHPAGE_TEXT_REBOOTLATER "Reboot manually, later."
        !define MUI_FINISHPAGE_TEXT_REBOOTNOW "Reboot automatically right now."
        !define MUI_FINISHPAGE_LINK         ${GOURMET_WEB_SITE}
        !define MUI_FINISHPAGE_LINK_LOCATION          ${GOURMET_WEB_SITE}
        !insertmacro MUI_PAGE_FINISH


        !define MUI_UNFINISHPAGE_NOAUTOCLOSE
        !insertmacro MUI_UNPAGE_WELCOME
        !insertmacro MUI_UNPAGE_CONFIRM
        !insertmacro MUI_UNPAGE_INSTFILES
        !insertmacro MUI_UNPAGE_FINISH


;--------------------------------
;Languages

  ;; English goes first because its the default. The rest are
  ;; in alphabetical order (at least the strings actually displayed
  ;; will be).

  !insertmacro MUI_LANGUAGE "English"

  !insertmacro MUI_LANGUAGE "Albanian"
  !insertmacro MUI_LANGUAGE "Bulgarian"
  !insertmacro MUI_LANGUAGE "Catalan"
  !insertmacro MUI_LANGUAGE "Czech"
  !insertmacro MUI_LANGUAGE "Danish"
  !insertmacro MUI_LANGUAGE "SimpChinese"
  !insertmacro MUI_LANGUAGE "TradChinese"
  !insertmacro MUI_LANGUAGE "German"
  !insertmacro MUI_LANGUAGE "Spanish"
  !insertmacro MUI_LANGUAGE "French"
  !insertmacro MUI_LANGUAGE "Hebrew"
  !insertmacro MUI_LANGUAGE "Italian"
  !insertmacro MUI_LANGUAGE "Japanese"
  !insertmacro MUI_LANGUAGE "Korean"
  !insertmacro MUI_LANGUAGE "Hungarian"
  !insertmacro MUI_LANGUAGE "Dutch"
  !insertmacro MUI_LANGUAGE "Norwegian"
  !insertmacro MUI_LANGUAGE "Polish"
  !insertmacro MUI_LANGUAGE "PortugueseBR"
  !insertmacro MUI_LANGUAGE "Portuguese"
  !insertmacro MUI_LANGUAGE "Romanian"
  !insertmacro MUI_LANGUAGE "Russian"
  !insertmacro MUI_LANGUAGE "Serbian"
  !insertmacro MUI_LANGUAGE "Slovak"
  !insertmacro MUI_LANGUAGE "Slovenian"
  !insertmacro MUI_LANGUAGE "Finnish"
  !insertmacro MUI_LANGUAGE "Swedish"

;--------------------------------
;Translations

  !define GOURMET_DEFAULT_LANGFILE "${GOURMET_NSIS_INCLUDE_PATH}\translations\english.nsh"

  !include "${GOURMET_NSIS_INCLUDE_PATH}\langmacros.nsh"

  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "ALBANIAN"        "${GOURMET_NSIS_INCLUDE_PATH}\translations\albanian.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "BULGARIAN"       "${GOURMET_NSIS_INCLUDE_PATH}\translations\bulgarian.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "CATALAN"     "${GOURMET_NSIS_INCLUDE_PATH}\translations\catalan.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "CZECH"       "${GOURMET_NSIS_INCLUDE_PATH}\translations\czech.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "DANISH"      "${GOURMET_NSIS_INCLUDE_PATH}\translations\danish.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "DUTCH"       "${GOURMET_NSIS_INCLUDE_PATH}\translations\dutch.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "ENGLISH"     "${GOURMET_NSIS_INCLUDE_PATH}\translations\english.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "FINNISH"     "${GOURMET_NSIS_INCLUDE_PATH}\translations\finnish.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "FRENCH"      "${GOURMET_NSIS_INCLUDE_PATH}\translations\french.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "GERMAN"      "${GOURMET_NSIS_INCLUDE_PATH}\translations\german.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "HEBREW"      "${GOURMET_NSIS_INCLUDE_PATH}\translations\hebrew.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "HUNGARIAN"       "${GOURMET_NSIS_INCLUDE_PATH}\translations\hungarian.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "ITALIAN"     "${GOURMET_NSIS_INCLUDE_PATH}\translations\italian.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "JAPANESE"        "${GOURMET_NSIS_INCLUDE_PATH}\translations\japanese.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "KOREAN"      "${GOURMET_NSIS_INCLUDE_PATH}\translations\korean.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "NORWEGIAN"       "${GOURMET_NSIS_INCLUDE_PATH}\translations\norwegian.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "POLISH"      "${GOURMET_NSIS_INCLUDE_PATH}\translations\polish.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "PORTUGUESE"      "${GOURMET_NSIS_INCLUDE_PATH}\translations\portuguese.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "PORTUGUESEBR"    "${GOURMET_NSIS_INCLUDE_PATH}\translations\portuguese-br.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "ROMANIAN"        "${GOURMET_NSIS_INCLUDE_PATH}\translations\romanian.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "RUSSIAN"     "${GOURMET_NSIS_INCLUDE_PATH}\translations\russian.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "SERBIAN"     "${GOURMET_NSIS_INCLUDE_PATH}\translations\serbian-latin.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "SIMPCHINESE" "${GOURMET_NSIS_INCLUDE_PATH}\translations\simp-chinese.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "SLOVAK"      "${GOURMET_NSIS_INCLUDE_PATH}\translations\slovak.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "SLOVENIAN"       "${GOURMET_NSIS_INCLUDE_PATH}\translations\slovenian.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "SPANISH"     "${GOURMET_NSIS_INCLUDE_PATH}\translations\spanish.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "SWEDISH"     "${GOURMET_NSIS_INCLUDE_PATH}\translations\swedish.nsh"
  !insertmacro GOURMET_MACRO_INCLUDE_LANGFILE "TRADCHINESE" "${GOURMET_NSIS_INCLUDE_PATH}\translations\trad-chinese.nsh"

;--------------------------------
;Reserve Files
  ; Only need this if using bzip2 compression

  !insertmacro MUI_RESERVEFILE_INSTALLOPTIONS
  !insertmacro MUI_RESERVEFILE_LANGDLL
  ReserveFile "${NSISDIR}\Plugins\UserInfo.dll"


;;;;;;;;;;;;;;;;;;;;;;;;;;;;
;; Start Install Sections ;;
;;;;;;;;;;;;;;;;;;;;;;;;;;;;


;--------------------------------
;Gourmet Install Section

Section $(GOURMET_SECTION_TITLE) SecGourmet
  SectionIn 1 RO

  Call CheckUserInstallRights
  Pop $R0

  StrCmp $R0 "NONE" gourmet_none
  StrCmp $R0 "HKLM" gourmet_hklm gourmet_hkcu

  gourmet_hklm:
    ReadRegStr $R1 HKLM ${GTK_REG_KEY} "Path"
    WriteRegStr HKLM "${HKLM_APP_PATHS_KEY}" "" "$INSTDIR\Gourmet.exe"
    WriteRegStr HKLM "${HKLM_APP_PATHS_KEY}" "Path" "$R1\bin"
    WriteRegStr HKLM ${GOURMET_REG_KEY} "" "$INSTDIR"
    WriteRegStr HKLM ${GOURMET_REG_KEY} "Version" "${GOURMET_VERSION}"
    WriteRegStr HKLM "${GOURMET_UNINSTALL_KEY}" "DisplayName" $(GOURMET_UNINSTALL_DESC)
    WriteRegStr HKLM "${GOURMET_UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\data\recbox.ico"
    WriteRegStr HKLM "${GOURMET_UNINSTALL_KEY}" "DisplayVersion" "${GOURMET_VERSION}"
    WriteRegStr HKLM "${GOURMET_UNINSTALL_KEY}" "UninstallString" "$INSTDIR\${GOURMET_UNINST_EXE}"
    WriteRegDWORD HKLM "${GOURMET_UNINSTALL_KEY}" "NoModify" "1"
    WriteRegDWORD HKLM "${GOURMET_UNINSTALL_KEY}" "NoRepair" "1"
    WriteRegStr HKLM "${GOURMET_UNINSTALL_KEY}" "URLUpdateInfo" "${GOURMET_DOWNLOAD_SITE}"
    WriteRegStr HKLM "${GOURMET_UNINSTALL_KEY}" "URLInfoAbout" "${GOURMET_WEB_SITE}"
    ; Sets scope of the desktop and Start Menu entries for all users.
    SetShellVarContext "all"
    Goto gourmet_install_files

  gourmet_hkcu:
    ReadRegStr $R1 HKCU ${GTK_REG_KEY} "Path"
    StrCmp $R1 "" 0 gourmet_hkcu1
      ReadRegStr $R1 HKLM ${GTK_REG_KEY} "Path"
    gourmet_hkcu1:
    WriteRegStr HKCU ${GOURMET_REG_KEY} "" "$INSTDIR"
    WriteRegStr HKCU ${GOURMET_REG_KEY} "Version" "${GOURMET_VERSION}"
    WriteRegStr HKCU "${GOURMET_UNINSTALL_KEY}" "DisplayName" $(GOURMET_UNINSTALL_DESC)
    WriteRegStr HKCU "${GOURMET_UNINSTALL_KEY}" "DisplayIcon" "$INSTDIR\data\recbox.ico"
    WriteRegStr HKCU "${GOURMET_UNINSTALL_KEY}" "DisplayVersion" "${GOURMET_VERSION}"
    WriteRegStr HKCU "${GOURMET_UNINSTALL_KEY}" "UninstallString" "$INSTDIR\${GOURMET_UNINST_EXE}"
    WriteRegDWORD HKCU "${GOURMET_UNINSTALL_KEY}" "NoModify" "1"
    WriteRegDWORD HKCU "${GOURMET_UNINSTALL_KEY}" "NoRepair" "1"
    WriteRegStr HKCU "${GOURMET_UNINSTALL_KEY}" "URLUpdateInfo" "${GOURMET_DOWNLOAD_SITE}"
    WriteRegStr HKCU "${GOURMET_UNINSTALL_KEY}" "URLInfoAbout" "${GOURMET_WEB_SITE}"
    Goto gourmet_install_files

  gourmet_none:
    ReadRegStr $R1 HKLM ${GTK_REG_KEY} "Path"

  gourmet_install_files:
    SetOutPath "$INSTDIR"
    SetOverwrite try

    ; fancy stuff here - recursively get everything from this dir with /r flag,
    ; instead of listing every file like we used to. thank you, gaim.
    File /r "${PYTHON_PATH}\dist\*.*"
    ;File "${PYTHON_PATH}\msvcr71.dll" ;dont need this, since already included by py2exe

    SetOutPath "$INSTDIR\data\"
    File /r "${PYTHON_PATH}\gourmet\data\*.*"

    SetOutPath "$INSTDIR\i18n\"
    File /r "${PYTHON_PATH}\gourmet\i18n\*.*"

    ; We include the plugin scripts separately into the install directory, because the gourmet executable
    ; freeze process is not able to incorporate them into the exe due to some funky way they are being
    ; imported.
    SetOutPath "$INSTDIR\data\plugins\"
    File "${PYTHON_PATH}\Lib\site-packages\gourmet\plugins\*.gourmet-plugin"
    File /r "${PYTHON_PATH}\Lib\site-packages\gourmet\plugins\*"
    ;File /r "${PYTHON_PATH}\Lib\site-packages\gourmet\plugins\*.pyc"


    SetOutPath "$INSTDIR\documentation\"
    SetOverwrite ifnewer
    File "..\TODO"
    File "..\README"
    File "..\LICENSE"
    File "..\CHANGES"

    SetOutPath "$INSTDIR"

    ; If we don't have install rights.. we're done
    StrCmp $R0 "NONE" done
    SetOverwrite off

    ; Write out installer language
    WriteRegStr HKCU "${GOURMET_REG_KEY}" "${GOURMET_REG_LANG}" "$LANGUAGE"

    ; write out uninstaller
    SetOverwrite on
    WriteUninstaller "$INSTDIR\${GOURMET_UNINST_EXE}"
    SetOverwrite off

  done:
SectionEnd ; end of default Gourmet section

;--------------------------------
;Shortcuts

SubSection /e $(GOURMET_SHORTCUTS_SECTION_TITLE) SecShortcuts
  Section /o $(GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE) SecDesktopShortcut
    SetOverwrite on
    CreateShortCut "$DESKTOP\Gourmet Recipe Manager.lnk" "$INSTDIR\Gourmet.exe" " " "$INSTDIR\data\recbox.ico" 0
    SetOverwrite off
  SectionEnd
  Section $(GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE) SecStartMenuShortcut
    SetOverwrite on
    CreateDirectory "$SMPROGRAMS\$ICONS_GROUP"
    CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Gourmet Recipe Manager.lnk" "$INSTDIR\Gourmet.exe" " " "$INSTDIR\data\recbox.ico" 0
    CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Gourmet Recipe Manager Debug Mode.lnk" "$INSTDIR\Gourmet_debug.exe" "-v -v -v -v -v -v" "$INSTDIR\data\recbox.ico" 0
    CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Uninstall Gourmet.lnk" "$INSTDIR\${GOURMET_UNINST_EXE}"
    WriteIniStr "$INSTDIR\${GOURMET_NAME}.url" "InternetShortcut" "URL" "${GOURMET_WEB_SITE}"
    CreateShortCut "$SMPROGRAMS\$ICONS_GROUP\Gourmet Website.lnk" "$INSTDIR\${GOURMET_NAME}.url"

    SetOverwrite off
  SectionEnd
SubSectionEnd

;--------------------------------
;GTK+ Themes
;TODO: not sure if we need/can use this, but lets try.
; well, gtk_theme_dir is kinda screwing us here so lets just comment this out for now.

;SubSection /e $(GTK_THEMES_SECTION_TITLE) SecGtkThemes
;  Section /o $(GTK_NOTHEME_SECTION_TITLE) SecGtkNone
;    Call CanWeInstallATheme
;    Pop $R0
;    StrCmp $R0 "" done
;    SetOverwrite on
;    Rename $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc.old
;    CopyFiles $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc.plain $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc
;    SetOverwrite off
;    done:
;  SectionEnd

;  Section $(GTK_WIMP_SECTION_TITLE) SecGtkWimp
;    Call CanWeInstallATheme
;    Pop $R0
;    StrCmp $R0 "" done
;    SetOverwrite on
;    Rename $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc.old
;    SetOutPath $R0\${GTK_DEFAULT_THEME_ENGINE_DIR}
;    File ${GTK_THEME_DIR}\engines\libwimp.dll
;    SetOutPath $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}
;    File ${GTK_THEME_DIR}\themes\gtkrc.gtkwimp
;    File /oname=gtkrc ${GTK_THEME_DIR}\themes\gtkrc.gtkwimp
;    SetOverwrite off
;    done:
;  SectionEnd

;  Section /o $(GTK_BLUECURVE_SECTION_TITLE) SecGtkBluecurve
;    Call CanWeInstallATheme
;    Pop $R0
;    StrCmp $R0 "" done
;    SetOverwrite on
;    Rename $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc.old
;    SetOutPath $R0\${GTK_DEFAULT_THEME_ENGINE_DIR}
;    File ${GTK_THEME_DIR}\engines\libbluecurve.dll
;    SetOutPath $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}
;    File ${GTK_THEME_DIR}\themes\gtkrc.bluecurve
;    File /oname=gtkrc ${GTK_THEME_DIR}\themes\gtkrc.bluecurve
;    SetOverwrite off
;    done:
;  SectionEnd

;  Section /o $(GTK_LIGHTHOUSEBLUE_SECTION_TITLE) SecGtkLighthouseblue
;    Call CanWeInstallATheme
;    Pop $R0
;    StrCmp $R0 "" done
;    SetOverwrite on
;    Rename $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}\gtkrc.old
;    SetOutPath $R0\${GTK_DEFAULT_THEME_ENGINE_DIR}
;    File ${GTK_THEME_DIR}\engines\liblighthouseblue.dll
;    SetOutPath $R0\${GTK_DEFAULT_THEME_GTKRC_DIR}
;    File ${GTK_THEME_DIR}\themes\gtkrc.lighthouseblue
;    File /oname=gtkrc ${GTK_THEME_DIR}\themes\gtkrc.lighthouseblue
;    SetOverwrite off
;    done:
;  SectionEnd
;SubSectionEnd


;--------------------------------
;GTK+ Runtime Install Section

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

  ;concatenate the string from language files with installed version
  StrCpy $GTK_UPGRADE_MESSAGE_CONTENT $(GTK_UPGRADE_PROMPT)
  StrCpy $GTK_UPGRADE_MESSAGE_CONTENT "$GTK_UPGRADE_MESSAGE_CONTENT $\rCurrently installed GTK+ version is $GTK_VERSION_INSTALLED."

  ; Make a more helpful GTK install failed message
  StrCpy $GTK_INSTALL_ERROR_HELPFUL $(GTK_INSTALL_ERROR)
  StrCpy $GTK_INSTALL_ERROR_HELPFUL "$GTK_INSTALL_ERROR_HELPFUL $\r \
                                    Please manually run $TEMP\gtk-runtime.exe after installation finishes to make sure GTK+ is installed."

  StrCmp $R0 "0" have_gtk
  StrCmp $R0 "1" upgrade_gtk
  StrCmp $R0 "2" no_gtk no_gtk

  no_gtk:
    StrCmp $R1 "NONE" gtk_no_install_rights
    ClearErrors
    MessageBox MB_YESNO "The installer has detected that you have no GTK+ on your machine. $\r \
                        It is required for Gourmet to run. Do you want to install GTK+ now (recommended)?" /SD IDYES IDNO done

    MessageBox MB_OK "We are now going to install GTK+ ${GTK_VERSION}. $\r Follow along with the installer, but \
                     please make sure NOT to select 'Reboot Now' at the end of GTK+ installation, if prompted. $\r \
                     Since this is your first time installing GTK+ on this computer, you might want to reboot \
                     after the entire installation process is finished, though." /SD IDOK

    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE /D=$GTK_FOLDER' ;removed silent flag

    SetRebootFlag true

    Goto gtk_install_cont

  upgrade_gtk:
    StrCpy $GTK_FOLDER $R6
    MessageBox MB_YESNO "$GTK_UPGRADE_MESSAGE_CONTENT" /SD IDYES IDNO done

    MessageBox MB_OK "First, we will uninstall the old version of GTK+. \
                     Then, we are going to install GTK+ ${GTK_VERSION}. $\r Follow along with the installer, but \
                     please make sure NOT to select 'Reboot Now' at the end of GTK+ installation, if prompted. $\r \
                     Since you are upgrading GTK+, you do not have to reboot after installation finishes." /SD IDOK

    ; We need to uninstall old version of GTK first.
    Call UninstallGtk

    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE /D=$GTK_FOLDER'

    Goto gtk_install_cont

  gtk_install_cont:
    IfErrors gtk_install_error
      StrCpy $R5 "1"  ; marker that says we installed...
      Goto done

    gtk_install_error:
      MessageBox MB_OK "$GTK_INSTALL_ERROR_HELPFUL" /SD IDOK
      StrCpy $R5 "2"   ; marker saying that there were errors in gtk install
      Goto done        ; instead of quitting install, we want to finish it properly, but indicate that gtk has to be installed manually.

  have_gtk:      ; Even if we have a sufficient version of GTK+, we give user choice to re-install.
    StrCpy $GTK_FOLDER $R6
    StrCmp $R1 "NONE" done ; If we have no rights.. can't re-install..

    ClearErrors
    MessageBox MB_YESNO "$GTK_UPGRADE_MESSAGE_CONTENT" /SD IDYES IDNO done
    MessageBox MB_OK "First, we will uninstall the old version of GTK+. \
                     Then, we are going to install GTK+ ${GTK_VERSION}. $\r Follow along with the installer, but \
                     please make sure NOT to select 'Reboot Now' at the end of GTK+ installation, if prompted. $\r \
                     Since you are upgrading GTK+, you do not have to reboot after installation finishes." /SD IDOK

    ; We need to uninstall old version of GTK first.
    Call UninstallGtk

    ClearErrors
    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE /D=$GTK_FOLDER' ;do not want /S flag, because silent mode places icons in root of start menu.
    Goto gtk_install_cont

  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; end got_install rights

  gtk_no_install_rights:
    ; Install GTK+ to Gourmet install dir
    StrCpy $GTK_FOLDER $INSTDIR
    ClearErrors

    ;MessageBox MB_OK "Please make sure NOT to select 'Reboot Now' at the end of GTK+ installation."

    MessageBox MB_OK "We are now going to install GTK+ ${GTK_VERSION}. $\r Follow along with the installer, but \
                     please make sure NOT to select 'Reboot Now' at the end of GTK+ installation, if prompted. $\r \
                     Since this is your first time installing GTK+ on this computer, you might want to reboot \
                     after the entire installation process is finished, though." /SD IDOK

    ExecWait '"$TEMP\gtk-runtime.exe" /L=$LANGUAGE /D=$GTK_FOLDER'  ;do not want /S flag, because silent mode places icons in root of start menu.
    IfErrors gtk_install_error

    SetOverwrite on
    ClearErrors
    CopyFiles /FILESONLY "$GTK_FOLDER\bin\*.dll" $GTK_FOLDER
    SetOverwrite off

    IfErrors gtk_install_error

    Delete "$GTK_FOLDER\bin\*.dll"

    SetRebootFlag true

    Goto done
  ;;;;;;;;;;;;;;;;;;;;;;;;;;;;
  ; end gtk_no_install_rights

  done:
    StrCmp $R5 "2" gtk_errors gtk_no_errors
    gtk_no_errors:
      Delete "$TEMP\gtk-runtime.exe"
    gtk_errors:
      ; leave the runtime in temp so the user can run it manually.
SectionEnd ; end of GTK+ section
!endif


;--------------------------------
;Uninstaller Section

Section Uninstall
  Call un.CheckUserInstallRights
  Pop $R0
  StrCmp $R0 "NONE" no_rights
  StrCmp $R0 "HKCU" try_hkcu try_hklm

  try_hkcu:
    ReadRegStr $R0 HKCU ${GOURMET_REG_KEY} ""
    StrCmp $R0 $INSTDIR 0 cant_uninstall
      ; HKCU install path matches our INSTDIR.. so uninstall
      DeleteRegKey HKCU ${GOURMET_REG_KEY}
      DeleteRegKey HKCU "${GOURMET_UNINSTALL_KEY}"
      Goto cont_uninstall

  try_hklm:
    ReadRegStr $R0 HKLM ${GOURMET_REG_KEY} ""
    StrCmp $R0 $INSTDIR 0 try_hkcu
      ; HKLM install path matches our INSTDIR.. so uninstall
      DeleteRegKey HKLM ${GOURMET_REG_KEY}
      DeleteRegKey HKLM "${GOURMET_UNINSTALL_KEY}"
      DeleteRegKey HKLM "${HKLM_APP_PATHS_KEY}"
      ; Sets start menu and desktop scope to all users..
      SetShellVarContext "all"

  cont_uninstall:

    !insertmacro MUI_STARTMENU_GETFOLDER "Application" $ICONS_GROUP ;get the name of our start menu folder

    ; Shortcuts
    RMDir /r "$SMPROGRAMS\$ICONS_GROUP"
    Delete "$DESKTOP\Gourmet Recipe Manager.lnk"

    ; Main Install Directories
    RMDir /r "$INSTDIR\documentation\"
    RMDir /r "$INSTDIR\data\"
    RMDir /r "$INSTDIR\i18n\"
    RMDir /r "$INSTDIR"

    ; Registry
    DeleteRegKey ${GOURMET_UNINST_ROOT_KEY} "${GOURMET_UNINSTALL_KEY}"
    DeleteRegKey HKLM "${GOURMET_DIR_REGKEY}"
    SetAutoClose false ; this lets us look at the uninstall log

    Goto done

  cant_uninstall:
    MessageBox MB_OK $(un.GOURMET_UNINSTALL_ERROR_1) /SD IDOK
    Quit

  no_rights:
    MessageBox MB_OK $(un.GOURMET_UNINSTALL_ERROR_2) /SD IDOK
    Quit

  done:
SectionEnd ; end of uninstall section

;--------------------------------
;Descriptions
!insertmacro MUI_FUNCTION_DESCRIPTION_BEGIN
  !insertmacro MUI_DESCRIPTION_TEXT ${SecGourmet} \
    $(GOURMET_SECTION_DESCRIPTION)
!ifdef WITH_GTK
  !insertmacro MUI_DESCRIPTION_TEXT ${SecGtk} \
    $(GTK_SECTION_DESCRIPTION)
!endif
  !insertmacro MUI_DESCRIPTION_TEXT ${SecGtkThemes} \
        $(GTK_THEMES_SECTION_DESCRIPTION)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecGtkNone} \
        $(GTK_NO_THEME_DESC)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecGtkWimp} \
    $(GTK_WIMP_THEME_DESC)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecGtkBluecurve} \
        $(GTK_BLUECURVE_THEME_DESC)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecGtkLighthouseblue} \
        $(GTK_LIGHTHOUSEBLUE_THEME_DESC)


  !insertmacro MUI_DESCRIPTION_TEXT ${SecShortcuts} \
        $(GOURMET_SHORTCUTS_SECTION_DESCRIPTION)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecDesktopShortcut} \
        $(GOURMET_DESKTOP_SHORTCUT_DESC)
  !insertmacro MUI_DESCRIPTION_TEXT ${SecStartMenuShortcut} \
        $(GOURMET_STARTMENU_SHORTCUT_DESC)
!insertmacro MUI_FUNCTION_DESCRIPTION_END

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

    ; If no rights check if gtk was installed to gourmet dir..
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
    StrCpy $1 "$0\GourMetFooB"
    ; Check if we can create dir on this drive..
    ClearErrors
    CreateDirectory $1
    IfErrors DirBad DirGood

  dir_exists:
    ClearErrors
    FileOpen $1 "$0\gourmetfoo.bar" w
    IfErrors PathBad PathGood

    DirGood:
      RMDir $1
      Goto PathGood1

    DirBad:
      RMDir $1
      Goto PathBad1

    PathBad:
      FileClose $1
      Delete "$0\gourmetfoo.bar"
      PathBad1:
      StrCpy $0 "0"
      Push $0
      Return

    PathGood:
      FileClose $1
      Delete "$0\gourmetfoo.bar"
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
  ; Store installed version in var for msgbox purposes
  StrCpy $GTK_VERSION_INSTALLED $6
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
  ;DetailPrint "CheckUserInstallRights returned $3"
  ;StrCmp $3 "HKLM" check_hklm
  ;StrCmp $3 "HKCU" check_hkcu check_hklm
    check_hkcu:
      ReadRegStr $0 HKCU ${GTK_REG_KEY} "Version"
      StrCpy $5 "HKCU"
      StrCmp $0 "" check_hklm have_gtk

    check_hklm:
      ReadRegStr $0 HKLM ${GTK_REG_KEY} "Version"
      StrCpy $5 "HKLM"
      StrCmp $0 "" no_gtk have_gtk


  have_gtk:
    ;DetailPrint "We have entered have_gtk"
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
  MessageBox MB_OK|MB_ICONEXCLAMATION $(GOURMET_IS_RUNNING) IDOK
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

Function .onInit
  System::Call 'kernel32::CreateMutexA(i 0, i 0, t "gourmet_installer_running") i .r1 ?e'
  Pop $R0
  StrCmp $R0 0 +3
    MessageBox MB_OK|MB_ICONEXCLAMATION $(INSTALLER_IS_RUNNING)
    Abort
  ;Call RunCheck
  StrCpy $name "${GOURMET_NAME} ${GOURMET_VERSION}"
  StrCpy $GTK_THEME_SEL ${SecGtkWimp}
  StrCpy $ISSILENT "/NOUI"

  ; GTK installer has two silent states.. one with Message boxes, one without
  ; If gourmet installer was run silently, we want to supress gtk installer msg boxes.
  IfSilent 0 set_gtk_normal
      StrCpy $ISSILENT "/S"
  set_gtk_normal:

  Call ParseParameters

  ; Select Language
  IntCmp $LANG_IS_SET 1 skip_lang
    ; Display Language selection dialog
    !insertmacro MUI_LANGDLL_DISPLAY
    skip_lang:

  ; If install path was set on the command, use it.
  StrCmp $INSTDIR "" 0 instdir_done

  ;  If gourmet is currently intalled, we should default to where it is currently installed
  ClearErrors
  ReadRegStr $INSTDIR HKCU "${GOURMET_REG_KEY}" ""
  IfErrors +2
  StrCmp $INSTDIR "" 0 instdir_done
  ReadRegStr $INSTDIR HKLM "${GOURMET_REG_KEY}" ""
  IfErrors +2
  StrCmp $INSTDIR "" 0 instdir_done

  Call CheckUserInstallRights
  Pop $0

  StrCmp $0 "HKLM" 0 user_dir
    StrCpy $INSTDIR "$PROGRAMFILES\Gourmet"
    Goto instdir_done
  user_dir:
    StrCpy $2 "$SMPROGRAMS"
    Push $2
    Call GetParent
    Call GetParent
    Pop $2
    StrCpy $INSTDIR "$2\Gourmet"

  instdir_done:

FunctionEnd

Function un.onInit
  ;Call un.RunCheck
  StrCpy $name "Gourmet ${GOURMET_VERSION}"

  ; Get stored language prefrence
  ReadRegStr $LANGUAGE HKCU ${GOURMET_REG_KEY} "${GOURMET_REG_LANG}"

FunctionEnd

Function .onSelChange
  Push $0
  Push $2

  StrCpy $2 ${SF_SELECTED}
  SectionGetFlags ${SecGtkNone} $0
  IntOp $2 $2 & $0
  SectionGetFlags ${SecGtkWimp} $0
  IntOp $2 $2 & $0
  SectionGetFlags ${SecGtkBluecurve} $0
  IntOp $2 $2 & $0
  SectionGetFlags ${SecGtkLighthouseblue} $0
  IntOp $2 $2 & $0
  StrCmp $2 0 skip
    SectionSetFlags ${SecGtkNone} 0
    SectionSetFlags ${SecGtkWimp} 0
    SectionSetFlags ${SecGtkBluecurve} 0
    SectionSetFlags ${SecGtkLighthouseblue} 0
  skip:

  !insertmacro UnselectSection $GTK_THEME_SEL

  ; Remember old selection
  StrCpy $2 $GTK_THEME_SEL

  ; Now go through and see who is checked..
  SectionGetFlags ${SecGtkNone} $0
  IntOp $0 $0 & ${SF_SELECTED}
  IntCmp $0 ${SF_SELECTED} 0 +2 +2
    StrCpy $GTK_THEME_SEL ${SecGtkNone}
  SectionGetFlags ${SecGtkWimp} $0
  IntOp $0 $0 & ${SF_SELECTED}
  IntCmp $0 ${SF_SELECTED} 0 +2 +2
    StrCpy $GTK_THEME_SEL ${SecGtkWimp}
  SectionGetFlags ${SecGtkBluecurve} $0
  IntOp $0 $0 & ${SF_SELECTED}
  IntCmp $0 ${SF_SELECTED} 0 +2 +2
    StrCpy $GTK_THEME_SEL ${SecGtkBluecurve}
  SectionGetFlags ${SecGtkLighthouseblue} $0
  IntOp $0 $0 & ${SF_SELECTED}
  IntCmp $0 ${SF_SELECTED} 0 +2 +2
    StrCpy $GTK_THEME_SEL ${SecGtkLighthouseblue}

  StrCmp $2 $GTK_THEME_SEL 0 +2 ; selection hasn't changed
    !insertmacro SelectSection $GTK_THEME_SEL

  Pop $2
  Pop $0
FunctionEnd

; Page enter and exit functions..

Function preWelcomePage
  ; If this installer dosn't have GTK, check whether we need it.
  ; We do this here an not in .onInit because language change in
  ; .onInit doesn't take effect until it is finished.
  !ifndef WITH_GTK
    Call DoWeNeedGtk
    Pop $0
    Pop $GTK_FOLDER

    StrCmp $0 "0" have_gtk need_gtk
    need_gtk:
      IfSilent skip_mb
      MessageBox MB_OK $(GTK_INSTALLER_NEEDED) IDOK
      skip_mb:
      Quit
    have_gtk:
  !endif
FunctionEnd

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
  StrCpy $name "Gourmet ${GOURMET_VERSION}"
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
Function ParseParameters
  IntOp $LANG_IS_SET 0 + 0
  Call GetParameters
  Pop $R0
  Push $R0
  Push "L="
  Call StrStr
  Pop $R1
  StrCmp $R1 "" next
  StrCpy $R1 $R1 4 2 ; Strip first 2 chars of string
  StrCpy $LANGUAGE $R1
  IntOp $LANG_IS_SET 0 + 1
  next:
FunctionEnd

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

Function UninstallGtk
; First, we find the uninstaller, by looking at the gtk registry key to find the gtk directory
; Then we execute it, if found.

  check_hkcu:
    ReadRegStr $0 HKCU ${GTK_REG_KEY} "Path"
    ;StrCpy $5 "HKCU"
    StrCmp $0 "" check_hklm found_gtk_path

  check_hklm:
    ReadRegStr $0 HKLM ${GTK_REG_KEY} "Path"
    ;StrCpy $5 "HKLM"
    StrCmp $0 "" no_gtk found_gtk_path

    found_gtk_path:
    ; We do this copyfiles thing cuz if we dont, it will do it for us, and execwait wont wait properly.
    ; See also http://nsis.sourceforge.net/Docs/AppendixD.html (section D.1) for detailed explanation.
    CopyFiles $0\uninst.exe $TEMP
    ExecWait '"$TEMP\uninst.exe" _?=$0'
    Delete "$TEMP\uninst.exe"

    no_gtk:
    ;do nothing

FunctionEnd