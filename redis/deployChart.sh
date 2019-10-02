#!/bin/bash

kubectl delete po redis-pod
kubectl delete pvc redis-pvc
kubectl delete pv redis-pv

kubectl create namespace redis
kubectl create -f redisChart.yml




