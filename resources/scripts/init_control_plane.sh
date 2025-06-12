# Configure Flannel version
FLANNEL_VERSION="0.27.0"

# Create cluster
IP_ADDR=$(hostname -I | awk '{print $1}')

kubeadm init --pod-network-cidr 10.244.0.0/16 --control-plane-endpoint=$IP_ADDR > /tmp/run.log
mkdir -p $HOME/.kube
cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
chown $(id -u):$(id -g) $HOME/.kube/config
wget https://github.com/flannel-io/flannel/releases/download/v${FLANNEL_VERSION}/kube-flannel.yml
kubectl apply -f kube-flannel.yml

# Generate kubeadm-client.conf file
echo $(sudo kubeadm token create) > /tmp/__TOKEN__
echo $(openssl x509 -pubkey -in /etc/kubernetes/pki/ca.crt | \
        openssl rsa -pubin -outform der 2>/dev/null | \
        openssl dgst -sha256 -hex | \
        sed 's/^.* //') > /tmp/__HASH_CERT__
