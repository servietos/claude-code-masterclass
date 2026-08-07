FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
        openssh-server \
        systemd \
        systemd-sysv \
        sudo \
        iproute2 \
        ca-certificates \
        curl \
        gnupg \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /run/sshd && systemctl enable ssh

RUN mkdir -p /root/.ssh && chmod 700 /root/.ssh
COPY keys/box_key.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys

CMD ["/sbin/init"]
