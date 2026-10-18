# Install WSL and Docker Desktop

Every lab in this module runs on a Windows host with Docker Desktop (WSL2 backend) and a bash shell. This guide gets both installed and verified.

## Step 1: Install WSL

Install WSL2 with the Windows Subsystem for Linux package. Either command below works; the second is the one that also installs a default Ubuntu distribution.

```powershell
winget install Microsoft.WSL
```

or, from an elevated PowerShell, the classic bootstrap:

```powershell
wsl --install
```

**Expected result:** A reboot may be required. After rebooting, check the installed distributions and versions:

```powershell
wsl -l -v
```

**Expected result:** A list with one distribution and `VERSION 2`. If your distribution reports `VERSION 1`, upgrade it:

```powershell
wsl --set-version <distro-name> 2
```

Downloads: [WSL install docs](https://learn.microsoft.com/en-us/windows/wsl/install), [WSL on the Microsoft Store](https://apps.microsoft.com/detail/9pdxjnl7w5cw).

## Step 2: Install Docker Desktop

Install Docker Desktop, which brings the Docker Engine and the Compose plugin on its WSL2 backend:

```powershell
winget install Docker.DockerDesktop
```

**Expected result:** Launch Docker Desktop from the Start menu, accept the license, and wait for the whale icon in the tray to stop animating. The first start may take a minute while the WSL2 backend initializes.

Downloads: [Docker Desktop for Windows](https://www.docker.com/products/docker-desktop/), [Docker Desktop release notes](https://docs.docker.com/desktop/release-notes/).

## Step 3: Verify

```powershell
docker compose version
wsl bash -c 'echo hello from wsl'
```

**Expected result:** `docker compose version` reports a v2 version (for example `Docker Compose version v5.0.0-desktop.1`), and the second command prints `hello from wsl`. That is everything the labs need: Docker for the containers, WSL for the bash shell.

## SSH Keys and WSL

The labs generate an SSH key on the Windows filesystem and use it from bash. WSL's `ssh` refuses a key it considers world-readable, and files on a Windows drive (`/mnt/c/...`) arrive with permissive modes. If `ssh` reports `UNPROTECTED PRIVATE KEY FILE`, copy the key into your WSL home instead:

```bash
cp /mnt/c/Users/<you>/.../box_key ~/.ssh/ && chmod 600 ~/.ssh/box_key
```

The labs' commands keep the key on the Windows side and run from git-bash, which does not enforce this check; the copy is only needed when running the same commands from inside WSL.
