"""Build NameSwipe name lists from SSA national data (names.zip).

Input : names.zip from https://www.ssa.gov/oact/babynames/names.zip
        (yobYYYY.txt files: name,sex,count; sorted by sex, count desc, name asc)
Output: ssa_yearly/boys_YYYY.csv, ssa_yearly/girls_YYYY.csv  (rank,name,count; top 1000)
        Boy Names.csv, Girl Names.csv (unique names + summary stats)
        names.json (for the app)
Usage : python3 build_names.py <folder containing names.zip> [first_year] [last_year]
"""
import csv, io, json, os, sys, zipfile

folder = sys.argv[1]
Y0 = int(sys.argv[2]) if len(sys.argv) > 2 else 1890
Y1 = int(sys.argv[3]) if len(sys.argv) > 3 else 2025
TOP = 1000

zf = zipfile.ZipFile(os.path.join(folder, "names.zip"))
available = sorted(int(n[3:7]) for n in zf.namelist() if n.startswith("yob") and n.endswith(".txt"))
missing = [y for y in range(Y0, Y1 + 1) if y not in available]
if missing:
    print("MISSING YEARS:", missing)

out_dir = os.path.join(folder, "ssa_yearly")
os.makedirs(out_dir, exist_ok=True)
stats = {"M": {}, "F": {}}
short = []

for y in range(Y0, Y1 + 1):
    if y in missing:
        continue
    rows = {"M": [], "F": []}
    with zf.open(f"yob{y}.txt") as fh:
        for line in io.TextIOWrapper(fh, encoding="utf-8"):
            line = line.strip()
            if not line:
                continue
            name, sex, count = line.split(",")
            rows[sex].append((name, int(count)))
    for sex, label in (("M", "boys"), ("F", "girls")):
        ranked = sorted(rows[sex], key=lambda r: (-r[1], r[0]))[:TOP]
        if len(ranked) < TOP:
            short.append((y, label, len(ranked)))
        with open(os.path.join(out_dir, f"{label}_{y}.csv"), "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["rank", "name", "count"])
            for i, (name, count) in enumerate(ranked, 1):
                w.writerow([i, name, count])
                s = stats[sex].setdefault(name, {"first": y, "last": y, "years": 0, "best": 10**9, "best_year": y})
                s["first"] = min(s["first"], y)
                s["last"] = max(s["last"], y)
                s["years"] += 1
                if i < s["best"]:
                    s["best"], s["best_year"] = i, y

app = {}
for sex, fname, key in (("M", "Boy Names.csv", "boy"), ("F", "Girl Names.csv", "girl")):
    names = sorted(stats[sex], key=str.lower)
    with open(os.path.join(folder, fname), "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["name", "first_year_top1000", "last_year_top1000", "years_in_top1000", "best_rank", "best_rank_year"])
        for n in names:
            s = stats[sex][n]
            w.writerow([n, s["first"], s["last"], s["years"], s["best"], s["best_year"]])
    app[key] = names
    print(f"{fname}: {len(names)} unique names")

with open(os.environ.get("APP_JSON", "names.json"), "w") as f:
    json.dump(app, f, separators=(",", ":"))
print("years in zip:", available[0], "-", available[-1])
print("yearly files written:", len(os.listdir(out_dir)))
if short:
    print("years with fewer than 1000 names:", short)
