;;

;;  vietnamese.nsh

;;

;;  Vietnamese language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1258

;;

;;  Version 2

;;  Note: The NSIS Installer does not yet have Vietnamese translations. Until

;;  it does, these Gourmet translations can not be used.

;;



; Startup GTK+ check

!define GTK_INSTALLER_NEEDED			"The GTK+ runtime environment không có hoặc cần được nâng cấp.$\rHãy cài đặt GTK+ runtime v${GTK_VERSION} hoặc mới hơn"



; License Page

!define GAIM_LICENSE_BUTTON			"Tiếp theo >"

!define GAIM_LICENSE_BOTTOM_TEXT		"$(^Name) được phát hành theo giấy  phép GPL. Giấy phép thấy ở đây chỉ là để cung cấp thông tin mà thôi. $_CLICK"



; Components Page

!define GAIM_SECTION_TITLE			"Gourmet Recipe Manager (phải có)"

!define GTK_SECTION_TITLE			"GTK+ Runtime Environment (phải có)"

!define GTK_THEMES_SECTION_TITLE		"GTK+ Theme"

!define GTK_NOTHEME_SECTION_TITLE		"Không có Theme"

!define GTK_WIMP_SECTION_TITLE		"Wimp Theme"

!define GTK_BLUECURVE_SECTION_TITLE		"Bluecurve Theme"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Light House Blue Theme"

!define GAIM_SECTION_DESCRIPTION		"Các tập tin Gourmet chính và dlls"

!define GTK_SECTION_DESCRIPTION		"Bộ công cụ giao diện đồ họa đa nền để dùng cho Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"GTK+ Themes có thể thay đổi diệm mạo và sác thái của các ứng dụng GTK+."

!define GTK_NO_THEME_DESC			"Không cài đặt GTK+ theme"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (Windows impersonator) là một GTK theme tích hợp tốt trong môi trường desktop của Windows."

!define GTK_BLUECURVE_THEME_DESC		"Bluecurve theme."

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Lighthouseblue theme."



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Phát hiện thấy có phiên bản cũ của  GTK+ runtime. Bạn muốn nâng cấp không?$\rNote: Gourmet có thể không chạy nếu không nâng cấp."



; Installer Finish Page

!define GAIM_FINISH_VISIT_WEB_SITE		"Hãy xem trang chủ Windows Gourmet"



; Gourmet Section Prompts and Texts

!define GAIM_UNINSTALL_DESC			"Gourmet (chỉ bỏ cài đặt)"

!define GAIM_PROMPT_WIPEOUT			"Thư mục Gourmet cũ sẽ bị xóa. Bạn muốn tiếp tục không?$\r$\rNote: Mọi plugin không chuẩn mà bạn đã cài sẽ bị xóa.$\rCác thiết lập người dùng Gourmet sẽ không còn tác dụng."

!define GAIM_PROMPT_DIR_EXISTS		"Thư mục cài đặt mà bạn định ra đã tồn tại rồi. Mọi nội dung$\rsẽ bị xóa. Bạn muốn tiếp tục không?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Lỗi cài đặt GTK+ runtime."

!define GTK_BAD_INSTALL_PATH			"Đường dẫn mà bạn nhập có thể không truy cập được hay không tạo được."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Bạn không có quyền hạn để cài đặt GTK+ theme."



; Uninstall Section Prompts

!define un.GAIM_UNINSTALL_ERROR_1		"Trình gỡ cài đặt không tìm được các  registry entry cho Gourmet.$\rCó thể là chương trình được người dùng khác cài đặt."

!define un.GAIM_UNINSTALL_ERROR_2		"Bạn không có quyền hạn để gỡ bỏ chương trình này."

