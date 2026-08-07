FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive
# systemd reads this variable to learn it is running in a container, not on hardware
ENV container=docker

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      systemd \
      systemd-sysv \
      dbus \
      openssh-server \
      rsyslog \
      iproute2 \
      iputils-ping \
      ca-certificates \
      curl \
      gnupg \
      less \
      nano \
 && rm -rf /var/lib/apt/lists/*

# the masked units need real hardware and would otherwise fail the boot
RUN systemctl enable ssh rsyslog \
 && systemctl mask \
      systemd-udevd.service \
      systemd-udev-trigger.service \
      systemd-networkd-wait-online.service \
      systemd-resolved.service \
      systemd-firstboot.service

RUN install -d -m 700 /root/.ssh
COPY keys/box_key.pub /root/.ssh/authorized_keys
RUN chmod 600 /root/.ssh/authorized_keys && chown root:root /root/.ssh/authorized_keys

# the signal systemd treats as shutdown, so docker stop ends the box cleanly
STOPSIGNAL SIGRTMIN+3

CMD ["/sbin/init"]
