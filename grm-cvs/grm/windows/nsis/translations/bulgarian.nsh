;;

;;  bulgarian.nsh

;;

;;  Bulgarian language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1251

;;

;;  Author: Hristo Todorov <igel@bofh.bg>

;;





; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ runtime липсва или трябва да бъде обновена.$\rМоля инсталирайте версия v${GTK_VERSION} или по-нова"



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (изисква се)"

!define GTK_SECTION_TITLE			"GTK+ Runtime Среда (required)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ Теми"

!define GTK_NOTHEME_SECTION_TITLE		"Без Тема"

!define GTK_WIMP_SECTION_TITLE		"Wimp Тема"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve Тема"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue Тема"

!define GAIM_SECTION_DESCRIPTION		"Файлове на ядрото на Gourmet и библиотеки"

!define GTK_SECTION_DESCRIPTION		"Мултиплатфорен кит за графичен изглед, използван от Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ темите могат да променят Изгледа на GTK+ приложения."

!define GTK_NO_THEME_DESC			"Не инсталирайте GTK+ тема"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) е GTK тема която се смесва добре със Windows."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve темата."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue темата."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Стара версия GTK+ runtime е открита. Искате ли да обновите?$\rNote: Gourmet може да не сработи ако не го направите."



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (само премахване)"

!define GAIM_PROMPT_WIPEOUT			"Вашата стара Gourmet директория ще бъде изтрита. Искате ли да продължите?$\r$\rЗабележка: Всички нестандартни добавки които сте инсталирали ще бъдат изтрити.$\rНастройките на Gourmet няма да бъдат повлияни."

!define GAIM_PROMPT_DIR_EXISTS		"Директорията която избрахте съществува. Всичко което е в нея$\rще бъде изтрито. Желаете ли да продължите?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Грешка при инсталиране на GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Въведеният път не може да бъде достъпен или създаден."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Нямате права за да инсталирате GTK+ тема."



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1         "Деисталатоа не може да намери записи в регистъра за Gourmet.$\rВероятно е бил инсталиран от друг потребител."

!define un.GAIM_UNINSTALL_ERROR_2         "Нямате права да деинсталирате тази програма."

