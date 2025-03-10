# Build Docker images
Write-Host "Building Docker images..."
docker build -t as:latest ../AS/
docker build -t fs:latest ../FS/
docker build -t us:latest ../US/

# Apply Kubernetes configurations
Write-Host "Applying Kubernetes configurations..."
kubectl apply -f deploy_dns.yml

# Wait for deployments to be ready
Write-Host "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/as-deployment
kubectl wait --for=condition=available --timeout=300s deployment/fs-deployment
kubectl wait --for=condition=available --timeout=300s deployment/us-deployment

# Get node IP and service information
Write-Host "Getting node IP and service information..."
$nodeIP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="ExternalIP")].address}'
if (-not $nodeIP) {
    $nodeIP = kubectl get nodes -o jsonpath='{.items[0].status.addresses[?(@.type=="InternalIP")].address}'
}

Write-Host "`nService URLs:"
Write-Host "AS Service: $nodeIP`:30001 (UDP)"
Write-Host "FS Service: $nodeIP`:30002"
Write-Host "US Service: $nodeIP`:30003`n"

# Get service status
Write-Host "Service Status:"
kubectl get services 