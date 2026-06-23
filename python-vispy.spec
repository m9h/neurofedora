Name:           python-vispy
Version:        0.16.2
Release:        1%{?dist}
Summary:        Interactive scientific visualization with OpenGL

License:        BSD-3-Clause
URL:            https://vispy.org
Source0:        %{pypi_source vispy}

# One Cython extension (vispy/visuals/text/_sdf_cpu) -> arch-specific build.
BuildRequires:  gcc
BuildRequires:  python3-devel
BuildRequires:  pyproject-rpm-macros
# vispy.ext.fontconfig dlopens libfontconfig at import time (font discovery);
# `import vispy` fails outright without it. Needed for %check and at runtime.
BuildRequires:  fontconfig

%global _description %{expand:
VisPy is a high-performance interactive 2D/3D data-visualization library that
leverages the GPU through OpenGL. It provides both low-level GL access (gloo)
and a high-level scene graph, and is the rendering engine used by napari.}

%description %{_description}

%package -n python3-vispy
Summary:        %{summary}
# libfontconfig is dlopen'd via ctypes (not caught by the auto-dep generator).
Requires:       fontconfig
# Runtime backend toolkits are optional extras upstream; pull a usable GUI
# backend by default without making it mandatory (napari brings its own).
Recommends:     python3-pyqt6
%description -n python3-vispy %{_description}

%prep
%autosetup -n vispy-%{version}

# Strip non-functional `#!/usr/bin/env python` shebangs from library modules
# (they are imported, not executed) — rpmlint: non-executable-script.
find vispy -name '*.py' -exec sed -i '1{\,^#!.*python,d}' {} +

%generate_buildrequires
# Tarball has no .git; setuptools_scm cannot derive the version -> pin it.
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_buildrequires

%build
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_wheel

%install
export SETUPTOOLS_SCM_PRETEND_VERSION=%{version}
%pyproject_install
%pyproject_save_files vispy

%check
# Top-level import only (-t): there is no OpenGL context/display/Qt in mock, so
# importing every submodule (backends, qt, tests) would fail. A bare
# `import vispy` exercises the font/freetype/fontconfig path and the package
# init without opening a GL context.
%pyproject_check_import -t

%files -n python3-vispy -f %{pyproject_files}
%license LICENSE.txt
%doc README.rst

%changelog
* Mon Jun 22 2026 Morgan Hough <morgan.hough@gmail.com> - 0.16.2-1
- Initial package: vispy 0.16.2 (GPU scientific visualization).
- napari's rendering engine; pinned to the 0.16.x line napari 0.7.x requires
  (vispy >=0.16.2,<0.17). One Cython extension (_sdf_cpu); runtime deps
  (freetype-py, hsluv, kiwisolver) all already in Fedora.
