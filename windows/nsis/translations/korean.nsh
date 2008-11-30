;;

;;  korean.nsh

;;

;;  Korean language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 949

;;

;;  Author: Kyung-uk Son <vvs740@chol.com>

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"GTK+ 런타임 환경에 문제가 있거나 업그레이드가 필요합니다.$\rGTK+ 런타임 환경을 v${GTK_VERSION}이나 그 이상 버전으로 설치해주세요."



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (필수)"

!define GTK_SECTION_TITLE			"GTK+ 런타임 환경 (필수)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ 테마"

!define GTK_NOTHEME_SECTION_TITLE		"테마 없음"

!define GTK_WIMP_SECTION_TITLE		"윔프 테마"

!define GTK_BLUECURVE_SECTION_TITLE		"블루커브 테마"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue 테마"

!define GOURMET_SECTION_DESCRIPTION		"가임의 코어 파일과 dll"

!define GTK_SECTION_DESCRIPTION		"가임이 사용하는 멀티 플랫폼 GUI 툴킷"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ 테마는 GTK+ 프로그램의 룩앤필을 바꿀 수 있습니다."

!define GTK_NO_THEME_DESC			"GTK+ 테마를 설치하지 않습니다."

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator)는 윈도우 데스크탑 환경에 잘 조화되는 GTK 테마입니다."

!define GTK_BLUECURVE_THEME_DESC		"블루커브 테마."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"The Lighthouseblue theme."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"옛날 버전 GTK+ 런타임을 찾았습니다. 업그레이드할까요?$\rNote: 업그레이드하지 않으면 가임이 동작하지 않을 수도 있습니다."



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (remove only)"

!define GOURMET_PROMPT_WIPEOUT			"가임 디렉토리가 지워질 것입니다. 계속 할까요?$\r$\rNote: 비표준 플러그인은 지워지지 않을 수도 있습니다.$\r가임 사용자 설정에는 영향을 미치지 않습니다."

!define GOURMET_PROMPT_DIR_EXISTS		"입력하신 설치 디렉토리가 이미 있습니다. 안에 들은 내용이 지워질 수도 있습니다. 계속할까요?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"GTK+ 런타임 설치 중 오류 발생."

!define GTK_BAD_INSTALL_PATH			"입력하신 경로에 접근할 수 없거나 만들 수 없었습니다."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"GTK+ 테마를 설치할 권한이 없습니다."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "언인스톨러가 가임의 레지스트리 엔트리를 찾을 수 없습니다.$\r이 프로그램을 다른 유저 권한으로 설치한 것 같습니다."

!define un.GOURMET_UNINSTALL_ERROR_2         "이 프로그램을 제거할 수 있는 권한이 없습니다."

