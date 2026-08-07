# Bootstrap and Harden an Ubuntu Host over SSH

Driving a host bootstrap through Claude Code is an ordering problem: every step that closes a door has to be preceded by a proof taken from the host, because the agent's transcript is a claim and only the host is evidence. You bring up a throwaway Ubuntu box and work through access, a non-root deploy user, patching, unattended upgrades, Docker Engine with the Compose plugin, key-only SSH and a firewall, checking each one yourself. You end up holding a box in the exact state every later demo assumes.

------

Budget thirty minutes; Docker is the only thing you need installed.

The box is a container running `sshd` on your own machine, standing in for a VM. Nothing else changes: every command Claude runs against it is the command it would run against a hyperscaler VM, and moving to a real one means swapping `-p 2222 root@localhost` for `root@<public-ip>`.

## Setup

```bash
cd demos/11-agentic-devops/02-ssh-deployment/box-stack
claude
```

The starter ships the throwaway target under `target-box/` and the application stack the next demo uses. The finished result of both demos lives beside it in `box-stack-solution/` as the completed reference.

## Step 1: Bring up the throwaway target

The target has to trust a key before it will let anyone in, so you generate the keypair first and the image bakes the public half into `root`'s `authorized_keys` at build time. Baking it beats bind-mounting it: `sshd` refuses an `authorized_keys` file that is group-writable, and a bind mount from a Windows host arrives with exactly those permissions.

```bash
ssh-keygen -t ed25519 -f target-box/keys/box_key -N "" -C "box-demo"
docker compose -f target-box/docker-compose.yml up -d --build
docker compose -f target-box/docker-compose.yml ps
```

Expected output:

```text
NAME         IMAGE            COMMAND        SERVICE   CREATED         STATUS         PORTS
box-target   target-box-box   "/sbin/init"   box       12 seconds ago  Up 12 seconds  0.0.0.0:2222->22/tcp, [::]:2222->22/tcp, 0.0.0.0:8080->80/tcp, [::]:8080->80/tcp, 0.0.0.0:8443->443/tcp, [::]:8443->443/tcp
```

Expected result: one container named `box-target`, service name `box`, with three published mappings. `2222` reaches SSH, and `8080` and `8443` reach the box's own `80` and `443`, which the next demo needs. Each mapping appears twice because Docker publishes it for IPv4 and IPv6 separately.

The container runs an init system and is privileged, which is what lets `systemctl`, `ufw` and a nested Docker daemon behave the way they do on a VM. A real VM needs none of that; it is the price of standing a VM in on your laptop.

## Step 2: Prove SSH access before you build anything

The single biggest time sink in a deployment is wiring images, CI and DNS before confirming you can actually get in. Prove access first. `-o IdentitiesOnly=yes` is mandatory rather than cosmetic: without it `ssh` offers every default key in your agent first, the server cuts you off after `MaxAuthTries`, and a perfectly correct key reports `Permission denied`.

```bash
export BOX='ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
$BOX root@localhost 'whoami; . /etc/os-release && echo $PRETTY_NAME'
```

PowerShell cannot run a command it holds in a string, so define a function instead of a variable. `UserKnownHostsFile` becomes `NUL` here, because Win32-OpenSSH takes the Bash form literally and creates a file called `dev\null` in the current folder:

```powershell
function BOX { ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no @args }
BOX root@localhost 'whoami; . /etc/os-release && echo $PRETTY_NAME'
```

Every later `$BOX ...` line in this demo runs as `BOX ...` in PowerShell; only the leading `$` comes off.

Expected output:

```text
Warning: Permanently added '[localhost]:2222' (ED25519) to the list of known hosts.
root
Ubuntu 24.04.5 LTS
```

Expected result: you are root on Ubuntu, and the patch level after `24.04` is whatever the base image currently ships. The warning line arrives on every single connection in this demo, because `UserKnownHostsFile=/dev/null` throws the host key away as soon as it is written. Those two `KnownHosts` options are here only because this box is disposable and gets a new host key on every rebuild; never carry them over to a real host, where an unexpected host key is a warning you want. Keep this terminal, it is your control terminal for the rest of the demo.

Now hand the connection details to Claude in the session you opened in Setup:

```text
Our deployment target for this session is an Ubuntu 24.04 host reachable as:

  ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes \
      -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no root@localhost

Confirm you can reach it and report back exactly three things: the OS release,
whether Docker is installed, and the contents of /root/.ssh/authorized_keys
reduced to key fingerprints only, never the key material.

Do not change anything on the host yet.
```

Expected result: Claude reports Ubuntu 24.04, no Docker, and one `ed25519` fingerprint. Compare that fingerprint against `ssh-keygen -l -f target-box/keys/box_key.pub` yourself. Matching keys by fingerprint rather than filename is the habit that saves you later, because a key file's name routinely names a different registered key.

## Step 3: Create the non-root deploy user

Deployments should not run as root, and the deploy user needs the same key you already proved, so it inherits `root`'s `authorized_keys` rather than getting a new one. It gets no password and no `sudo`: everything it must do at deploy time is Docker, which comes from group membership in Step 5.

```text
Create a non-root deploy user on the box:

- user "deploy", no password login (--disabled-password), no sudo
- copy /root/.ssh/authorized_keys to /home/deploy/.ssh/authorized_keys
- ownership deploy:deploy, 700 on the .ssh directory, 600 on the file

Then tell me the exact commands you ran and what you verified.
```

Claude will report success. Check it against the host from your control terminal instead of believing the report:

```bash
$BOX root@localhost 'id deploy; stat -c "%a %U:%G %n" /home/deploy/.ssh /home/deploy/.ssh/authorized_keys'
```

Expected output:

```text
uid=1001(deploy) gid=1001(deploy) groups=1001(deploy),100(users)
700 deploy:deploy /home/deploy/.ssh
600 deploy:deploy /home/deploy/.ssh/authorized_keys
```

Expected result: the user exists with the right modes. Two details in that first line are worth reading rather than pattern-matching: the uid is `1001` because Ubuntu's 24.04 image already ships a `ubuntu` account at `1000`, and the extra `100(users)` group is `adduser`'s own default on Ubuntu. Neither affects the deploy, and neither is something to "fix".

A `755` on `.ssh` or a file still owned by `root` is the real failure to watch for, and it is the most common outcome of a hurried copy. `sshd` silently ignores such a file rather than telling you why the login failed. Do not test the `deploy` login yet; that is Step 6, and it matters that it happens there.

## Step 4: Patch the box and turn on unattended upgrades

Security patching is the part of hardening that has to keep working after everyone stops paying attention, which is what `unattended-upgrades` buys. `fail2ban` covers the other standing exposure, SSH brute force, by banning repeat offenders at the firewall.

```text
Bring the box up to date and put automatic security patching in place:

- apt-get update and upgrade
- install ufw, fail2ban, unattended-upgrades, ca-certificates, curl and gnupg
- enable unattended-upgrades non-interactively
- enable and start fail2ban

Do not touch the SSH configuration or the firewall yet. Report what each
package changed.
```

Two host checks, one per claim:

```bash
$BOX root@localhost 'cat /etc/apt/apt.conf.d/20auto-upgrades; fail2ban-client status sshd'
```

Expected output:

```text
APT::Periodic::Update-Package-Lists "1";
APT::Periodic::Unattended-Upgrade "1";
Status for the jail: sshd
|- Filter
|  |- Currently failed:	0
|  |- Total failed:	0
|  `- Journal matches:	_SYSTEMD_UNIT=sshd.service + _COMM=sshd
`- Actions
   |- Currently banned:	0
   |- Total banned:	0
   `- Banned IP list:
```

Expected result: both periodic keys are `"1"` and the `sshd` jail is live. `dpkg -l unattended-upgrades` proves only that a package is installed, which is why the check reads the config file that actually drives it. `fail2ban-client status` with no jail named would have told you the service is running; naming the jail is what proves it is watching SSH.

Read the `Journal matches` line rather than glossing over it. Ubuntu 24.04 ships `backend = systemd` in `/etc/fail2ban/jail.d/defaults-debian.conf`, so the jail tails the journal and never opens a log file; a walkthrough that expects `File list: /var/log/auth.log` there was written against a pre-24.04 box. If the command answers `Failed to access socket path`, run it again a second later: `fail2ban-client` can beat its own server to the socket right after the service starts.

## Step 5: Install Docker Engine and the Compose plugin

Docker goes in before SSH hardening, while you are still root-capable and can recover from a mistake with a second root login. Use the official Docker repository rather than the convenience script: the script is fine for a throwaway first bring-up, but a box that will be hardened and kept wants the repository, its signing key and its upgrade path.

```text
Install Docker Engine on the box from the official Docker apt repository, not
the get.docker.com script:

- add the Docker GPG key to /etc/apt/keyrings
- add the repository for this Ubuntu codename
- install docker-ce, docker-ce-cli, containerd.io, docker-buildx-plugin and
  docker-compose-plugin
- enable and start the docker service
- add the deploy user to the docker group

Do not install the standalone docker-compose binary. Report the versions of
the engine and the compose plugin.
```

```bash
$BOX root@localhost 'docker compose version; systemctl is-enabled docker; id -nG deploy'
```

Expected output:

```text
Docker Compose version v5.3.1
enabled
deploy users docker
```

Expected result: `docker compose` answers as a plugin subcommand, the service is enabled so it survives a reboot, and `deploy` is in the `docker` group next to the `users` group `adduser` gave it in Step 3. The version number will differ from the one above and has long since moved past `2.x`, which is exactly why the check reads the answer instead of matching a number. What must not differ is the shape: three answers, one per claim.

Group membership is granted at process start, so anything already running as `deploy` will not see the `docker` group until it is restarted, which is why this step comes before anything that runs as that user.

## Step 6: Prove the deploy key in a second session, then close the door

This is the step that locks people out of their own boxes. The moment you set `PasswordAuthentication no` and `PermitRootLogin no` is the moment a wrong key stops being an inconvenience and becomes a rebuild, so the proof has to come first and it has to come from a session you keep open.

Start by seeing the failure while it is still harmless. Make a key the box has never heard of and try it:

```bash
ssh-keygen -t ed25519 -f target-box/keys/decoy_key -N "" -C "wrong-key"
ssh -p 2222 -i target-box/keys/decoy_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost 'whoami'
```

PowerShell does not continue a line on a backslash, and Win32-OpenSSH creates a literal `dev\null` file from the Bash form, so use one line and `NUL`:

```powershell
ssh-keygen -t ed25519 -f target-box/keys/decoy_key -N '""' -C "wrong-key"
ssh -p 2222 -i target-box/keys/decoy_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no deploy@localhost 'whoami'
```

Expected output:

```text
Warning: Permanently added '[localhost]:2222' (ED25519) to the list of known hosts.
deploy@localhost: Permission denied (publickey).
```

Expected result: refused. Right now that costs you nothing, because root and password auth are still available behind it. Read the message carefully: it is identical whether the key is wrong, the `authorized_keys` permissions are wrong, or the user does not exist. After hardening, this exact message with no fallback path is what being locked out looks like, and nothing in it tells you which of the three went wrong.

So prove the real key now, in a **second terminal that you leave open** for the rest of the step:

```bash
cd demos/11-agentic-devops/02-ssh-deployment/box-stack
ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost
```

```powershell
cd demos/11-agentic-devops/02-ssh-deployment/box-stack
ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no deploy@localhost
```

Expected result: an interactive shell as `deploy`. Run `id` and `docker ps` in it to confirm the user and its Docker access, then leave the session sitting there. An already-open session survives an `sshd` restart, so it is your way back in if the next prompt gets the config wrong.

Only now hand the hardening to Claude:

```text
Harden SSH on the box. I have an open deploy session as a fallback.

In /etc/ssh/sshd_config set:
  PermitRootLogin no
  PasswordAuthentication no
  PubkeyAuthentication yes

Check /etc/ssh/sshd_config.d/ for any file that overrides those settings and
fix it there too. Validate with sshd -t before restarting, then restart ssh
and report the effective values from sshd -T, not from the file.
```

Verify the effective config yourself. Root SSH is closed now and `deploy` has no `sudo`, so the check runs out of band through the container, which is the laptop equivalent of a provider's serial console:

```bash
docker compose -f target-box/docker-compose.yml exec -T box \
  sshd -T | grep -E '^(permitrootlogin|passwordauthentication|pubkeyauthentication) '
```

Expected output:

```text
permitrootlogin no
pubkeyauthentication yes
passwordauthentication no
```

Expected result: the three values are as asked, in the order `sshd` itself dumps them rather than the order you set them. Write the command as bare `sshd`, not `/usr/sbin/sshd`: Git Bash rewrites any argument that starts with a slash into a Windows path, so `/usr/sbin/sshd` arrives at the container as `C:/Program Files/Git/usr/sbin/sshd` and `exec` fails with `no such file or directory` and exit code 127. The unqualified name is found on the container's `PATH` and behaves identically on Linux, macOS and WSL.

`sshd -T` is the check that matters and grepping `sshd_config` is not, because Ubuntu's config begins with `Include /etc/ssh/sshd_config.d/*.conf` and `sshd` keeps the first value it obtains. A dropped-in `50-cloud-init.conf` carrying `PasswordAuthentication yes` therefore beats your edit further down the main file, and the file you edited reads exactly as you intended while the running daemon disagrees. Confirm the door is shut with `$BOX root@localhost 'whoami'`, which should now be refused, while the second terminal keeps working.

## Step 7: Close the box down to three ports

The firewall goes last, after you have a working non-root login, because a `ufw` mistake and an SSH mistake are hard to tell apart once both land at the same time. This is defence in depth: on a real VM it sits behind the provider's own network firewall rather than replacing it.

That ordering has a consequence you have to plan for rather than discover. `ufw` refuses to run as anything but root, Step 6 just closed root SSH, and `deploy` has no `sudo` (the package is not even installed on this box). So the last step of the bootstrap cannot travel over the deploy connection at all, and it goes out of band through the container instead, the same channel the Step 6 check used. On a real VM that channel is the provider's serial console, or a separate admin account that does have `sudo`.

```text
Configure ufw on the box. Root SSH is closed and deploy has no sudo, so every
ufw command has to run out of band through the container rather than over ssh:

  docker compose -f target-box/docker-compose.yml exec -T box <command>

- default deny incoming, default allow outgoing
- allow 22/tcp, 80/tcp and 443/tcp
- enable it without an interactive prompt

Nothing else gets an inbound rule. Report the full ufw status.
```

```bash
docker compose -f target-box/docker-compose.yml exec -T box ufw status verbose
```

Expected output:

```text
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), deny (routed)
New profiles: skip

To                         Action      From
--                         ------      ----
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
22/tcp (v6)                ALLOW IN    Anywhere (v6)
80/tcp (v6)                ALLOW IN    Anywhere (v6)
443/tcp (v6)               ALLOW IN    Anywhere (v6)
```

Expected result: active, incoming denied by default, three ports open. Six rules appear for three ports because `ufw allow 22/tcp` writes an IPv4 rule and an IPv6 rule, and a count that surprises you is worth resolving before you decide a rule is missing.

Ports 80 and 443 are open before anything listens on them because the next demo's Caddy edge needs port 80 reachable for its first certificate challenge, and a firewall rule added after the challenge fails does not un-fail it. Re-run the `deploy` login from Step 6 in a fresh terminal to confirm the rule set did not cost you SSH.

One honest limit of this rule set: it governs traffic to the host's own listeners, not to containers. Docker publishes a port by writing its own `DNAT` rules ahead of the chain `ufw` filters, so the next demo's published 80 and 443 would answer even with no `ufw` rule permitting them. `ufw` is the control for host services and the provider's network firewall is the control for the box; neither one is a substitute for the app not publishing ports it does not need.

## Helpful Claude Slash Commands

| Command | Usage |
|---|---|
| `/permissions` | Allow `Bash(ssh:*)` and `Bash(docker:*)` once, so a twenty-command bootstrap does not stop at every prompt |
| `/agents` | Hand the whole loop to the `ssh-deploy-agent` from [01: The Deployment Agent](../01-devops-agent/readme.md) after you have driven it manually and know what the checks should say |
| `/rewind` | Roll back a bad hardening prompt in the conversation; remember it restores files and history, never the host |
| `/clear` | Drop the bootstrap transcript before starting the Compose and TLS demo, so the box state comes from checks rather than from stale context |

## Key Topics Covered in This Demo

- [OpenSSH server on Ubuntu](https://documentation.ubuntu.com/server/how-to/security/openssh-server/): key-based authentication and the hardening options set in Step 6
- [sshd_config manual](https://manpages.ubuntu.com/manpages/noble/en/man5/sshd_config.5.html): the `Include` directive and the first-value-wins rule that makes `sshd -T` the only reliable check
- [Install Docker Engine on Ubuntu](https://docs.docker.com/engine/install/ubuntu/): the apt repository procedure used in Step 5, and why the convenience script is a bootstrap-only tool
- [Docker post-installation steps](https://docs.docker.com/engine/install/linux-postinstall/): the `docker` group and running the daemon as a non-root user
- [Ubuntu firewall documentation](https://documentation.ubuntu.com/server/how-to/security/firewalls/): `ufw` defaults, rule syntax and status output
- [Automatic security updates](https://help.ubuntu.com/community/AutomaticSecurityUpdates): what `unattended-upgrades` installs unattended and what it deliberately leaves alone
- [Claude Code settings and permissions](https://code.claude.com/docs/en/settings): scoping the shell verbs an agent may use against a live host

