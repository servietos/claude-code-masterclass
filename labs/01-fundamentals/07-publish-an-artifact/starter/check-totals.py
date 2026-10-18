import csv
import sys
from collections import defaultdict

count = defaultdict(int)
minutes = defaultdict(int)
path = sys.argv[1] if len(sys.argv) > 1 else "ci-failures.csv"
for row in csv.DictReader(open(path, newline="")):
    count[row["service"]] += 1
    minutes[row["service"]] += int(row["duration_min"])
for service in sorted(count, key=lambda s: -minutes[s]):
    print(f"{service:18} {count[service]:3} failures {minutes[service]:4} min")
print(f"{'total':18} {sum(count.values()):3} failures {sum(minutes.values()):4} min")
