# It's the same for releases, but different for pre-releases: please
# don't remove, even if it seems superfluous - AdamW 2008/03
%define fversion	%{version}

Summary:	Eee PC hardware control and configuration
Name:		eee-control
Version:	0.9.6
Release:	5
# Source code from git repository:
# git clone git://greg.geekmind.org/eee-control.git && cd eee-control && git checkout 0.9.6 && \
# cd .. && tar zcvf eee-control-0.9.6.tar.gz --exclude=.git eee-control
Source0:	%{name}-%{version}.tar.gz
Source1:	eee-control.init
Source2:	eee-control-fi.po
Patch2:		eee-control-daemon_no-powerdev-group.patch
Patch3:		eee-control_fix-setup.patch
Patch5:		eee-control_add-fi-lang.patch
Patch6:		eee-control_use_ath5k.patch
Patch7:		eee-control-brightness_fix.patch
Patch8:		eee-control-0.9.6-pynotify.patch
License:	MIT
Group:		System/Configuration/Hardware
URL:		http://greg.geekmind.org/eee-control/
# Asus Eee PC comes with x86_32 CPUs
ExclusiveArch:	%ix86
BuildRequires:	imagemagick
BuildRequires:	python-devel
Requires:	python-smbus
Requires:	gnome-python-gconf
Requires:	python-notify
Requires:	python-gobject
Requires:	pygtk2.0
Requires:	python-dbus
Requires:	xset
Requires(post):	rpm-helper
Requires(preun):	rpm-helper

%description
Eee-control can switch hardware of your Eee PC on and off (WiFi, Bluetooth,
Camera, and so on), adjust the performance level, control your fan, give you
a bigger LCD brightness range, program hotkeys and more. It all does that
with a clean client-server-like architecture and a nice GUI.

Compatible with: ASUS Eee PC 700/700SE, 701/701SD, 702, 900/900A/900SD/900HD,
901, 904HA/904HD, 1000/1000H/1000HD/1000HE, 1002HA.

%prep
%setup -q -n %{name}
%patch2 -p0
%patch3 -p0
%patch5 -p0
%patch6 -p1
%patch7 -p1
%patch8 -p0

# fix langs and install fi language file
%{__cp} %{SOURCE2} locale/fi.po
%{_buildshell} locale/update.sh

# fix desktop file
sed -i -e 's,Categories=Application;System;,Categories=GTK;System;Monitor;X-MandrivaLinux-CrossDesktop;,g' data/eee-control-tray.desktop

%build
%{__python} setup.py build

%install
%{__python} setup.py install \
	-O1 \
	--prefix=%{_prefix} \
	--root=%{buildroot} \
	--skip-build

# Generate and install 32x32 and 16x16 icons.
%{__mkdir} -p %{buildroot}%{_iconsdir}/hicolor/{64x64,32x32,24x24,16x16}/apps
convert -scale 32 data/eee-icon.png %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png
convert -scale 16 data/eee-icon.png %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png

# Install some stuff manually because the build process can't.
%{__install} -D -m644 data/eee-icon.png %{buildroot}%{_iconsdir}/hicolor/64x64/apps/%{name}.png
%{__install} -D -m644 data/eee-icon-small.png %{buildroot}%{_iconsdir}/hicolor/24x24/apps/%{name}.png

# Initfile
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__install} -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}

# Install config file
%{__mv} %{buildroot}%{_datadir}/%{name}/%{name}.conf %{buildroot}%{_sysconfdir}/%{name}.conf

# Not needed
%{__rm} -rf %{buildroot}%{_bindir}/eee-control-setup.sh

%find_lang %{name}

%post
%_post_service eee-control

%preun
%_preun_service eee-control
%preun_uninstall_gconf_schemas %{name}

%files -f %{name}.lang
%defattr(-,root,root)
%doc doc/NOTES doc/README doc/901-ACPI.txt
%{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%{_sysconfdir}/dbus-1/system.d/eee-control-daemon.conf
%{_sysconfdir}/xdg/autostart/eee-control-tray.desktop
%{_sysconfdir}/gconf/schemas/%{name}.schemas
%{_bindir}/eee-*
%{_datadir}/applications/%{name}-tray.desktop
%{_datadir}/%{name}
%{_iconsdir}/hicolor/*/apps/*
%{py_platsitedir}/EeeControl
%{py_platsitedir}/eee_control-%{fversion}-py%{py_ver}.egg-info


%changelog
* Fri May 13 2011 Jani Välimaa <wally@mandriva.org> 0.9.6-4mdv2011.0
+ Revision: 674331
- add patch to workaround missing attach_to_status_icon in latest python-notify

* Mon Mar 28 2011 Sergio Rafael Lemke <sergio@mandriva.com> 0.9.6-3
+ Revision: 648704
- Added pygtk2.0 and python-gobject as requires

* Sat Oct 30 2010 Jani Välimaa <wally@mandriva.org> 0.9.6-2mdv2011.0
+ Revision: 590551
- clean spec; drop support for old mdv releases
- drop py_requires macro
- rebuild for python 2.7

* Sat Jul 10 2010 Jani Välimaa <wally@mandriva.org> 0.9.6-1mdv2011.0
+ Revision: 550021
- new version 0.9.6
- drop P4, applied upstream
- rediff P5

* Wed Dec 30 2009 Jani Välimaa <wally@mandriva.org> 0.9.4-4mdv2010.1
+ Revision: 483863
- fix icons
- install only one config file
- add Patch7:
  o add brightness control file locations for other models than 901
  o don't fail if no brightness control file found

* Sun Nov 08 2009 Jani Välimaa <wally@mandriva.org> 0.9.4-3mdv2010.1
+ Revision: 462975
- require xset (for turning display off with hotkeys)

* Fri Sep 11 2009 Jani Välimaa <wally@mandriva.org> 0.9.4-2mdv2010.0
+ Revision: 438175
- Remove P0 & P1 as eee 901 freezes after Fn+F2
- Add P5 (really add fi translation)
- Split ath5k part from P0 to own patch P6

* Mon Sep 07 2009 Jani Välimaa <wally@mandriva.org> 0.9.4-1mdv2010.0
+ Revision: 432754
- new version 0.9.4
- P0: use ath5k instead of madwifi
- P0 & P1: let kernel handle wlan on/off (Fn+F2)
- P2: no powerdev group in Mandriva
- P3: fix gconf schema location
- P4: fix SHE control file location (for kernel 2.6.31)
- added fi language
- removed fsb-method fix (kernel >2.6.30 supports SHE method)
- don't start service after installation

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - import eee-control


* Wed Aug 19 2009 Guillaume Rousse <guillomovitch@mandriva.org> 0.9.3-1mdv2010.0
- initial mdv release, contributed by Joseph Wang <joequant@gmail.com>
