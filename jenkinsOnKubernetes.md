1. Installation of helm and tiller

```
wget https://storage.googleapis.com/kubernetes-helm/helm-v2.9.1-linux-amd64.tar.gz

tar zxfv helm-v2.9.1-linux-amd64.tar.gz

cp linux-amd64/helm .

mv helm /usr/bin/

kubectl create clusterrolebinding cluster-admin-binding 
--clusterrole=cluster-admin --user=$USER

kubectl create serviceaccount tiller --namespace kube-system

kubectl create clusterrolebinding tiller-admin-binding --clusterrole=cluster-admin --serviceaccount=kube-system:tiller

./helm init --service-account=tiller
./helm update

helm search jenkins
```

2. Installation of **jenkins Using helm**

```
cat>values.yaml<<EOF
Master:
  Image: "smartbuddy/jenkins-master"
  ImageTag: "1.0"
  ImagePullPolicy: "Always"
  InstallPlugins:
    - kubernetes:1.12.6
    - workflow-job:2.31
    - workflow-aggregator:2.5
    - credentials-binding:1.16
    - git:3.9.3
    - google-oauth-plugin:0.7
    - google-source-plugin:0.3
  Cpu: "1"
  Memory: "350Mi"
  JavaOpts: "-Xms350m -Xmx350m"
  ServiceType: ClusterIP
Agent:
  Enabled: true
  resources:
    requests:
      cpu: "200m"
      memory: "206Mi"
    limits:
      cpu: "1"
      memory: "512Mi"
Persistence:
  Size: 250Mi
NetworkPolicy:
  ApiVersion: networking.k8s.io/v1
rbac:
  install: true
  serviceAccountName: cd-jenkins
EOF
```

```
helm install -n jenkinscicd stable/jenkins -f values.yaml --version 0.16.5 --wait
```

3. Configuring the ClusterIP svc to NodePort

```
kubectl get all

kubectl get svc cd-jenkins -o yaml | tee cd-jenkins.yaml
 NodePort

kubectl apply -f cd-jenkins.yaml

kubectl get svc

minikube service cd-jenkins
```

4. for getting jenkins-admin password from **secret**

```
printf $(kubectl get secret cd-jenkins -o jsonpath="{.data.jenkins-admin-password}" | base64 --decode);echo
```

5. Flushing all steps
kubectl get events
helm list
helm del jenkisn --purge