%define name	eee-control
%define version	0.9.4
%define release	%mkrel 1

# It's the same for releases, but different for pre-releases: please
# don't remove, even if it seems superfluous - AdamW 2008/03
%define fversion	%{version}

Summary:	Eee PC hardware control and configuration
Name:		%{name}
Version:	%{version}
Release:	%{release}
Source0:	http://greg.geekmind.org/eee-control/src/%{name}-%{version}.tar.gz
Source1:	eee-control.init
Source2:	eee-control-fi.po
Patch0:		eee-control_models.patch
Patch1:		eee-control_actions.patch
Patch2:		eee-control_fi-lang.patch
Patch3:		eee-control-daemon_no-powerdev-group.patch
Patch4:		eee-control_fix-setup.patch
Patch5:		eee-control_fix_she_config_location.patch
License:	MIT
Group:		System/Configuration/Hardware
URL:		http://greg.geekmind.org/eee-control/
# Asus Eee PC comes with x86_32 CPUs
ExclusiveArch:	i586
BuildRequires:	imagemagick
%py_requires -d
Requires:	python-smbus
Requires:	gnome-python-gconf
Requires:	python-notify
Requires:	python-dbus
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
%setup -q -n %{name}-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p0
%patch3 -p0
%patch4 -p0
%patch5 -p1

# fix langs
cp %{SOURCE2} locale/fi.po
chmod +x locale/update.sh
locale/update.sh

# correct version
#sed -i -e 's,version=\"0.9.1\",version=\"0.9.2\",g' setup.py

# fix desktop file
sed -i -e 's,Categories=Application;System;,Categories=GTK;System;Monitor;X-MandrivaLinux-CrossDesktop;,g' data/eee-control-tray.desktop

%build
python setup.py build

%install
%{__rm} -rf %{buildroot}
python setup.py install \
	-O1 \
	--prefix=%{_prefix} \
	--root=%{buildroot} \
	--skip-build \
	--record=INSTALLED_FILES 

# Generate and install 32x32 and 16x16 icons.
%{__mkdir} -p %{buildroot}%{_iconsdir}/hicolor/{64x64,32x32,24x24,16x16}/apps
convert -scale 32 data/eee-icon.png %{buildroot}%{_iconsdir}/hicolor/32x32/apps/%{name}.png
convert -scale 16 data/eee-icon.png %{buildroot}%{_iconsdir}/hicolor/16x16/apps/%{name}.png

# Install some stuff manually because the build process can't.
install -D -m644 data/eee-icon.png %{buildroot}%{_iconsdir}/hicolor/64x64/apps/
install -D -m644 data/eee-icon-small.png %{buildroot}%{_iconsdir}/hicolor/24x24/apps/%{name}.png

# Initfile
%{__mkdir} -p %{buildroot}%{_initrddir}
install %{SOURCE1} %{buildroot}%{_initrddir}/%{name}

# Install config file
install -D -m644 %{buildroot}%{_datadir}/eee-control/eee-control.conf %{buildroot}%{_sysconfdir}/eee-control.conf

# Install RT2860STA.dat
install -D -m644 data/RT2860STA.dat %{buildroot}%{_sysconfdir}/Wireless/RT2860STA/RT2860STA.dat

# Module options
%{__mkdir} -p %{buildroot}%{_sysconfdir}/modprobe.d
cat <<EOF >%{buildroot}%{_sysconfdir}/modprobe.d/%{name}.conf
options pciehp pciehp_force=1 pciehp_poll_mode=1
options snd_hda_intel power_save=1 power_save_controller=1
EOF

# Don't want these
%{__rm} -rf %{buildroot}%{_bindir}/eee-control-query
%{__rm} -rf %{buildroot}%{_bindir}/eee-control-setup.sh
%{__rm} -rf %{buildroot}%{_bindir}/eee-dispswitch.sh
%{__rm} -rf %{buildroot}%{_datadir}/eee-control/eee-control.conf
%{__rm} -rf %{buildroot}%{_usrsrc}/*

%find_lang %{name}

%post
%_post_service eee-control

%preun
%_preun_service eee-control

%clean
%{__rm} -rf %{buildroot}

%files -f %{name}.lang
%defattr(-,root,root)
%doc doc/*
%attr(755,root,root) %{_initrddir}/%{name}
%config(noreplace) %{_sysconfdir}/dbus-1/system.d/eee-control-daemon.conf
%config(noreplace) %{_sysconfdir}/%{name}.conf
%config(noreplace) %{_sysconfdir}/Wireless/RT2860STA/RT2860STA.dat
%config(noreplace) %{_sysconfdir}/modprobe.d/%{name}.conf
%{_sysconfdir}/xdg/autostart/eee-control-tray.desktop
%{_sysconfdir}/gconf/schemas/%{name}.schemas
%{_bindir}/eee-*
%{_datadir}/applications/%{name}-tray.desktop
%{_datadir}/%{name}
%{_iconsdir}/hicolor/*/apps/*
%{py_puresitedir}/EeeControl
%{py_puresitedir}/eee_control-%{fversion}-py%{pyver}.egg-info
