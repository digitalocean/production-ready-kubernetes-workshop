# Appendix

## [Create a Kubernetes Cluster from the DigitalOcean Control Panel](https://docs.digitalocean.com/products/kubernetes/how-to/create-clusters/)
1. From the Create menu in the [control panel](https://cloud.digitalocean.com/), click Kubernetes.
1. Select a Kubernetes version. The latest version is selected by default and is the best choice if you have no specific need for an earlier version.
1. Choose a datacenter region.
1. Customize the default node pool, choose the node pool names, and add additional node pools.
1. Name the cluster, select the project you want the cluster to belong to, and optionally add a tag.
1. Click Create Cluster. Provisioning the cluster takes several minutes.
1. Download the cluster configuration file by clicking Actions, then Download Config from the cluster home page.

## API Endpoints for the OTS App
1. **POST** */secrets*
    1. Vars
        1. message - required - The message to encrypt
        1. passphrase - required - The passphrase for the message
        1. expiration_time - optional - How long for the message to persist in seconds. Default is 604800
    1. Returns JSON
        1. Vars
            1. id - unique ID of the secret for retrieval
            1. success - Boolean
    1. **POST** */secrets/<id>*
        1. Vars
            1. passphrase - required - The passphrase to unlock the secret
        1. Returns JSON
            1. Vars
                1. message - The decrypted message
                1. success - Boolean
1. If the message doesn't exist, has already been read, or has expired
    ```json
    {
        "message": "This secret either never existed or it was already read",
        "success": "False"
    }
    ```

## Use `httpie` to verify your application works in the cluster 
1. Find the IP address of your pod and copy one address to your clipboard
    ```shell
    kubectl get pods -n secrets-app -o wide
    ```
1. Create a utilities pod
    ```shell
    kubectl apply -f kubernetes/utilities.yaml
    ```
    1. Get the unique id of the pod and copy that to your clipboard.
    ```shell
    kubectl get pods -n secrets-app
    ```
    
    You will see something like this:
    
    ```shell
    NAME                              READY   STATUS    RESTARTS   AGE
    one-time-secret-5b757b96f-6nbm7   1/1     Running   0          10m
    one-time-secret-5b757b96f-b9t54   1/1     Running   0          10m
    one-time-secret-5b757b96f-cjtsx   1/1     Running   0          10m
    utilities-6d8f574894-kt59m        1/1     Running   0          10s
    ```
1. Exec into that pod 
    ```shell
    kubectl exec -it <utilities_pod_name> -n secrets-app -- /bin/sh
    ```
1. Install `httpie`
    ```shell
    curl -SsL https://packages.httpie.io/deb/KEY.gpg | apt-key add - && curl -SsL -o /etc/apt/sources.list.d/httpie.list https://packages.httpie.io/deb/httpie.list && apt update && apt install httpie
    ```
    The installation will take a minute or two. 
1.  Test write 
    ```bash
    http POST <pod_ip_address>:8080/secrets message="YOUR_MESSAGE" passphrase="YOUR_PASSPHRASE"
    ```
    1. Sample Response
    ```json
    {
        "id": "ea54d2701885400cafd0c11279672c8f",
        "success": "True"
    }
    ```
1. Test read, using the id from above
    ```bash
    http POST <pod_ip_address>:8080/secrets/<id> passphrase="YOUR_PASSPHRASE"
    ```
    1. Sample Response
    ```json
    {
        "message": "Hello there",
        "success": "True"
    }
    ```
1. Exit out of the utilities pod
    ```shell
    exit
    ```

## [Destroy your cluster from the Cloud Console](https://docs.digitalocean.com/products/kubernetes/how-to/destroy-clusters/)
1. Go to the Kubernetes page in the control panel. From the cluster’s More menu, select Destroy and click Destroy. 
1. In the Destroy Kubernetes cluster dialog box, select the resources, such as load balancers and block storage volumes, associated with the cluster to delete them automatically when the cluster is deleted. Enter the name of the cluster, then click Destroy to confirm.


---
## Step 1 - Installing the Ambassador Edge Stack

In this step, you will deploy the `Ambassador Edge Stack` to your `DOKS` cluster, via `Helm`.

1. Add the `Helm` repo, and list the available `charts`:

    ```shell
    helm repo add datawire https://app.getambassador.io

    helm repo update datawire

    helm search repo datawire
    ```

    The output looks similar to the following:

    ```text
        NAME                        	CHART VERSION	APP VERSION	DESCRIPTION
        datawire/ambassador         	6.9.5        	1.14.4     	A Helm chart for Datawire Ambassador
        datawire/ambassador-operator	0.3.0        	v1.3.0     	A Helm chart for Kubernetes
        datawire/edge-stack         	8.0.0        	3.0.0      	A Helm chart for Ambassador Edge Stack
        datawire/emissary-ingress   	8.0.0        	3.0.0      	A Helm chart for Emissary Ingress
        datawire/telepresence       	2.6.8        	2.6.8      	A chart for deploying the server-side component...
        edge-stack/ambassador       	6.9.4        	1.14.3     	A Helm chart for Datawire Ambassador
        edge-stack/edge-stack       	7.3.2        	2.2.2      	A Helm chart for Ambassador Edge Stack
        edge-stack/emissary-ingress 	7.3.2        	2.2.2      	A Helm chart for Emissary Ingress  
    ```

    **Note:**

    The chart of interest is `datawire/edge-stack`, which will install `Ambassador Edge Stack` on the cluster. Please visit the [ambassador-edge-stack](https://github.com/emissary-ingress/emissary) page, for more details about this chart.

3. Install the Ambassador Edge Stack CRDs for `getambassador.io/v3alpha1` and `getambassador.io/v2`.

    ```shell
    kubectl apply -f https://app.getambassador.io/yaml/edge-stack/3.0.0/aes-crds.yaml

    kubectl wait --timeout=90s --for=condition=available deployment emissary-apiext -n emissary-system
    ```

4. Then, open and inspect the [ambassador-values.yaml](./ambassador/ambassador-values.yaml) file.

    ```shell
    code ambassador/ambassador-values.yaml
    ```


5. Finally, install `Ambassador Edge Stack` using `Helm` (a dedicated `ambassador` namespace will be created as well):

    ```shell
    HELM_CHART_VERSION="8.0.0"

    helm install edge-stack datawire/edge-stack --version "$HELM_CHART_VERSION" \
        --namespace ambassador \
        --create-namespace \
        -f "ambassador/ambassador-values.yaml"
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
NAME      	NAMESPACE 	REVISION	UPDATED                             	STATUS  	CHART           	APP VERSION
edge-stack	ambassador	1       	2022-07-05 17:44:59.266134 -0600 MDT	deployed	edge-stack-8.0.0	3.0.0
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



Next, apply the manifest to create the `Listener`:

```shell
kubectl apply -f ambassador/listener.yaml
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


```
HELM_CHART_VERSION="8.0.0"

helm upgrade edge-stack datawire/edge-stack --version "$HELM_CHART_VERSION" \
--namespace ambassador  \
-f "ambassador/ambassador-values.yaml"
```




