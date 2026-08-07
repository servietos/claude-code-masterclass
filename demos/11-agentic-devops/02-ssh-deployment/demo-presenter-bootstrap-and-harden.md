---
presents: demo-bootstrap-and-harden.md
budget: 6 min
beats: 6
---

# Present: Bootstrap and Harden an Ubuntu Host over SSH

Hardening is an ordering problem: every closed door needs a proof taken from the host in front of it. Six beats: the client option, the `.ssh` modes, the ambiguous refusal, the door closed with a session open, the effective config read out of band, the firewall last.

------

The whole deliverable is host state. Nothing lands in [`box-stack-solution/`](box-stack-solution/), which belongs to the next demo, and `/rewind` restores your files and your conversation, never the box.

**Shell:** beats quote Bash; in PowerShell `BOX` is a function called as `BOX ...`, because a command held in a string will not invoke, and `UserKnownHostsFile` reads `NUL`, because Win32-OpenSSH takes `/dev/null` literally and creates a file called `dev\null`. The beat 3 `ssh` goes on one line there, since PowerShell does not continue a line on a backslash.

## Beats

### Beat 1: one client option decides whether a correct key is accepted (1 min)

**Open:** [Step 2: Prove SSH access before you build anything](demo-bootstrap-and-harden.md#step-2-prove-ssh-access-before-you-build-anything) · [`target-box/docker-compose.yml`](box-stack/target-box/docker-compose.yml)
**Say:** The options on your own command line decide which credential is even offered. A key that never gets offered is indistinguishable from a key that was rejected.

```text
export BOX='ssh -p 2222 -i target-box/keys/box_key -o IdentitiesOnly=yes -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no'
$BOX root@localhost 'whoami; . /etc/os-release && echo $PRETTY_NAME'
```

**Result:** root on Ubuntu 24.04, with the key pair now sitting git-ignored in [`target-box/keys/`](box-stack/target-box/keys) and its public half baked into the image

```text
Warning: Permanently added '[localhost]:2222' (ED25519) to the list of known hosts.
root
Ubuntu 24.04.5 LTS
```

**Gotcha:** `IdentitiesOnly=yes` is mandatory rather than cosmetic: without it `ssh` offers every default key first, the server cuts the connection at `MaxAuthTries`, and a correct key reports `Permission denied`.

### Beat 2: the modes on `.ssh` are the login, and `sshd` will not tell you (1 min)

**Open:** [Step 3: Create the non-root deploy user](demo-bootstrap-and-harden.md#step-3-create-the-non-root-deploy-user) · [`target-box/Dockerfile`](box-stack/target-box/Dockerfile)
**Say:** Public-key login has a second input besides the key, the permissions on the files that hold it. A daemon that declines a world-writable credential file declines silently.

```bash
$BOX root@localhost 'id deploy; stat -c "%a %U:%G %n" /home/deploy/.ssh /home/deploy/.ssh/authorized_keys'
```

**Result:** the user exists on the box with the same three modes the image already sets for `root`; nothing lands in the repository

```text
uid=1001(deploy) gid=1001(deploy) groups=1001(deploy),100(users)
700 deploy:deploy /home/deploy/.ssh
600 deploy:deploy /home/deploy/.ssh/authorized_keys
```

**Gotcha:** a `755` on `.ssh` or a file still owned by `root` is the usual hurried copy, and `sshd` ignores it silently while Claude reports success.

### Beat 3: the refusal message is identical for three different causes (1 min)

**Open:** [Step 6: Prove the deploy key in a second session, then close the door](demo-bootstrap-and-harden.md#step-6-prove-the-deploy-key-in-a-second-session-then-close-the-door) · [readme.md](readme.md#phase-1-prove-access-before-you-build-anything)
**Say:** Diagnosis never comes from the error text, it comes from what you can still reach and read on the host. See the failure while it is still harmless.

```bash
ssh-keygen -t ed25519 -f target-box/keys/decoy_key -N "" -C "wrong-key"
ssh -p 2222 -i target-box/keys/decoy_key -o IdentitiesOnly=yes \
    -o UserKnownHostsFile=/dev/null -o StrictHostKeyChecking=no deploy@localhost 'whoami'
```

**Result:** refused, and `decoy_key` plus `decoy_key.pub` land beside `box_key` in [`target-box/keys/`](box-stack/target-box/keys), where nothing is tracked except `.gitkeep`

```text
deploy@localhost: Permission denied (publickey).
```

**Gotcha:** that one line arrives whether the key is wrong, the mode is wrong or the user does not exist, and after hardening nothing is left behind it.

### Beat 4: prove the new key in a session you leave open, then close the door (1 min)

**Open:** [readme.md](readme.md#phase-2-bootstrap-and-harden-in-an-order-that-cannot-lock-you-out) · [Step 6: Prove the deploy key in a second session, then close the door](demo-bootstrap-and-harden.md#step-6-prove-the-deploy-key-in-a-second-session-then-close-the-door)
**Say:** Never remove a way in until its replacement has actually been used. Configured and proven are different states, and lockouts live in the distance between them.

```text
In /etc/ssh/sshd_config set:
  PermitRootLogin no
  PasswordAuthentication no
  PubkeyAuthentication yes

Check /etc/ssh/sshd_config.d/ for any file that overrides those settings and
fix it there too. Validate with sshd -t before restarting, then restart ssh
and report the effective values from sshd -T, not from the file.
```

**Result:** the deliverable is `/etc/ssh/sshd_config` on the box, with `$BOX root@localhost 'whoami'` refused from then on while the open `deploy` session keeps working; the starter is byte-identical before and after.

**Gotcha:** an `sshd` restart is instant and unconditional, so the prompt is only safe with a verified `deploy` session open in a second terminal.

### Beat 5: read the effective config, and read it out of band (1 min)

**Open:** [`target-box/docker-compose.yml`](box-stack/target-box/docker-compose.yml) · [Step 6: Prove the deploy key in a second session, then close the door](demo-bootstrap-and-harden.md#step-6-prove-the-deploy-key-in-a-second-session-then-close-the-door)
**Say:** A configuration file is an input to a program, not a description of what that program is doing. A check that travels over the connection you are hardening disappears exactly when it would have been worth having.

```bash
docker compose -f target-box/docker-compose.yml exec -T box \
  sshd -T | grep -E '^(permitrootlogin|passwordauthentication|pubkeyauthentication) '
```

**Result:** three effective values from the daemon itself, taken through the `container_name: box-target` channel rather than over a network path

```text
permitrootlogin no
pubkeyauthentication yes
passwordauthentication no
```

**Gotcha:** `sshd` keeps the first value it obtains from `Include /etc/ssh/sshd_config.d/*.conf`, so a dropped-in `50-cloud-init.conf` beats an edit further down a main file that then reads exactly as intended.

### Beat 6: the firewall goes last, and it cannot travel over the deploy connection (1 min)

**Open:** [Step 7: Close the box down to three ports](demo-bootstrap-and-harden.md#step-7-close-the-box-down-to-three-ports) · [`target-box/docker-compose.yml`](box-stack/target-box/docker-compose.yml)
**Say:** A firewall rule and an SSH policy both end in a connection that will not open, so they belong in separate steps with a working login in between. `ufw` needs root, which beat 4 just closed.

```text
Configure ufw on the box. Root SSH is closed and deploy has no sudo, so every
ufw command has to run out of band through the container rather than over ssh:

  docker compose -f target-box/docker-compose.yml exec -T box <command>

- default deny incoming, default allow outgoing
- allow 22/tcp, 80/tcp and 443/tcp
- enable it without an interactive prompt
```

**Result:** `ufw` active on the box, incoming denied by default, six rules for the three ports the target publishes

```text
Status: active
Logging: on (low)
Default: deny (incoming), allow (outgoing), deny (routed)
...
22/tcp                     ALLOW IN    Anywhere
80/tcp                     ALLOW IN    Anywhere
443/tcp                    ALLOW IN    Anywhere
```

**Gotcha:** 80 and 443 open before anything listens, since a rule added after an ACME challenge failed does not un-fail it, and Docker's `DNAT` rules sit ahead of the chain `ufw` filters.

## If the room asks

| Question | Answer |
|---|---|
| `fail2ban-client status sshd` shows `Journal matches` and no log file. Is it broken? | No. Ubuntu 24.04 ships `backend = systemd`, so the jail tails the journal instead of `/var/log/auth.log`. |
| Six `ufw` rules appear for three ports. Is one duplicated? | No. `ufw allow 22/tcp` writes an IPv4 rule and an IPv6 rule. |
| Does any of this differ on a real VM? | Only the connection string and the out-of-band channel: the container `exec` becomes a serial console or an admin account with `sudo`. |
