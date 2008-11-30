;;

;;  french.nsh

;;

;;  French language strings for the Windows Gourmet NSIS installer.

;;  Windows Code page: 1252

;;

;;  Version 3

;;  Author: Eric Boumaour <zongo_fr@users.sourceforge.net>, 2003-2005.

;;



; Make sure to update the GOURMET_MACRO_LANGUAGEFILE_END macro in

; langmacros.nsh when updating this file



; Startup Checks

!define INSTALLER_IS_RUNNING			"Le programme d'installation est dj en cours d'excution."

!define GOURMET_IS_RUNNING			"Une instance de Gourmet est en cours d'excution. Veuillez quitter Gourmet et ressayer."

!define GTK_INSTALLER_NEEDED			"Les bibliothques de l'environnement GTK+ ne sont pas installes ou ont besoin d'une mise  jour.$\rVeuillez installer la version ${GTK_VERSION} ou plus rcente des bibliothques GTK+."



; License Page

!define GOURMET_LICENSE_BUTTON			"Suivant >"

!define GOURMET_LICENSE_BOTTOM_TEXT		"$(^Name) est disponible sous licence GNU General Public License (GPL). Le texte de licence suivant est fourni uniquement  titre informatif. $_CLICK" 



; Components Page

!define GOURMET_SECTION_TITLE			"Gourmet Recipe Manager (obligatoire)"

!define GTK_SECTION_TITLE			"Bibliothques GTK+ (obligatoire)"

!define GTK_THEMES_SECTION_TITLE		"Thmes GTK+"

!define GTK_NOTHEME_SECTION_TITLE		"Pas de thme"

!define GTK_WIMP_SECTION_TITLE		"Thme Wimp"

!define GTK_BLUECURVE_SECTION_TITLE		"Thme Bluecurve"

!define GTK_LIGHTHOUSEBLUE_SECTION_TITLE	"Thme Light House Blue"

!define GOURMET_SHORTCUTS_SECTION_TITLE "Raccourcis"

!define GOURMET_DESKTOP_SHORTCUT_SECTION_TITLE "Bureau"

!define GOURMET_STARTMENU_SHORTCUT_SECTION_TITLE "Menu Dmarrer"

!define GOURMET_SECTION_DESCRIPTION		"Fichiers et DLLs de base de Gourmet"

!define GTK_SECTION_DESCRIPTION		"Un ensemble d'outils pour interfaces graphiques multi-plateforme, utilis par Gourmet"

!define GTK_THEMES_SECTION_DESCRIPTION	"Les thmes GTK+ permettent de changer l'aspect des applications GTK+."

!define GTK_NO_THEME_DESC			"Ne pas installer de thme GTK+"

!define GTK_WIMP_THEME_DESC			"GTK-Wimp (imitateur de Windows) est un thme de GTK+ qui se fond dans l'environnement graphique de Windows."

!define GTK_BLUECURVE_THEME_DESC		"Thme Bluecurve"

!define GTK_LIGHTHOUSEBLUE_THEME_DESC	"Thme Lighthouseblue"

!define GOURMET_SHORTCUTS_SECTION_DESCRIPTION   "Raccourcis pour lancer Gourmet"

!define GOURMET_DESKTOP_SHORTCUT_DESC   "Crer un raccourci pour Gourmet sur le bureau"

!define GOURMET_STARTMENU_SHORTCUT_DESC   "Crer un raccourci pour Gourmet dans le menu Dmarrer"



; GTK+ Directory Page

!define GTK_UPGRADE_PROMPT			"Une ancienne version des bibliothques GTK+ a t trouve. Voulez-vous la mettre  jour ?$\rNote : Gourmet peut ne pas fonctionner si vous ne le faites pas."



; Installer Finish Page

!define GOURMET_FINISH_VISIT_WEB_SITE		"Visitez la page web de Gourmet Windows"



; Gourmet Section Prompts and Texts

!define GOURMET_UNINSTALL_DESC			"Gourmet (supprimer uniquement)"

!define GOURMET_PROMPT_WIPEOUT			"L'ancien dossier de Gourmet va tre supprim. Voulez-vous continuer ?$\r$\rNote : Tous les plugins non standards que vous avez installs seront aussi supprims.$\rLes configurations et les comptes utilisateurs de Gourmet ne sont pas touchs."

!define GOURMET_PROMPT_DIR_EXISTS		"Le dossier d'installation que vous avez choisi existe dj. Son contenu sera effac.$\rVoulez-vous continuer ?"



; GTK+ Section Prompts

!define GTK_INSTALL_ERROR			"Erreur lors de l'installation des bibliothques GTK+"

!define GTK_BAD_INSTALL_PATH			"Le dossier d'installation ne peut pas tre cr ou n'est pas accessible."



; GTK+ Themes section

!define GTK_NO_THEME_INSTALL_RIGHTS		"Vous n'avez pas les permissions pour installer un thme GTK+."



; Uninstall Section Prompts

!define un.GOURMET_UNINSTALL_ERROR_1         "Le programme de dsinstallation n'a pas retrouv les entres de Gourmet dans la base de registres.$\rL'application a peut-tre t installe par un utilisateur diffrent."

!define un.GOURMET_UNINSTALL_ERROR_2         "Vous n'avez pas les permissions pour supprimer cette application."

