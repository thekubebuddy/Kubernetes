Table of Contents
=================
   1. [Installation](https://github.com/ishaq4466/Kubernetes/blob/master/PAGE2.md#1-quick-installation-of-k8s-components)
   2. [Upgrading the cluster components](#2-Upgrading-the-kubernetes-cluster-components)
   3. [NetworkPolicy in k8s](#3-Network-Policies-in-k8s)
   4. [CA and TLS](#4-CA-and-TLS)
   5. [Private Docker Registery Configuration in k8s](#5-Private-Docker-Registery-in-k8s)
   6. [Securitiy Context in k8s](#securityContext)
   7. [Monitoring and Logging cluster components and Applications](#7-monitoring-and-logging-cluster-components-and-applications)
   8. [Troubleshooting k8s cluster](#8-troubleshooting)
   9. [Minikube](#9-minikube)
      * [Installing](#1-installing-minikube-is-quite-simple-and-easy-for-installation-first-check-whether-the-system-supports-virtualization-or-not)
      * [Cluster Creation](#2-creating-minikube-cluster) 
   10. [Context switching](#10-context-switching)
   11. [Deleting the namespace forcefully](#11-forcefully-deleting-the-namespace)
   12. [Kubernetes imperative cheetsheet](#12-kubernetes-imperative-cheetsheet)
   13. [Scheduller in K8s](#13-scheduller-in-k8s)
   14. [PV and PVC](#14-pv-and-pvc)
   15. [Upgrade the cluster components](#15-upgrade-the-cluster-components-through-kubeadm)
   16. [Overcommitted state](#16-overcommit-state)
   17. [Two tier flask app](https://raw.githubusercontent.com/ishaq4466/Kubernetes/master/flask-two-tier-app.yaml)
   18. [Mysql stack on k8s with pv](https://raw.githubusercontent.com/ishaq4466/Kubernetes/master/mysql-with-pv-stack.yaml)
   19. [Nginx ingress controller on minikube](https://github.com/kubernetes/ingress-nginx/blob/eedcdcdbf6ab319da435de8c266a1c156eb834b3/docs/deploy/index.md#minikube)
   20. SMB Fileshare with windows containers for RWX access modes
   21. Internal GKE ingress with self-signed TLS cert.
   22. 


### 1. Quick installation of k8s components
```
sudo apt-get install software-properties-common
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

**Adding** the current user in the docker group so that we **dont use sudo docker again and again**
```
sudo usermod -aG docker ${USER}
su - ${USER}
id -nG
```
 
### 2. Upgrading the kubernetes cluster components

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

# Installing the kubectl(client) also
export VERSION=v1.13.5
export ARCH=amd64
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

### 3. Network Policies in k8s
* Network policies allows pods to allow or deny traffic with the cluster i.e locking down the pods access
* NetworkPolicy uses selectors to apply rules to pods within the cluster
* NetworkPolicy is supported by plugin called "canal" which has to installed first 
```
k apply -f https://docs.projectcalico.org/v3.5/getting-started/kubernetes/installation/hosted/canal/canal.yaml
```
* NetworkPolicies are **applied** to the pods that mathes the **"podSelector" or "namespaceSelector"** in netpol yaml(k get netpol -n default)

1. Deny-all netpol
By applying the netPolicy the pods cannot be able to reach out with each other withing the default ns
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-all
  namespace: default
spec:
  podSelector: {} #All pods in that ns inherit this networkpolicy
  policyTypes:
  - Ingress
```
2. Pod Selector netpol
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: db-netpolicy
spec:
  podSelector: # these policy is applied to those pods which matches the labels "app:db"
    matchLabels:
      app: db
  ingress:
  - from:
    - podSelector:
        matchLabels: # communication is accepted only by pods with label "app:web" over port 5432
          app: web
    ports:
    - port: 5432
```


3. Network Policy Using ipBlock
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ipblock-netpolicy
spec:
  podSelector:
    matchLabels:
      app: db
  ingress:
  - from:
    - ipBlock:
        cidr: 192.168.1.0/24 # All 254 pods with that ip Range can communicate with the pods that matches app:db
```

4. Namespacewide net policy
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: ns-netpolicy
spec:
  podSelector:
    matchLabels:
      app: db
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          tenant: web
    ports:
    - port: 5432
```

4. Egress NetPol
```
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: egress-netpol
spec:
  podSelector:
    matchLabels:
      app: web
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: db
    ports:
    - port: 5432
```

### 4. CA and TLS 
* Certificate Auth. is used to generate the TLS certificate and auth with the API server
* By default ca.crt and serviceaccount are bundled in every pods bu default at /var/run/secrets/kubernetes.io/serviceaccount
* For creation of new certificate, we have to create a CSR resource in K8s by using "cfssl and cfssl_json" tool
* With the custom cert. we can authenticate the API server
```
wget -q --show-progress --https-only --timestamping \
  https://pkg.cfssl.org/R1.2/cfssl_linux-amd64 \
  https://pkg.cfssl.org/R1.2/cfssljson_linux-amd64

chmod +x cfssl_linux-amd64 cfssljson_linux-amd64
sudo mv cfssl_linux-amd64 /usr/local/bin/cfssl
sudo mv cfssljson_linux-amd64 /usr/local/bin/cfssl_json

cfssl version

# CSR file creation
cat <<EOF | cfssl genkey - | cfssljson -bare server
{
  "hosts": [
    "my-svc.my-namespace.svc.cluster.local",
    "my-pod.my-namespace.pod.cluster.local",
    "172.168.0.24",
    "10.0.34.2"
  ],
  "CN": "my-pod.my-namespace.pod.cluster.local",
  "key": {
    "algo": "ecdsa",
    "size": 256
  }
}
EOF

cat <<EOF | kubectl create -f -
apiVersion: certificates.k8s.io/v1beta1
kind: CertificateSigningRequest
metadata:
  name: pod-csr.web
spec:
  groups:
  - system:authenticated
  request: $(cat server.csr | base64 | tr -d '\n')
  usages:
  - digital signature
  - key encipherment
  - server auth
EOF

# Viewing the CSR in cluster
kubectl get csr

# getting the details for the csr 
kubectl describe csr pod-csr.web

# Apporiving the csr by the admin 
kubectl certificate approve pod-csr.web


# View the certificate within the CSR
kubectl get csr pod-csr.web -o yaml

# Extract and decode your certificate to use in a file:

kubectl get csr pod-csr.web -o jsonpath='{.status.certificate}' \
    | base64 --decode > server.crt
```

### 5. Private Docker Registery in k8s
* Since k8s uses docker as a **container runtime**, therefore all images are pulled by docker hub by default
* Pulling Unauth public images from the public registry, can open the gate for vulneribilities into our k8s cluster.
* For e.g, The public image might contains bin which can tear down our control plane components and bringing our cluster down. 
* Hence it is wise to use a private registry and also seting the "imagePullPolicy: Always" in pod template
* There are free tools that can be use to safe-gaurd against the vulnebility such as "coreOs-clair" and "aquasecurity-microscanner" which scans the container activity
* For setting up the private registry with k8s, it uses an **imagePullSecrets** in the Pod templates, that needs to be generated and **pathced up with the default service-account** in particular namespace
1. Creating an image secret in a particular namespace
```
k create secrets docker-registry imgsecret --docker-server=<registry-url> --docker-username=<user-name>
--docker-password=<passwd> --namespace=<ns-if-required>  

```
2. Patching the created image secret with the default service account so that **"there is no need to mention 
it in the Pod template"**
```
kubectl patch sa default -p '{"imagePullSecrets": [{"name": "<secret-name>"}]}'

```


### [6.securityContext](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-the-security-context-for-a-container)
* securityContext allows locking down the containers to control certain processes only.
* This ensures the security stability of the containers. 
* "securityContext" can be added to the pod-yaml file which is applied to all the containers within the pod or it can be applied to container spec where it applies to that specfic container.
* We can also set the [linux capabities](http://man7.org/linux/man-pages/man7/capabilities.7.html) for the containers by using the "capabilities" attribute for the securityContext

1. runAsUser,runAsGroup, runAsNonRoot
Running the nginx pod with user and group as nginx 
```
apiVersion: v1
kind: Pod
metadata:
  name: nginx-user-context
spec:     
  containers:
  - name: main
    image: nginx
    command: ["/bin/sleep", "999999"]
    securityContext:
      runAsNonRoot: true # if you dont know the user-id than this can be set to "true" for running container as non-root
      runAsUser: 101 # 101 uid is for nginx, for knowing that you can cat /etc/passwd for the nginx pod
      runAsGroup: 101
```
*if you want to run the container as root than, set runAsNonRoot: false(Not a good practice though)*

2. [privileged-pod](https://kubernetes.io/docs/concepts/policy/pod-security-policy/#privileged)
By default the container in the pod does not have access to any devices on host
```
apiVersion: v1
kind: Pod
metadata:
  name: privileged-pod
spec:
  containers:
  - name: main
    image: alpine
    command: ["/bin/sleep", "999999"]
    securityContext:
      privileged: true
```
Running the below cmd will return more devices as compared to normal pod
```
kubectl exec -it privileged-pod ls /dev
```
3. [capabilites](https://kubernetes.io/docs/tasks/configure-pod-container/security-context/#set-capabilities-for-a-container)
```
apiVersion: v1
kind: Pod
metadata:
  name: kernelchange-pod
spec:
  containers:
  - name: main
    image: alpine
    command: ["/bin/sleep", "999999"]
    securityContext:
      capabilities:
        add:				# "drop" can be used to drop-down the capabilities
        - SYS_TIME
```
The container will have capability to change the time
```
kubectl exec -it kernelchange-pod -- date +%T -s "12:00:00"
```
Similarly we can provide many [capabilities](http://man7.org/linux/man-pages/man7/capabilities.7.html)

4. Reading and writing to the file-system

```
apiVersion: v1
kind: Pod
metadata:
  name: readonly-pod
spec:
  containers:
  - name: main
    image: alpine
    command: ["/bin/sleep", "999999"]
    securityContext:
      readOnlyRootFilesystem: true # if set to "false", be able to write to '/'
    volumeMounts:
    - name: my-volume
      mountPath: /volume
      readOnly: false
  volumes:
  - name: my-volume
    emptyDir:
```
The pod can read only the **"local filesystem"** but cannot write to it.
```
k exec -it readonly-pod touch /file1 #error will be raised
```
However it can write to **"container's local filesystem" i.e on /volume** 
```
k exec -it readonly-pod touch /volume/file1 #will not
```

```
apiVersion: v1
kind: Pod
metadata:
  name: group-context
spec:
  securityContext:
    fsGroup: 555
    supplementalGroups: [666, 777]
  containers:
  - name: first
    image: alpine
    command: ["/bin/sleep", "999999"]
    securityContext:
      runAsUser: 1111
    volumeMounts:
    - name: shared-volume
      mountPath: /volume
      readOnly: false
  - name: second
    image: alpine
    command: ["/bin/sleep", "999999"]
    securityContext:
      runAsUser: 2222
    volumeMounts:
    - name: shared-volume
      mountPath: /volume
      readOnly: false
  volumes:
  - name: shared-volume
    emptyDir:
#k exec -it group-context -c first sh
```


### [7. Monitoring and Logging cluster components and Applications](https://kubernetes.io/docs/tasks/debug-application-cluster/resource-usage-monitoring/)
1. Metric server
* Metric server enables us to monitor the **CPU and memory utilization** at cluster level as well as at pod and container level
* Installation of Metric server:
```
git clone https://github.com/ishaq4466/Kubernetes
# Installing for apiVersion 1.8+, can be known by using
k version --short 
k apply -f Kubernetes/metrics-server/deploy/1.8+/
# Getting the response back from metric server API
kubectl get --raw /apis/metrics.k8s.io/
```
* Handy command to monitor the cpu  metrics:
```
k top no # Getting the nodes cpu and memory utilization 
k top po 
k top po --all-namespace
k top po -n kube-system
k top po -l app=nginx -n web
k top po multi-containers --containers
k top po multi-containers --containers 
```
2. Monitoring application health through ["Liveness and Readiness probe"](https://kubernetes.io/docs/concepts/workloads/pods/pod-lifecycle/#container-probes)
* Liveness Probe: Checks whether the container is live or not
* Readiness Probe: Checks wheter the container is ready to serve the client request is ready or not
```
apiVersion: v1
kind: Pod
metadata:
  name: liveness
  labels:
    app: nginx
spec:
  containers:
  - image: nginx
    name: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 80
    readinessProbe:
      httpGet:
        path: /
        port: 80
      initialDelaySeconds: 5
      periodSeconds: 5

```

* The below yaml fails in l
```
apiVersion: v1
kind: Pod
metadata:
  name: liveness
  labels:
    app: nginx
spec:
  containers:
  - image: nginx
    name: nginx
    livenessProbe:
      httpGet:
        path: /
        port: 8080
    readinessProbe:
      httpGet:
        path: /
        port: 8080
      initialDelaySeconds: 5
      periodSeconds: 5
```
3. Monitoring the logs of cluster-component
```
apiVersion: v1
kind: Pod
metadata:
  name: counter
spec:
  containers:
  - name: count
    image: busybox
    args:
    - /bin/sh
    - -c
    - >
      i=0;
      while true;
      do
        echo "$i: $(date)" >> /var/log/1.log;
        echo "$(date) INFO $i" >> /var/log/2.log;
        i=$((i+1));
        sleep 1;
      done
    volumeMounts:
    - name: varlog
      mountPath: /var/log
  volumes:
  - name: varlog
    emptyDir: {}
```


### 8. Troubleshooting
1. Woker node failure issues
```
sudo systemctl status docker
sudo systemctl enable docker && systemctl start docker
sudo su -
swapoff -a && sed -i '/ swap / s/^/#/' /etc/fstab
sudo systemctl status kubelet
sudo systemctl enable kubelet && systemctl start kubelet
sudo kubeadm token generate
sudo kubeadm token create [token_name] --ttl 2h --print-join-command
sudo kubeadm token create [token_name] --ttl 2h --print-join-command

sudo more /var/log/syslog | tail -120 | grep kubelet
```

### 9. Minikube

* Minikube is really helpfull if you want to practice k8s on a single node cluster, it offers that functionality.
* Minikube allows to run k8s cluster locally, if the underlying system support virtualization
* "minikube" Installation and some cmd is listed below

#### 1. Installing minikube is quite simple and easy, for installation first check whether the system [supports virtualization or not.](https://kubernetes.io/docs/tasks/tools/install-minikube/#before-you-begin)
Here is an easy installation guide for [minikube on ubuntu](https://matthewpalmer.net/kubernetes-app-developer/articles/install-kubernetes-ubuntu-tutorial.html).

#### 2. Creating minikube cluster
```
# Starting minikube cluster with specific k8s api-version and vm-drivers 
minikube start --vm-driver virtualbox --kubernetes-version v1.17.0
```
```
# for commicating with the docker daemon-installed inside "minikube" vm 
eval $(minikube docker-env)
```
```
# Enabling the k8s dashboard which comes pre-installed for minikube
minikube dashboard
```
```
# start minikube with "none" vm-driver 
sudo minikube start --vm-driver=none --kubernetes-version=1.16.2
```
* **Starting minikube with custom resource capactity by default it spins with 2Gi and 2cores**
```
# spinning a k8s cluster with 8Gi of RAM, 4cpu's, disk-size of 50gb
minikube start --vm-driver=virtualbox --kubernetes-version=1.16.0 --memory=8192 --cpus=4 --disk-size=50g
```

### 10. Context Switching
``` 
k config get-contexts
k config use-context <context-names>
# setting up the namespace
k config set-context --current --namespace=<your-namespace>
```

### 11. Forcefully deleting the namespace
```
(
NAMESPACE=your-rogue-namespace
kubectl proxy &
kubectl get namespace $NAMESPACE -o json |jq '.spec = {"finalizers":[]}' >temp.json
curl -k -H "Content-Type: application/json" -X PUT --data-binary @temp.json 127.0.0.1:8001/api/v1/namespaces/$NAMESPACE/finalize
)
```


### 12. Kubernetes imperative cheetsheet
```
# common images nginx:alpine redis:alpine

k config set-context $(k config current-context) --namespace=new

# Dry-running the nginx pod creation and it will provide us the yaml
k run nginx --generator=run-pod/v1 --image=nginx:alpine --namespace=default --dry-run -o yaml 
# apk update && apk add busybox-extras curl

# DR the nginx deployment generating the yaml 
k create deploy nginx --image=nginx:alpine --namespace=default --dry-run -o yaml 

# Scaling up the replicas within the nginx deploy
k scale deploy nginx --replicas=3

# Getting all pods in all namespace showing all the labels and all the nodes in which it is scheduled
k get po --all-namespaces --show-labels -o wide

# Labels 
k get po --show-labels -l tier=frontend 
k get all --show-labels -l env=prod

k get all --selector env=prod,tier=frontend # get all with env prod and tier is frontend 
# Exposing a pod

# Alpine deployment
k run  test-$RANDOM --rm -it --image=alpine --  sh
apk add curl && apk add busybox-extras

# Service trouble-shooting pods and cmd
k run test-$RANDOM --imag=alpine --rm -it -- sh
nslookup svc web.operations.svc.cluster.local
wget -qO- --timeout=2 http://web.operations.svc.cluster.local
```

### 13. Scheduller in K8s
* Every pod definition has a field names "nodeName" trough which you can scedule a pod to a specific Node

**Manually schedulling a pod to a node if the scheduler is not running up**
```
apiVersion: v1
kind: Pod
metadata:
  name: nginx
spec:
  containers:
  -  image: nginx
     name: nginx
  nodeName:
    node01
```

**Taints and tolerations***

* Tainting does not gurantees that the pod will note goto the tolerated node instead it avoids the nodes to expect the
intolerated pod

```
k taint node node1 spary=blue:NoSchedule

tolerations

apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
    labels:
    run: mosquito  
    name: bee
spec:
  containers:
  - image: nginx
    imagePullPolicy: IfNotPresent
    name: mosquito    
    resources: {}  
    tolerations:
    - key: "spray"    
      operator: "Equal"
      value: "mortein"    
      effect: "NoSchedule"
```
* NodeSelector
```
# Labling a node
k lable no node1 size=large
# Unlabing
k lable no node1 size-

apiVersion: v1
kind: Pod
metadata:
  creationTimestamp: null
    labels:
    run: mosquito  
    name: bee
spec:
  containers:
  - image: nginx
    imagePullPolicy: IfNotPresent
    name: mosquito    
    resources: {}  
    tolerations:
    - key: "spray"    
      operator: "Equal"
      value: "mortein"    
      effect: "NoSchedule"
```

### [14. PV and PVC](https://kubernetes.io/docs/concepts/storage/persistent-volumes/#class-1)
```
---
apiVersion: v1
kind: PersistentVolume
metadata:
  name: nginx-vol
  labels:
    app: nginx-vol
spec:
  accessModes:
    - ReadWriteOnce
  capacity:
    storage: 2Gi
  persistentVolumeReclaimPolicy: Retain
  hostPath:
    path: /home/ishaqshaikh/k8sdata
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: nginx-pvc-claim
  labels:
    app: nginx-pvc
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: "" # This is very important
  resources:
    requests:
      storage: 1Gi
  selector:
    matchLabels:
      app: "nginx-vol"
---
apiVersion: apps/v1
kind: Deployment
metadata:
  creationTimestamp: null
  labels:
    app: nginx
  name: nginx
  namespace: operations
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      creationTimestamp: null
      labels:
        app: nginx
    spec:
      containers:
      - image: nginx
        name: nginx
        env:
        - name: APP_NAME
          value: "Hello App!"
        volumeMounts:
        - name: nginx-storage
          mountPath: /data
      volumes:
      - name: nginx-storage
        persistentVolumeClaim:
          claimName: nginx-pvc-claim
```

### 15. Upgrade the cluster components through kubeadm

**On master node**
Step 1: drain the master node if not tainted 
```
k drain master --ignore-daemonset 
```
Step 2 : Upgrade the kubeadm first
```
apt-get update -y kubeadm=1.12.0-00
```
Step 3 : kubeadm upgrade plan
```
kubeadm --version

# provide the suitable component versiob 
kubeadm upgrade plan
kubeadm upgrade apply v1.12.0
```
Step 4 : Kubelet and kubectl upgrade

```
# Finnnally upgrade the kubelet and kubectl version
apt-get update -y kubelet=1.12.0-00 kubectl=1.12.0-00
service kubelet restart
k get no
k version --short

kubeadm upgrade node config --kubelet-version $(kubelet --version | cut -d ' ' -f 2)

```

Step 5: Uncorden or make the node the node Schedulable 
```
k uncorden master
```

**On worker node**

Step 1: drain the worker node
```
k drain node01 --ignore-daemonset 
```

Step 2:Kubelet and kubectl upgrade
```
apt-get update -y kubelet=1.12.0-00 kubectl=1.12.0-00
service kubelet restart
```

Step 3: Uncorden or make the node the node Schedulable 
```
k uncorden node01
```


### 16. [Overcommit state](https://cloud.google.com/blog/products/gcp/kubernetes-best-practices-resource-requests-and-limits)

**Request -> Requests are what the container is guaranteed to get**
**Limits  -> Limits, on the other hand, make sure a container never goes above a certain value. The container is only allowed to go up to the limit, and then it is restricted.**

Limits can be higher than the requests. What if you have a Node where the sum of all the container Limits is actually higher than the resources available on the machine?
At this point, Kubernetes goes into something called an **“overcommitted state.”** Here is where things get interesting. Because CPU can be compressed, Kubernetes will make sure your containers get the CPU they requested and will throttle the rest. Memory cannot be compressed, so Kubernetes needs to start making 
decisions on what containers to terminate if the Node runs out of memory.


```
1. Ip allocation range for the pods can be found by:
k logs weave-pod -n kube-system | grep ipalloc-range

2. IP allocation range for the svc can be found by quring the kube-api service:
ps -aux | grep kube-api| grep service-cluster-ip

3. Type of proxy is the kube-proxy configured to use.
kubectl logs kube-proxy-ft6n7 -n kube-system
```

### COREDNS
* coredns manages the dns resolution or service discovery of various svc and pods within the k8s
* it uses a configuration file located at /etc/coredns/Corefile in the coredns pod
* The Corefile is injected into the coredns pod as a **cm in kube-system ns**
* in this file the top level domain name is set i.e cluster.local is set in the corefile
* by default the pod domain name resolutions are not set by default 
* With the core-dns pod we also have a service configured with the core-dns pod to make it available to other
  component
  k get svc -n kube-system
* The ip-address of the coredns service is configured **as a nameserver in the newly pod's /ect/resolve.conf**  ,this is taken care by the kubelet component once the pod is created.
* fqdn: web-service.namespace.svc.cluster.local


### INGRESS
* A layer 7 load balancer resource which supports 
* Ingress controller examples: nginx, gcp https loadbalancer, conotur, traefik, HAPROXY, ISTIO
* Igress reource supports domain(host) based routing[] and path based routing[]



### ETCD
* ETCD is a high available distributed key-value store, which is simple,secure and fast
* ETCD replicates the data within the cluster
* A successfull write in etcd will be when the data is replicated in majority of the nodes
* Only one node with etcd cluster is able to write and replicates the data among the other etcd node
* It uses the **RAFT** algo to elect the master node in the etcd cluster


# Increment the size of pvc
```
k edit pvc <pvc-name>
k delete po <which-mounts-tht-pvc>
```





1. [Network CNI issue](https://stackoverflow.com/questions/44305615/pods-are-not-starting-networkplugin-cni-failed-to-set-up-pod)

