#!/bin/bash

CLUSTER_VERSION="1.33.1-1.1"
CONTAINERD_VERSION="2.1.1"
RUNC_VERSION="1.3.0"

modprobe overlay
modprobe br_netfilter

cat <<EOF | sudo tee /etc/sysctl.d/kubernetes.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
net.ipv4.ip_forward = 1
EOF

cat <<EOF | sudo tee /etc/modules-load.d/k8s.conf
overlay
br_netfilter
EOF

sysctl --system

# Install Containerd
wget https://github.com/containerd/containerd/releases/download/v${CONTAINERD_VERSION}/containerd-${CONTAINERD_VERSION}-linux-amd64.tar.gz
tar Cxzvf /usr/local containerd-${CONTAINERD_VERSION}-linux-amd64.tar.gz
wget https://github.com/opencontainers/runc/releases/download/v${RUNC_VERSION}/runc.amd64
install -m 755 runc.amd64 /usr/local/sbin/runc
rm -rf containerd-${CONTAINERD_VERSION}-linux-amd64.tar.gz
mkdir /etc/containerd
containerd config default | tee /etc/containerd/config.toml
sed -i "s/SystemdCgroup = false/SystemdCgroup = true/g" /etc/containerd/config.toml
curl -L https://raw.githubusercontent.com/containerd/containerd/main/containerd.service -o /etc/systemd/system/containerd.service
systemctl daemon-reload
systemctl enable --now containerd
systemctl restart containerd

# Install Kubernetes
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-apt-keyring.gpg] https://pkgs.k8s.io/core:/stable:/v${CLUSTER_VERSION:0:4}/deb/ /" | sudo tee /etc/apt/sources.list.d/kubernetes.list
curl -fsSL https://pkgs.k8s.io/core:/stable:/v${CLUSTER_VERSION:0:4}/deb/Release.key | sudo gpg --dearmor -o /etc/apt/keyrings/kubernetes-apt-keyring.gpg

apt-get update -y
apt-get install -y kubelet=${CLUSTER_VERSION} kubeadm=${CLUSTER_VERSION}
apt-mark hold kubelet kubeadm kubectl

# Configure crictl to use containerd.sock
echo "runtime-endpoint: unix:///var/run/containerd/containerd.sock
image-endpoint: unix:///var/run/containerd/containerd.sock" >> /etc/crictl.yaml
