%global debug_package %{nil}

Name:           antimony
Version:        3.1.3
Release:        1%{?dist}
Summary:        Human-readable model definition language that translates to/from SBML

# sys-bio/antimony is MIT.
License:        MIT
URL:            https://github.com/sys-bio/antimony
Source0:        antimony-%{version}.tar.gz

BuildRequires:  gcc-c++
BuildRequires:  cmake
BuildRequires:  ninja-build
BuildRequires:  python3-devel
BuildRequires:  libsbml-devel
BuildRequires:  libsbmlnetwork-devel
BuildRequires:  expat-devel
BuildRequires:  chrpath

%description
Antimony is a human-readable, human-writable model definition language for
biochemical reaction networks. The antimony command-line translators convert
between Antimony text and SBML (and CellML). This Fedora build links the system
libSBML and libSBMLNetwork (no superbuild) and omits the non-essential
CellML/Qt-GUI/compression features.

%package -n python3-antimony
Summary:        Python bindings for Antimony (SBML authoring)
Requires:       libsbml
%description -n python3-antimony
ctypes-based Python bindings for libAntimony — load, write, and translate
Antimony/SBML models from Python. Used by CompuCell3D and other tools for
human-readable SBML authoring.

%prep
%autosetup -n antimony-%{version}

# Link the SHARED system libSBMLNetwork (Fedora ships no static *-static lib).
sed -i 's/NAMES libsbmlnetwork-static.lib sbmlnetwork-static.lib/NAMES sbmlnetwork libsbmlnetwork-static.lib sbmlnetwork-static.lib/' CMakeLists.txt

# Fedora's libSBML is GLOBAL-namespace; antimony is written for the namespaced
# build (160 `libsbml::` qualifiers + `using namespace libsbml;` in 28 files).
# Requalify `libsbml:: -> ::` (explicit global scope, collision-free) and drop the
# now-invalid using-directives, so the libSBML types resolve from global scope.
find src -type f \( -name '*.h' -o -name '*.cpp' -o -name '*.ypp' \) -print0 \
  | xargs -0 sed -i 's/libsbml::/::/g;/using namespace libsbml;/d'

# ModelHistory::unsetParentSBMLObject() is protected in Fedora's libSBML 5.20.5
# (was public in antimony's pinned libSBML). antimony only calls it to tidy the
# parent pointer of a local ModelHistory copy it keeps for re-emission — safe to drop.
sed -i '/m_history.unsetParentSBMLObject();/d' src/annotated.cpp

# Fedora's libSBML 5.20.5 lacks the DISTRIB package and has the older fbc API.
# Adapt antimony (built against a newer libSBML from libroadrunner-deps):
python3 - <<'PY'
# (1) ArcTypeToString is defined+used unguarded but declared only under
#     LIBSBML_HAS_PACKAGE_DISTRIB (absent on Fedora) — pull the declaration out.
f='src/typex.h'; s=open(f).read()
s=s.replace("std::string ArcTypeToString(const arc_type type);\n#endif",
            "#endif\nstd::string ArcTypeToString(const arc_type type);")
open(f,'w').write(s)

# (2) fbc GeneProductAssociation: getAssociationAsASTNode/createChildAssociationFromASTNode
#     are post-5.20.5. Use the symmetric infix API (toInfix / setAssociation(string)).
f='src/module-sbml.cpp'; s=open(f).read()
s=s.replace("          ASTNode* astn = gpa->getAssociationAsASTNode();\n          if (astn) {",
            "          const FbcAssociation* assoc = gpa->getAssociation();\n          if (assoc) {")
s=s.replace("            Formula form;\n            char* formula = SBML_formulaToL3String(astn);\n            setFormulaWithString(formula, &form, this);\n            delete formula;",
            "            Formula form;\n            setFormulaWithString(assoc->toInfix(), &form, this);")
s=s.replace("    ASTNode* astn = parseStringToASTNode(gpavar->GetFormula()->ToSBMLString());\n    gpa->createChildAssociationFromASTNode(astn);\n    delete astn;",
            "    gpa->setAssociation(gpavar->GetFormula()->ToSBMLString(), false, true);")
open(f,'w').write(s)

# (3) FbcSpeciesPlugin::isWellFormedChemicalFormula() is post-5.20.5; it only
#     validates a formula string for an error message. Skip the validation.
f='src/variable.cpp'; s=open(f).read()
s=s.replace("""    if (!FbcSpeciesPlugin::isWellFormedChemicalFormula(name)) {
      g_registry.SetError("Cannot set a species chemical formula to '" + name + "': that string is not a legal chemical formula.");
    }""",
            "    /* isWellFormedChemicalFormula() unavailable in libSBML 5.20.5; skip check */")
open(f,'w').write(s)
PY

%build
# libSBMLNetwork's installed headers cross-include siblings by bare name
# (#include "libsbmlnetwork_sbmldocument.h"), so the sbmlnetwork header dir must be
# on the include path in addition to %{_includedir} (used for the <sbmlnetwork/...> form).
export CXXFLAGS="%{optflags} -I%{_includedir}/sbmlnetwork"
# Bypass antimony's prebuilt-deps CONFIG find_package()s (sbml-static, expat
# CONFIG, ZLIB CONFIG) — which don't match Fedora's shared packages — by passing
# the library/include locations directly. Python bindings are ctypes (no SWIG).
%cmake -GNinja \
    -DCMAKE_BUILD_TYPE=Release \
    -DWITH_SBML=ON \
    -DWITH_STATIC_SBML=OFF \
    -DWITH_COMP_SBML=ON \
    -DWITH_CELLML=OFF \
    -DWITH_QTANTIMONY=OFF \
    -DWITH_LIBSBML_COMPRESSION=OFF \
    -DWITH_CHECK=OFF \
    -DWITH_PYTHON=ON \
    -DWITH_SWIG=OFF \
    -DPYTHON_LOCAL_INSTALL=ON \
    -DPYTHON_SYSTEM_INSTALL=OFF \
    -DLIBSBML_LIBRARY=%{_libdir}/libsbml.so \
    -DLIBSBML_INCLUDE_DIR=%{_includedir} \
    -DEXPAT_LIBRARY=%{_libdir}/libexpat.so \
    -DEXPAT_INCLUDE_DIR=%{_includedir} \
    -DANT_DEPENDENCIES_INSTALL_PREFIX=%{_prefix}
%cmake_build

%install
%cmake_install

# The ctypes Python package is installed under <prefix>/bindings/python/antimony
# (PYTHON_LOCAL_INSTALL). Relocate it to the real sitearch. antimony.py loads
# libantimony.so from its own directory, so the shared lib travels with it.
install -d %{buildroot}%{python3_sitearch}
mv %{buildroot}%{_prefix}/bindings/python/antimony %{buildroot}%{python3_sitearch}/antimony
rm -rf %{buildroot}%{_prefix}/bindings
# Drop the bits we don't ship in the python dir (license/readme/pth handled by RPM).
rm -f %{buildroot}%{python3_sitearch}/antimony/libantimony.pth \
      %{buildroot}%{python3_sitearch}/antimony/LICENSE.txt \
      %{buildroot}%{python3_sitearch}/antimony/NEWS.txt \
      %{buildroot}%{python3_sitearch}/antimony/README.md 2>/dev/null || :

# The CLI tools statically link libantimony-static; the standalone shared lib and
# static archive + headers are not shipped (no -devel consumer yet). Antimony's
# CMake installs these under %%{_prefix}/lib (not %%{_libdir}).
rm -f %{buildroot}%{_prefix}/lib/libantimony.so* %{buildroot}%{_prefix}/lib/libantimony-static.a
rm -rf %{buildroot}%{_includedir}/antimony* %{buildroot}%{_includedir}/*.h
# Drop the test driver and the rehash utility (not user-facing translators).
rm -f %{buildroot}%{_bindir}/testantimony %{buildroot}%{_bindir}/rehashantimony

# Strip RPATHs.
chrpath --delete %{buildroot}%{_bindir}/* 2>/dev/null || :
chrpath --delete %{buildroot}%{python3_sitearch}/antimony/libantimony.so 2>/dev/null || :

%files
%license LICENSE.txt
%doc README.md
%{_bindir}/sbml2antimony
%{_bindir}/antimony2sbml
%{_bindir}/sbtranslate

%files -n python3-antimony
%license LICENSE.txt
%{python3_sitearch}/antimony/

%changelog
* Fri Jun 19 2026 Morgan Hough <morgan.hough@gmail.com> - 3.1.3-1
- Initial package: Antimony 3.1.3, system libSBML + libSBMLNetwork (no superbuild).
- ctypes Python bindings + CLI translators; CellML/Qt-GUI/compression disabled.
