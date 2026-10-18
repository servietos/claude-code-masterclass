+++
date = '2026-08-07T10:30:00+02:00'
title = "GitHub Actions for Beginners"
draft = false
tags = ["DevOps", "GitHub"]
+++

GitHub Actions runs a script on GitHub's machines whenever something happens in
your repository. A push, a pull request, a tag, a schedule: each one can start a
workflow, and a workflow is a YAML file in `.github/workflows/` that lists jobs,
and jobs list steps. That is the entire model. The confusion beginners hit is
rarely the syntax; it is that the runner starts empty every time, so anything your
build needs has to be installed or restored inside the workflow itself.

## A Practical Use Case

The clearest first workflow is a deployment. On every push to `main`, one job
checks out the repository, builds a container image, and pushes it to a registry.
A second job connects to the target host over SSH, pulls the new tag, and restarts
the service. The credentials live in repository secrets rather than the file, and
the second job depends on the first, so a failed build never reaches the host.
What used to be a checklist someone followed by hand is now a file everyone on the
team can read, and every run leaves a log that says exactly what happened.

Start smaller than that. Add a workflow that runs your test suite on every pull
request, watch it go green, then break a test on purpose and watch it go red. Once
you trust the signal, add the build. Once the build is reliable, add the deploy.
Each step earns the next one, and the workflow file grows in the order you
actually learned to trust it.
