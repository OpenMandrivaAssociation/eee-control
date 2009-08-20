# It's the same for releases, but different for pre-releases: please
# don't remove, even if it seems superfluous - AdamW 2008/03
%define fversion	%{version}

Summary:	Eee PC hardware control
Name:		eee-control
Version:	0.9.3
Release:	%mkrel 1
Source1:	eee-control.init
License:	MIT
Group:		Graphical desktop/Other
URL:		http://greg.geekmind.org/eee-control/
Source0:	http://greg.geekmind.org/eee-control/src/eee-control-%{version}.tar.gz
Requires:	python-smbus
Requires:	gnome-python-gconf
Requires:	python-notify
Requires:	python-dbus
BuildRequires:	python
BuildRoot:	%{_tmppath}/%name-%version

%description
Eee PC hardware control and configuration
 eee-control can switch hardware of your Eee PC on and off (WiFi, Bluetooth,
 Camera, and so on), adjust the performance level, control your fan, give you
 a bigger LCD brightness range, program hotkeys and more. It all does that
 with a clean client-server-like architecture and a nice GUI.
 .
 Compatible with: ASUS Eee PC 700/700SE, 701/701SD, 702,
 900/900A/900SD/900HD, 901, 904HA/904HD, 1000/1000H/1000HD/1000HE, 1002HA

%prep
%setup -q
sed -i -e 's,Categories=Application;System;,Categories=GTK;System;Monitor;X-MandrivaLinux-CrossDesktop;,g' data/eee-control-tray.desktop
# set default to i2c since mandriva default kernel does not have eee_acpi
# module
sed -i -e 's,fsb-method: she,fsb-method: i2c-dev,' data/eee-control.conf

%build

%install
%{__rm} -rf %{buildroot}
%{_buildshell} locale/update.sh
%{__python} setup.py install --prefix=%{_prefix} --root=%{buildroot}

# Generate and install 32x32 and 16x16 icons.
%{__mkdir} -p %{buildroot}%{_iconsdir}/hicolor/{64x64,32x32,16x16}/apps
convert -scale 32 data/eee-icon.png %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png
convert -scale 16 data/eee-icon.png %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png

# Install some stuff manually because the build process can't.
%{__install} -D -m644 data/*.png %{buildroot}%{_iconsdir}/hicolor/64x64/apps/
%{__mkdir} -p %{buildroot}/etc/rc.d/init.d
%{__install} -m 755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}


# Menu file
%{__rm} -f %{buildroot}%{_datadir}/applications/%{name}.desktop
%{__rm} -f %{buildroot}%{_datadir}/applications/%{name}-mobile.desktop

%{find_lang} %{name}

%post
%_post_service eee-control
%if %mdkversion < 200900
%{update_menus}
%{update_icon_cache hicolor}
%endif

%preun
%_preun_service eee-control
%if %mdkversion < 200900
%{clean_menus}
%{clean_icon_cache hicolor}
%endif

%clean
%{__rm} -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc doc/NOTES doc/README doc/901-ACPI.txt
%{_bindir}/%{name}-tray
%{_bindir}/%{name}-daemon
%{_bindir}/eee-control-query.sh
%{_bindir}/eee-control-setup.sh
%{_bindir}/eee-dispswitch.sh
%{_sysconfdir}/xdg/autostart/eee-control-tray.desktop
%{_sysconfdir}/dbus-1/system.d/eee-control-daemon.conf
%{_initrddir}/%{name}
%{_datadir}/applications/%{name}-tray.desktop
%{_datadir}/%{name}
%{_iconsdir}/hicolor/*/apps/*
%{_usrsrc}/eeepc-laptop-20090415/*
%{py_puresitedir}/EeeControl/*
%{py_puresitedir}/eee_control-%{fversion}-py%{pyver}.egg-info

