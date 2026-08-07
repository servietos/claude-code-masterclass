+++
date = 2026-07-24T11:00:00+02:00
title = "GitHub Actions for Beginners"
draft = false
tags = ["DevOps", "GitHub"]
+++

GitHub Actions runs automation directly inside your repository. A workflow is a YAML file in .github/workflows that describes when to run (a push, a pull request, a schedule, a manual trigger) and what to do (a sequence of jobs made of steps). Each job gets a fresh virtual machine, so the environment is the same on every run.

## A Practical Use Case

Publishing a static site is the classic first workflow. On every push to the default branch, one job checks out the code, installs the toolchain, runs the build and uploads the output folder as an artifact. A second job takes that artifact and deploys it to GitHub Pages. The whole pipeline is roughly forty lines of YAML and needs no server of your own.

To get started, create the .github/workflows folder, add a file, and give it a name, a trigger and a single job that echoes a message. Push it and watch the Actions tab. Once the first run goes green, replace the echo with a real build command and add the steps you need one at a time.
