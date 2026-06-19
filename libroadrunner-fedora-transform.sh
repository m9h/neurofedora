#!/bin/bash
# Reproducible no-NLEQ / system-libs / global-libSBML transform for RoadRunner v2.9.2.
set -euo pipefail
cd "$1"   # roadrunner source root

# Reset any prior edits, start clean
rm -rf source/clapack

### CMakeLists.txt — dependency surgery (use system libs, drop superbuild gate) ###
# Drop the non-free/absent clapack + nleq find_package calls.
sed -i '/^find_package(clapack CONFIG REQUIRED)/d;/^find_package(nleq1 CONFIG REQUIRED)/d;/^find_package(nleq2 CONFIG REQUIRED)/d' CMakeLists.txt
# Drop the install(DIRECTORY ${prefix}/...) lines (would install all of /usr).
sed -i '\#install(DIRECTORY "${RR_DEPENDENCIES_INSTALL_PREFIX}/lib"#d;\#install(DIRECTORY "${RR_DEPENDENCIES_INSTALL_PREFIX}/bin"#d;\#install(DIRECTORY "${RR_DEPENDENCIES_INSTALL_PREFIX}/include"#d;\#install(DIRECTORY "${RR_DEPENDENCIES_INSTALL_PREFIX}/share"#d' CMakeLists.txt
# Replace the libsbml find_package (Fedora's config chains absent BZ2/minizip/LIBXML) with a manual target.
python3 - <<'PY'
f='CMakeLists.txt'; s=open(f).read()
old='find_package(${SBML_TARGET_NAME} CONFIG REQUIRED)'
new='''find_library(SBML_LIBRARY NAMES sbml REQUIRED)
find_path(SBML_INCLUDE_DIR NAMES sbml/SBMLTypes.h REQUIRED)
if (NOT TARGET ${SBML_TARGET_NAME})
    add_library(${SBML_TARGET_NAME} UNKNOWN IMPORTED)
    set_target_properties(${SBML_TARGET_NAME} PROPERTIES
        IMPORTED_LOCATION "${SBML_LIBRARY}"
        INTERFACE_INCLUDE_DIRECTORIES "${SBML_INCLUDE_DIR}")
endif ()'''
assert old in s; open(f,'w').write(s.replace(old,new))
PY

### source/CMakeLists.txt — remove NLEQ, map clapack -> system lapack/blas ###
sed -i '/NLEQ1Solver\.cpp/d;/NLEQ2Solver\.cpp/d;/NLEQSolver\.cpp/d;/rrNLEQ1Interface\.cpp/d;/rrNLEQ2Interface\.cpp/d' source/CMakeLists.txt
sed -i '/NLEQ1Solver\.h/d;/NLEQ2Solver\.h/d;/NLEQSolver\.h/d;/rrNLEQ1Interface\.h/d;/rrNLEQ2Interface\.h/d' source/CMakeLists.txt
sed -i '/nleq1::nleq1-static/d;/nleq2::nleq2-static/d' source/CMakeLists.txt
sed -i 's/clapack::lapack clapack::blas clapack::f2c/lapack blas/g' source/CMakeLists.txt

### Remove NLEQ solver registration (keep BasicNewtonIteration + LinesearchNewtonIteration) ###
sed -i '/#include "NLEQ1Solver.h"/d;/#include "NLEQ2Solver.h"/d;/registerSolver(new NLEQ1Solver)/d;/registerSolver(new NLEQ2Solver)/d' source/SteadyStateSolverFactory.cpp
sed -i '/NLEQ1Interface/d;/NLEQ2Interface/d;/NLEQ1Solver/d;/NLEQ2Solver/d' source/rr_pch.h

### libSBML namespace: Fedora's is GLOBAL. Re-qualify libsbml:: -> :: (collision-free
### with rr:: classes), drop using-namespace, unwrap namespace-libsbml forward-decl blocks. ###
find source -type f \( -name '*.cpp' -o -name '*.h' \) -print0 \
  | xargs -0 sed -i 's/libsbml::/::/g;/using namespace libsbml/d'
python3 - <<'PY'
import re, glob
for f in glob.glob('source/**/*.h', recursive=True)+glob.glob('source/**/*.cpp', recursive=True):
    s=open(f).read()
    n=re.sub(r'namespace\s+libsbml\s*\{([^{}]*)\}', r'\1', s)
    if n!=s: open(f,'w').write(n)
PY

### CLAPACK header shims for RoadRunner's SVD/RK (Fedora dropped clapack; symbols in liblapack/blas) ###
mkdir -p source/clapack
cat > source/clapack/f2c.h <<'EOF'
#ifndef RR_CLAPACK_F2C_REDIRECT
#define RR_CLAPACK_F2C_REDIRECT
#include <f2c.h>
#undef abs
#undef min
#undef max
#undef dabs
#undef dmin
#undef dmax
#endif
EOF
cat > source/clapack/blaswrap.h <<'EOF'
#ifndef RR_CLAPACK_BLASWRAP_NOOP
#define RR_CLAPACK_BLASWRAP_NOOP
#endif
EOF
cat > source/clapack/clapack.h <<'EOF'
#ifndef RR_CLAPACK_SHIM_H
#define RR_CLAPACK_SHIM_H
#include <f2c.h>
#ifdef __cplusplus
extern "C" {
#endif
/* Subroutine */ int dgesdd_(char *jobz, integer *m, integer *n, doublereal *a, integer *lda, doublereal *s, doublereal *u, integer *ldu, doublereal *vt, integer *ldvt, doublereal *work, integer *lwork, integer *iwork, integer *info);
/* Subroutine */ int dgesvd_(char *jobu, char *jobvt, integer *m, integer *n, doublereal *a, integer *lda, doublereal *s, doublereal *u, integer *ldu, doublereal *vt, integer *ldvt, doublereal *work, integer *lwork, integer *info);
/* Subroutine */ int dcopy_(integer *n, doublereal *dx, integer *incx, doublereal *dy, integer *incy);
/* Subroutine */ int daxpy_(integer *n, doublereal *da, doublereal *dx, integer *incx, doublereal *dy, integer *incy);
doublereal dnrm2_(integer *n, doublereal *x, integer *incx);
#ifdef __cplusplus
}
#endif
#endif
EOF

### SVD.cpp: f2c min/max macros are #undef'd above; use std:: + <algorithm> ###
sed -i -E 's/([^a-zA-Z0-9_:.])min\(/\1std::min(/g;s/([^a-zA-Z0-9_:.])max\(/\1std::max(/g' source/SVD.cpp
grep -q '#include <algorithm>' source/SVD.cpp || sed -i '1i #include <algorithm>' source/SVD.cpp



### SWIG: stop wrapping the removed NLEQ solvers (else _roadrunner.so refs
### the uncompiled rr::NLEQ1Solver ctor -> ImportError undefined symbol) ###
sed -i '/NLEQ1Solver.h/d;/NLEQ2Solver.h/d;/NLEQSolver.h/d' wrappers/Python/roadrunner/roadrunner.i

### Default steady-state solver was NLEQ2 (removed) -> the free Newton solver ###
sed -i 's/setSteadyStateSolver("nleq2")/setSteadyStateSolver("newton")/g' source/rrRoadRunner.cpp

### Guard NewtonIteration/FixedPointIteration createKinsol() against a NULL model:
### base createKinsol() bails with no model (as at RoadRunner construction) but the
### derived class then calls KINInit on NULL KINSOL memory -> segfault. ###
python3 - <<'PY'
import re
for f in ['source/NewtonIteration.cpp', 'source/FixedPointIteration.cpp']:
    s = open(f).read()
    s = re.sub(r'(KinsolSteadyStateSolver::createKinsol\(\);\n)',
               r'\1        if (!mKinsol_Memory) { return; }\n', s, count=1)
    open(f, 'w').write(s)
PY

echo "RoadRunner transform applied."
