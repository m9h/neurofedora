#!/usr/bin/env bash
# CompuCell3D + network-solver chain smoke test (Fedora 44, mhough/neurofedora COPR).
# Run on the target machine after installing. GUI checks need a display (or xvfb).
set -uo pipefail
PASS=0; FAIL=0
ok()   { echo "  PASS: $1"; PASS=$((PASS+1)); }
bad()  { echo "  FAIL: $1"; FAIL=$((FAIL+1)); }
hdr()  { echo; echo "== $1 =="; }

hdr "1. packages installed"
for p in compucell3d python3-compucell3d cc3d-player5 cc3d-twedit5 \
         libroadrunner python3-roadrunner python3-cc3dext python3-simservice \
         antimony python3-antimony libsbmlnetwork; do
  if rpm -q "$p" >/dev/null 2>&1; then ok "$(rpm -q $p)"; else bad "$p not installed"; fi
done

hdr "2. CompuCell3D core imports"
python3 - <<'PY' && ok "import cc3d (+ MaBoSSCC3D/RoadRunner core)" || bad "cc3d core import"
import cc3d
from cc3d.core import MaBoSSCC3D       # the MaBoSS integration module
print("    cc3d", getattr(cc3d, "__version__", "?"))
PY

hdr "3. SBML / RoadRunner (continuous kinetics)"
python3 - <<'PY' && ok "roadrunner CVODE time-course" || bad "roadrunner simulate"
import roadrunner
sbml = """<?xml version="1.0" encoding="UTF-8"?>
<sbml xmlns="http://www.sbml.org/sbml/level3/version1/core" level="3" version="1">
 <model id="m"><listOfCompartments><compartment id="c" size="1" constant="true"/></listOfCompartments>
  <listOfSpecies>
   <species id="S1" compartment="c" initialConcentration="10" hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/>
   <species id="S2" compartment="c" initialConcentration="0"  hasOnlySubstanceUnits="false" boundaryCondition="false" constant="false"/>
  </listOfSpecies>
  <listOfParameters><parameter id="k" value="1" constant="true"/></listOfParameters>
  <listOfReactions><reaction id="r" reversible="false">
   <listOfReactants><speciesReference species="S1" stoichiometry="1" constant="true"/></listOfReactants>
   <listOfProducts><speciesReference species="S2" stoichiometry="1" constant="true"/></listOfProducts>
   <kineticLaw><math xmlns="http://www.w3.org/1998/Math/MathML"><apply><times/><ci>k</ci><ci>S1</ci></apply></math></kineticLaw>
  </reaction></listOfReactions></model></sbml>"""
rr = roadrunner.RoadRunner(sbml); rr.simulate(0, 5, 11)
assert abs((rr.S1 + rr.S2) - 10.0) < 1e-6, "mass not conserved"
print("    roadrunner %s: S1 10.0->%.3f conserved=%.3f" % (roadrunner.__version__, rr.S1, rr.S1+rr.S2))
PY

hdr "4. MaBoSS (Boolean networks, bundled via cc3dext)"
python3 - <<'PY' && ok "cc3dext.MaBoSSCC3DPy engine class" || bad "cc3dext MaBoSS import"
from cc3dext import MaBoSSCC3DPy
assert hasattr(MaBoSSCC3DPy, "CC3DMaBoSSEngine")
assert hasattr(MaBoSSCC3DPy, "CC3DMaBoSSEngineContainer")
print("    cc3dext OK:", MaBoSSCC3DPy.CC3DMaBoSSEngine)
PY

hdr "5. simservice (service mode)"
python3 -c "import simservice; print('    simservice', getattr(simservice,'__version__','?'))" \
  && ok "import simservice" || bad "import simservice"

hdr "6. Antimony <-> SBML authoring"
python3 - <<'PY' && ok "antimony round-trip" || bad "antimony round-trip"
import antimony as a
m = "model ex\n  S1 -> S2; k*S1;\n  k=0.1; S1=10; S2=0;\nend"
assert a.loadAntimonyString(m) >= 0
name = a.getModuleNames()[-1]
sbml = a.getSBMLString(name)
assert "<sbml" in sbml and "reaction" in sbml.lower()
assert a.loadSBMLString(sbml) >= 0
print("    antimony OK: module=%s, SBML %d bytes, round-trip clean" % (name, len(sbml)))
PY

hdr "7. CLI translators"
d=$(mktemp -d); ( cd "$d"
  printf 'model m; S1 -> S2; k*S1; k=0.1; S1=5; end\n' > in.txt
  # the CLI derives the output name from the input; try both arg forms
  antimony2sbml in.txt out.xml >/dev/null 2>&1 || antimony2sbml in.txt >/dev/null 2>&1
  grep -lq "<sbml" ./*.xml 2>/dev/null )
[ $? -eq 0 ] && ok "antimony2sbml CLI emits SBML" || bad "antimony2sbml CLI"
rm -rf "$d"

hdr "8. GUI launch (needs a display; auto-skips/xvfb)"
launch_gui() {
  timeout 25 cc3d-player5 --help >/dev/null 2>&1
  return $?
}
if [ -n "${DISPLAY:-}" ]; then
  launch_gui && ok "cc3d-player5 launches (DISPLAY=$DISPLAY)" || bad "cc3d-player5 launch"
elif command -v xvfb-run >/dev/null 2>&1; then
  QT_QPA_PLATFORM=xcb xvfb-run -a bash -c 'timeout 25 cc3d-player5 --help >/dev/null 2>&1' \
    && ok "cc3d-player5 launches (xvfb)" || bad "cc3d-player5 launch (xvfb)"
else
  echo "  SKIP: no \$DISPLAY and no xvfb-run (install xorg-x11-server-Xvfb to test headless)"
fi

echo
echo "==================================================="
echo "  RESULT: $PASS passed, $FAIL failed"
echo "  Interactive demos: run 'cc3d-demo' (copies demos to ~/cc3d-demos and opens Player),"
echo "  then open Demos/MaBoSS/MaBoSSCellCycle and Demos/.../angiogenesis."
echo "==================================================="
[ "$FAIL" -eq 0 ]
