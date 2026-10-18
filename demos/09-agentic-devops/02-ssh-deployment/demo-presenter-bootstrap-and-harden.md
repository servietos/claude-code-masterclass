---
presents: demo-bootstrap-and-harden.md
budget: 4 min
beats: 4
---

# Present: Bootstrap and Harden an Ubuntu Host over SSH

Hardening is an ordering problem: every closed door needs a proof taken from the host in front of it. Four beats: the client option, the `.ssh` modes, the door closed with a session open, the effective config read out of band.

------

The whole deliverable is host state. Nothing lands in [`box-stack-solution/`](box-stack-solution), which belongs to the next demo, and `/rewind` restores your files and your conversation, never the box.

**Shell:** beats quote Bash; in PowerShell `BOX` is a function called as `BOX ...`, because a command held in a string will not invoke, and `UserKnownHostsFile` reads `NUL`, because Win32-OpenSSH takes `/dev/null` literally and creates a file called `dev\null`.

## Beats

### Beat 1: one client option decides whether a correct key is accepted (1 min)

**Open:** [Step 1: Prove SSH access before you build anything](demo-bootstrap-and-harden.md#step-1-prove-ssh-access-before-you-build-anything) · [`target-box/docker-compose.yml`](box-stack/target-box/docker-compose.yml)
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

**Gotcha:** `IdentitiesOnly=yes` is mandatory: without it `ssh` offers every default key first, the server cuts the connection at `MaxAuthTries`, and a correct key reports `Permission denied`.

### Beat 2: the modes on `.ssh` are the login, and `sshd` will not tell you (1 min)

**Open:** [Step 2: Create the non-root deploy user](demo-bootstrap-and-harden.md#step-2-create-the-non-root-deploy-user) · [`target-box/Dockerfile`](box-stack/target-box/Dockerfile)
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

### Beat 3: prove the new key in a session you leave open, then close the door (1 min)

**Open:** [readme.md](readme.md#phase-2-bootstrap-and-harden-in-an-order-that-cannot-lock-you-out) · [Step 3: Prove the deploy key in a second session, then close the door](demo-bootstrap-and-harden.md#step-3-prove-the-deploy-key-in-a-second-session-then-close-the-door)
**Say:** Never remove a way in until its replacement has actually been used. Configured and proven are different states, and lockouts live in the distance between them.

```text
In /etc/ssh/sshd_config set:
  PermitRootLogin no
  PasswordAuthentication no
  PubkeyAuthentication yes

Check /etc/ssh/sshd_config.d/ for any file that overrides those settings and
fix it there too. Validate with sshd -t before restarting, then restart ssh
and report the effective values from sshd -T, which reads the running daemon.
```

**Result:** the deliverable is `/etc/ssh/sshd_config` on the box, with `$BOX root@localhost 'whoami'` refused from then on while the open `deploy` session keeps working; the starter is byte-identical before and after.

**Gotcha:** an `sshd` restart is instant and unconditional, so the prompt is only safe with a verified `deploy` session open in a second terminal.

### Beat 4: read the effective config, and read it out of band (1 min)

**Open:** [`target-box/docker-compose.yml`](box-stack/target-box/docker-compose.yml) · [Step 3: Prove the deploy key in a second session, then close the door](demo-bootstrap-and-harden.md#step-3-prove-the-deploy-key-in-a-second-session-then-close-the-door)
**Say:** A configuration file is an input to a program, and the running daemon can disagree with it. A check that travels over the connection you are hardening disappears exactly when it would have been worth having.

```bash
docker compose -f target-box/docker-compose.yml exec -T box \
  sshd -T | grep -E '^(permitrootlogin|passwordauthentication|pubkeyauthentication) '
```

**Result:** three effective values from the daemon itself, taken through the `container_name: box-target` channel, outside any network path

```text
permitrootlogin no
pubkeyauthentication yes
passwordauthentication no
```

**Gotcha:** `sshd` keeps the first value it obtains from `Include /etc/ssh/sshd_config.d/*.conf`, so a dropped-in `50-cloud-init.conf` beats an edit further down a main file that then reads exactly as intended.

## If the room asks

| Question | Answer |
|---|---|
| `fail2ban-client status sshd` shows `Journal matches` and no log file. Is it broken? | No. Ubuntu 24.04 ships `backend = systemd`, so the jail tails the journal and never reads `/var/log/auth.log`. |
| Six `ufw` rules appear for three ports. Is one duplicated? | No. `ufw allow 22/tcp` writes an IPv4 rule and an IPv6 rule. |
| Does any of this differ on a real VM? | Only the connection string and the out-of-band channel: the container `exec` becomes a serial console or an admin account with `sudo`. |
