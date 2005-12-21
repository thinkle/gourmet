;;

;;  simp-chinese.nsh

;;

;;  Simplified Chinese language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 936

;;

;;  Author: Funda Wang" <fundawang@linux.net.cn>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"可能缺少 GTK+ 运行时刻环境，或者需要更新该环境。$\r请安装 v${GTK_VERSION} 或更高版本的 GTK+ 运行时刻环境"



; License Page

!define GAIM_LICENSE_BUTTON			"下一步 >"

!define GAIM_LICENSE_BOTTOM_TEXT		"$(^Name) 以 GPL 许可发布。在此提供此许可仅为参考。$_CLICK"



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (必需)"

!define GTK_SECTION_TITLE			"GTK+ 运行时刻环境(必需)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ 主题"

!define GTK_NOTHEME_SECTION_TITLE		"无主题"

!define GTK_WIMP_SECTION_TITLE		"Wimp 主题"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve 主题"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue 主题"

!define GAIM_SECTION_DESCRIPTION		"Gourmet 核心文件和 DLLs"

!define GTK_SECTION_DESCRIPTION		"Gourmet 所用的多平台 GUI 工具包"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ 主题可以更改 GTK+ 程序的观感。"

!define GTK_NO_THEME_DESC			"不安装 GTK+ 主题"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator)是 is a GTK theme that blends well into the Windows desktop environment."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve 主题。"

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue 主题。"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"发现了旧版本的 GTK+ 运行时刻。您想要升级吗?$\r注意: 除非您进行升级，否则 Gourmet 可能无法工作。"



; Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"浏览 Windows Gourmet 网页"



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (只能删除)"

!define GAIM_PROMPT_WIPEOUT			"即将删除您的旧 Gourmet 目录。您想要继续吗?$\r$\r注意: 您所安装的任何非标准的插件都将被删除。$\r但是不会影响 Gourmet 用户设置。"

!define GAIM_PROMPT_DIR_EXISTS		"您指定的安装目录已经存在。$\r所有内容都将被删除。您想要继续吗?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"安装 GTK+ 运行时刻失败。"

!define GTK_BAD_INSTALL_PATH			"无法访问或创建您输入的路径。"



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"您没有权限安装 GTK+ 主题。"



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1         "卸载程序找不到 Gourmet 的注册表项目。$\r可能是另外的用户安装了此程序。"

!define un.GAIM_UNINSTALL_ERROR_2         "您没有权限卸载此程序。"

