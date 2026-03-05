# 1. Full Commit Hash for bicpl
%global commit 8be98a9a978543455fba2e6ac2b8b8402fbd73ac
%global shortcommit %(c=%{commit}; echo ${c:0:7})
%global date 20260106

Name:           bicpl
Version:        2.0.0
Release:        1.%{date}git%{shortcommit}%{?dist}
Summary:        Brain Imaging Centre Programming Library

License:        BSD-3-Clause
URL:            https://github.com/BIC-MNI/bicpl
Source0:        https://github.com/BIC-MNI/%{name}/archive/%{commit}/%{name}-%{shortcommit}.tar.gz
# FIX: Download the missing M4 macros required for Autotools
# Point directly to the file we just downloaded manually
# Ensure the URL follows this pattern for downloading a snapshot
Source1: 	https://github.com/BIC-MNI/mni-acmacros/archive/master.tar.gz#/mni-acmacros.tar.gz

# Autotools Dependencies
BuildRequires:  automake
BuildRequires:  autoconf
BuildRequires:  libtool
BuildRequires:  make
BuildRequires:  gcc-c++

# Library Dependencies
BuildRequires:  libminc-devel
BuildRequires:  netcdf-devel
BuildRequires:  zlib-devel

%description
BICPL is a programming library that provides higher-level functions 
on top of libminc, specifically for object manipulation and 
advanced volume operations used by the MNI autoreg tools.

%package devel
Summary:        Development files for %{name}
Requires:       %{name}%{?_isa} = %{version}-%{release}
Requires:       libminc-devel

%description devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

%prep
# Tell setup the folder is named bicpl-<commit>
%setup -q -n bicpl-%{commit}

# ... rest of prep
# Create the directory for external macros
mkdir m4_external

# Extract the macros.
# Note: The folder inside the tarball will be 'mni-acmacros-master'
tar -xf %{SOURCE1} --strip-components=1 -C m4_external

%build
# 1. Regenerate configure script
mkdir -p m4
cp m4_external/*.m4 m4/
autoreconf -ifv -I m4

# 2. Patch configure to use Fedora library names
sed -i 's/volume_io2/minc_io/g' configure

# ----------------------------------------------------------------------
# 3. GENERATE COMPATIBILITY HEADER (v20 - Linker Fix)
# ----------------------------------------------------------------------
cat > compat_minc.h <<EOF
#ifndef COMPAT_MINC_H
#define COMPAT_MINC_H

/* 1. Fix Redefinition Warnings */
#undef MI_ORIGINAL_TYPE
#undef MAX_VAR_DIMS

/* 2. Include System Headers */
#include <unistd.h>
#include <math.h>

/* 3. Include the real MINC headers */
#include <minc.h>
#include <volume_io.h>

/* 4. KEYWORD COMPATIBILITY */
#undef private
#define private static
#undef public
#define public

/* 5. Type Definitions */
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

#define Spr_type          float

/* 6. Enums */
#define Filter_types      VIO_Filter_types
#define Data_types        VIO_Data_types
#define Object_types      VIO_Object_types

/* 7. Constants */
#define OK                VIO_OK
#define ERROR             VIO_ERROR
#define END_OF_FILE       VIO_END_OF_FILE

#define SURFPROP_AMBIENT    VIO_SURFPROP_AMBIENT
#define SURFPROP_DIFFUSE    VIO_SURFPROP_DIFFUSE
#define SURFPROP_SPECULAR   VIO_SURFPROP_SPECULAR
#define SURFPROP_SHININESS  VIO_SURFPROP_SHININESS
#define SURFPROP_OPACITY    VIO_SURFPROP_OPACITY

#ifndef Surfprop_t
#define Surfprop_t(s)       ((s).coefficients[VIO_SURFPROP_OPACITY])
#endif

#ifndef PI
#define PI M_PI
#endif

#define DEG_TO_RAD                  VIO_DEG_TO_RAD
#define RAD_TO_DEG                  VIO_RAD_TO_DEG
#define END_OF_STRING               VIO_END_OF_STRING
#define EXTREMELY_LARGE_STRING_SIZE VIO_EXTREMELY_LARGE_STRING_SIZE

#ifndef MAX_DIMENSIONS
#define MAX_DIMENSIONS    VIO_MAX_DIMENSIONS
#endif

#ifndef N_DIMENSIONS
#define N_DIMENSIONS      VIO_N_DIMENSIONS
#endif

/* 8. Data Types */
#define FLOAT             VIO_FLOAT
#define DOUBLE            VIO_DOUBLE
#define UNSIGNED_BYTE     VIO_UNSIGNED_BYTE
#define SIGNED_BYTE       VIO_SIGNED_BYTE
#define UNSIGNED_SHORT    VIO_UNSIGNED_SHORT
#define SIGNED_SHORT      VIO_SIGNED_SHORT
#define UNSIGNED_INT      VIO_UNSIGNED_INT
#define SIGNED_INT        VIO_SIGNED_INT

/* 9. Macros & Math Helpers */
#ifndef ALLOC2D
#define ALLOC2D( ptr, r, c )       VIO_ALLOC2D( ptr, r, c )
#endif

#ifndef FREE2D
#define FREE2D( ptr )              VIO_FREE2D( ptr )
#endif

#ifndef ALLOC3D
#define ALLOC3D( ptr, d1, d2, d3 ) VIO_ALLOC3D( ptr, d1, d2, d3 )
#endif

#ifndef FREE3D
#define FREE3D( ptr )              VIO_FREE3D( ptr )
#endif

#define SIZEOF_STATIC_ARRAY(a) (sizeof(a)/sizeof((a)[0]))

#define INTERPOLATE       VIO_INTERPOLATE
#define FRACTION          VIO_FRACTION
#define ROUND             VIO_ROUND
#define FABS              VIO_FABS
#define FLOOR(x)          ((int)floor(x))
#define CEILING(x)        ((int)ceil(x))
#define IS_INT(x)         ( (x) == (int)(x) )

/* FIX: Added missing math macros for Linker */
#ifndef ABS
#define ABS(x) ((x) < 0 ? -(x) : (x))
#endif

#ifndef MAX
#define MAX(x,y) ((x) > (y) ? (x) : (y))
#endif

#ifndef MIN
#define MIN(x,y) ((x) < (y) ? (x) : (y))
#endif

#define IJ( i, j, nj )    ( (i)*(nj) + (j) )

#undef IJK
#define IJK( i, j, k, nj, nk ) ( (i)*(nj)*(nk) + (j)*(nk) + (k) )

/* 10. Map Axis Constants */
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

# 4. Compiler Flags
export CFLAGS="%{optflags} -std=gnu17 -I/usr/include/libminc \
    -include $(pwd)/compat_minc.h \
    -Dprivate=static -Dpublic= \
    -Wno-error=implicit-function-declaration -Wno-error=implicit-int \
    -Wno-error=incompatible-pointer-types -Wno-error=int-conversion"

export CXXFLAGS="%{optflags} -std=gnu17 -I/usr/include/libminc \
    -include $(pwd)/compat_minc.h \
    -Dprivate=static -Dpublic="

# 5. Configure
%configure \
    --with-minc2 \
    --with-build-path=%{_prefix} \
    --disable-static \
    --enable-shared \
    LIBS="-lminc_io -lminc2 -lnetcdf -lhdf5 -lz -lm"

%make_build

%install
%make_install

# Clean up libtool archives
find %{buildroot} -name '*.la' -delete

# ----------------------------------------------------------------------
# 6. FILES SECTION
# ----------------------------------------------------------------------

# ----------------------------------------------------------------------
# 6. FILES SECTION
# ----------------------------------------------------------------------

%files
# Capture documentation
%doc COPYING

# Capture the main shared library
%{_libdir}/libbicpl.so.*

# Capture ALL the tools in /usr/bin
%{_bindir}/*

%files devel
# Capture headers
%{_includedir}/*

# Capture the link-time symlink
%{_libdir}/libbicpl.so

%changelog
* Tue Jan 06 2026 Morgan Hough <morgan.hough@gmail.comn> - 2.0.0-1.20260106git
- Switch to Autotools build system
- Inject missing mni-ac-macros manually
