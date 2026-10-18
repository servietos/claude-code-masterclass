# Bootstrap and Harden an Ubuntu Host over SSH

Driving a host bootstrap through Claude Code is an ordering problem: every step that closes a door has to be preceded by a proof taken from the host, because the agent's transcript is a claim and only the host is evidence. You end up holding a box in the exact state every later demo assumes.

------

Work in [`box-stack/`](box-stack) after generating the key and starting the target as its [readme](box-stack/readme.md#start-and-destroy-the-target) shows; the finished result of both demos lives beside it in [`box-stack-solution/`](box-stack-solution).

## Step 1: Prove SSH access before you build anything

Prove access from your own terminal first, then hand the same connection string to Claude. `-o IdentitiesOnly=yes` is mandatory: without it `ssh` offers every default key in your agent first, the server cuts you off after `MaxAuthTries`, and a perfectly correct key reports `Permission denied`.

```bash
export BOX='ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
$BOX root@localhost 'whoami; . /etc/os-release && echo $PRETTY_NAME'
```

```powershell
function BOX { ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=NUL -o StrictHostKeyChecking=no @args }
BOX root@localhost 'whoami; . /etc/os-release && echo $PRETTY_NAME'
```

```text
root
Ubuntu 24.04.5 LTS
```

You are root on Ubuntu; every later `$BOX ...` line runs as `BOX ...` in PowerShell.

## Step 2: Create the non-root deploy user

Deployments should not run as root, so the deploy user inherits the key you already proved; patching (`unattended-upgrades`, `fail2ban`) and Docker Engine from the official apt repository, with `deploy` in the `docker` group, follow the same pattern of one prompt and one host check per claim. Claude will report success, so check it against the host from your control terminal:

```text
Create a non-root deploy user on the box:
- user "deploy", no password login (--disabled-password), no sudo
- copy /root/.ssh/authorized_keys to /home/deploy/.ssh/authorized_keys
- ownership deploy:deploy, 700 on the .ssh directory, 600 on the file
```

```bash
$BOX root@localhost 'id deploy; stat -c "%a %U:%G %n" /home/deploy/.ssh /home/deploy/.ssh/authorized_keys'
```

```text
700 deploy:deploy /home/deploy/.ssh
600 deploy:deploy /home/deploy/.ssh/authorized_keys
```

A `755` on `.ssh` or a file still owned by `root` is the real failure to watch for, and `sshd` silently ignores such a file.

## Step 3: Prove the deploy key in a second session, then close the door

This is the step that locks people out of their own boxes, so log in as `deploy` with `box_key` in a second terminal and leave that session open. Only now hand the hardening to Claude, then verify the effective config yourself out of band through the container:

```text
Harden SSH on the box. I have an open deploy session as a fallback.
In /etc/ssh/sshd_config set:
  PermitRootLogin no
  PasswordAuthentication no
  PubkeyAuthentication yes
```

```bash
docker compose -f target-box/docker-compose.yml exec -T box \
  sshd -T | grep -E '^(permitrootlogin|passwordauthentication|pubkeyauthentication) '
```

```text
permitrootlogin no
pubkeyauthentication yes
passwordauthentication no
```

`sshd -T` is the check that matters, because a dropped-in `50-cloud-init.conf` carrying `PasswordAuthentication yes` beats your edit; `ufw` (22, 80, 443) goes last through the same container channel, since root SSH is now closed.
