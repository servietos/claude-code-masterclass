import subprocess
import json
import time

REPO = "alexander-kastil/masterclass-claude-code"
PROJECT_NUM = 24
PROJECT_ID = "PVT_kwHOAPlzd84BXrlQ"
FIELD_ID = "PVTSSF_lAHOAPlzd84BXrlQzhS2z9w"
STATUS_IDS = {"planned": "03b7c51f", "doing": "9301fa23", "done": "1593b600"}

MODULES = [
    {"num": "01", "name": "Fundamentals",    "theory": "done",    "demos": "done",    "labs": "done",    "slides": "planned"},
    {"num": "02", "name": "Harness",         "theory": "done",    "demos": "done",    "labs": "done",    "slides": "planned"},
    {"num": "03", "name": "MCP",             "theory": "done",    "demos": "done",    "labs": "done",    "slides": "planned"},
    {"num": "04", "name": "Skills",          "theory": "done",    "demos": "done",    "labs": "doing",   "slides": "planned"},
    {"num": "05", "name": "Planning",        "theory": "planned", "demos": "planned", "labs": "done",    "slides": "planned"},
    {"num": "06", "name": "Optimize",        "theory": "planned", "demos": "planned", "labs": "done",    "slides": "planned"},
    {"num": "07", "name": "Subagents",       "theory": "done",    "demos": "done",    "labs": "done",    "slides": "planned"},
    {"num": "08", "name": "CLI",             "theory": "planned", "demos": "planned", "labs": "done",    "slides": "planned"},
    {"num": "09", "name": "Managed Agents",  "theory": "planned", "demos": "planned", "labs": "doing",   "slides": "planned"},
    {"num": "10", "name": "Observability",   "theory": "planned", "demos": "planned", "labs": "doing",   "slides": "planned"},
    {"num": "11", "name": "Distribution",    "theory": "planned", "demos": "planned", "labs": "done",    "slides": "planned"},
    {"num": "12", "name": "Claude SDK",      "theory": "planned", "demos": "planned", "labs": "done",    "slides": "planned"},
    {"num": "13", "name": "Agentic DevOps",  "theory": "doing",   "demos": "doing",   "labs": "done",    "slides": "planned"},
]

def gh(*args):
    result = subprocess.run(["gh"] + list(args), capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"gh {' '.join(args)} failed: {result.stderr}")
    return result.stdout.strip()

def module_overall_status(m):
    states = [m["theory"], m["demos"], m["labs"], m["slides"]]
    if all(s == "done" for s in states):
        return "done"
    if all(s == "planned" for s in states):
        return "planned"
    return "doing"

def create_issue(title, body=""):
    url = gh("issue", "create", "--repo", REPO, "--title", title, "--body", body)
    number = url.rstrip("/").split("/")[-1]
    return int(number), url

def close_issue(number):
    gh("issue", "close", str(number), "--repo", REPO)

def get_integer_id(number):
    return int(gh("api", f"repos/{REPO}/issues/{number}", "--jq", ".id"))

def link_sub_issue(parent_number, sub_integer_id):
    gh("api", "--method", "POST", f"repos/{REPO}/issues/{parent_number}/sub_issues",
       "-F", f"sub_issue_id={sub_integer_id}")

def add_to_project(issue_url):
    out = gh("project", "item-add", str(PROJECT_NUM), "--owner", "alexander-kastil",
             "--url", issue_url, "--format", "json")
    return json.loads(out)["id"]

def set_status(item_id, status):
    option_id = STATUS_IDS[status]
    query = f"""mutation {{
  updateProjectV2ItemFieldValue(input: {{
    projectId: "{PROJECT_ID}"
    itemId: "{item_id}"
    fieldId: "{FIELD_ID}"
    value: {{ singleSelectOptionId: "{option_id}" }}
  }}) {{ projectV2Item {{ id }} }}
}}"""
    gh("api", "graphql", "-f", f"query={query}")

print("=== Rebuilding GitHub project ===\n")

for m in MODULES:
    num = m["num"]
    name = m["name"]
    overall = module_overall_status(m)

    print(f"Module {num} - {name} (overall: {overall})")

    # Create parent issue
    parent_title = f"Module {num} - {name}"
    parent_num, parent_url = create_issue(parent_title)
    print(f"  Parent #{parent_num}")

    # Close parent if done
    if overall == "done":
        close_issue(parent_num)

    # Add parent to project and set status
    parent_item_id = add_to_project(parent_url)
    set_status(parent_item_id, overall)

    # Create sub-issues
    components = [
        ("Theory",      m["theory"]),
        ("Code Demos",  m["demos"]),
        ("Labs",        m["labs"]),
        ("Slides",      m["slides"]),
    ]

    for comp_name, comp_status in components:
        sub_title = f"[Module {num}] {comp_name}"
        sub_num, sub_url = create_issue(sub_title)
        print(f"    #{sub_num} {sub_title} ({comp_status})")

        if comp_status == "done":
            close_issue(sub_num)

        # Link to parent
        sub_int_id = get_integer_id(sub_num)
        link_sub_issue(parent_num, sub_int_id)

        # Add to project and set status
        sub_item_id = add_to_project(sub_url)
        set_status(sub_item_id, comp_status)

        time.sleep(0.3)

    print()

print("=== Done ===")
