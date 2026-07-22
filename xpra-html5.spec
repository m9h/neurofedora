# xpra-html5 — HTML5 browser client for Xpra.
# Fedora/COPR build for mhough/neurofedora (noarch). Based on the upstream spec
# (Xpra-org/xpra-html5, GPL-2.0+ AND BSD-3-Clause AND LGPL-3.0+ AND MIT),
# adapted to source the released tag tarball from GitHub.
#
# Build the SRPM and submit:
#   rpmbuild -bs xpra-html5.spec   # after placing the tarball in ~/rpmbuild/SOURCES
#   copr-cli build mhough/neurofedora <built>.src.rpm
# or build straight from this spec with copr-cli's --srpm flow (see build-copr.sh).

%define minifier uglifyjs

Name:           xpra-html5
Version:        21
Release:        1%{?dist}
Summary:        HTML5 client for Xpra
License:        GPL-2.0+ AND BSD-3-Clause AND LGPL-3.0+ AND MIT
URL:            https://github.com/Xpra-org/xpra-html5
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/xpra-html5-%{version}.tar.gz
BuildArch:      noarch

BuildRequires:  python3
BuildRequires:  python3-setuptools
BuildRequires:  uglify-js
BuildRequires:  brotli
BuildRequires:  js-jquery
BuildRequires:  desktop-backgrounds-compat
Requires:       js-jquery
Recommends:     desktop-backgrounds-compat
# The server-side xpra package serves these files at --html=on:
Conflicts:      xpra < 2.1

%description
The HTML5 client for Xpra. An xpra server (or any web server) can serve it so
that a full xpra session is usable from a web browser, with no native client
to install. Installs the web assets under %{_datadir}/xpra/www.

%prep
%autosetup -n xpra-html5-%{version}

%install
mkdir -p %{buildroot}%{_datadir}/xpra/www
mkdir -p %{buildroot}%{_sysconfdir}/xpra/html5-client
python3 ./setup.py install %{buildroot} %{_datadir}/xpra/www/ \
        %{_sysconfdir}/xpra/html5-client %{minifier}
# No executable web assets.
find %{buildroot}%{_datadir}/xpra/www/ -type f -exec chmod 0644 {} \;

%files
%license LICENSE
%{_sysconfdir}/xpra/html5-client
%{_datadir}/xpra/www

%changelog
* Mon Jul 20 2026 Morgan Hough <morgan.hough@gmail.com> - 21-1
- Update to 21

* Tue Jun 09 2026 Morgan Hough <morgan.hough@gmail.com> - 20-1
- Initial neurofedora COPR build of xpra-html5 v20 for Fedora 44 (aarch64+x86_64).
- Provides the browser GUI client for the student-access gateway.
