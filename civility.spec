Name:           civility
Version:        1.0.0
Release:        1%{?dist}
Summary:        Tractography and diffusion tools (Needs Description)

License:        MIT
URL:            https://github.com/YourRepo/civility
Source0:        %{name}-%{version}.tar.gz

# Dependencies we just built
BuildRequires:  libminc-devel
BuildRequires:  bicpl-devel
BuildRequires:  make
BuildRequires:  gcc
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool

%description
Tools for diffusion MRI and tractography processing using the BICPL library.

%prep
%setup -q

%build
# 1. Regenerate build system (Standard MNI step)
mkdir -p m4
autoreconf -ifv -I m4

# 2. GENERATE COMPATIBILITY HEADER
# (Reusing the robust V19 header we created for bicpl)
cat > compat_minc.h <<EOF
#ifndef COMPAT_MINC_H
#define COMPAT_MINC_H
/* Fix Redefinitions */
#undef MI_ORIGINAL_TYPE
#undef MAX_VAR_DIMS

/* System & Libs */
#include <unistd.h>
#include <math.h>
#include <minc.h>
#include <volume_io.h>
#include <bicpl.h>  /* Include BICPL specifically */

/* Keyword Fixes */
#undef private
#define private static
#undef public
#define public

/* Type Mappings (Old -> New) */
#define Point             VIO_Point
#define Vector            VIO_Vector
#define Real              VIO_Real
#define STRING            VIO_STR
#define BOOLEAN           VIO_BOOL
#define Status            VIO_Status
#define Colour            VIO_Colour
#define File_formats      VIO_File_formats
#define IO_types          VIO_IO_types
#define General_transform VIO_General_transform
#define Transform         VIO_Transform
#define Transform_2d      VIO_Transform_2d
#define Surfprop          VIO_Surfprop
#define Volume            VIO_Volume
#define Progress_struct   VIO_Progress_struct
#define progress_struct   VIO_progress_struct
#define Smallest_int      signed char

#define Transform_elem_type VIO_Transform_elem_type
#define Point_coord_type    VIO_Point_coord_type
#define Spr_type            float

/* Constants */
#define OK                VIO_OK
#define ERROR             VIO_ERROR
#define END_OF_FILE       VIO_END_OF_FILE

#ifndef PI
#define PI M_PI
#endif

#define DEG_TO_RAD        VIO_DEG_TO_RAD
#define RAD_TO_DEG        VIO_RAD_TO_DEG
#define END_OF_STRING     VIO_END_OF_STRING

/* Macros */
#define ALLOC2D(p,r,c)       VIO_ALLOC2D(p,r,c)
#define FREE2D(p)            VIO_FREE2D(p)
#define ALLOC3D(p,d1,d2,d3)  VIO_ALLOC3D(p,d1,d2,d3)
#define FREE3D(p)            VIO_FREE3D(p)
#define SIZEOF_STATIC_ARRAY(a) (sizeof(a)/sizeof((a)[0]))

#define INTERPOLATE       VIO_INTERPOLATE
#define FRACTION          VIO_FRACTION
#define ROUND             VIO_ROUND
#define FABS              VIO_FABS
#define FLOOR(x)          ((int)floor(x))
#define CEILING(x)        ((int)ceil(x))
#define IS_INT(x)         ((x)==(int)(x))
#define IJ(i,j,nj)        ((i)*(nj)+(j))
#define IJK(i,j,k,nj,nk)  ((i)*(nj)*(nk)+(j)*(nk)+(k))

#ifndef ABS
#define ABS(x) ((x) < 0 ? -(x) : (x))
#endif
#ifndef MAX
#define MAX(x,y) ((x) > (y) ? (x) : (y))
#endif
#ifndef MIN
#define MIN(x,y) ((x) < (y) ? (x) : (y))
#endif

/* Axis Constants */
#ifndef X
#define X VIO_X
#endif
#ifndef Y
#define Y VIO_Y
#endif
#ifndef Z
#define Z VIO_Z
#endif

#endif
EOF

# 3. Configure
# Inject the compatibility header and force legacy keyword support
export CFLAGS="%{optflags} -std=gnu17 -I/usr/include/libminc \
    -include $(pwd)/compat_minc.h \
    -Dprivate=static -Dpublic= \
    -Wno-error=implicit-function-declaration -Wno-error=implicit-int \
    -Wno-error=incompatible-pointer-types -Wno-error=int-conversion"

export CXXFLAGS="$CFLAGS"

%configure --with-minc2 --disable-static

# 4. Build
%make_build

%install
%make_install

%files
%doc COPYING
%{_bindir}/*
# If it installs libraries:
# %{_libdir}/*.so.*

%changelog
* Tue Jan 06 2026 User <user@example.com> - 1.0.0-1
- Initial package build
