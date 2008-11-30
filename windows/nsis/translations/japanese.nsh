;;

;;  japanese.nsh

;;

;;  Japanese language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 932

;;

;;  Author: "Takeshi Kurosawa" <t-kuro@abox23.so-net.ne.jp>

;;  Version 2

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ランタイム環境が無いかもしくはアップグレードする必要があります。$\rv${GTK_VERSION}もしくはそれ以上のGTK+ランタイムをインストールしてください。"



; License Page

!define GAIM_LICENSE_BUTTON			"次へ >"

!define GAIM_LICENSE_BOTTOM_TEXT		"$(^Name)はGPLライセンスの元でリリースされています。ライセンスはここに参考のためだけに提供されています。 $_CLICK"



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (必須)"

!define GTK_SECTION_TITLE			"GTK+ Runtime Environment (必須)"

!define GTK_THEMES_SECTION_TITLE		"GTK+のテーマ"

!define GTK_NOTHEME_SECTION_TITLE		"テーマなし"

!define GTK_WIMP_SECTION_TITLE		"Wimpテーマ"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurveテーマ"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blueテーマ"

!define GAIM_SECTION_DESCRIPTION		"Gourmetの核となるファイルとdll"

!define GTK_SECTION_DESCRIPTION		"Gourmetの使っているマルチプラットフォームGUIツールキット"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+のテーマは、GTK+のアプリケーションのルック＆フィールを変えられます。"

!define GTK_NO_THEME_DESC			"GTK+のテーマをインストールしない"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator)はWindowsのデスクトップ環境とよく調和したテーマです。"

!define GTK_BLUECURVE_THEME_DESC		"Bluecurveテーマ。"

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblueテーマ。"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"古いバージョンのGTK+ランタイムが見つかりました。アップグレードしますか?$\r注意: Gourmetはアップグレードしない限り動かないでしょう。"



; Installer Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"Windows GourmetのWebページを訪れてください。"



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (削除のみ)"

!define GAIM_PROMPT_WIPEOUT			"古いGourmetのフォルダの削除に関して。続行しますか?$\r$\r注意: あなたのインストールしたすべての非標準なプラグインは削除されます。$\rGourmetの設定は影響を受けません。"

!define GAIM_PROMPT_DIR_EXISTS		"あなたの指定したインストール先のフォルダはすでに存在しています。内容はすべて$\r削除されます。続行しますか?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"GTK+ランタイムのインストールでエラーが発生しました。"

!define GTK_BAD_INSTALL_PATH			"あなたの入力したパスにアクセスまたは作成できません。"



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"あなたはGTK+のテーマをインストールする権限を持っていません。"



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1		"アンインストーラはGourmetのレジストリエントリを発見できませんでした。$\rおそらく別のユーザにインストールされたでしょう。"

!define un.GAIM_UNINSTALL_ERROR_2		"あなたはこのアプリケーションをアンインストールする権限を持っていません。"

