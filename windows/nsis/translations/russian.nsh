;;

;;  russian.nsh

;;

;;  Russian language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1251

;;

;;  Author: Tasselhof <anr@nm.ru>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"Окружение для запуска GTK+ недоступно или нуждается в обновлении.$\rПожалуйста установите v${GTK_VERSION} или более старшую версию GTK+."



; License Page

!define GAIM_LICENSE_BUTTON			"Следующее >"

!define GAIM_LICENSE_BOTTOM_TEXT		"$(^Name) выпущено под лицензией GPL. Лицензия приведена здесь для ознакомительных целей. $_CLICK"



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (необходимо)."

!define GTK_SECTION_TITLE			"GTK+ окружение для запуска (необходимо)."

!define GTK_THEMES_SECTION_TITLE		"Темы для GTK+."

!define GTK_NOTHEME_SECTION_TITLE		"Без темы."

!define GTK_WIMP_SECTION_TITLE		"Тема 'Wimp Theme'"

!define GTK_BLUECURVE_SECTION_TITLE		"Тема 'Bluecurve'."

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Тема 'Light House Blue'."

!define GAIM_SECTION_DESCRIPTION		"Основная часть Gourmet и библиотеки."

!define GTK_SECTION_DESCRIPTION		"Мультиплатформенный графический инструментарий, используемый Gourmet."

!define GTK_THEMES_SECTION_DESCRIPTION	"Темы для GTK+ изменяют его внешний вид и восприятие пользователем."

!define GTK_NO_THEME_DESC			"Не устанавливать темы для GTK+."

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows-подстройка) это тема для GTK, которая очень гармонично подстроится под визуальное окружение из среды рабочего стола Windows."

!define GTK_BLUECURVE_THEME_DESC		"Тема 'The Bluecurve'."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Тема 'The Lighthouseblue'."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Найдена старая версия GTK+. Вы не хотели бы обновить её ?$\rПримечание: Gourmet может не работать если Вы не сделаете этого."



; Installer Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"Посетите веб-страницу Gourmet для пользователей Windows."



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (только удаление)"

!define GAIM_PROMPT_WIPEOUT			"Ваша старая директория Gourmet будет фактически удалена. Вы желаете продолжить ?$\r$\rПримечание: Все нестандартные плагины которые Вы установили будут удалены..$\rПользовательские настройки Gourmet не пострадают."

!define GAIM_PROMPT_DIR_EXISTS		"Директория, которую Вы указали для установки уже существует. Всё содержимое$\rбудет удалено. Вы желаете продолжить?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Ошибка при установке окружения GTK+."

!define GTK_BAD_INSTALL_PATH			"Путь который Вы ввели недоступен или не существует."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"У Вас нет прав на установление темы для GTK+."



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1		"Программа удаления не может найти данные Gourmet в регистре..$\rВероятно это приложение установил другой пользователь."

!define un.GAIM_UNINSTALL_ERROR_2		"У Вас нет прав на удаление этого приложения."

