# ===============================================
# Simple Dev Environment Variables
# ===============================================

variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "cluster_name" {
  description = "EKS cluster name"
  type        = string
  default     = "ims-MVP-cluster"
}

variable "node_instance_type" {
  description = "EC2 instance type for worker nodes"
  type        = string
  default     = "t2.micro"  # Cost-effective for dev
}

variable "node_count" {
  description = "Number of worker nodes"
  type        = number
  default     = 1  # Minimal for dev
}

# ===============================================
# Essential Add-ons Only
# ===============================================

variable "install_argocd" {
  description = "Install ArgoCD for GitOps"
  type        = bool
  default     = true
}

variable "argocd_admin_password" {
  description = "ArgoCD admin password"
  type        = string
  default     = "ragulanna"
  sensitive   = true
}

variable "git_repo_url" {
  description = "Your Git repository URL for deployments"
  type        = string
  default     = "https://github.com/priyanka0572/incubation_management.git"
}

variable "git_username" {
  description = "Git username (for private repos)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "git_password" {
  description = "Git password/token (for private repos)"
  type        = string
  default     = ""
  sensitive   = true
}

variable "git_repo_branch" {
  description = "Git repository branch"
  type        = string
  default     = "main"
}

variable "git_repo_path" {
  description = "Path to manifests in your repo"
  type        = string
  default     = "manifest"
}

variable "create_default_app" {
  description = "Create default ArgoCD application for IMS"
  type        = bool
  default     = true
}


variable "install_monitoring" {
  description = "Install Prometheus + Grafana monitoring stack"
  type        = bool
  default     = false
}

variable "grafana_admin_password" {
  description = "Grafana admin password"
  type        = string
  default     = "admin123"
  sensitive   = true
}