# FreeSurfer 8.2.0 — Fedora 43 Build Report

## Summary

We have successfully built FreeSurfer 8.2.0 CLI tools from the v8.2.0 source tag on Fedora 43 (GCC 15.2.1, CMake 3.31, Ninja 1.13) using system VTK 9.5.2 and ITK 5.4.5. The resulting RPM contains 468 binaries including all core recon-all stream tools. This report documents the issues encountered and suggested upstream fixes to improve portability.

**Build configuration:**
```
-DMINIMAL=ON -DBUILD_GUIS=OFF -DDISTRIBUTE_FSPYTHON=OFF
-DTIFF_SYSLIBS=ON -DGLUT_SYSLIBS=ON -DINTEGRATE_SAMSEG=ON
-DVTK_SYSLIBS=ON -DITK_SYSLIBS=ON
```

---

## 1. Platform Detection

**Issue:** `host_os()` in `cmake/functions.cmake` does not recognize Fedora. It falls through to `undefined`, causing none of the `*_SYSLIBS` flags to be set, incorrect library search paths, and the VTK `find_package()` falling into the generic `else` branch.

**Fix applied:** Added `elseif(OS_IDENT MATCHES "Fedora")` to `host_os()` and corresponding Fedora blocks for SYSLIBS flags, gfortran/blas/lapack paths, VTK component list, and ITK directory.

**Suggested upstream improvement:** Consider a generic Linux fallback that sets all `*_SYSLIBS=ON` and uses standard `find_package()` / `pkg-config` paths when `HOST_OS` is unrecognized, rather than falling through with empty variables. This would make FreeSurfer buildable on any Linux distribution with system packages without requiring per-distro patches. Alternatively, accept a `-DUSE_SYSTEM_LIBS=ON` umbrella flag.

---

## 2. GCC 15 / C23 Default Standard Compatibility

GCC 15 defaults to `-std=gnu23` for C code, which enforces stricter rules than previous defaults.

### 2a. K&R Function Prototypes in Bundled DICOM Library

**Issue:** `packages/dicom/condition.h` and `packages/dicom/lst.h` declare callback function parameters with empty parentheses `()`, but the corresponding `.c` files define them with explicit parameters. GCC 15 treats this as a hard error ("conflicting types").

**Files affected:**
- `packages/dicom/condition.h:63` — `COND_ExtractConditions(CTNBOOLEAN(*callback) ())`
- `packages/dicom/condition.h:68` — `COND_EstablishCallback(void (*callback) ())`
- `packages/dicom/lst.h:83` — `LST_Sort(LST_HEAD ** list, size_t nodeSize, int (*compare) ())`

**Fix applied:** Updated header declarations to match the definitions:
```c
// condition.h
COND_ExtractConditions(CTNBOOLEAN(*callback) (CONDITION, const char*));
COND_EstablishCallback(void (*callback) (CONDITION, const char*));
// lst.h
LST_Sort(LST_HEAD ** list, size_t nodeSize, int (*compare) (LST_NODE*, LST_NODE*));
```

### 2b. K&R Style Throughout Bundled C Libraries

**Issue:** The bundled `cephes`, `dicom`, `nrrdio`, and other C libraries use extensive K&R-style empty-paren function declarations, implicit function declarations, and other constructs rejected by C23.

**Fix applied:** Added `-std=gnu89` to `packages/CMakeLists.txt`:
```cmake
add_compile_options(-w -fPIC -std=gnu89)
```

**Suggested upstream improvement:** Either update the bundled C libraries to use C99+ prototypes, or explicitly set `-std=gnu89` (or `-std=gnu99`) in the packages subdirectory as we did. The latter is a one-line change and doesn't affect the rest of FreeSurfer.

### 2c. Fortran BOZ Constants

**Issue:** `talairach_avi/t4_sub.f` uses nonstandard postfix BOZ syntax rejected by modern gfortran.

**Fix applied:** Added `-fallow-invalid-boz -fallow-argument-mismatch` to Fortran flags.

---

## 3. VTK 9.5 Compatibility

### 3a. `VTK_INCLUDE_DIRS` Empty in Modern VTK

**Issue:** `vtkutils/CMakeLists.txt` uses `${VTK_INCLUDE_DIRS}` for include paths, but VTK 9.x CMake config does not populate this variable — it uses target-based includes instead. Result: `vtkObject.h: No such file or directory`.

**Fix applied:** Added VTK CMake targets to `target_link_libraries()`:
```cmake
target_link_libraries(vtkutils tiff VTK::CommonCore VTK::CommonDataModel
    VTK::RenderingCore VTK::RenderingOpenGL2 VTK::FiltersCore
    VTK::FiltersSources VTK::ImagingCore)
```

**Suggested upstream improvement:** Use `target_link_libraries()` with VTK CMake targets instead of the legacy `VTK_INCLUDE_DIRS`/`VTK_LIBRARIES` variables. This is the recommended approach since VTK 8.90+ and is already done elsewhere in the FreeSurfer codebase.

### 3b. `VTK_LEGACY` Macro in `vtkRGBATransferFunction`

**Issue:** `vtkutils/vtkRGBATransferFunction.h:163` uses `VTK_LEGACY(void SetColorSpaceToHSVNoWrap())` which expands differently in VTK 9.5, causing a compile error ("ISO C++ forbids declaration of 'VTK_LEGACY' with no type").

**Fix applied:** Removed the deprecated `SetColorSpaceToHSVNoWrap()` declaration and definition.

### 3c. VTK `find_package()` Component List

**Issue:** The Fedora/generic `else` branch at line 632 does `find_package(VTK HINTS ${VTK_DIR})` without specifying components. With system VTK installations that have multiple configurations, this can pick up incorrect VTK installations (e.g., FSL's bundled VTK 9.3 was found on the developer's workstation before the system VTK).

**Suggested upstream improvement:** Always specify the required VTK components explicitly rather than relying on a bare `find_package(VTK)`. The Rocky9/Ubuntu24 branches already do this correctly.

---

## 4. Install Phase — `DESTDIR` Compatibility

This was the most significant category of issues. Multiple `install(CODE ...)` blocks in the CMake build system hardcode `${CMAKE_INSTALL_PREFIX}` (expanded at configure time to a literal path like `/usr/lib/freesurfer`) and do not respect the `DESTDIR` environment variable that RPM, DEB, and other packaging systems use.

### Affected Functions and Patterns

| Location | Function/Pattern | Issue |
|---|---|---|
| `CMakeLists.txt:275` | `install(CODE "file(WRITE ${CMAKE_INSTALL_PREFIX}/build-stamp.txt ...)")` | Writes directly to install prefix |
| `CMakeLists.txt:765-769` | `symlink()` calls for python | Creates symlinks at install prefix |
| `cmake/functions.cmake` | `install_configured()` | Uses `file(MAKE_DIRECTORY)` and `configure_file()` with bare prefix |
| `cmake/functions.cmake` | `install_append_help()` | Runs `cmake --build` at install time to build fsPrintHelp, then writes to bare prefix |
| `python/CMakeLists.txt` | Multiple `install(CODE ...)` blocks | pip install using fspython at bare prefix |
| `qatools/CMakeLists.txt` | `install(CODE ...)` | pip install using fspython |
| `scripts/CMakeLists.txt` | `install_append_help()` calls | cmake --build at install time |
| `samseg/CMakeLists.txt`, `samseg_scripts/CMakeLists.txt`, 20+ others | Various `install(CODE ...)` | fspython/pip references |
| `distribution/average/CMakeLists.txt` | `install_tarball()` | Extracts git-annex tarballs (not present in source checkout) |

### Fixes Applied

1. **build-stamp.txt**: Removed the `install(CODE)` line from `CMakeLists.txt`
2. **Python symlinks**: Removed `symlink()` calls from `CMakeLists.txt`
3. **python/CMakeLists.txt**: Replaced with empty file (no fspython in RPM)
4. **install_configured()**: Patched to use `$ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}` instead of bare `${CMAKE_INSTALL_PREFIX}`
5. **install_append_help()**: Replaced function body to remove the `cmake --build` / `execute_process` block (helptext XML is still installed separately)
6. **Generated cmake_install.cmake files**: Post-configure sed to add `$ENV{DESTDIR}` prefix to `file(MAKE_DIRECTORY)` and `configure_file()` calls that contain the bare prefix
7. **fspython references**: Post-configure script to empty any generated cmake_install.cmake that references `fspython`, `pip install`, or `python3.8`
8. **distribution/average**: Emptied cmake_install.cmake (annex data not in source tarball)

### Suggested Upstream Improvements

**This is the single highest-impact change for distribution packaging.** The core issue is that `install(CODE ...)` blocks expand `${CMAKE_INSTALL_PREFIX}` at configure time into a literal string, bypassing CMake's built-in `DESTDIR` support.

Recommended fixes, in priority order:

1. **`install_configured()`**: Use `$ENV{DESTDIR}` prefix:
   ```cmake
   file(MAKE_DIRECTORY $ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/${INSTALL_DESTINATION})
   configure_file(... $ENV{DESTDIR}${CMAKE_INSTALL_PREFIX}/${INSTALL_DESTINATION} @ONLY)
   ```

2. **`install_append_help()`**: Build `fsPrintHelp` during `%build`, not during `install(CODE)`. The current approach runs `cmake --build` at install time which requires the full build environment and fails in packaging chroots.

3. **`build-stamp.txt`**: Use a normal `install(FILES ...)` instead of `install(CODE "file(WRITE ...)")`.

4. **Python/fspython**: Add a cmake option (e.g., `SKIP_PYTHON_INSTALL`) that disables all `install(CODE)` blocks related to pip/fspython. Distribution packages use the system Python and install Python modules via their own packaging system.

5. **`install_tarball()`**: Consider making the average/fsaverage data installation conditional on the files existing, with a clear warning instead of `FATAL_ERROR`, to support builds from source tarballs without git-annex data.

---

## 5. Bundled vs System Libraries

FreeSurfer bundles several third-party libraries in `packages/`. For the Fedora build, we used system versions where available:

| Library | Status | System Package |
|---|---|---|
| zlib | **System** | zlib-devel |
| openssl | **System** | openssl-devel |
| libtiff | **System** | libtiff-devel |
| blas/lapack | **System** | blas-devel, lapack-devel |
| VTK | **System** | vtk-devel 9.5.2 |
| ITK | **System** | InsightToolkit5-devel 5.4.5 |
| freeglut | **System** | freeglut-devel |
| jpeg | Bundled | libjpeg-turbo-devel available |
| expat | Bundled | expat-devel available |
| libxml2 | Bundled | libxml2-devel available |
| minc | Bundled | libminc-devel available |
| netcdf | Bundled | netcdf-cxx-devel available |
| nifti | Bundled | nifticlib-devel available |
| gifti | Bundled | gifticlib-devel available |
| tetgen | Bundled | tetgen-devel available |
| nrrdio | Bundled | teem-devel available |
| dcm2niix | Bundled | dcm2niix available |
| dicom (CTN) | Bundled | No system equivalent (custom library) |
| cephes | Bundled | Not packaged |
| svm | Bundled | Custom implementation (not libsvm) |

**Suggested upstream improvement:** For libraries marked "available" above, adding `USE_SYSTEM_<LIB>` cmake options (similar to the existing `TIFF_SYSLIBS`) would make unbundling straightforward for distribution packagers. The existing `*_SYSLIBS` pattern for VTK/ITK/Qt/GLUT is excellent — extending it to jpeg, expat, xml2, nifti, gifti, etc. would be very helpful.

---

## 6. Build Environment

- **OS:** Fedora 43 (mock chroot)
- **Compiler:** GCC 15.2.1
- **CMake:** 3.31.10
- **Build system:** Ninja 1.13
- **VTK:** 9.5.2-11 (custom COPR build with ImagingOpenGL2 module enabled)
- **ITK:** 5.4.5-15 (custom COPR build)
- **Build time:** ~15 minutes compilation (914 targets, -j8)
- **Result:** 27 MB RPM, 468 binaries, 673 total files

---

## Contact

Morgan Hough <morgan.hough@gmail.com>
NeuroFedora COPR: https://copr.fedorainfracloud.org/coprs/mhough/neurofedora/
