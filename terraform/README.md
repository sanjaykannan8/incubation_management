# 🚀 Simple Dev EKS Cluster

Super simple, cost-effective EKS setup for development. No complex networking, just the basics!

## 📋 What This Creates

- **EKS Cluster** - Your Kubernetes control plane
- **1 Worker Node** - t3.small instance (cost-effective)
- **ArgoCD** - For GitOps deployments
- **Uses Default VPC** - No complex networking

## 💰 Cost-Optimized for Dev

- Uses default VPC (no extra networking costs)
- Single t3.small node (~$15/month)
- No NAT gateways or complex setup
- Perfect for learning and development

## 🚀 Quick Start

### 1. Setup
```bash
# Copy example config
make setup

# Edit terraform.tfvars with your settings
```

### 2. Deploy
```bash
# Initialize
make init

# Deploy (takes ~10 minutes)
make apply
```

### 3. Connect
```bash
# Configure kubectl
make kubeconfig

# Check your cluster
kubectl get nodes
```

### 4. Access ArgoCD
```bash
# Get ArgoCD info
make argocd

# Access ArgoCD locally
kubectl port-forward svc/argocd-server -n argocd 8080:80

# Open: http://localhost:8080
# Username: admin
# Password: (what you set in terraform.tfvars)
```

## ⚙️ Configuration

Edit `terraform.tfvars`:

```hcl
cluster_name = "my-dev-cluster"
aws_region   = "ap-south-1"

# Node configuration
node_instance_type = "t3.small"  # Cost-effective
node_count         = 1           # Minimal for dev

# ArgoCD
argocd_admin_password = "your-secure-password"

# Optional: Your Git repo for deployments
git_repo_url  = "https://github.com/yourusername/k8s-manifests.git"
git_username  = "your-username"
git_password  = "your-personal-access-token"
```

## 📁 Git Repository Structure

If you want GitOps, organize your repo like this:

```
your-k8s-repo/
├── app.yaml           # Your application manifests
├── service.yaml
├── deployment.yaml
└── README.md
```

## 🔧 Common Commands

```bash
# Terraform
make init              # Initialize
make plan              # Show plan
make apply             # Deploy
make destroy           # Delete everything

# Kubernetes
kubectl get nodes      # List nodes
kubectl get pods -A    # List all pods
kubectl get svc -A     # List all services

# ArgoCD
kubectl port-forward svc/argocd-server -n argocd 8080:80
kubectl get applications -n argocd
```

## 🛠️ Deploy Your App with ArgoCD

### 1. Via ArgoCD UI
1. Open ArgoCD: `http://localhost:8080`
2. Login with admin credentials
3. Click "NEW APP"
4. Fill in:
   - **Name:** `my-app`
   - **Repository:** Your Git repo URL
   - **Path:** `.` (root of repo)
   - **Destination:** `https://kubernetes.default.svc`
   - **Namespace:** `default`
5. Click "CREATE"

### 2. Via kubectl
```bash
# Create application
kubectl apply -f - <<EOF
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  source:
    repoURL: https://github.com/yourusername/k8s-manifests.git
    path: .
    targetRevision: main
  destination:
    server: https://kubernetes.default.svc
    namespace: default
  syncPolicy:
    automated:
      selfHeal: true
      prune: true
EOF
```

## 💡 Tips

### Cost Optimization
- **Stop when not using:** `terraform destroy` saves money
- **Use t3.micro:** Even cheaper for light workloads
- **Monitor costs:** Check AWS billing dashboard

### Development Workflow
1. **Code:** Write your app and Kubernetes manifests
2. **Push:** Commit to Git repository
3. **Deploy:** ArgoCD automatically deploys changes
4. **Test:** Access your app via LoadBalancer or port-forward

### Common Issues

#### 1. Can't connect to cluster
```bash
# Reconfigure kubectl
aws eks update-kubeconfig --region ap-south-1 --name my-dev-cluster
```

#### 2. ArgoCD not accessible
```bash
# Check if ArgoCD is running
kubectl get pods -n argocd

# Port forward again
kubectl port-forward svc/argocd-server -n argocd 8080:80
```

#### 3. Nodes not ready
```bash
# Check node status
kubectl describe nodes

# Usually just needs a few more minutes
```

## 🧹 Cleanup

```bash
# Delete everything (saves money!)
make destroy
```

## 📚 What's Different from Production?

This dev setup is intentionally simple:

- **Uses default VPC** (production would use custom VPC)
- **No SSL/HTTPS** (production would have proper certificates)
- **Single node** (production would have multiple nodes)
- **No monitoring** (production would have CloudWatch, Prometheus)
- **No backup** (production would have backup strategies)

Perfect for learning and development! 🎉

---

**Pro Tip:** This setup costs ~$15-20/month when running. Always `terraform destroy` when not using to save money! 💰