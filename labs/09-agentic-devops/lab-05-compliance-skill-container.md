# Build a Compliance Skill and Audit Your Site

Research three sources each for accessibility, the DSGVO and the EU AI Act, build a compliance skill of your own from those nine links, and use it to audit and fix the Hugo blog you deployed in Lab 03.

The repository ships a `compliance` skill: a short router plus one reference file per regulation, each written from sources someone checked. A skill like that is only as good as its sources. Regulations change, summaries go stale, and a checklist copied from a vendor's blog carries the vendor's agenda. In this lab you pick the sources yourself, three per topic, and every check in your skill points back to one of them.

This lab is optional. The [Azure lab VM edition](lab-05-compliance-skill-vm.md) teaches the same steps on a VM your instructor provides.

Each step follows the same pattern:

- **Overview**: what this step achieves
- **Research / Planning / Discussion**: an open prompt to reason through the problem before acting
- **Finding**: what to read and evaluate in Claude's response before moving on
- **Recipe**: a complete implementation prompt you can use as-is or adapt from your own findings
- **Expected Outcome**: observable artefacts that confirm success

## Prerequisites

- Lab 01 completed through Step 4, with the box from [lab-01-deploy-to-an-ubuntu-box-container.md](lab-01-deploy-to-an-ubuntu-box-container.md) still in place and the key at `react-devops/deploy/target-box/keys/box_key`.
- Lab 03 completed, or at least read: this lab works in the same starter at [my-blog/](my-blog), which already carries the three posts Claude wrote there and the containerized `dockerfile`. Lab 03's Cleanup removed its containers, so the starter section below deploys the blog again.
- Docker Desktop or Docker Engine, running before you start.
- A shell: Bash (git-bash or WSL on Windows, any shell on macOS and Linux) or PowerShell 7. Every command block that differs between the two ships a `powershell` twin below the `bash` one, with the substitutions Lab 03 introduced: `UserKnownHostsFile=NUL` for `/dev/null`, `curl.exe` for `curl`, and a staged tar file for `docker save | ssh`.
- Web access for Claude Code: Steps 1 to 3 use its WebSearch and WebFetch tools. Approve each domain when Claude asks to fetch it.

---

## Running the Lab Starter

From the repository root, change into the blog starter, bring the box up, build the blog as it stands and run it on the box under the name and port Lab 03 used:

**Bash:**

```bash
cd labs/09-agentic-devops/my-blog
docker compose -f ../react-devops/deploy/target-box/docker-compose.yml up -d
export DEPLOY='ssh -p 2222 -i ../react-devops/deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost'
docker build -f dockerfile -t my-blog:compliance-0 .
docker save my-blog:compliance-0 | gzip -1 | $DEPLOY 'docker load'
$DEPLOY 'docker rm -f my-blog my-blog-v2; docker run -d --name my-blog --restart unless-stopped -p 8083:80 my-blog:compliance-0'
```

**PowerShell:**

```powershell
cd labs/09-agentic-devops/my-blog
docker compose -f ../react-devops/deploy/target-box/docker-compose.yml up -d
$SshOpts = @('-i','../react-devops/deploy/target-box/keys/box_key','-o','IdentitiesOnly=yes','-o','UserKnownHostsFile=NUL','-o','StrictHostKeyChecking=no')
function Deploy { ssh -p 2222 @SshOpts deploy@localhost @args }
docker build -f dockerfile -t my-blog:compliance-0 .
docker save my-blog:compliance-0 -o my-blog-compliance-0.tar
scp -P 2222 @SshOpts my-blog-compliance-0.tar deploy@localhost:/tmp/
Deploy 'docker load -i /tmp/my-blog-compliance-0.tar && rm /tmp/my-blog-compliance-0.tar'
Deploy 'docker rm -f my-blog my-blog-v2; docker run -d --name my-blog --restart unless-stopped -p 8083:80 my-blog:compliance-0'
```

Open the tunnel in a second terminal, from the same folder, and leave it running:

**Bash:**

```bash
ssh -p 2222 -i ../react-devops/deploy/target-box/keys/box_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no -N -L 8083:localhost:8083 deploy@localhost
```

**PowerShell:**

```powershell
ssh -p 2222 -i ../react-devops/deploy/target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no -N -L 8083:localhost:8083 deploy@localhost
```

Back in the first terminal, check the served blog and start Claude Code in the starter:

**Bash:**

```bash
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8083/
curl -s http://localhost:8083/ | grep -o '<title>[^<]*</title>' | head -1
claude
```

**PowerShell:**

```powershell
curl.exe -s -o NUL -w '%{http_code}\n' http://localhost:8083/
curl.exe -s http://localhost:8083/ | Select-String -CaseSensitive -AllMatches '<title>[^<]*</title>' | ForEach-Object { $_.Matches.Value } | Select-Object -First 1
claude
```

A successful start prints `200` and `<title>My New Hugo Project</title>`, and Claude Code opens in `my-blog`, where `.claude/skills/` loads from.

---

## Step 1: Find three sources for accessibility

**Overview:** Collect three links that decide what accessible means for a public website in the EU. The skill you build in Step 4 may only contain checks these links support, so their quality sets the quality of every later finding.

**Research / Planning / Discussion:**

```text
I run a small Hugo blog, served as static files and readable by anyone in the
EU. Search the web for what makes a website accessible in a legally relevant
sense in the EU and in my country. Which laws or directives apply, which
technical standard do they point to, and does a private blog fall inside their
scope? List the sources you found and say for each one who published it and
whether it is a primary legal text, an official standard or guidance page, or a
third-party summary. Do not write any file.
```

**Finding:** A good answer keeps three layers apart: the law (the European Accessibility Act, Directive (EU) 2019/882, and for public bodies the Web Accessibility Directive 2016/2102), the harmonised standard EN 301 549, and WCAG 2.1 level AA, which that standard points to. It should say that a private blog likely sits outside the services the EAA lists, and still name WCAG 2.1 AA as the baseline worth checking against. Push back when the list leans on vendors of accessibility overlays, cites a page without a date, or states a deadline without a source behind it.

**Recipe:**

```text
Search the web and choose exactly three links on web accessibility for a
website in the EU: one primary legal text, one technical standard, and one
official guidance or checklist page. Open each with WebFetch and keep it only
if it answers with the content you expect.

Create .claude/skills/site-compliance/sources.md with the heading
"# Sources" and a section "## Accessibility" holding one bullet per link in
this form:
- [<page title>](<url>): <publisher>, <what it decides for a static blog, one sentence>, checked <today's date>
```

**Expected Outcome:** `.claude/skills/site-compliance/sources.md` exists with an Accessibility section of three bullets, each naming its publisher and today's date:

**Bash:**

```bash
grep -A3 '^## Accessibility' .claude/skills/site-compliance/sources.md
```

**PowerShell:**

```powershell
Select-String -Path .claude/skills/site-compliance/sources.md -Pattern '^## Accessibility' -Context 0,3
```

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 2: Find three sources for the DSGVO

**Overview:** Collect three links on what the DSGVO (GDPR) asks of a static site with no forms and no login. Even a site like that processes personal data, so the question is which data and what the reader has to be told.

**Research / Planning / Discussion:**

```text
The same Hugo blog is served from a container in the EU. It has no forms, no
login and no comments. Search the web for what the DSGVO (GDPR) requires from a
site like this. Which personal data does a static blog process without any
form, what must its privacy notice contain, and which court decisions or
regulator statements deal with a website loading resources from third-party
hosts, such as web fonts or CDNs? Name the publisher of every source and say
whether it is primary law, regulator guidance or commentary. Do not write any
file.
```

**Finding:** A good answer names the IP address as personal data: the web server logs it, and so does every third-party host the page loads from. It points to the information duties of Article 13 for the privacy notice and cites Regulation (EU) 2016/679 itself, a data protection authority or the EDPB for guidance, and the Munich Regional Court's Google Fonts judgment of January 2022 as the case that turned remotely loaded fonts into a DSGVO question. Push back when it recommends a cookie banner for a site whose cookies it has not checked, or when its main source is a consent-management vendor.

**Recipe:**

```text
Search the web and choose exactly three links on the DSGVO (GDPR) for a static
website without forms: one primary legal text, one page from a data protection
authority or the EDPB, and one court decision or authority statement about a
website loading resources from third-party hosts. Open each with WebFetch and
keep it only if it answers with the content you expect.

Append a section "## DSGVO" to .claude/skills/site-compliance/sources.md with
one bullet per link in this form:
- [<page title>](<url>): <publisher>, <what it decides for a static blog, one sentence>, checked <today's date>
```

**Expected Outcome:** `sources.md` holds a DSGVO section of three bullets below the Accessibility section:

**Bash:**

```bash
grep -A3 '^## DSGVO' .claude/skills/site-compliance/sources.md
```

**PowerShell:**

```powershell
Select-String -Path .claude/skills/site-compliance/sources.md -Pattern '^## DSGVO' -Context 0,3
```

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 3: Find three sources for the EU AI Act

**Overview:** Collect three links on what the EU AI Act says about publishing AI-generated text. Every post on this blog came out of a Claude Code prompt in Lab 03, so the blog is a real case for the regulation.

**Research / Planning / Discussion:**

```text
The posts on this blog were written by Claude Code and published as they came
out. Search the web for what the EU AI Act says about publishing AI-generated
text on a website. Which article applies, who carries the duty (provider or
deployer), from which date, and which exceptions exist? Name the publisher of
every source and say whether it is the regulation, official Commission guidance
or commentary. Do not write any file.
```

**Finding:** A good answer cites Regulation (EU) 2024/1689 and its Article 50, places the blog owner as the deployer, and quotes the paragraph on text published to inform the public on matters of public interest. It names the exception for text that went through human review or editorial control with a person holding editorial responsibility, and gives the date the transparency duties apply from (2 August 2026) together with its source. Push back when it classifies the blog as high-risk, or quotes a date from a summary page without linking the article itself.

**Recipe:**

```text
Search the web and choose exactly three links on the EU AI Act and AI-generated
text on a website: the regulation text, Article 50 on its own page, and one
official page of the European Commission about the transparency duties for
AI-generated content. Open each with WebFetch and keep it only if it answers
with the content you expect.

Append a section "## EU AI Act" to .claude/skills/site-compliance/sources.md
with one bullet per link in this form:
- [<page title>](<url>): <publisher>, <what it decides for a blog with AI-written posts, one sentence>, checked <today's date>
```

**Expected Outcome:** `sources.md` holds nine links in three sections. Check that every link answers:

**Bash:**

```bash
grep -c '^- \[' .claude/skills/site-compliance/sources.md
grep -o 'https://[^)]*' .claude/skills/site-compliance/sources.md | while read -r u; do echo "$(curl -s -o /dev/null -L -m 20 -w '%{http_code}' "$u") $u"; done
```

**PowerShell:**

```powershell
(Select-String -Path .claude/skills/site-compliance/sources.md -Pattern '^- \[').Count
Select-String -Path .claude/skills/site-compliance/sources.md -Pattern 'https://[^)]*' -AllMatches | ForEach-Object { $_.Matches.Value } | ForEach-Object { "$(curl.exe -s -o NUL -L -m 20 -w '%{http_code}' $_) $_" }
```

The count is `9`, and most links answer `200`. EUR-Lex answers a script with `202` because of its bot check; open those links in your browser once to see the page.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 4: Build the skill from the nine links

**Overview:** Turn the nine links into a project skill with the same shape as the repository's `compliance` skill: a router that names its leaves, one reference file per topic, and conventions every leaf follows. The leaves carry checks you can run against a built Hugo site, each one citing its source.

**Research / Planning / Discussion:**

```text
Read ../../../.claude/skills/compliance/SKILL.md and list its references/
folder. Explain how it is organised: what the frontmatter description does,
how the router decides which reference file to read, and which conventions
apply to every leaf. Then read .claude/skills/site-compliance/sources.md and
propose the layout of a smaller skill of the same shape, built only from those
nine links and aimed at auditing a static Hugo site. Do not write any file.
```

**Finding:** A good answer explains the router pattern: the description carries the trigger phrases that make Claude load the skill, the body routes to one leaf per regulation, and shared conventions such as "not legal advice" and "re-check the sources" apply to all of them. The proposal should have one leaf per topic, each a checklist of things you can test in the served HTML, the theme templates, `hugo.toml` or the post front matter, with a source link on every check. Push back when a proposed check has no source among your nine links, or when Claude copies wording from the repository's `compliance` skill into your leaves.

**Recipe:**

```text
Build a project skill at .claude/skills/site-compliance/ from the nine links in
.claude/skills/site-compliance/sources.md. Use the layout of
../../../.claude/skills/compliance/ as the model and write the content only
from those nine links.

1. SKILL.md with frontmatter name: site-compliance and a description that
   lists trigger phrases (compliance audit, accessibility check, DSGVO check,
   AI disclosure check). The body routes to three leaves and states two rules
   for every leaf: the result is engineering orientation and no legal advice,
   and every finding cites the source link it rests on.
2. references/accessibility.md, references/dsgvo.md and
   references/eu-ai-act.md. Each opens with what its sources require of a
   site like this one, followed by a numbered checklist. Every check says how
   to test it (the served HTML at http://localhost:8083/, the templates under
   themes/clarity/layouts, hugo.toml, or the post front matter) and ends with
   the source link it comes from.
3. An "Audit" section in SKILL.md: fetch the served pages, run every check of
   the leaves in scope, and write the report to
   .compliance/<YYYY-MM-DD>/audit-<hhmm>.md as a table with one row per
   finding: topic, check, evidence, source link, the file that owns the fix.

Use no source outside sources.md.
```

**Expected Outcome:** Five files under `.claude/skills/site-compliance/`, and every leaf cites links:

**Bash:**

```bash
find .claude/skills/site-compliance -type f | sort
grep -c 'https://' .claude/skills/site-compliance/references/*.md
```

**PowerShell:**

```powershell
Get-ChildItem -Recurse -File .claude/skills/site-compliance | Resolve-Path -Relative
Get-ChildItem .claude/skills/site-compliance/references/*.md | ForEach-Object { "$($_.Name): $((Select-String -Path $_ -Pattern 'https://').Count)" }
```

The list shows `SKILL.md`, `sources.md` and the three leaves under `references/`, and every leaf has a non-zero link count. Type `/site-compliance` in the session; when it does not autocomplete, run `/exit` and start `claude` again in `my-blog`.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 5: Audit the deployed blog

**Overview:** Run your skill against the blog as the box serves it. Scoping first keeps theme features that render nothing out of the findings.

**Research / Planning / Discussion:**

```text
Load the site-compliance skill. Before auditing, inspect the blog as it is
served at http://localhost:8083/ and as it is built from this folder: which
pages exist, which requests a page makes to hosts other than localhost, what
the theme stores in the browser, whether the posts say anything about how they
were written, and which templates under themes/clarity/layouts render the
page frame, the footer and the post metadata. Recommend which checks of the
three leaves apply to this site. Do not write any file.
```

**Finding:** A good answer reads the served bytes. The pages are the home page, the post list, three posts, tag and category pages and a 404 page, and `<html lang="en">` is set. Fonts, icons, CSS and JavaScript all come from `localhost:8083`, and the Twitter and Facebook share links are plain links that send nothing until a reader clicks them; the theme script keeps the colour-mode choice in `localStorage`. The page has no skip link, the inline SVG icons carry titles such as `to-top` and `open-menu` that become their accessible names, no page links to a privacy notice, and no post says it was written with AI.

Push back when Claude reports Google Analytics, Tag Manager or KaTeX as active: their partials exist under `themes/clarity/layouts`, and they render nothing because `hugo.toml` configures neither.

**Recipe:**

```text
Run an audit with the site-compliance skill against the blog served at
http://localhost:8083/: the home page, the post list and every post under
/posts/. Read the served HTML with curl, and read the templates under
themes/clarity/layouts and hugo.toml to name the file that owns each fix.
Report a theme partial as a finding only when its output appears in the served
HTML. Write the report as the skill's Audit section defines it and end it with
the top finding per topic.
```

**Expected Outcome:** A report at `.compliance/<today>/audit-<hhmm>.md` with findings grouped by topic, each citing a link from `sources.md`:

**Bash:**

```bash
ls .compliance/*/
grep -c 'https://' .compliance/*/audit-*.md
```

**PowerShell:**

```powershell
Get-ChildItem .compliance -Recurse -File | Resolve-Path -Relative
Get-ChildItem .compliance -Recurse -Filter 'audit-*.md' | ForEach-Object { "$($_.Name): $((Select-String -Path $_ -Pattern 'https://').Count)" }
```

Typical findings: for accessibility, the missing skip link and the slug-named icons; for the DSGVO, no privacy notice reachable from the pages, which also has to name the access logs nginx writes on the box with readers' IP addresses; for the EU AI Act, three Claude-written posts with no disclosure and no named editor.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 6: Fix one finding per topic and redeploy

**Overview:** Fix the top finding of each topic in the file that owns it, rebuild the image under a new tag and replace the running container. Hugo looks up a template in the site's own `layouts/` folder before the theme's, so an override there changes the page and leaves the vendored theme untouched.

**Research / Planning / Discussion:**

```text
Read the latest report under .compliance/. For the top finding of each topic,
name the file that owns the fix (content, hugo.toml, or a template), whether
the fix belongs in an override under layouts/ or in content, the exact change,
and the curl command that will prove it on http://localhost:8083/ after the
redeploy. Explain how Hugo's template lookup order lets a file under layouts/
replace one under themes/clarity/layouts. Do not change any file.
```

**Finding:** A good plan has three rows. The skip link needs an override of `layouts/_default/baseof.html`, because Clarity offers hooks only at the end of the head and the end of the body. The privacy notice is a new page under `content/` plus a link from an override of `layouts/partials/footer.html`. The AI disclosure is a front matter flag on the posts and a line rendered from an override of `layouts/partials/post-meta.html`.

Push back when Claude edits anything under `themes/clarity/`, proposes a cookie banner, or names a fix it cannot prove with a request to the served site.

**Recipe:**

```text
Apply these three fixes. Never edit a file under themes/clarity/.

1. Accessibility: copy themes/clarity/layouts/_default/baseof.html to
   layouts/_default/baseof.html. Add <a class="skip-link"
   href="#main-content">Skip to content</a> as the first element inside
   <body> and id="main-content" on <main>. Create
   layouts/partials/hooks/head-end.html with a <style> block that keeps
   .skip-link off screen until it receives keyboard focus.
2. DSGVO: create content/privacy.md (title "Privacy Notice") written from the
   DSGVO links in .claude/skills/site-compliance/sources.md: who runs the site,
   that the web server logs IP addresses and for how long, that the site sets
   no cookies and loads nothing from third-party hosts, that the colour-mode
   choice stays in the reader's browser, and the reader's rights. Copy
   themes/clarity/layouts/partials/footer.html to layouts/partials/footer.html
   and add a link to {{ "privacy/" | absURL }} labelled "Privacy".
3. EU AI Act: add ai_generated = true to the front matter of every post under
   content/posts/. Copy themes/clarity/layouts/partials/post-meta.html to
   layouts/partials/post-meta.html and, when .Params.ai_generated is true,
   render the line "This post was written with Claude Code and reviewed by
   <your name> before publishing."

Then rebuild and redeploy with SSH as the only channel to the box (port 2222,
user deploy, key ../react-devops/deploy/target-box/keys/box_key, options
IdentitiesOnly=yes, StrictHostKeyChecking=no and UserKnownHostsFile pointing at
the null device of your shell):
1. docker build -f dockerfile -t my-blog:compliance-1 .
2. docker save my-blog:compliance-1 -o my-blog-compliance-1.tar, copy it to
   /tmp/ on the box with scp, and run docker load -i on the box.
3. On the box: docker rm -f my-blog && docker run -d --name my-blog
   --restart unless-stopped -p 8083:80 my-blog:compliance-1
4. Delete my-blog-compliance-1.tar locally and on the box.

Report what you changed and which tag the running container uses.
```

Check the claims from your own shell, because Claude's summary is a claim:

**Bash:**

```bash
$DEPLOY 'docker inspect my-blog --format "{{.Config.Image}}"'
curl -s http://localhost:8083/ | grep -o 'href=#main-content[^<]*' | head -1
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8083/privacy/
curl -s http://localhost:8083/ | grep -o 'localhost:8083/privacy/' | head -1
curl -s http://localhost:8083/posts/getting-started-with-ai/ | grep -o 'written with Claude Code[^<]*'
git status --short themes
```

**PowerShell:**

```powershell
Deploy 'docker inspect my-blog --format "{{.Config.Image}}"'
curl.exe -s http://localhost:8083/ | Select-String -AllMatches 'href=#main-content[^<]*' | ForEach-Object { $_.Matches.Value } | Select-Object -First 1
curl.exe -s -o NUL -w '%{http_code}\n' http://localhost:8083/privacy/
curl.exe -s http://localhost:8083/ | Select-String -AllMatches 'localhost:8083/privacy/' | ForEach-Object { $_.Matches.Value } | Select-Object -First 1
curl.exe -s http://localhost:8083/posts/getting-started-with-ai/ | Select-String -AllMatches 'written with Claude Code[^<]*' | ForEach-Object { $_.Matches.Value }
git status --short themes
```

**Expected Outcome:** The running image is `my-blog:compliance-1`, and the home page starts its body with the skip link. `/privacy/` answers `200`, the footer links to it, and each post shows the disclosure line with your name. `git status --short themes` prints nothing. The minified HTML drops attribute quotes, which is why the patterns above carry none.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Step 7: Re-audit and prove each fix on the served site

**Overview:** Run the same audit again and compare it with the first report. A fix counts once the finding is gone from the second report and a request to the served site shows the change.

**Research / Planning / Discussion:**

```text
Compare the two newest reports under .compliance/ without running anything
new. Which findings would you expect to close after the three fixes, which
should stay open, and which evidence in the served HTML would prove each
closure? Do not write any file.
```

**Finding:** A good answer expects the three top findings to close and the rest of the first report to stay open, for example the slug-named icons, which no fix touched. It names one piece of served evidence per closed finding. Push back when it closes a finding on the strength of a changed file alone.

**Recipe:**

```text
Run a second audit with the site-compliance skill against
http://localhost:8083/ with the same scope as the first, writing a new
report. Then compare it with the first report and append a table to the new
report with one row per fix: topic, finding, the file that owns the fix, the
source link from sources.md, and the curl evidence from the served site.
```

**Expected Outcome:** A second `audit-<hhmm>.md` under `.compliance/`, whose comparison table has three rows, one per topic, each with its source link and curl evidence. The findings you did not fix remain listed and form the backlog for your next pass with the skill.

> The recipe above is one possible prompt based on typical findings from the research above. If your conversation led to different conclusions, use those instead.

---

## Cleanup

Copy the skill to your user skills first if you want to use it in other projects, then remove what this lab added and stop the container:

**Bash:**

```bash
cp -r .claude/skills/site-compliance ~/.claude/skills/
$DEPLOY 'docker rm -f my-blog'
docker image rm my-blog:compliance-0 my-blog:compliance-1
rm -rf .claude/skills/site-compliance .compliance layouts content/privacy.md
git checkout -- content/posts
git status --short
```

**PowerShell:**

```powershell
Copy-Item -Recurse .claude/skills/site-compliance $HOME/.claude/skills/
Deploy 'docker rm -f my-blog'
docker image rm my-blog:compliance-0 my-blog:compliance-1
Remove-Item -Recurse -Force .claude/skills/site-compliance, .compliance, layouts, content/privacy.md, my-blog-compliance-0.tar
git checkout -- content/posts
git status --short
```

`git status --short` prints nothing inside `my-blog`. Stop the tunnel with `Ctrl+C` in its terminal. The box itself stays: it is shared with the other labs of this module.

---

## What You Just Practised

| Mechanic | Step | Use it for |
| --- | --- | --- |
| Choosing sources by type: law, standard or guidance, case or authority | 1 to 3 | Skills whose rules trace back to text you can check |
| A sources file with publisher and check date per link | 1 to 3 | Re-checking a live regulation before you rely on a skill |
| A router skill with one leaf per regulation | 4 | Skills that load only the part a task needs |
| Scoping an audit from the served bytes | 5 | Keeping inactive theme features out of the findings |
| Template overrides under `layouts/` | 6 | Fixing a vendored theme without editing it |
| A new image tag and `curl` against the served site | 6, 7 | Proving a compliance fix reached readers |
