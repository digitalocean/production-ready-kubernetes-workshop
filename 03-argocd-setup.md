# Chapter 3 - Setup ArgoCD

![](https://raw.githubusercontent.com/digitalocean/Kubernetes-Starter-Kit-Developers/main/15-continuous-delivery-using-gitops/assets/images/argocd_overview.png)

## Rationale 
In this chapter, you will learn to:

- Use `Helm` to provision `Argo CD` to your `DOKS` cluster.
- Keep your `Kubernetes` cluster applications state synchronized with a `Git` repository, using `GitOps` principles.
- Deploy and manage your application via Argo CD.

After finishing all the steps from this tutorial, you should have a `DOKS` cluster with `Argo CD` deployed. 

## Instructions
### Step 1 - Install Argo CD
1. Add the Argo CD Helm repository:
    ```shell
    helm repo add argo https://argoproj.github.io/argo-helm

    helm repo update argo 
    ```
1. Inspect the Argo CD Helm values file.
    ```shell
    code argo/argo-values.yaml
    ```
1. Deploy Argo CD to your DOKS cluster:
    ```shell
    HELM_CHART_VERSION="4.9.7"

    helm install argocd argo/argo-cd --version "${HELM_CHART_VERSION}" \
      --namespace argocd \
      --create-namespace \
      -f "argo/values.yaml"
    ```
1. Check if the Helm release was successful:
    ```shell
    helm ls -n argocd
    ```
1. The output looks similar to (`STATUS` column value should be set to `deployed`):
    ```text
    NAME    NAMESPACE       REVISION        UPDATED                                 STATUS          CHART           APP VERSION
    argocd  argocd          1               2022-03-23 11:22:48.486199 +0200 EET    deployed        argo-cd-4.2.1   v2.3.1
    ```
1. Verify Argo CD application deployment status:
    ```shell
    kubectl get deployments -n argocd
    ```

    The output looks similar to (check the `READY` column - all `Pods` must be running):

    ```text
    NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
    argocd-applicationset-controller   1/1     1            1           2m9s
    argocd-dex-server                  1/1     1            1           2m9s
    argocd-notifications-controller    1/1     1            1           2m9s
    argocd-redis-ha-haproxy            3/3     3            3           2m9s
    argocd-repo-server                 2/2     2            2           2m9s
    argocd-server                      2/2     2            2           2m9s
    ```
    Argo CD server must have a `replicaset` minimum value of `2` for the `HA` mode. If for some reason some deployments are not healthy, please check Kubernetes events and logs for the affected component Pods.

## Step 2 - Access and Explore the Argo CD Web Interface
1. Port forward the `argocd-server` Kubernetes service
    ```shell
    kubectl port-forward svc/argocd-server -n argocd 8080:443
    ```
1. Open a web browser and navigate to [localhost:8080](http://localhost:8080) (please ignore the invalid TLS certificates for now). You will be greeted with the Argo CD log in page. The default administrator username is `admin`, and the password is generated randomly at installation time. You can fetch it by running below command:
    ```shell
    kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
    ```
1. Next, you will be redirected to the applications dashboard page. From here you can view, create or manage applications via the UI (an YAML editor is also available), as well as perform sync or refresh operations:

## Step 3 - Bootstrap an ArgoCD Application

On a fresh install, Argo CD doesn't know where to sync your applications from, or what Git repositories are available for sourcing application manifests. So, the first step is to perform a one time operation called bootstrapping. You can perform all the operations presented in this section by either using the [argocd](https://argo-cd.readthedocs.io/en/stable/cli_installation) CLI, or the graphical user interface.

## Step 4 -  Update the image in the deployment, push to github and observe the ArgoCD reconciliation process

### Learn More
- [DigitalOcean Kubernetes Starter Kit: GitOps and Continuous Delivery](https://github.com/digitalocean/Kubernetes-Starter-Kit-Developers/tree/main/15-continuous-delivery-using-gitops)
- [Argo CD Helm chart](https://github.com/argoproj/argo-helm/tree/master/charts/argo-cd) 
- [Using Argo CD with Sealed Secrets](https://utkuozdemir.org/blog/argocd-helm-secrets)