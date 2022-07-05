# Chapter 2 - Deploy the Application to Kubernetes

### Instructions

1. Use`kubectl` to verify that you can connect to your cluster. 
    ```shell
    kubectl get nodes
    ```

    You should see output like this: 
    ```shell
    NAME                   STATUS   ROLES    AGE     VERSION
    pool-vj14tarbi-csyw0   Ready    <none>   30s   v1.22.8
    pool-vj14tarbi-csyw1   Ready    <none>   30s   v1.22.8
    pool-vj14tarbi-csywd   Ready    <none>   30s   v1.22.8
    ```

1. Create a namespace where you will deploy your application
    ```shell
    kubectl apply -f kubernetes/namespace.yaml
    ```

    Check that your new namespace exists by running 
    ```shell
    kubectl get namespaces
    ```

    You should see a list of namespaces, including the `secrets-app`, like this:
    ```shell
    NAME              STATUS   AGE
    secrets-app     Active   3s
    default           Active   10m
    kube-node-lease   Active   10m
    kube-public       Active   10m
    kube-system       Active   10m
    ```
1. Create a Kubernetes Deployment that will ensure there are 3 replicas of the One Time Secret application running at once.
    ```shell
    kubectl apply -f kubernetes/deployment.yaml
    ```
    Check that there are three `one-time-secret` pods running in your `secrets-app` namespace.
    ```shell
    kubectl get pods -n secrets-app
    ```
    You should see something like this:
    ```shell
    NAME                              READY   STATUS    RESTARTS   AGE
    one-time-secret-5b757b96f-6nbm7   1/1     Running   0          12s
    one-time-secret-5b757b96f-b9t54   1/1     Running   0          12s
    one-time-secret-5b757b96f-cjtsx   1/1     Running   0          12s
    ```

1. Deploy a service to create a Load Balancer that will direct traffic from the internet to your application replicas 
    ```shell
    kubectl apply -f kubernetes/service.yaml
    ```
    Find the external IP address of the Load Balancer
    ```shell
    kubectl get svc -A
    ```
    You will see something like this:
    ```shell
    NAMESPACE       NAME          TYPE           CLUSTER-IP      EXTERNAL-IP      PORT(S)                  AGE
    secrets-app   ots-service   LoadBalancer   10.245.26.224   143.198.247.38   80:31965/TCP             60m
    default         kubernetes    ClusterIP      10.245.0.1      <none>           443/TCP                  2d12h
    kube-system     kube-dns      ClusterIP      10.245.0.10     <none>           53/UDP,53/TCP,9153/TCP   2d12h
    ```
    It takes a few minutes for Load Balancer to be created and be assigned an IP address. 


1. Add resource requests and limits
    1. In the [Deployment manifest](./kubernetes/deployment.yaml), uncomment lines 25-31.
    1. Update the Deployment with 
    ```shell
    kubectl apply -f kubernetes/deployment.yaml
    ```







