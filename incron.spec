# TODO:
# - ignore in system incron.d some files: *~, *.rpmnew, *.rpmsave, ...
# - directories for incrontab, and many other things
Summary:	incron :: inotify cron system
Name:		incron
Version:	0.5.7
Release:	0.9
License:	GPL v2/LGPL v2.1/BSD-like?
Group:		Daemons
Source0:	http://inotify.aiken.cz/download/incron/%{name}-%{version}.tar.bz2
# Source0-md5:	f2be35d85854ed76a78f1a192d253139
Source1:	%{name}.init
Patch0:		%{name}-gcc43.patch
URL:		http://incron.aiken.cz/
Patch1:		%{name}-DESTDIR.patch
Requires(post):	fileutils
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

%build
%{__make} \
	LDFLAGS="%{rpmldflags} -Wall" \
	CXXFLAGS="%{rpmcxxflags} -pipe -Wall" \
	CXX="%{__cxx}" \

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/{rc.d/init.d,incron.d} \
	$RPM_BUILD_ROOT/var/spool/%{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT \
	PREFIX=%{_prefix}

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

mv -f $RPM_BUILD_ROOT%{_sysconfdir}/incron.conf{.example,}

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 117 -r -f crontab
%useradd -u 134 -r -d /var/spool/cron -s /bin/false -c "crontab User" -g crontab crontab

%post
/sbin/chkconfig --add %{name}
%service %{name} restart "incron Daemon"

%preun
if [ "$1" = "0" ]; then
	%service %{name} stop
	/sbin/chkconfig --del %{name}
fi

%postun
if [ "$1" = "0" ]; then
	%userremove crontab
	%groupremove crontab
fi

%files
%defattr(644,root,root,755)
%doc CHANGELOG COPYING doc/html/ README TODO
%attr(754,root,root) /etc/rc.d/init.d/%{name}
%attr(640,root,crontab) %config(noreplace) %{_sysconfdir}/incron.conf
%attr(755,root,root) %{_sbindir}/incrond
%attr(4755,root,crontab) %{_bindir}/incrontab
%dir %attr(751,root,crontab) /etc/incron.d
%{_mandir}/man1/incrontab.1*
%{_mandir}/man5/incron.conf.5*
%{_mandir}/man5/incrontab.5*
%{_mandir}/man8/incrond.8*
%attr(1730,root,crontab) /var/spool/%{name}
