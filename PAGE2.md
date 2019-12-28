Table of Contents
=================
<!--ts-->
   1. [Installation](https://github.com/ishaq4466/Kubernetes/blob/master/PAGE2.md#1-quick-installation-of-k8s-components)
   2. [Upgrading the cluster components](#2-Upgrading-the-kubernetes-cluster-components)
   3. [NetworkPolicy in k8s](#3-Network-Policies-in-k8s)
<!--te-->



### 1. Quick installation of k8s components
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
        cidr: 192.168.1.0/24		# All 254 pods with ipBlock can communicate with the pods
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
1. Running the nginx pod with user as nginx and group also as nginx
```
apiVersion: v1
kind: Pod
metadata:
  name: nginx-user-context
spec:     
  fsGroup: 9999 # fs group is 999 i.e file created will have 999 fileid
  containers:
  - name: main
    image: nginx
    command: ["/bin/sleep", "999999"]
    securityContext:
      runAsUser: 101 # 101 id is for nginx, for knowing that you can cat /etc/passwd for the nginx pod
      runAsGroup: 101
      runAsNonRoot: true 
```

101-> nginx
### Trobleshooting

1. [Network CNI issue](https://stackoverflow.com/questions/44305615/pods-are-not-starting-networkplugin-cni-failed-to-set-up-pod)





