# Deployment Guide

## Overview

DocIntell supports multiple deployment strategies:
- Local development with Docker Compose
- Production deployment with Docker Compose
- Kubernetes deployment with Helm charts
- Cloud platform deployment (AWS, GCP, Azure)

## Prerequisites

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.21+ (for K8s deployment)
- Helm 3.0+ (for Helm deployment)
- OpenAI API key

## Environment Configuration

### Required Environment Variables

```bash
# Database
POSTGRES_SERVER=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your-secure-password
POSTGRES_DB=docintell

# Redis
REDIS_URL=redis://redis:6379

# Security
SECRET_KEY=your-secret-key-min-32-chars
OPENAI_API_KEY=sk-your-openai-api-key

# Application
LOG_LEVEL=INFO
CORS_ORIGINS=["https://yourdomain.com"]
```

### Optional Environment Variables

```bash
# AI Configuration
EMBEDDING_MODEL=text-embedding-3-small
LLM_MODEL=gpt-3.5-turbo

# File Limits
MAX_UPLOAD_SIZE=10485760  # 10MB

# Monitoring
GRAFANA_PASSWORD=secure-password
```

## Docker Compose Deployment

### Development Environment

```bash
# Clone repository
git clone https://github.com/yourusername/docintell.git
cd docintell

# Configure environment
cp .env.example .env
# Edit .env with your configuration

# Start services
docker-compose up -d

# Check service health
docker-compose ps
docker-compose logs -f
```

### Production Environment

```bash
# Use production compose file
docker-compose -f docker-compose.prod.yml up -d

# Scale services
docker-compose -f docker-compose.prod.yml up -d --scale backend=3 --scale frontend=2

# Monitor logs
docker-compose -f docker-compose.prod.yml logs -f backend
```

### Service Access

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001

## Kubernetes Deployment

### Using kubectl

```bash
# Create namespace
kubectl apply -f deployment/k8s/namespace.yaml

# Deploy database and cache
kubectl apply -f deployment/k8s/postgres.yaml
kubectl apply -f deployment/k8s/redis.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n docintell --timeout=300s

# Deploy application
kubectl apply -f deployment/k8s/backend.yaml
kubectl apply -f deployment/k8s/frontend.yaml

# Check deployment status
kubectl get pods -n docintell
kubectl get services -n docintell
```

### Using Helm

```bash
# Add Helm repository (if needed)
helm repo add stable https://charts.helm.sh/stable
helm repo update

# Install with default values
helm install docintell deployment/helm/ -n docintell --create-namespace

# Install with custom values
helm install docintell deployment/helm/ -n docintell \
  --create-namespace \
  --set backend.env.OPENAI_API_KEY="sk-your-key" \
  --set postgres.auth.password="secure-password"

# Upgrade deployment
helm upgrade docintell deployment/helm/ -n docintell

# Check status
helm status docintell -n docintell
kubectl get pods -n docintell
```

### Accessing the Application

```bash
# Port forward for testing
kubectl port-forward svc/docintell-frontend 8080:80 -n docintell

# Or configure ingress
kubectl apply -f deployment/k8s/frontend.yaml  # includes ingress
```

## Cloud Platform Deployment

### AWS EKS

```bash
# Create EKS cluster
eksctl create cluster --name docintell --region us-west-2 --nodes 3

# Configure kubectl
aws eks update-kubeconfig --region us-west-2 --name docintell

# Install ingress controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.0.0/deploy/static/provider/aws/deploy.yaml

# Deploy application
helm install docintell deployment/helm/ -n docintell --create-namespace \
  --set ingress.className=nginx \
  --set ingress.hosts[0].host=docintell.yourdomain.com
```

### Google GKE

```bash
# Create GKE cluster
gcloud container clusters create docintell \
  --num-nodes=3 \
  --zone=us-central1-a

# Get credentials
gcloud container clusters get-credentials docintell --zone=us-central1-a

# Deploy application
helm install docintell deployment/helm/ -n docintell --create-namespace
```

### Azure AKS

```bash
# Create resource group
az group create --name docintell-rg --location eastus

# Create AKS cluster
az aks create \
  --resource-group docintell-rg \
  --name docintell \
  --node-count 3 \
  --enable-addons monitoring \
  --generate-ssh-keys

# Get credentials
az aks get-credentials --resource-group docintell-rg --name docintell

# Deploy application
helm install docintell deployment/helm/ -n docintell --create-namespace
```

## SSL/TLS Configuration

### Using Let's Encrypt with cert-manager

```bash
# Install cert-manager
kubectl apply -f https://github.com/jetstack/cert-manager/releases/download/v1.7.1/cert-manager.yaml

# Create ClusterIssuer
cat <<EOF | kubectl apply -f -
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: your-email@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
EOF

# Deploy with TLS enabled
helm install docintell deployment/helm/ \
  --set ingress.enabled=true \
  --set ingress.hosts[0].host=docintell.yourdomain.com \
  --set ingress.tls[0].secretName=docintell-tls \
  --set ingress.tls[0].hosts[0]=docintell.yourdomain.com
```

## Scaling

### Horizontal Pod Autoscaling

```bash
# Enable metrics server (if not present)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml

# Create HPA for backend
kubectl autoscale deployment docintell-backend \
  --cpu-percent=70 \
  --min=2 \
  --max=10 \
  -n docintell

# Create HPA for frontend
kubectl autoscale deployment docintell-frontend \
  --cpu-percent=70 \
  --min=2 \
  --max=5 \
  -n docintell

# Check HPA status
kubectl get hpa -n docintell
```

### Manual Scaling

```bash
# Scale backend
kubectl scale deployment docintell-backend --replicas=5 -n docintell

# Scale frontend
kubectl scale deployment docintell-frontend --replicas=3 -n docintell
```

## Monitoring Setup

### Prometheus and Grafana

```bash
# Add Prometheus Helm repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# Install Prometheus
helm install prometheus prometheus-community/kube-prometheus-stack -n monitoring --create-namespace

# Access Grafana
kubectl port-forward svc/prometheus-grafana 3000:80 -n monitoring
# Default credentials: admin/prom-operator

# Import DocIntell dashboard
# Use the dashboard JSON from deployment/grafana/dashboards/
```

## Backup and Recovery

### Database Backup

```bash
# Create backup
kubectl exec -n docintell deployment/postgres -- pg_dump -U postgres docintell > backup.sql

# Restore backup
kubectl exec -i -n docintell deployment/postgres -- psql -U postgres docintell < backup.sql
```

### Persistent Volume Backup

```bash
# List persistent volumes
kubectl get pv

# Create volume snapshot (cloud-specific)
# AWS EBS snapshot, GCP Persistent Disk snapshot, etc.
```

## Troubleshooting

### Common Issues

**Pods not starting:**
```bash
# Check pod status
kubectl describe pod <pod-name> -n docintell

# Check logs
kubectl logs <pod-name> -n docintell

# Check events
kubectl get events -n docintell --sort-by='.lastTimestamp'
```

**Database connection issues:**
```bash
# Test database connectivity
kubectl exec -it deployment/postgres -n docintell -- psql -U postgres -d docintell -c "SELECT 1;"

# Check service endpoints
kubectl get endpoints -n docintell
```

**Ingress not working:**
```bash
# Check ingress controller
kubectl get pods -n ingress-nginx

# Check ingress configuration
kubectl describe ingress docintell-ingress -n docintell

# Check DNS resolution
nslookup docintell.yourdomain.com
```

### Performance Tuning

**Backend optimization:**
- Increase worker processes
- Tune database connection pool
- Enable response caching
- Optimize embedding batch size

**Frontend optimization:**
- Enable gzip compression
- Configure CDN
- Optimize bundle size
- Enable service worker caching

## Security Considerations

### Network Policies

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: docintell-network-policy
  namespace: docintell
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: ingress-nginx
  egress:
  - to: []
    ports:
    - protocol: TCP
      port: 443  # HTTPS
    - protocol: UDP
      port: 53   # DNS
```

### Pod Security Policies

```yaml
apiVersion: policy/v1beta1
kind: PodSecurityPolicy
metadata:
  name: docintell-psp
spec:
  privileged: false
  allowPrivilegeEscalation: false
  requiredDropCapabilities:
    - ALL
  volumes:
    - 'configMap'
    - 'emptyDir'
    - 'projected'
    - 'secret'
    - 'downwardAPI'
    - 'persistentVolumeClaim'
  runAsUser:
    rule: 'MustRunAsNonRoot'
  seLinux:
    rule: 'RunAsAny'
  fsGroup:
    rule: 'RunAsAny'
```

## Maintenance

### Updates

```bash
# Update backend image
helm upgrade docintell deployment/helm/ \
  --set backend.image.tag=v1.1.0

# Rolling update
kubectl rollout status deployment/docintell-backend -n docintell
kubectl rollout history deployment/docintell-backend -n docintell

# Rollback if needed
kubectl rollout undo deployment/docintell-backend -n docintell
```

### Health Checks

```bash
# Check application health
curl -f https://docintell.yourdomain.com/health

# Check all pods
kubectl get pods -n docintell

# Check resource usage
kubectl top pods -n docintell
kubectl top nodes
```