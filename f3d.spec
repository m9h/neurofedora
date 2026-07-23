## START: Set by rpmautospec
## (rpmautospec version 0.8.4)
## RPMAUTOSPEC: autorelease, autochangelog
%define autorelease(e:s:pb:n) %{?-p:0.}%{lua:
    release_number = 1;
    base_release_number = tonumber(rpm.expand("%{?-b*}%{!?-b:1}"));
    print(release_number + base_release_number - 1);
}%{?-e:.%{-e*}}%{?-s:.%{-s*}}%{!?-n:%{?dist}}
## END: Set by rpmautospec

%bcond_without python

%bcond_with check

%global usd 0

%global forgeurl https://github.com/f3d-app/f3d
Version:        3.5.0
%forgemeta

Name:           f3d
Release:        2%{?dist}
Summary:        Fast and minimalist 3D viewer

License:        BSD-3-Clause
URL:            %{forgeurl}
Source0:        %{forgesource}

# https://fedoraproject.org/wiki/Changes/EncourageI686LeafRemoval
ExcludeArch: %{ix86}

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  json-devel
BuildRequires:  cxxopts-devel
BuildRequires:  vtk-devel
BuildRequires:  lapack-devel
BuildRequires:  assimp-devel
BuildRequires:  cmake(draco)
# fedora 39 do not ship draco-static package
%if 0%{?fedora} != 39
BuildRequires:  draco-static
%endif
BuildRequires:  alembic-devel
BuildRequires:  opencascade-devel

%if %{usd}
BuildRequires:  cmake(pxr)
BuildRequires:  openshadinglanguage-devel
BuildRequires:  OpenImageIO-devel
BuildRequires:  opensubdiv-devel
BuildRequires:  openvdb-devel
BuildRequires:  ptex-devel
BuildRequires:  OpenColorIO-devel
BuildRequires:  embree-devel
%endif

BuildRequires:  imath-devel
BuildRequires:  help2man

%if %{with check}
BuildRequires:  xorg-x11-drv-dummy
BuildRequires:  mesa-dri-drivers
# provides /usr/bin/xvfb-run
BuildRequires:  xorg-x11-server-Xvfb
BuildRequires:  python3-pytest
%endif

BuildRequires:  desktop-file-utils
BuildRequires:  libappstream-glib

Requires:       hicolor-icon-theme
Requires:       shared-mime-info

# COPR rebuild links VTK 9.6.2 (libvtk*.so.1 collides with Fedora's 9.5.2);
# pin the COPR VTK so f3d resolves to it, not the system 9.5.x.
Requires:       vtk%{?_isa} >= 9.6.2

%description
F3D is a fast and minimalist 3D viewer desktop application. It supports many
file formats, from digital content to scientific datasets (including glTF, USD,
STL, STEP, PLY, OBJ, FBX, Alembic), can show animations and support thumbnails
and many rendering and texturing options including real time physically based
rendering and raytracing.

It is fully controllable from the command line and support configuration files.
It can provide thumbnails, support interactive hotkeys, drag&drop and
integration into file managers.

F3D also contains the libf3d, a simple library to render meshes, with C++ and
Python Bindings, as well as experimental Java and Javascript bindings.

%package        devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    devel
This package contains development files for %{name}.

%if %{with python}
%package        python3
Summary:        Python 3 bindings for the %{name}
BuildRequires:  python3-devel
BuildRequires:  python3-pybind11
Requires:       %{name}%{?_isa} = %{version}-%{release}
Provides:       python3-%{name} = %{version}-%{release}

%description    python3
This package contains Python 3 bindings for %{name}.
%endif

%ifarch %{java_arches}
%package        java
Summary:        Java bindings for the %{name}
BuildRequires:  javapackages-tools
BuildRequires:  java-25-devel
Requires:       %{name}%{?_isa} = %{version}-%{release}

%description    java
This package contains Java bindings for %{name}.
%endif

%prep
%forgeautosetup -p1
# remove bundled libraries of cxxopts and nlohmann_json
rm -rf external/{cxxopts,nlohmann_json}
# fix install location for -java sub-package
sed -i 's|${CMAKE_INSTALL_LIBDIR}|${CMAKE_INSTALL_LIBDIR}/f3d|' java/CMakeLists.txt
sed -i 's|share/java|%{_jnidir}|' java/CMakeLists.txt

%build
%cmake \
    -GNinja \
    -DCMAKE_BUILD_TYPE=RelWithDebInfo \
    -DF3D_PLUGINS_STATIC_BUILD=OFF \
    -DF3D_PLUGINS_INSTALL_DIR=%{_libdir}/f3d/plugins \
    -DF3D_USE_EXTERNAL_CXXOPTS=ON \
    -DF3D_USE_EXTERNAL_NLOHMANN_JSON=ON \
    -DF3D_LINUX_INSTALL_DEFAULT_CONFIGURATION_FILE_IN_PREFIX=ON \
    -DF3D_LINUX_GENERATE_MAN=ON \
    -DF3D_MODULE_RAYTRACING=OFF \
    -DF3D_MODULE_EXTERNAL_RENDERING=OFF \
    -DF3D_PLUGIN_BUILD_ALEMBIC=ON \
    -DF3D_PLUGIN_BUILD_ASSIMP=ON \
    -DF3D_PLUGIN_BUILD_DRACO=ON \
    -DF3D_PLUGIN_BUILD_EXODUS=ON \
    -DF3D_PLUGIN_BUILD_OCCT=ON \
%if %{usd}
    -DF3D_PLUGIN_BUILD_USD=ON \
%endif
    -DF3D_PLUGIN_OCCT_COLORING_SUPPORT=ON \
    -DF3D_PLUGIN_BUILD_VDB=OFF \
%if %{with python}
    -DF3D_BINDINGS_PYTHON=ON \
%endif
%ifarch %{java_arches}
    -DF3D_BINDINGS_JAVA=ON \
%endif
%if %{with check}
    -DBUILD_TESTING=ON \
    -DF3D_TESTING_ENABLE_OSMESA_TESTS=OFF \
%endif
    -DCMAKE_SKIP_INSTALL_RPATH=ON \

%cmake_build

%install
%cmake_install

%cmake_install --component mimetypes
%cmake_install --component sdk
%cmake_install --component configuration

rm -r %{buildroot}%{_datadir}/doc/F3D

%check
%if %{with check}
export MESA_DEBUG=silent
export LIBGL_ALWAYS_SOFTWARE=true
export MESA_LOADER_DRIVER_OVERRIDE=llvmpipe
xvfb-run -a bash -c "%ctest"
%endif

desktop-file-validate %{buildroot}%{_datadir}/applications/*.desktop
appstream-util validate-relax --nonet %{buildroot}%{_metainfodir}/*.metainfo.xml

%files
%license LICENSE.md
%doc README.md
%{_bindir}/f3d
%{bash_completions_dir}/f3d
%{zsh_completions_dir}/_f3d
%{fish_completions_dir}/f3d.fish
%{_datadir}/icons/hicolor/*/apps/f3d.png
%{_datadir}/icons/hicolor/scalable/apps/f3d.svg
%{_datadir}/icons/HighContrast/
%{_datadir}/applications/f3d-plugin-*.desktop
%{_datadir}/applications/f3d.desktop
%{_datadir}/mime/packages/f3d-*.xml
%dir %{_datadir}/f3d
%dir %{_datadir}/f3d/configs
%dir %{_datadir}/f3d/configs/config.d
%dir %{_datadir}/f3d/configs/thumbnail.d
%dir %{_datadir}/f3d/plugins
%{_datadir}/f3d/configs/config.d/*.json
%{_datadir}/f3d/configs/thumbnail.d/*.json
%{_datadir}/f3d/plugins/*.json
%{_datadir}/thumbnailers/f3d-plugin-*.thumbnailer
%{_mandir}/man1/f3d.1*
%{_metainfodir}/app.f3d.F3D.metainfo.xml

%{_libdir}/libf3d.so.3*
%{_libdir}/libvtkext.so
%dir %{_libdir}/f3d
%dir %{_libdir}/f3d/plugins
%{_libdir}/f3d/plugins/libf3d-plugin-*.so

%files devel
%{_libdir}/libf3d.so
%dir %{_includedir}/f3d
%{_includedir}/f3d/*.h
%{_libdir}/cmake/f3d/

%if %{with python}
%files python3
%{python3_sitearch}/f3d/
%endif

%ifarch %{java_arches}
%files java
%{_libdir}/f3d/libf3d-java.so
%{_jnidir}/f3d.jar
%endif

%changelog
* Wed Jul 22 2026 Morgan Hough <morgan.hough@gmail.com> - 3.5.0-2
- Rebuild against COPR VTK 9.6.2; pin Requires: vtk >= 9.6.2 to resolve the
  libvtk*.so.1 SONAME collision with Fedora's system VTK 9.5.x. Converted
  %%autorelease to a concrete Release for the COPR (no dist-git context).

## START: Generated by rpmautospec
* Sun Apr 19 2026 topazus <topazus@outlook.com> - 3.5.0-1
- 3.5.0

* Mon Mar 16 2026 Orion Poplawski <orion@nwra.com> - 3.4.1-3
- Rebuild with vtk 9.6.0

* Fri Jan 16 2026 Fedora Release Engineering <releng@fedoraproject.org> - 3.4.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_44_Mass_Rebuild

* Thu Jan 08 2026 Packit <hello@packit.dev> - 3.4.1-1
- Update to 3.4.1 upstream release
- Resolves: rhbz#2426775

* Wed Oct 22 2025 Packit <hello@packit.dev> - 3.3.0-1
- Update to 3.3.0 upstream release
- Resolves: rhbz#2331280

* Thu Oct 02 2025 topazus <topazus@outlook.com> - 3.2.0-1
- 3.2.0

* Fri Sep 19 2025 Python Maint <python-maint@redhat.com> - 3.0.0-11
- Rebuilt for Python 3.14.0rc3 bytecode

* Sat Aug 23 2025 Orion Poplawski <orion@nwra.com> - 3.0.0-10
- Fix build with VTK 9.5

* Mon Aug 18 2025 Sandro Mani <manisandro@gmail.com> - 3.0.0-9
- Backport fix for building with assimp-6.x

* Mon Aug 18 2025 Sandro Mani <manisandro@gmail.com> - 3.0.0-8
- Rebuild (assimp)

* Fri Aug 15 2025 Python Maint <python-maint@redhat.com> - 3.0.0-7
- Rebuilt for Python 3.14.0rc2 bytecode

* Tue Jul 29 2025 Jiri Vanek <jvanek@redhat.com> - 3.0.0-6
- Rebuilt for java-25-openjdk as preffered jdk

* Wed Jul 23 2025 Fedora Release Engineering <releng@fedoraproject.org> - 3.0.0-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_43_Mass_Rebuild

* Wed Jun 04 2025 Python Maint <python-maint@redhat.com> - 3.0.0-4
- Rebuilt for Python 3.14

* Thu May 29 2025 Richard Shaw <hobbes1069@gmail.com> - 3.0.0-3
- Rebuild for opencascade 7.9.1.

* Wed May 28 2025 Richard Shaw <hobbes1069@gmail.com> - 3.0.0-2
- Rebuild for opencascade 7.9.1.

* Tue Feb 25 2025 Orion Poplawski <orion@nwra.com> - 3.0.0-1
- Update to 3.0.0

* Thu Jan 16 2025 Fedora Release Engineering <releng@fedoraproject.org> - 2.5.0-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_42_Mass_Rebuild

* Wed Jul 17 2024 Fedora Release Engineering <releng@fedoraproject.org> - 2.5.0-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_41_Mass_Rebuild

* Sat Jul 06 2024 topazus <topazus@outlook.com> - 2.5.0-1
- 2.5.0

* Sun Jun 09 2024 Python Maint <python-maint@redhat.com> - 2.4.0-2
- Rebuilt for Python 3.13

* Tue Jun 04 2024 topazus <topazus@outlook.com> - 2.4.0-1
- 2.4.0; fix rhbz#2284434

* Sun Mar 31 2024 topazus <topazus@outlook.com> - 2.3.1-1
- initial import; rhbz#2193288
## END: Generated by rpmautospec
