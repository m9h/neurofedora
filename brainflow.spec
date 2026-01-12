Name:           brainflow
Version:        5.19.0
Release:        1%{?dist}
Summary:        Biosensor Library (EEG, EMG, ECG)
License:        MIT
URL:            https://brainflow.org
Source0:        https://github.com/brainflow-dev/brainflow/archive/refs/tags/5.19.0.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  bluez-libs-devel
BuildRequires:  dbus-devel
BuildRequires:  libusb1-devel
BuildRequires:  openblas-devel

%description
BrainFlow is a library intended to obtain, parse and analyze EEG, EMG, ECG 
and other kinds of data from biosensors.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
%autosetup -p1

# --- FIX: Force SONAME Versioning for Fedora Compliance ---
# We append CMake commands to the main CMakeLists.txt to apply version info 
# to the targets. This fixes 'invalid-soname' errors in rpmlint.
# We use '5' (Major Version) as the SOVERSION.

cat >> CMakeLists.txt <<EOF

# PATCH INJECTED BY FEDORA SPEC FILE
# Force versioning on shared libraries
set_target_properties(BoardController PROPERTIES VERSION %{version} SOVERSION 5)
set_target_properties(DataHandler PROPERTIES VERSION %{version} SOVERSION 5)
set_target_properties(MLModule PROPERTIES VERSION %{version} SOVERSION 5)

# Try to version the core wrapper if it is built as shared
if(TARGET BrainFlow)
    set_target_properties(BrainFlow PROPERTIES VERSION %{version} SOVERSION 5)
endif()
EOF

%build
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DBUILD_OYMOTION_SDK=OFF \
    -DBUILD_GFORCE_SDK=OFF \
    -DBUILD_GFORCE_PRO_SDK=OFF \
    -DBUILD_SHARED_LIBS=ON \
    -DKISSFFT_STATIC=OFF \
    -DCMAKE_SKIP_INSTALL_RPATH=ON

%cmake_build

%install
mkdir -p %{buildroot}%{_libdir}
mkdir -p %{buildroot}%{_includedir}/brainflow

# 1. Install Shared Libraries (The .so files)
#    We use 'find' to grab them from compiled/ or lib/ to be safe
find . -name "libBoardController.so*" -exec cp -P {} %{buildroot}%{_libdir}/ \;
find . -name "libDataHandler.so*"     -exec cp -P {} %{buildroot}%{_libdir}/ \;
find . -name "libMLModule.so*"        -exec cp -P {} %{buildroot}%{_libdir}/ \;

# 2. Install The C++ Wrapper Library (It was built as a static .a file)
find . -name "libBrainflow.a" -exec cp {} %{buildroot}%{_libdir}/ \; || :
# Just in case it was built as .so with a capital F
find . -name "libBrainFlow.so*" -exec cp -P {} %{buildroot}%{_libdir}/ \; || :

# 3. Install Headers
#    Install ALL headers found in src/ and cpp_package/
#    This covers both the C API and the C++ API (BoardShim)
find src -name "*.h" -exec cp {} %{buildroot}%{_includedir}/brainflow/ \;
find cpp_package -name "*.h" -exec cp {} %{buildroot}%{_includedir}/brainflow/ \;

%files
%license LICENSE
%doc README.md
%{_libdir}/libBoardController.so.*
%{_libdir}/libDataHandler.so.*
%{_libdir}/libMLModule.so.*
# Include libBrainFlow.so if it exists (it might not)
%if 0%{?_file_exists:%{_libdir}/libBrainFlow.so.*}
%{_libdir}/libBrainFlow.so.*
%endif

%files devel
%{_includedir}/brainflow/
%{_libdir}/libBoardController.so
%{_libdir}/libDataHandler.so
%{_libdir}/libMLModule.so
# Explicitly claim the static library we just found
%{_libdir}/libBrainflow.a
# Claim the symlink if it exists (optional but good practice)
%if 0%{?_file_exists:%{_libdir}/libBrainFlow.so}
%{_libdir}/libBrainFlow.so
%endif

%changelog
* Wed Jan 07 2026 Your Name <your.email@example.com> - 5.19.0-1
- Initial package for Fedora
- Enforced SONAME versioning (SOVERSION 5)
- Disabled proprietary SDKs
