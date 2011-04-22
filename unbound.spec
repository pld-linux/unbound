#
Summary:	Recursive, validating DNS server
Name:		unbound
Version:	1.4.9
Release:	1
License:	BSD
Group:		Applications
Source0:	http://www.unbound.net/downloads/%{name}-%{version}.tar.gz
# Source0-md5:	7079e75210c656761d3804a9f2ac7b9f
Source1:	%{name}.init
URL:		http://unbound.net/
BuildRequires:	ldns-devel >= 1.6.9
BuildRequires:	libevent-devel
BuildRequires:	rpmbuild(macros) >= 1.228
Requires(post,preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Unbound is a validating, recursive, and caching DNS resolver.

The C implementation of Unbound is developed and maintained by NLnet
Labs. It is based on ideas and algorithms taken from a java prototype
developed by Verisign labs, Nominet, Kirei and ep.net.

Unbound is designed as a set of modular components, so that also
DNSSEC (secure DNS) validation and stub-resolvers (that do not run as
a server, but are linked into an application) are easily possible.

%package devel
Summary:	Header files for unbound library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki unbound
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

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

%prep
%setup -q

%build
%configure 
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/%{name}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig

%postun
/sbin/ldconfig
/sbin/chkconfig --add %{name}
%service %{name} restart

%preun
if [ "$1" = "0" ]; then
	%service -q %{name} stop
	/sbin/chkconfig --del %{name}
fi

%files
%defattr(644,root,root,755)
%doc doc/Changelog doc/CREDITS doc/control_proto_spec.txt
%doc doc/example.conf doc/README doc/FEATURES doc/ietf67-design-02.odp
%doc doc/ietf67-design-02.pdf doc/requirements.txt doc/TODO 
%attr(754,root,root) /etc/rc.d/init.d/unbound
%dir %{_sysconfdir}/%{name}
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/%{name}/unbound.conf
%attr(755,root,root) %{_libdir}/libunbound.so.*.*.*
%attr(755,root,root) %ghost %{_libdir}/libunbound.so.2
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

%files devel
%defattr(644,root,root,755)
%{_includedir}/unbound.h
%{_libdir}/libunbound.la
%{_libdir}/libunbound.so
%{_mandir}/man3/libunbound.3*

%files static
%defattr(644,root,root,755)
%{_libdir}/libunbound.a
