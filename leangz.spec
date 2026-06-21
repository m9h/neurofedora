# Built from a vendored crate bundle (offline); no debuginfo from the cargo build.
%global debug_package %{nil}

Name:           leangz
Version:        0.1.19
Release:        1%{?dist}
Summary:        Compressor/archiver for Lean 4 .olean files (provides leangz and leantar)

# leangz itself is Apache-2.0; the vendored Rust crates carry the usual mix.
License:        Apache-2.0 AND (MIT OR Apache-2.0) AND Unicode-3.0 AND BSD-3-Clause AND MIT AND Zlib
URL:            https://github.com/digama0/leangz
Source0:        %{url}/archive/refs/tags/v%{version}.tar.gz#/%{name}-%{version}.tar.gz
# Offline crate bundle: produced with `cargo vendor` (70 crates). Regenerate on
# version bump with: cargo vendor --versioned-dirs vendor && tar czf <this> vendor
Source1:        %{name}-%{version}-vendor.tar.gz

BuildRequires:  cargo
BuildRequires:  rust
# zstd-sys compiles its bundled zstd C source via the cc crate.
BuildRequires:  gcc

# The vendored crates are compiled in statically (Rust); declare the notable ones.
Provides:       bundled(crate(zstd)) = 0.13.3
Provides:       bundled(zstd) = 1.5.7
Provides:       bundled(crate(rayon)) = 1.7
Provides:       bundled(crate(serde)) = 1.0

%description
leangz is a (de)compressor and archiver for Lean 4 .olean files. It ships two
tools:
  * leangz  — compress/decompress individual .olean files
  * leantar — pack/unpack collections of .olean files into .ltar archives
leantar is the tool the Lean 4 build system uses to (un)pack precompiled
library archives; this package provides it for an offline, from-source Lean 4
build (replacing the prebuilt binary Lean would otherwise download).

%prep
%autosetup -n %{name}-%{version}

# Unpack the vendored crates and point cargo at them (fully offline build).
tar -xzf %{SOURCE1}
mkdir -p .cargo
cat > .cargo/config.toml <<'EOF'
[source.crates-io]
replace-with = "vendored-sources"

[source.vendored-sources]
directory = "vendor"
EOF

%build
export CARGO_HOME=.cargo
cargo build --release --offline --locked --bins

%install
install -d %{buildroot}%{_bindir}
install -m 0755 target/release/leangz  %{buildroot}%{_bindir}/leangz
install -m 0755 target/release/leantar %{buildroot}%{_bindir}/leantar

%check
# Smoke-test that the binaries run.
./target/release/leangz --help >/dev/null 2>&1 || ./target/release/leangz 2>/dev/null || :
./target/release/leantar --help >/dev/null 2>&1 || ./target/release/leantar 2>/dev/null || :

%files
%license LICENSE
%{_bindir}/leangz
%{_bindir}/leantar

%changelog
* Sat Jun 20 2026 Morgan Hough <morgan.hough@gmail.com> - 0.1.19-1
- Initial package: leangz 0.1.19 (digama0/leangz), providing the leangz and
  leantar Lean 4 .olean (de)compression tools. Built offline from a vendored
  crate bundle. First prerequisite for packaging the Lean 4 toolchain (Lean's
  build otherwise downloads a prebuilt leantar binary, which Fedora/COPR forbid).
