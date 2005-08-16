%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

Name:		gourmet
Version:	0.8.6.1
Release:	1
Summary:	PyGTK Recipe Manager

Group:		Applications/Productivity
License:	GPL
URL:		http://grecipe-manager.sourceforge.net
Source0:	http://easynews.dl.sourceforge.net/sourceforge/grecipe-manager/gourmet-0.8.6.1.tar.gz
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildArch:	noarch
BuildRequires:	python >= 0:2.2
BuildRequires:	gettext
BuildRequires:	desktop-file-utils
#Requires:	python-abi = %(%{__python} -c "import sys ; print sys.version[:3]")
Requires:	libglade
Requires:	metakit
Requires:	pygtk2 > 2.3.9
Requires:	python-imaging
# The following are really optional
#Requires:	PyRTF
Requires:	gnome-python2
#Requires:	gnome-python2-gnomeprint

%description
Gourmet Recipe Manager is a recipe-organizer for GNOME that generates shopping
lists and allows rapid searching of recipes. It imports mealmaster & mastercook
files and exports webpages & other formats. Gourmet uses python, gtk and
metakit.

%prep
%setup -q
#%patch0 -p1

%build
pushd i18n
find -name \*.mo |xargs rm -f
for file in *.po; do
	sh make_mo.sh $(basename $file .po)
done
popd

cp gourmet.desktop gourmet.desktop.orig
cat gourmet.desktop.orig \
|sed -e s?"\.$"?""?g \
|sed -e s?"=True"?"=true"?g > gourmet.desktop

%{__python} setup.py build

%install
rm -rf %buildroot
%{__python} setup.py install -O1 --skip-build --root %buildroot \
--disable-modules-check --install-lib %_datadir

desktop-file-install %buildroot%_datadir/applications/gourmet.desktop \
--vendor=fedora \
--add-category=X-Fedora \
--dir=%buildroot%_datadir/applications \
--delete-original


%find_lang %{name}

%clean
rm -rf %buildroot


%files -f %{name}.lang
%defattr(-,root,root,-)
%doc CHANGES PKG-INFO README TODO
%doc documentation
%_bindir/gourmet
# sitelib stuff
# python_sitelib -> _datadir (changed by tom)
# This will put gourmet .py files in /usr/share/,
# which doesn't allow gourmet to be used as a python module,
# but *does* allow one RPM to be used for python2.3 and python2.4
%dir %{_datadir}/gourmet
%{_datadir}/gourmet/*.py
%{_datadir}/gourmet/*.pyc
%ghost %{_datadir}/gourmet/*.pyo
%dir %{_datadir}/gourmet/backends
%{_datadir}/gourmet/backends/*.py
%{_datadir}/gourmet/backends/*.pyc
%ghost %{_datadir}/gourmet/backends/*.pyo
%dir %{_datadir}/gourmet/exporters
%{_datadir}/gourmet/exporters/*.py
%{_datadir}/gourmet/exporters/*.pyc
%ghost %{_datadir}/gourmet/exporters/*.pyo
%dir %{_datadir}/gourmet/importers
%{_datadir}/gourmet/importers/*.py
%{_datadir}/gourmet/importers/*.pyc
%ghost %{_datadir}/gourmet/importers/*.pyo
# datadir stuff
%{_datadir}/applications/fedora-gourmet.desktop
%{_datadir}/pixmaps/recbox.png
%dir %{_datadir}/gourmet
%{_datadir}/gourmet/*.glade
%{_datadir}/gourmet/*.css
%{_datadir}/gourmet/*.dtd
%{_datadir}/gourmet/*.png


%changelog
* Mon May 09 2005 Thomas M. Hinkle <Thomas_Hinkle@alumni.brown.edu> - 0.8.4.0-1
- Various enhancements (see CHANGES)

* Thu Apr 28 2005 Thomas M. Hinkle <Thomas_Hinkle@alumni.brown.edu> - 0.8.3.5-1
- Apply patches from Michael Peters
- Make lines wrap in splash screen so i18n'd versions don't suffer
- Use this specfile for gourmet builds rather than python setup.py bdist_rpm

* Sun Apr 24 2005 Michael A. Peters <mpeters@mac.com> - 0.8.3.4-1.3
- patch for rtf importer (submitted upstream to)

* Sun Apr 24 2005 Michael A. Peters <mpeters@mac.com> - 0.8.3.4-1.2
- remove desktop patch, use sed script instead (so that patch doesn't
fail when new languages are added to desktop file)

* Sat Apr 23 2005 Michael A. Peters <mpeters@mac.com> - 0.8.3.4-1.1
- stylistic cleanup

* Sat Apr 23 2005 Michael A. Peters <mpeters@mac.com> - 0.8.3.4-1
- upstream version bump
- locale stuff fixed upstream

* Sun Apr 17 2005 Michael A. Peters <mpeters@mac.com> - 0.8.3.3-1.1
- working on i18n stuff

* Sat Apr 16 2005 Michael A. Peters <mpeters@mac.com> - 0.8.3.3-1
- upstream version bump

* Wed Apr 13 2005 Michael A. Peters <mpeters@mac.com> - 0.8.3.2-1
- Created initial spec file
