# ===============================================
# Terraform and Provider Configuration
# ===============================================

terraform {
  required_version = ">= 1.5"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.23"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "~> 2.11"
    }
  }
}

# ===============================================
# AWS Provider Configuration
# ===============================================

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile != "" ? var.aws_profile : null

  # Common tags applied to all resources
  default_tags {
    tags = {
      Project     = "IMS-MVP"
      Environment = var.environment
      ManagedBy   = "Terraform"
      CreatedBy   = "EKS-Terraform-Module"
    }
  }
}

# ===============================================
# EKS Data Sources
# ===============================================

# Get EKS cluster information
data "aws_eks_cluster" "cluster" {
  name = module.eks.cluster_name
  depends_on = [module.eks]
}

# Get EKS cluster authentication token
data "aws_eks_cluster_auth" "cluster" {
  name = module.eks.cluster_name
  depends_on = [module.eks]
}

# Get current AWS caller identity
data "aws_caller_identity" "current" {}

# ===============================================
# Kubernetes Provider Configuration
# ===============================================

provider "kubernetes" {
  host                   = data.aws_eks_cluster.cluster.endpoint
  cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
  token                  = data.aws_eks_cluster_auth.cluster.token
}

# ===============================================
# Helm Provider Configuration
# ===============================================

provider "helm" {
  kubernetes {
    host                   = data.aws_eks_cluster.cluster.endpoint
    cluster_ca_certificate = base64decode(data.aws_eks_cluster.cluster.certificate_authority[0].data)
    token                  = data.aws_eks_cluster_auth.cluster.token
  }
}