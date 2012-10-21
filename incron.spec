# TODO:
# - processing files from system dir has little side effect:
#   if file specified in system (or any) table has inexistent paths, incrond
#   will report on the whole table an error without much detail which entry was it:
#   haarber incrond[4025]: cannot create watch for system table ble: (2) No such file or directory
Summary:	incron :: inotify cron system
Name:		incron
Version:	0.5.10
Release:	5
License:	GPL v2
Group:		Daemons
Source0:	http://inotify.aiken.cz/download/incron/%{name}-%{version}.tar.bz2
# Source0-md5:	038190dc64568883a206f3d58269b850
Source1:	%{name}.init
Source2:	%{name}.service
Source3:	%{name}.allow
Source4:	%{name}.deny
Patch0:		%{name}-DESTDIR.patch
Patch1:		%{name}-gcc47.patch
Patch2:		%{name}-man_bugs.patch
Patch3:		configdir.patch
Patch4:		excludefiles.patch
URL:		http://incron.aiken.cz/
BuildRequires:	rpmbuild(macros) >= 1.644
Requires:	systemd-units >= 38
Requires(post):	fileutils
Requires(post,preun,postun):	systemd-units >= 38
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/bin/id
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(pre):	/usr/sbin/useradd
Requires:	rc-scripts
Requires:	uname(release) >= 2.6.13
Provides:	group(crontab)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
This program is an "inotify cron" system. It consists of a daemon and
a table manipulator. You can use it a similar way as the regular cron.
The difference is that the inotify cron handles filesystem events
rather than time periods.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1

%build
%{__make} \
	LDFLAGS="%{rpmldflags} -Wall" \
	CXX="%{__cxx}" \
	OPTIMIZE="%{rpmcxxflags}" \
	DEBUG=""

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{_sysconfdir}/{%{name},%{name}.d}} \
	$RPM_BUILD_ROOT{/var/spool/%{name},%{systemdunitdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX=%{_prefix}

install -p %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
cp -p incron.conf.example $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/%{name}.conf
cp -p %{SOURCE2} $RPM_BUILD_ROOT%{systemdunitdir}
cp -p %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}
cp -p %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 117 -r -f crontab
%useradd -u 134 -r -d /var/spool/%{name} -s /bin/false -c "crontab User" -g crontab crontab

%post
/sbin/chkconfig --add %{name}
%service %{name} restart "incron Daemon"
%systemd_post %{name}.service

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove crontab
	%groupremove crontab
fi
%systemd_reload

%files
%defattr(644,root,root,755)
%doc CHANGELOG COPYING README TODO
%attr(750,root,crontab) %dir %{_sysconfdir}/%{name}
%attr(640,root,crontab) %config(noreplace) %{_sysconfdir}/%{name}/%{name}.conf
%attr(640,root,crontab) %config(noreplace,missingok) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.allow
%attr(640,root,crontab) %config(noreplace,missingok) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/%{name}.deny
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%{systemdunitdir}/%{name}.service
%attr(755,root,root) %{_sbindir}/incrond
%attr(4755,root,crontab) %{_bindir}/incrontab
%dir %attr(751,root,crontab) %{_sysconfdir}/%{name}.d
%{_mandir}/man1/incrontab.1*
%{_mandir}/man5/incron.conf.5*
%{_mandir}/man5/incrontab.5*
%{_mandir}/man8/incrond.8*
%attr(1730,root,crontab) /var/spool/%{name}
