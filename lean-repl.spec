# Lean-compiled native binary; C debuginfo/debugsource extraction yields nothing.
%global debug_package %{nil}

Name:           lean-repl
Version:        4.32.0
Release:        1%{?dist}
Summary:        Read-eval-print loop / JSON server for Lean 4

# Apache-2.0 (upstream leanprover-community/repl)
License:        Apache-2.0
URL:            https://github.com/leanprover-community/repl
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/repl-%{version}.tar.gz

# Built with Lake against the system lean4 toolchain (its lean-toolchain pins
# leanprover/lean4:v%%{version}; with system lean4 on PATH, lake uses it directly
# — no elan). The final `leanc` link needs the -devel .so symlinks for
# gmp/openssl (Lean 4.32 links libssl/libcrypto for Std.Http).
BuildRequires:  lean4 = %{version}
BuildRequires:  gmp-devel
BuildRequires:  openssl-devel
BuildRequires:  libuv-devel
Requires:       lean4 = %{version}

%description
REPL provides a read-eval-print loop for Lean 4 that communicates over JSON on
stdin/stdout: send it Lean commands or tactics and it returns the resulting
goals, messages, and sorries. It is the backend used by tools such as
python-leanclient for programmatic interaction with Lean.

%prep
%autosetup -n repl-%{version}

%build
# system lean4 provides lean/lake; build the repl executable offline
lake build repl

%install
install -Dm0755 .lake/build/bin/repl %{buildroot}%{_bindir}/repl
# ship the compiled REPL library (.olean) under the lean library tree so the
# modules are importable; keep the package's own copy under its libdir.
mkdir -p %{buildroot}%{_libdir}/lean-repl
cp -a .lake/build/lib/lean/REPL %{buildroot}%{_libdir}/lean-repl/
cp -a .lake/build/lib/lean/REPL.olean %{buildroot}%{_libdir}/lean-repl/ 2>/dev/null || :

%files
%license LICENSE
%doc README.md
%{_bindir}/repl
%{_libdir}/lean-repl/

%changelog
* Mon Jul 20 2026 Morgan Hough <morgan.hough@gmail.com> - 4.32.0-1
- Reconstructed spec; build repl via Lake against system lean4 4.32.0
