1. 2 API endpoints
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


1. [Create a Kubernetes Cluster from the DigitalOcean Control Panel](https://docs.digitalocean.com/products/kubernetes/how-to/create-clusters/)
    1. From the Create menu in the [control panel](https://cloud.digitalocean.com/), click Kubernetes.
    1. Select a Kubernetes version. The latest version is selected by default and is the best choice if you have no specific need for an earlier version.
    1. Choose a datacenter region.
    1. Customize the default node pool, choose the node pool names, and add additional node pools.
    1. Name the cluster, select the project you want the cluster to belong to, and optionally add a tag.
    1. Click Create Cluster. Provisioning the cluster takes several minutes.
    1. Download the cluster configuration file by clicking Actions, then Download Config from the cluster home page.

1.  Configure `doctl` 
    1. [Create an API token](https://cloud.digitalocean.com/account/api/)
    1. Export your token as an environment variable called `DO_TOKEN`.
    ```sh
    export DO_TOKEN="<YOUR_DO_TOKEN>"
    ```
    **Note**
     Since Windows doesn't support enviornment variables, Windows users should keep the token on their clipboard to easily paste.
    1. [Use the API token to grant account access to doctl](https://docs.digitalocean.com/reference/doctl/how-to/install/#step-3-use-the-api-token-to-grant-account-access-to-doctl)
    ```sh
    doctl auth init 
    ```
    1. [Validate that doctl is working](https://docs.digitalocean.com/reference/doctl/how-to/install/#step-4-validate-that-doctl-is-working)
    ```sh
    doctl account get
    ```

    You should see output like this: 

    ```sh
    Email                            Droplet Limit    Email Verified    UUID                                    Status
    kschlesinger@digitalocean.com    25               true              4ba4b281-ie98-4888-a843-2365cf961232    active
    ```


1. Use `httpie` to verify your application works over the internet
    1.  Test write 
        ```bash
        http POST <load_balancer_ip_address>/secrets message="YOUR_MESSAGE" passphrase="YOUR_PASSPHRASE"
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
        http POST <load_balancer_ip_address/secrets/<id> passphrase="YOUR_PASSPHRASE"
        ```
        1. Sample Response
        ```json
        {
            "message": "Hello there",
            "success": "True"
        }
        ```


1. Use `httpie` to verify your application works in the cluster 
    1. Find the IP address of your pod and copy one address to your clipboard
        ```shell
        kubectl get pods -n secrets-app -o wide
        ```
    1. Create a utilities pod
        ```shell
        kubectl apply -f kubernetes/manifests/utilities.yaml
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

1. [Destroy your cluster](https://docs.digitalocean.com/products/kubernetes/how-to/destroy-clusters/)
    1. Go to the Kubernetes page in the control panel. From the cluster’s More menu, select Destroy and click Destroy. 
    1. In the Destroy Kubernetes cluster dialog box, select the resources, such as load balancers and block storage volumes, associated with the cluster to delete them automatically when the cluster is deleted. Enter the name of the cluster, then click Destroy to confirm.

1. Celebrate! You just deployed an application to Kubernetes and directed traffic to it from the internet! 🎉