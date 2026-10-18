import json

from common import client, runs_file

runs = json.loads(runs_file.read_text())

for run in runs:
    client.beta.sessions.delete(run["session"])
    print(f"deleted session      {run['session']}")

for environment_id in sorted({run["environment"] for run in runs}):
    client.beta.environments.delete(environment_id)
    print(f"deleted environment  {environment_id}")

runs_file.unlink()
print(f"removed      {runs_file.name}")
