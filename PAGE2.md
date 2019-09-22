## Quick installation 
```

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update
sudo apt-get install -y docker-ce=18.06.1~ce~3-0~ubuntu

curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
cat << EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF

sudo apt-get update
sudo apt-get install -y kubelet=1.12.7-00 kubeadm=1.12.7-00 kubectl=1.12.7-00



sudo apt-mark hold kubelet kubeadm kubectl docker-ce



```

## Upgrading the kubernetes cluster component

1. Upgrading the kubeadm component to the desired state
```
export VERSION=v1.13.5
export ARCH=amd64

curl -sSL https://dl.k8s.io/release/${VERSION}/bin/linux/${ARCH}/kubeadm > kubeadm
sudo install -o root -g root -m 0755 ./kubeadm /usr/bin/kubeadm
sudo kubeadm version

```

2. Upgrading the control plan component with kubeadm
```
sudo kubeadm upgrade plan
sudo kubeadm upgrade apply $VERSION

```

3. Installing the kubelet of desired version
```
curl -sSL https://dl.k8s.io/release/${VERSION}/bin/linux/${ARCH}/kubelet > kubelet
sudo install -o root -g root -m 0755 ./kubelet /usr/bin/kubelet
sudo systemctl restart kubelet.service
kubectl get nodes # installation verification

# Installing the kubectl also
curl -sSL https://dl.k8s.io/release/${VERSION}/bin/linux/${ARCH}/kubectl > kubectl
sudo install -o root -g root -m 0755 ./kubectl /usr/bin/kubectl
kubectl version
```

4. Upgrade only the kubelet and kubectl version on minions
```
export VERSION=v1.13.5
export ARCH=amd64
curl -sSL https://dl.k8s.io/release/${VERSION}/bin/linux/${ARCH}/kubelet > kubelet
sudo install -o root -g root -m 0755 ./kubelet /usr/bin/kubelet
sudo systemctl restart kubelet.service

curl -sSL https://dl.k8s.io/release/${VERSION}/bin/linux/${ARCH}/kubectl > kubectl
sudo install -o root -g root -m 0755 ./kubectl /usr/bin/kubectl
kubectl version # On master also
```


