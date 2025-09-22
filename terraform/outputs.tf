# ===============================================
# Simple Dev Cluster Outputs
# ===============================================

output "cluster_name" {
  description = "EKS cluster name"
  value       = aws_eks_cluster.dev_cluster.name
}

output "cluster_endpoint" {
  description = "EKS cluster endpoint"
  value       = aws_eks_cluster.dev_cluster.endpoint
}

output "kubeconfig_command" {
  description = "Command to configure kubectl"
  value       = "aws eks update-kubeconfig --region ${var.aws_region} --name ${aws_eks_cluster.dev_cluster.name}"
}

# ===============================================
# ArgoCD Access Info
# ===============================================

output "argocd_url" {
  description = "ArgoCD access URL (run this command to get LoadBalancer URL)"
  value       = var.install_argocd ? "kubectl get svc argocd-server -n argocd" : "ArgoCD not installed"
}

output "argocd_credentials" {
  description = "ArgoCD login credentials"
  value = var.install_argocd ? {
    username = "admin"
    password = var.argocd_admin_password
  } : "ArgoCD not installed"
  sensitive = true
}

output "argocd_port_forward" {
  description = "Command to access ArgoCD locally"
  value       = var.install_argocd ? "kubectl port-forward svc/argocd-server -n argocd 8080:80" : "ArgoCD not installed"
}

# ===============================================
# Quick Commands
# ===============================================

output "useful_commands" {
  description = "Useful commands for your dev cluster"
  value = {
    get_nodes    = "kubectl get nodes"
    get_pods     = "kubectl get pods --all-namespaces"
    argocd_access = "kubectl port-forward svc/argocd-server -n argocd 8080:80"
  }
}