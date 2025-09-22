# ===============================================
# Essential Dev Tools Only
# ===============================================
# Just ArgoCD for GitOps - nothing fancy

# ArgoCD namespace
resource "kubernetes_namespace" "argocd" {
  count = var.install_argocd ? 1 : 0
  
  metadata {
    name = "argocd"
  }
  
  depends_on = [aws_eks_node_group.dev_nodes]
}

# Simple ArgoCD installation
resource "helm_release" "argocd" {
  count      = var.install_argocd ? 1 : 0
  name       = "argocd"
  repository = "https://argoproj.github.io/argo-helm"
  chart      = "argo-cd"
  namespace  = "argocd"
  version    = "5.51.6"

  # Simple dev configuration
  set {
    name  = "configs.secret.argocdServerAdminPassword"
    value = bcrypt(var.argocd_admin_password)
  }

  set {
    name  = "server.service.type"
    value = "LoadBalancer"
  }

  set {
    name  = "server.insecure"
    value = "true"  # No SSL for dev
  }

  depends_on = [kubernetes_namespace.argocd]
}

# Create ArgoCD Application for IMS Services (using plain manifests)
resource "kubernetes_manifest" "ims_application" {
  count = var.create_default_app && var.git_repo_url != "" ? 1 : 0
  
  manifest = {
    apiVersion = "argoproj.io/v1alpha1"
    kind       = "Application"
    
    metadata = {
      name      = "ims-services"
      namespace = "argocd"
    }
    
    spec = {
      project = "default"
      
      source = {
        repoURL        = var.git_repo_url
        targetRevision = var.git_repo_branch
        path           = var.git_repo_path  # Points to manifest/ folder
      }
      
      destination = {
        server    = "https://kubernetes.default.svc"
        namespace = "default"  # ArgoCD ONLY manages this namespace
      }
      
      syncPolicy = {
        automated = {
          selfHeal = true
          prune    = true
        }
        syncOptions = [
          "CreateNamespace=true"
        ]
      }
    }
  }
  
  depends_on = [helm_release.argocd]
}

# Create Git repository secret for ArgoCD
resource "kubernetes_secret" "git_repo_secret" {
  count = var.git_username != "" && var.git_password != "" ? 1 : 0
  
  metadata {
    name      = "ims-repo-secret"
    namespace = "argocd"
    
    labels = {
      "argocd.argoproj.io/secret-type" = "repository"
    }
  }
  
  data = {
    type     = "git"
    url      = var.git_repo_url
    username = var.git_username
    password = var.git_password
  }
  
  depends_on = [kubernetes_namespace.argocd]
}

# Install Prometheus + Grafana (for monitoring)
resource "helm_release" "prometheus" {
  count      = var.install_monitoring ? 1 : 0
  name       = "prometheus"
  repository = "https://prometheus-community.github.io/helm-charts"
  chart      = "kube-prometheus-stack"
  namespace  = "monitoring"
  version    = "51.2.0"

  create_namespace = true

  # Grafana configuration
  set {
    name  = "grafana.adminPassword"
    value = var.grafana_admin_password
  }

  set {
    name  = "grafana.service.type"
    value = "LoadBalancer"
  }

  depends_on = [aws_eks_node_group.dev_nodes]
}