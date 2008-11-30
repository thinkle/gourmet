;;

;;  hebrew.nsh

;;

;;  Hebrew language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1255

;;

;;  Author: Eugene Shcherbina <eugene@websterworlds.com>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			".לא נמצאת או צריכה שידרוג GTK+ סביבת$\rבבקשה התקן v${GTK_VERSION} .GTK+ או גבוהה יותר של סביבת"



; License Page

!define GOURMET_LICENSE_BUTTON			"הבא >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) .הרישיון נמצא כאן בשביל מידע בלבד .GPL משוחרר תחת רישיון $_CLICK"



; Components Page

!define GOURMET_SECTION_TITLE			"(חובה) .GOURMET RECIPE MANAGER"

!define GTK_SECTION_TITLE			"(חובה) .GTK+ סביבת"

!define GTK_THEMES_SECTION_TITLE		"GTK+ מראות של"

!define GTK_NOTHEME_SECTION_TITLE		"ללא מראה"

!define GTK_WIMP_SECTION_TITLE		"Wimp מראה"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve מראה"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue מראה"

!define GOURMET_SECTION_DESCRIPTION		".בסיססים DLL-ו GOURMET קבצי"

!define GTK_SECTION_DESCRIPTION		".מולטי-פלטפורמיים GUI כלי"

!define GTK_THEMES_SECTION_DESCRIPTION	" .GTK+ יכולים לשנות את המראה של תוכנות GTK+ מראות"

!define GTK_NO_THEME_DESC			".GTK+ לא להתקין מראה של"

!define GTK_WIMP_THEME_DESC			".זה מראה שמשתלב למראה של חלונות GTK-Wimp (Windows impersonator)"

!define GTK_BLUECURVE_THEME_DESC		".Bluecurve המראה של"

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	".Lighthouseblueהמראה של"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"A?נמצאה. לשדרג GTK+ סביבה ישנה של$\rNote: .יכול לא לעבוד אם לא GOURMET"



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		".GOURMETבקרו באתר של"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"GOURMET (מחיקה בלבד)"

!define GOURMET_PROMPT_WIPEOUT			"?הישנה הולכת להימחק. להמשיך GOURMET תיקיית$\r$\rNote: הערה: תוספות לא רגילות ימחקו.$\r.הגדרות המשתמש לא ישתנו"

!define GOURMET_PROMPT_DIR_EXISTS		"תיקיית ההתקנה כבר קיימת. כל משבתוכה $\r?ימחק. להמשיך"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			".GTK+ שגיאה בהתקנת סביבת"

!define GTK_BAD_INSTALL_PATH			".המסלול שציינת לא יכול להיווצר"



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		".GTK+ אין לך זכות להתקין מראה של"



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1		".GTK+ ההתקנה לא מצאה את הרישומים של$\r.יכול להיות שמשמתמש אחר התקין את התוכנה הזאת"

!define un.GOURMET_UNINSTALL_ERROR_2		".אין לך זכות למחוק תוכנה זאת"

