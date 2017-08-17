#
# Conditional build:
%bcond_without	python	# Python binding
%bcond_with	dnstap	# dnstap replication support
%bcond_with	systemd	# systemd support
#
Summary:	Recursive, validating DNS resolver
Summary(pl.UTF-8):	Rekurencyjny, weryfikujący resolver DNS
Name:		unbound
Version:	1.6.4
Release:	1
License:	BSD
Group:		Applications/Network
Source0:	http://www.unbound.net/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	ab6f7c07610907f1d87191c9ac2db87a
Source1:	%{name}.init
Source2:	%{name}.service
Source3:	https://data.iana.org/root-anchors/icannbundle.pem
# Source3-md5:	24a426d59b61524623695f1b849f159b
Source4:	ftp://ftp.internic.net/domain/named.cache
# Source4-md5:	153ae04e1f10021385681f44a6ebc0f7
Patch0:		%{name}-default_trust_anchor.patch
Patch1:		%{name}-sh.patch
Patch2:		%{name}-pythondir.patch
Patch3:		%{name}-flex.patch
URL:		http://unbound.net/
BuildRequires:	autoconf >= 2.56
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	expat-devel
BuildRequires:	flex
%{?with_dnstap:BuildRequires:	fstrm-devel}
BuildRequires:	libevent-devel
BuildRequires:	libtool
BuildRequires:	openssl-devel >= 1.0
%{?with_dnstap:BuildRequires:	protobuf-c-devel}
BuildRequires:	rpmbuild(macros) >= 1.671
%{?with_systemd:BuildRequires:	systemd-devel}
%if %{with python}
BuildRequires:	python-devel >= 1:2.4.0
BuildRequires:	swig-python
%endif
Provides:	user(unbound)
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/userdel
Requires(pre):	/bin/id
Requires(pre):	/usr/sbin/useradd
Requires:	systemd-units >= 38
Requires:	%{name}-libs = %{version}-%{release}
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Unbound is a validating, recursive, and caching DNS resolver.

The C implementation of Unbound is developed and maintained by NLnet
Labs. It is based on ideas and algorithms taken from a Java prototype
developed by Verisign labs, Nominet, Kirei and ep.net.

Unbound is designed as a set of modular components, so that also
DNSSEC (secure DNS) validation and stub-resolvers (that do not run as
a server, but are linked into an application) are easily possible.

%description -l pl.UTF-8
Unbound to weryfikujący, rekurencyjny i cache'ujący resolver (kod
rozwiązujący nazwy) DNS.

Implementacja Unbound w C jest tworzona i utrzymywana przez NLnet
Labs. Jest oparta na pomysłach i algorytmach zaczerpniętych z
prototypu w Javie stworzonego przez Verisign Labs, Nominet, Kirei oraz
ep.net.

Unbound został zaprojektowany jako zbiór modularnych komponentów, więc
możliwe są także weryfikacja DNSSEC (bezpieczny DNS) oraz
resolvery-zaślepki (nie działające jako serwer, ale wbudowane w
aplikację).

%package libs
Summary:	Unbound shared library
Summary(pl.UTF-8):	Biblioteka współdzielona Unbound
Group:		Libraries
Conflicts:	unbound < 1.4.18-1

%description libs
Unbound shared library.

%description libs -l pl.UTF-8
Biblioteka współdzielona Unbound.

%package devel
Summary:	Header files for unbound library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki unbound
Group:		Development/Libraries
Requires:	%{name}-libs = %{version}-%{release}
Requires:	openssl-devel

%description devel
Header files for unbound library.

%description devel -l pl.UTF-8
Pliki nagłówkowe biblioteki unbound.

%package static
Summary:	Static unbound library
Summary(pl.UTF-8):	Statyczna biblioteka unbound
Group:		Development/Libraries
Requires:	%{name}-devel = %{version}-%{release}

%description static
Static unbound library.

%description static -l pl.UTF-8
Statyczna biblioteka unbound.

%package -n python-unbound
Summary:	Python interface to unbound library
Summary(pl.UTF-8):	Pythonowy interfejs do biblioteki unbound
Group:		Python/Libraries
Requires:	%{name}-libs = %{version}-%{release}

%description -n python-unbound
Python interface to unbound library.

%description -n python-unbound -l pl.UTF-8
Pythonowy interfejs do biblioteki unbound.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__autoheader}
%configure \
	%{?with_dnstap:--enable-dnstap} \
	%{?with_systemd:--enable-systemd} \
	%{__with_without python pyunbound} \
	%{__with_without python pythonmodule} \
	--with-pidfile=/run/%{name}.pid \
	--with-chroot-dir="" \
	--with-conf-file=%{_sysconfdir}/%{name}/%{name}.conf \
	--with-rootkey-file=/var/lib/%{name}/root.key \
	--with-rootcert-file=%{_sysconfdir}/%{name}/icannbundle.pem

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/rc.d/init.d,%{systemdunitdir},/var/lib/%{name}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}
install %{SOURCE2} $RPM_BUILD_ROOT%{systemdunitdir}/%{name}.service
install %{SOURCE3} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/icannbundle.pem
install %{SOURCE4} $RPM_BUILD_ROOT%{_sysconfdir}/%{name}/named.cache

touch $RPM_BUILD_ROOT/var/lib/%{name}/root.key

%if %{with python}
%{__rm} $RPM_BUILD_ROOT%{py_sitedir}/_unbound.la
%py_comp $RPM_BUILD_ROOT%{py_sitedir}
%py_ocomp $RPM_BUILD_ROOT%{py_sitedir}
%py_postclean
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%systemd_post %{name}.service
%service %{name} restart

%pre
%useradd -u 196 -g 99 -d /tmp -s /bin/false -c "unbound user" unbound

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi
%systemd_preun %{name}.service

%postun
if [ "$1" = "0" ]; then
	%userremove unbound
fi
%systemd_reload

%triggerpostun -- %{name} < 1.4.22-1
%systemd_trigger %{name}.service

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc doc/{CREDITS,Changelog,FEATURES,LICENSE,README,TODO,control_proto_spec.txt,example.conf,ietf67-design-02.pdf,requirements.txt}
%attr(754,root,root) /etc/rc.d/init.d/unbound
%{systemdunitdir}/%{name}.service
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/unbound.conf
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/named.cache
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/icannbundle.pem
%attr(755,root,root) %{_sbindir}/unbound
%attr(755,root,root) %{_sbindir}/unbound-anchor
%attr(755,root,root) %{_sbindir}/unbound-checkconf
%attr(755,root,root) %{_sbindir}/unbound-control*
%attr(755,root,root) %{_sbindir}/unbound-host
%{_mandir}/man1/unbound-host.1*
%{_mandir}/man5/unbound.conf.5*
%{_mandir}/man8/unbound-checkconf.8*
%{_mandir}/man8/unbound.8*
%{_mandir}/man8/unbound-anchor.8*
%{_mandir}/man8/unbound-control*.8*
%dir %attr(755,unbound,nobody) /var/lib/%{name}
%ghost /var/lib/%{name}/root.key

%files libs
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libunbound.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libunbound.so.2

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libunbound.so
%{_libdir}/libunbound.la
%{_includedir}/unbound.h
%{_mandir}/man3/libunbound.3*
%{_mandir}/man3/ub_*.3*

%files static
%defattr(644,root,root,755)
%{_libdir}/libunbound.a

%if %{with python}
%files -n python-unbound
%defattr(644,root,root,755)
%attr(755,root,root) %{py_sitedir}/_unbound.so*
%{py_sitedir}/unbound.py[co]
%{py_sitedir}/unboundmodule.py[co]
%endif
