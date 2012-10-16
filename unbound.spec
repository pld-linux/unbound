#
# Conditional build:
%bcond_without	python	# Python binding
#
Summary:	Recursive, validating DNS resolver
Summary(pl.UTF-8):	Rekurencyjny, weryfikujący resolver DNS
Name:		unbound
Version:	1.4.18
Release:	1
License:	BSD
Group:		Applications/Network
Source0:	http://www.unbound.net/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	2cad65b6a2d08bb6e0210ea92156ca4b
Source1:	%{name}.init
URL:		http://unbound.net/
BuildRequires:	expat-devel
BuildRequires:	ldns-devel >= 1.6.9
BuildRequires:	libevent-devel
BuildRequires:	openssl-devel
BuildRequires:	rpmbuild(macros) >= 1.228
%if %{with python}
BuildRequires:	python-devel >= 1:2.4.0
BuildRequires:	swig-python
%endif
Requires(post,preun):	/sbin/chkconfig
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
Requires:	ldns-devel
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

%build
%configure \
	%{?with_python:--with-pyunbound}
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%if %{with python}
%{__rm} $RPM_BUILD_ROOT%{py_sitedir}/_unbound.{la,a}
%py_comp $RPM_BUILD_ROOT%{py_sitedir}
%py_ocomp $RPM_BUILD_ROOT%{py_sitedir}
%py_postclean
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%post	libs -p /sbin/ldconfig
%postun	libs -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc doc/{CREDITS,Changelog,FEATURES,LICENSE,README,TODO,control_proto_spec.txt,example.conf,ietf67-design-02.pdf,requirements.txt}
%attr(754,root,root) /etc/rc.d/init.d/unbound
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/unbound.conf
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
%{_mandir}/man8/unbound-control.8*

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

%files static
%defattr(644,root,root,755)
%{_libdir}/libunbound.a

%if %{with python}
%files -n python-unbound
%defattr(644,root,root,755)
%attr(755,root,root) %{py_sitedir}/_unbound.so*
%{py_sitedir}/unbound.py[co]
%endif
