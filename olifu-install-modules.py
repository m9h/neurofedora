import sys, os, re, shutil
srcroot, buildroot, slicer_inst = sys.argv[1], sys.argv[2], sys.argv[3]
SMREL = "lib/Slicer-5.11/qt-scripted-modules"
destroot = os.path.join(buildroot + slicer_inst, SMREL)
fileslist = sys.argv[4]
# Directories that already belong to the 3dslicer package (don't %dir-own them):
SHARED = {"", SMREL, SMREL+"/Resources", SMREL+"/Resources/UI", SMREL+"/Resources/Icons"}

def parse_list(text, var, mn):
    m = re.search(r'set\(\s*'+var+r'\b(.*?)\)', text, re.S)
    if not m: return []
    out=[]
    for ln in m.group(1).splitlines():
        ln=ln.split('#',1)[0].strip()
        if ln: out.append(ln.replace('${MODULE_NAME}', mn))
    return out

owned_dirs=set(); files=[]
for mod in sorted(os.listdir(srcroot)):
    cml=os.path.join(srcroot,mod,'CMakeLists.txt')
    if not os.path.isfile(cml): continue
    t=open(cml).read()
    if 'slicerMacroBuildScriptedModule' not in t: continue
    mn=re.search(r'set\(\s*MODULE_NAME\s+(\S+?)\s*\)',t)
    mn=mn.group(1) if mn else mod
    for rel in parse_list(t,'MODULE_PYTHON_SCRIPTS',mn)+parse_list(t,'MODULE_PYTHON_RESOURCES',mn):
        src=os.path.join(srcroot,mod,rel); dst=os.path.join(destroot,rel)
        if not os.path.isfile(src): print("MISSING",mod,rel); sys.exit(3)
        os.makedirs(os.path.dirname(dst),exist_ok=True); shutil.copy2(src,dst)
        files.append(rel)
        d=os.path.dirname(rel)
        while d and (SMREL+"/"+d) not in SHARED:
            owned_dirs.add(SMREL+"/"+d); d=os.path.dirname(d)

with open(fileslist,'w') as fh:
    for d in sorted(owned_dirs): fh.write("%%dir %s/%s\n"%(slicer_inst,d))
    for f in sorted(files): fh.write("%s/%s/%s\n"%(slicer_inst,SMREL,f))
print("installed %d files, own %d dirs"%(len(files),len(owned_dirs)))
