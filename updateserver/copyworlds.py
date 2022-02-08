import json
import platform
import subprocess

with open("worlds.json") as f:
    data = json.loads(f.read())
for i in data['worlds']:
    val = str(i)
    print("copying worldregions to %s" % val)
    if platform.system() == "Windows":
        cmd = str('copy "world/region" "%s/region"' % val)
        print(cmd)
        subprocess.run(cmd, shell=True)
    elif platform.system() == "Linux":
        subprocess.run("cp -r 'world/region' '%s/'" % val, shell=True)
