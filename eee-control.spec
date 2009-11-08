# It's the same for releases, but different for pre-releases: please
# don't remove, even if it seems superfluous - AdamW 2008/03
%define fversion	%{version}

Summary:	Eee PC hardware control and configuration
Name:		eee-control
Version:	0.9.4
Release:	%mkrel 3
Source0:	http://greg.geekmind.org/eee-control/src/%{name}-%{version}.tar.gz
Source1:	eee-control.init
Source2:	eee-control-fi.po
Patch2:		eee-control-daemon_no-powerdev-group.patch
Patch3:		eee-control_fix-setup.patch
Patch4:		eee-control_fix_she_config_location.patch
Patch5:		eee-control_add-fi-lang.patch
Patch6:		eee-control_use_ath5k.patch
License:	MIT
Group:		System/Configuration/Hardware
URL:		http://greg.geekmind.org/eee-control/
# Asus Eee PC comes with x86_32 CPUs
ExclusiveArch:	%ix86
BuildRequires:	imagemagick
%py_requires -d
Requires:	python-smbus
Requires:	gnome-python-gconf
Requires:	python-notify
Requires:	python-dbus
Requires:	xset
Requires(post):         rpm-helper
Requires(preun):        rpm-helper
BuildRoot:	%{_tmppath}/%{name}-%{version}-buildroot

%description
Eee-control can switch hardware of your Eee PC on and off (WiFi, Bluetooth,
Camera, and so on), adjust the performance level, control your fan, give you
a bigger LCD brightness range, program hotkeys and more. It all does that
with a clean client-server-like architecture and a nice GUI.

Compatible with: ASUS Eee PC 700/700SE, 701/701SD, 702, 900/900A/900SD/900HD,
901, 904HA/904HD, 1000/1000H/1000HD/1000HE, 1002HA

%prep
%setup -q
%patch2 -p0
%patch3 -p0
%patch4 -p1
%patch5 -p0
%patch6 -p1

# fix langs and install fi language file
%{__cp} %{SOURCE2} locale/fi.po
%{_buildshell} locale/update.sh

# fix desktop file
sed -i -e 's,Categories=Application;System;,Categories=GTK;System;Monitor;X-MandrivaLinux-CrossDesktop;,g' data/eee-control-tray.desktop

%build
%{__python} setup.py build

%install
%{__rm} -rf %{buildroot}
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
%{__install} -D -m644 data/eee-icon.png %{buildroot}%{_iconsdir}/hicolor/64x64/apps/
%{__install} -D -m644 data/eee-icon-small.png %{buildroot}%{_iconsdir}/hicolor/24x24/apps/%{name}.png

# Initfile
%{__mkdir} -p %{buildroot}%{_initrddir}
%{__install} -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}

# Install config file
%{__cp} %{buildroot}%{_datadir}/eee-control/eee-control.conf %{buildroot}%{_sysconfdir}/eee-control.conf

# Not needed
%{__rm} -rf %{buildroot}%{_bindir}/eee-control-setup.sh

# Kernel version >2.6.30 supports SHE, dkms module not needed
%{__rm} -rf %{buildroot}%{_usrsrc}/eeepc-laptop-20090415/

%find_lang %{name}

%post
%_post_service eee-control
%if %mdkversion < 200900
%{update_menu}
%{update_icon_cache hicolor}
%endif

%preun
%_preun_service eee-control
%preun_uninstall_gconf_schemas %{name}
%if %mdkversion < 200900 
%{clean_menus}
%{clean_icon_cache hicolor}
%endif

%clean
%{__rm} -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc doc/NOTES doc/README doc/901-ACPI.txt
%attr(755,root,root) %{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}.conf
%{_sysconfdir}/dbus-1/system.d/eee-control-daemon.conf
%{_sysconfdir}/xdg/autostart/eee-control-tray.desktop
%{_sysconfdir}/gconf/schemas/%{name}.schemas
%{_bindir}/eee-*
%{_datadir}/applications/%{name}-tray.desktop
%{_datadir}/%{name}
%{_iconsdir}/hicolor/*/apps/*
%{py_platsitedir}/EeeControl
%{py_platsitedir}/eee_control-%{fversion}-py%{pyver}.egg-info
