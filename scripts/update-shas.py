"""Pin each git-subdir plugin to the latest upstream commit that touched its path."""
import json, subprocess, tempfile

PATH = ".claude-plugin/marketplace.json"
m = json.load(open(PATH))
clones = {}

def git(*args):
    return subprocess.run(["git", *args], check=True, capture_output=True, text=True).stdout.strip()

for p in m["plugins"]:
    s = p["source"]
    if not isinstance(s, dict) or s.get("source") != "git-subdir":
        continue
    if s["url"] not in clones:
        d = tempfile.mkdtemp()
        git("clone", "-q", "--filter=blob:none", "--no-checkout", s["url"], d)
        clones[s["url"]] = d
    sha = git("-C", clones[s["url"]], "log", "-1", "--format=%H", "--", s["path"])
    if s.get("sha") != sha:
        print(f"{p['name']}: {s.get('sha')} -> {sha}")
        s["sha"] = sha

with open(PATH, "w") as f:
    json.dump(m, f, indent=2)
    f.write("\n")
