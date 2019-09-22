# 1.Configuring and Bootstarping the kubernetes cluster

* Main component of kubernetes cluster are kubeadm, kubelet, kubectl
* **kubeadm** does most of the configuration part in automate way
* **kubelet** works as a middle man between the kubernetes api and container
  runtime, it actually manges the container's creation, running deletion and more
* **kubectl** communicates with the kunernetes cluster for administration,
   deployments of the obejct into the cluster

Configurng kubernetes cluster on Ubuntu 18.04.2 LTS(1 manager and 2 minions) 

Step 1. Installation of docker 

```

curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
sudo apt-get update

sudo apt-get install -y docker-ce=18.06.1~ce~3-0~ubuntu

sudo apt-mark hold docker-ce

```



Step 2. Insatllation of kubeadm, kubelet, kubectl 
```
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
cat << EOF | sudo tee /etc/apt/sources.list.d/kubernetes.list
deb https://apt.kubernetes.io/ kubernetes-xenial main
EOF

sudo apt-get update
sudo apt-get install -y kubelet=1.12.7-00 kubeadm=1.12.7-00 kubectl=1.12.7-00

sudo apt-mark hold kubelet kubeadm kubectl docker-ce



```



Step3. Bootstarting the master node and joining the two other minion node
       to the master

(Only on master)
sudo kubeadm init --pod-network-cidr=10.244.0.0/16

Step 4. cluster Network configuration with flannel CNI plugin(All three nodes)

[On All three node]

echo "net.bridge.bridge-nf-call-iptables=1" | sudo tee -a /etc/sysctl.conf

sudo sysctl -p

[Only on master]
#for v1.12.7	
kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/bc79dd1505b0c8681ece4de4c0d86c5cd2643275/Documentation/kube-flannel.yml

#kubectl apply -f https://raw.githubusercontent.com/coreos/flannel/master/Documentation/kube-flannel.yml

kubectl cluster-info

kubectl get nodes 

kubectl get pods -n kube-system


# 2. Pods in kubernetes
1. Pods is the smallest unit of kubernetes cluster, its the building
	block of the cluster.
2. Pods may contains one or more containers inside it 
3. Pods or any kubernetes object may be deployed by using .yml file
	e.g deploying the pods
```
	cat << EOF | kubectl create -f -
	apiVersion: v1
	kind: Pod
	metadata:
		name: nginx
	spec:
		containers:
		- name: nginx
	  	  image: nginx
	EOF

kubectl get pods -n default
kubectl delete pod nginx
kubectl describe pods -n kube-system
```