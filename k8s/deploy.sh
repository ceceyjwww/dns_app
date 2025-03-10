#!/bin/bash

# Build Docker images
echo "Building Docker images..."
docker build -t as:latest ../AS/
docker build -t fs:latest ../FS/
docker build -t us:latest ../US/

# Apply Kubernetes configurations
echo "Applying Kubernetes configurations..."
kubectl apply -f as-deployment.yaml
kubectl apply -f fs-deployment.yaml
kubectl apply -f us-deployment.yaml

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/as-deployment
kubectl wait --for=condition=available --timeout=300s deployment/fs-deployment
kubectl wait --for=condition=available --timeout=300s deployment/us-deployment

# Get service URLs
echo "Getting service URLs..."
echo "FS Service URL:"
kubectl get service fs-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}'
echo -e "\nUS Service URL:"
kubectl get service us-service -o jsonpath='{.status.loadBalancer.ingress[0].ip}' 