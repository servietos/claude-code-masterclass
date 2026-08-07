FROM mcr.microsoft.com/devcontainers/dotnet:10.0

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

ARG DEBIAN_FRONTEND=noninteractive

ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /workspace

RUN chown -R vscode:vscode /workspace \
    && chmod -R u+rwX,go+rX /workspace \
    && find /workspace -type d \( -name "obj" -o -name "bin" \) -exec rm -rf {} + 2>/dev/null || true

USER vscode
