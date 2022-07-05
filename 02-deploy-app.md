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
## Step 1 - Installing the Ambassador Edge Stack

In this step, you will deploy the `Ambassador Edge Stack` to your `DOKS` cluster, via `Helm`.

Steps to follow:

1. First, clone the `Starter Kit` repository and change directory to your local copy.

    ```shell
    git clone https://github.com/digitalocean/Kubernetes-Starter-Kit-Developers.git

    cd Kubernetes-Starter-Kit-Developers
    ```

2. Next, add the `Helm` repo, and list the available `charts`:

    ```shell
    helm repo add datawire https://app.getambassador.io

    helm repo update datawire

    helm search repo datawire
    ```

    The output looks similar to the following:

    ```text
    NAME                            CHART VERSION   APP VERSION     DESCRIPTION                   
    datawire/ambassador             6.9.4           1.14.3          A Helm chart for Datawire Ambassador       
    datawire/ambassador-operator    0.3.0           v1.3.0          A Helm chart for Kubernetes              
    datawire/edge-stack             7.3.2           2.2.2           A Helm chart for Ambassador Edge Stack  
    datawire/emissary-ingress       7.3.2           2.2.2           A Helm chart for Emissary Ingress
    datawire/telepresence           2.6.5           2.6.5           A chart for deploying the server-side component...
    ```

    **Note:**

    The chart of interest is `datawire/edge-stack`, which will install `Ambassador Edge Stack` on the cluster. Please visit the [ambassador-edge-stack](https://github.com/emissary-ingress/emissary) page, for more details about this chart.
3. Before installing **Ambassador Edge Stack 2.X** itself, you must configure your Kubernetes cluster to support the `getambassador.io/v3alpha1` and `getambassador.io/v2` configuration resources. This is required.

    ```shell
    kubectl apply -f https://app.getambassador.io/yaml/edge-stack/2.3.0/aes-crds.yaml
    ```

    **Note:**

    **Ambassador Edge Stack 2.X** includes a Deployment in the `emissary-system` namespace called `edge-stack-apiext`. This is the APIserver extension that supports converting Ambassador Edge Stack CRDs between `getambassador.io/v3alpha1` and `getambassador.io/v2`. This Deployment needs to be running at all times.
4. Then, open and inspect the `03-setup-ingress-controller/assets/manifests/ambassador-values-v7.3.2.yaml` file provided in the `Starter Kit` repository, using an editor of your choice (preferably with `YAML` lint support). For example, you can use [VS Code](https://code.visualstudio.com):

    ```shell
    code 03-setup-ingress-controller/assets/manifests/ambassador-values-v7.3.2.yaml
    ```

    **Note:**

    There are times when you want to re-use the existing `Load Balancer`. This is for preserving your `DNS` settings and other `Load Balancer` configurations. If so, make sure to modify the `ambassador-values-v7.3.2.yaml` file, and add the annotation for your existing `Load Balancer`. Likewise, you can enable `Proxy Protocol` as part of modules section in the `ambassador-values-v7.3.2.yaml` file. Please refer to the `DigitalOcean Kubernetes` guide - [How To Migrate Load Balancers](https://docs.digitalocean.com/products/kubernetes/how-to/migrate-load-balancers) for more details.
5. Finally, install `Ambassador Edge Stack` using `Helm` (a dedicated `ambassador` namespace will be created as well):

    ```shell
    HELM_CHART_VERSION="7.3.2"

    helm install edge-stack datawire/edge-stack --version "$HELM_CHART_VERSION" \
        --namespace ambassador \
        --create-namespace \
        -f "03-setup-ingress-controller/assets/manifests/ambassador-values-v${HELM_CHART_VERSION}.yaml"
    ```

    **Note:**

    A `specific` version for the ambassador `Helm` chart is used. In this case `7.3.2` was picked, which maps to the `2.2.2` release of `Ambassador Edge Stack` (see the output from `Step 2.`). It’s good practice in general, to lock on a specific version. This helps to have predictable results, and allows versioning control via `Git`.

**Observations and results:**

You can verify Ambassador deployment status via:

```shell
helm ls -n ambassador
```

The output looks similar to (notice that the `STATUS` column value is `deployed`):

```text
NAME         NAMESPACE   REVISION  UPDATED                                STATUS      CHART               APP VERSION
edge-stack   ambassador  1         2022-02-03 09:56:55.80197 +0200 EET   deployed    edge-stack-7.3.2   2.2.2
```

Next check Kubernetes resources created for the `ambassador` namespace (notice the `deployment` and `replicaset` resources which should be healthy, as well as the `LoadBalancer` resource having an `external IP` assigned):

```shell
kubectl get all -n ambassador
```

The output looks similar to:

```text
NAME                                    READY   STATUS    RESTARTS   AGE
pod/edge-stack-5bdc64f9f6-hhwdc         1/1     Running   0          6m14s
pod/edge-stack-5bdc64f9f6-xz9jl         1/1     Running   0          6m14s
pod/edge-stack-agent-bcdd8ccc8-m9blv    1/1     Running   0          6m14s
pod/edge-stack-redis-64b7c668b9-69c5p   1/1     Running   0          6m14s

NAME                       TYPE           CLUSTER-IP       EXTERNAL-IP       PORT(S)                      AGE
service/edge-stack         LoadBalancer   10.245.189.240   68.183.252.190    80:30323/TCP,443:30510/TCP   6m14s
service/edge-stack-admin   ClusterIP      10.245.170.181   <none>            8877/TCP,8005/TCP            6m14s
service/edge-stack-redis   ClusterIP      10.245.205.49    <none>            6379/TCP                     6m14s

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.apps/edge-stack         2/2     2            2           6m14s
deployment.apps/edge-stack-agent   1/1     1            1           6m14s
deployment.apps/edge-stack-redis   1/1     1            1           6m14s

NAME                                          DESIRED   CURRENT   READY   AGE
replicaset.apps/edge-stack-5bdc64f9f6         2         2         2       6m14s
replicaset.apps/edge-stack-agent-bcdd8ccc8    1         1         1       6m14s
replicaset.apps/edge-stack-redis-64b7c668b9   1         1         1       6m14s
```

Finally, list all load balancer resources from your `DigitalOcean` account, and print the `IP`, `ID`, `Name` and `Status`:

```shell
doctl compute load-balancer list --format IP,ID,Name,Status
```

The output looks similar to (should contain the new `load balancer` resource created for `Ambassador Edge Stack` in a healthy state):

```text
IP                 ID                                      Name                                Status
68.183.252.190     0471a318-a98d-49e3-aaa1-ccd855831447    acdc25c5cfd404fd68cd103be95af8ae    active
```

In the next step, you will learn how to create the `Listener` CRDs that tells to Ambassador Edge Stack what port to listen on.

## Step 2 - Defining the Listener for Ambassador Edge Stack

The `Listener` CRD defines where, and how, Ambassador Edge Stack should listen for requests from the network (e.g. DO Load Balancer), and which Host definitions should be used to process those requests.

**Note:**

The `Listeners` are never created at the installation, the below steps will guide you how to do it.

A typical `Listener` configuration looks like below:

```yaml
apiVersion: getambassador.io/v3alpha1
kind: Listener
metadata:
  name: http-listener
spec:
  port: 8080
  protocol: HTTPS
  securityModel: XFP
  hostBinding:
    namespace:
      from: ALL
```

Explanations for the above configuration:

- `port`: The network port on which Ambassador Edge Stack should listen.
- `protocol`: The protocol Type on which Ambassador Edge Stack will use.
- `protocolStack`: Allows configuring exactly which protocols will be layered together.
- `securityModel`: Defines how the Listener will decide whether a request is secure or insecure.
- `hostBinding`: Mechanism for determining which Hosts will be associated with this Listener.

**Note:**

Ambassador Edge Stack offers multiple configurations for [protocolStack](https://www.getambassador.io/docs/edge-stack/2.1/topics/running/listener/#securitymodel) and our recommandation is the `XFP` flag to be setup for all the connections to be secure. If the `X-Forwarded-Proto` header is present in the requests the AES will decide automatically to redirect all the requests from HTTP over to HTTPS for greater security.

For more details, please visit the AES [Listener](https://www.getambassador.io/docs/edge-stack/2.2/topics/running/listener/) CRD official documentation.

First, change directory (if not already) where you cloned the `Starter Kit` repository.

```shell
cd Kubernetes-Starter-Kit-Developers
```

Next, apply the manifest to create the `Listener`:

```shell
kubectl apply -f 03-setup-ingress-controller/assets/manifests/ambassador/ambassador_listener.yaml
```

**Observations and results:**

Inspect the AES `Listener`:

```shell
kubectl describe listener.getambassador.io
```

The output looks similar to the following (notice the creation of host bindings via the `Spec.Host Binding` field):

```text
Name:         http-listener
API Version:  getambassador.io/v3alpha1
Kind:         Listener
...
Spec:
  Host Binding:
    Namespace:
      From:        ALL
  Port:            8080
  Protocol:        HTTPS
  Security Model:  XFP
  Stats Prefix:    http-listener
  Events:            <none>

Name:         https-listener
API Version:  getambassador.io/v3alpha1
Kind:         Listener
...
Spec:
  Host Binding:
    Namespace:
      From:        ALL
  Port:            8443
  Protocol:        HTTPS
  Security Model:  XFP
  Stats Prefix:    https-listener
Events:            <none>
```

In the next step, you will learn how to create the `Host` CRDs which tell `Ambassador` how to expose backend hosts (services) to the outside world.

## Step 3 - Defining the Hosts for Ambassador Edge Stack

In a real world scenario each `host` maps to a `service`, so you need a way to tell `AES` about your intentions - meet the [Host](https://www.getambassador.io/docs/edge-stack/2.1/topics/running/host-crd/) CRD. The `Host` CRD can handle `TLS termination` automatically, by using `HTTP-01` ACME challenge to request `TLS certificates` from a well known `Certificate Authority` (like [Let's Encrypt](https://letsencrypt.org/)). Certificates creation and renewal happens automatically once you configure and enable this feature in the `Host` CRD.

The custom `Host` resource defines how `Ambassador Edge Stack` will be visible to the outside world. It collects all the following information in a single configuration resource. The most relevant parts are:

- The `hostname` by which `Ambassador Edge Stack` will be reachable.
- How `Ambassador Edge Stack` should handle `TLS` certificates.
- How `Ambassador Edge Stack` should handle secure and insecure requests.

A typical `Host` configuration looks like below:

```yaml
apiVersion: getambassador.io/v3alpha1
kind: Host
metadata:
  name: echo-host
  namespace: ambassador
spec:
  hostname: echo.starter-kit.online
  acmeProvider:
    email: echo@gmail.com
  tlsSecret:
    name: tls2-cert
  requestPolicy:
    insecure:
      action: Redirect
      additionalPort: 8080
```

Explanations for the above configuration:

- `hostname`: The hostname by which `Ambassador Edge Stack` will be reachable.
- `acmeProvider`: Tells Ambassador Edge Stack what `Certificate Authority` to use, and request certificates from. The `email` address is used by the `Certificate Authority` to notify about any lifecycle events of the certificate.
- `tlsSecret`: The `Kubernetes Secret` name to use for storing the `certificate`, after the Ambassador Edge Stack `ACME challenge` finishes successfully.
- `requestPolicy`: Tells how `Ambassador Edge Stack` should handle secure and insecure requests.

**Notes:**

- The `hostname` must be reachable from the internet so the `CA` can check `POST` to an endpoint in `Ambassador Edge Stack`.
- In general the `registrant email address` is mandatory when using `ACME`, and it should be a valid one in order to receive notifications when the certificates are going to expire.
- The Ambassador Edge Stack built-in `ACME` client knows to handle `HTTP-01` challenges only. For other `ACME` challenge types like `DNS-01` for example, an `external` certificate management tool is required (e.g. [Cert-Manager](https://cert-manager.io)).

For more details, please visit the AES [Host](https://www.getambassador.io/docs/edge-stack/2.1/topics/running/host-crd/) CRD official documentation.

The following examples configure the `TLS` enabled `hosts` for this tutorial: [echo_host](assets/manifests/ambassador/echo_host.yaml) and [quote_host](assets/manifests/ambassador/quote_host.yaml).

Steps to follow:

1. First, change directory (if not already) where you cloned the `Starter Kit` repository.

    ```shell
    cd Kubernetes-Starter-Kit-Developers
    ```

2. Then, apply the manifests:

    ```shell
    kubectl apply -f 03-setup-ingress-controller/assets/manifests/ambassador/echo_host.yaml

    kubectl apply -f 03-setup-ingress-controller/assets/manifests/ambassador/quote_host.yaml
    ```

3. Finally, inspect the `AES` hosts:

    ```shell
    kubectl get hosts -n ambassador
    ```

    The output looks similar to the following:

    ```text
    NAME         HOSTNAME                   STATE     PHASE COMPLETED      PHASE PENDING              AGE
    echo-host    echo.starter-kit.online    Pending   ACMEUserRegistered   ACMECertificateChallenge   3s
    quote-host   quote.starter-kit.online   Pending   ACMEUserRegistered   ACMECertificateChallenge   3s
    ```

**Observations and results:**

It takes around `30s` to get the signed certificate for the hosts. At this point, you have the `Ambassador Edge Stack` installed and the `hosts` configured. But you still don't have the networking (eg. `DNS` and `Load Balancer`) configured to `route` traffic to the `cluster`. The missing parts can be noticed in the `Kubernetes` events of the hosts that you configured earlier.

Take a look and see what happens for the `echo-host`:

```shell
kubectl describe host echo-host -n ambassador
```

The output looks similar to the following:

```text
Events:
  Type     Reason   Age                From                   Message
  ----     ------   ----               ----                   -------
  Normal   Pending  32m                Ambassador Edge Stack  waiting for Host DefaultsFilled change to be reflected in snapshot
  Normal   Pending  32m                Ambassador Edge Stack  creating private key Secret
  Normal   Pending  32m                Ambassador Edge Stack  waiting for private key Secret creation to be reflected in snapshot
  Normal   Pending  32m                Ambassador Edge Stack  waiting for Host status change to be reflected in snapshot
  Normal   Pending  32m                Ambassador Edge Stack  registering ACME account
  Normal   Pending  32m                Ambassador Edge Stack  ACME account registered
  Normal   Pending  32m                Ambassador Edge Stack  waiting for Host ACME account registration change to be reflected in snapshot
  Normal   Pending  16m (x4 over 32m)  Ambassador Edge Stack  tlsSecret "tls2-cert"."ambassador" (hostnames=["echo.starter-kit.online"]): needs updated: tlsSecret does not exist
  Normal   Pending  16m (x4 over 32m)  Ambassador Edge Stack  performing ACME challenge for tlsSecret "tls2-cert"."ambassador" (hostnames=["echo.starter-kit.online"])...
  Warning  Error    16m (x4 over 32m)  Ambassador Edge Stack  obtaining tlsSecret "tls2-cert"."ambassador" (hostnames=["echo.starter-kit.online"]): acme: Error -> One or more domains had a problem:
[echo.starter-kit.online] acme: error: 400 :: urn:ietf:params:acme:error:dns :: DNS problem: SERVFAIL looking up A for echo.starter-kit.online - the domain's nameservers may be malfunctioning
...
```

As seen above, the last `event` tells that there's no `A` record to point to the `echo` host for the `starter-kit.online` domain, which results in a lookup failure. You will learn how to fix this issue, in the next step of the tutorial.

## Step 4 - Configuring DNS for Ambassador Edge Stack

In this step, you will configure `DNS` within your `DigitalOcean` account, using a `domain` that you own. Then, you will create the domain `A` records for each host: `echo` and `quote`. Please bear in mind that `DigitalOcean` is not a domain name registrar. You need to buy a domain name first from [Google](https://domains.google), [GoDaddy](https://uk.godaddy.com), etc.

First, please issue the below command to create a new `domain` (`starter-kit.online`, in this example):

```shell
doctl compute domain create starter-kit.online
```

The output looks similar to the following:

```text
Domain                TTL
starter-kit.online    0
```

**Note:**

**YOU NEED TO ENSURE THAT YOUR DOMAIN REGISTRAR IS CONFIGURED TO POINT TO DIGITALOCEAN NAME SERVERS**. More information on how to do that is available [here](https://www.digitalocean.com/community/tutorials/how-to-point-to-digitalocean-nameservers-from-common-domain-registrars).

Next, you will add required `A` records for the `hosts` you created earlier. First, you need to identify the load balancer `external IP` created by the `Ambassador Edge Stack` deployment:

```shell
kubectl get svc -n ambassador
```

The output looks similar to (notice the `EXTERNAL-IP` column value for the `ambassador` service):

```text
NAME               TYPE           CLUSTER-IP       EXTERNAL-IP       PORT(S)                      AGE
edge-stack         LoadBalancer   10.245.189.240   68.183.252.190    80:30323/TCP,443:30510/TCP   6m14s
edge-stack-admin   ClusterIP      10.245.170.181   <none>            8877/TCP,8005/TCP            6m14s
edge-stack-redis   ClusterIP      10.245.205.49    <none>            6379/TCP                     6m14s
```

Then, add the records (please replace the `<>` placeholders accordingly). You can change the `TTL` value as per your requirement:

```shell
doctl compute domain records create starter-kit.online --record-type "A" --record-name "echo" --record-data "<YOUR_LB_IP_ADDRESS>" --record-ttl "30"

doctl compute domain records create starter-kit.online --record-type "A" --record-name "quote" --record-data "<YOUR_LB_IP_ADDRESS>" --record-ttl "30"
```

**Hint:**

If you have only `one load balancer` in your account, then please use the following snippet:

```shell
LOAD_BALANCER_IP=$(doctl compute load-balancer list --format IP --no-header)

doctl compute domain records create starter-kit.online --record-type "A" --record-name "echo" --record-data "$LOAD_BALANCER_IP" --record-ttl "30"

doctl compute domain records create starter-kit.online --record-type "A" --record-name "quote" --record-data "$LOAD_BALANCER_IP" --record-ttl "30"
```

**Observation and results:**

List the available records for the `starter-kit.online` domain:

```shell
doctl compute domain records list starter-kit.online
```

The output looks similar to the following:

```text
ID           Type    Name     Data                    Priority    Port    TTL     Weight
164171755    SOA     @        1800                    0           0       1800    0
164171756    NS      @        ns1.digitalocean.com    0           0       1800    0
164171757    NS      @        ns2.digitalocean.com    0           0       1800    0
164171758    NS      @        ns3.digitalocean.com    0           0       1800    0
164171801    A       echo     143.244.208.191         0           0       3600    0
164171809    A       quote    143.244.208.191         0           0       3600    0
```

Next, check the `AES` hosts status:

```shell
kubectl get hosts -n ambassador
```

The output looks similar to the following (the `STATE` column should display `Ready`):

```text
NAME         HOSTNAME                   STATE   PHASE COMPLETED   PHASE PENDING   AGE
echo-host    echo.starter-kit.online    Ready                                     2m11s
quote-host   quote.starter-kit.online   Ready                                     2m12s
```

**Note:**

In case the `hosts` are still in a `pending` state, it might be due to the `DNS` propagation delay. Please wait for a couple of minutes, and verify your hosts `STATE` column again.

At this point the network traffic will reach the `AES` enabled cluster, but you need to configure the `backend services paths` for each of the hosts. All `DNS` records have one thing in common: `TTL` or time to live. It determines how long a `record` can remain cached before it expires. Loading data from a local cache is faster, but visitors won’t see `DNS` changes until their local cache expires and gets updated after a new `DNS` lookup. As a result, higher `TTL` values give visitors faster performance, and lower `TTL` values ensure that `DNS` changes are picked up quickly. All `DNS` records require a minimum `TTL` value of `30 seconds`.

Please visit the [How to Create, Edit and Delete DNS Records](https://docs.digitalocean.com/products/networking/dns/how-to/manage-records) page for more information.

In the next step, you will create two simple `backend` services, to help you test the `Ambassador Edge Stack` setup.

## Step 5 - Creating the Ambassador Edge Stack Backend Services

In this step, you will deploy two example `backend` services (applications), named `echo` and `quote` to test the `Ambassador Edge Stack` setup.

You can have multiple `TLS` enabled `hosts` on the same cluster. On the other hand, you can have multiple `deployments` and `services` as well. So for each `backend` application, a corresponding Kubernetes `Deployment` and `Service` has to be created.








