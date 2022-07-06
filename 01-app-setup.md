# Chapter 1 - Containerize an Application

## Instructions
1. Fork and Clone the [Workshop Repository](https://github.com/digitalocean/production-ready-kubernetes-workshop)
1. Have your developer environment setup
    1. You will need Docker and httpie on your local device
        1. Install [Docker](https://docs.docker.com/get-docker/)
        1. (optional) Install [httpie](https://httpie.io/cli) 

1. Navigate to the Python Directory
    ```bash
    cd python
    ```
1. (Optional) Review API endpoints in the [Appendix](./06-appendix.md#api-endpoints-for-the-ots-app)

1. (Optional) Create a Redis Cluster.
    - You can deploy the application without a Redis cluster, but there will be no data persistence.

    ```bash
    doctl databases create workshop-redis-cluster --engine redis --region sfo3
    ```
    
1. Build the docker container 
    ```bash
    docker build -t ots .
    ```
1. Add your Redis credentials and run the image locally 
    ```bash
    docker run -p 8080:8080 --env DB_HOST="<REDIS_HOST_URL>" --env DB_PORT="25061" --env DB_PASSWORD="<REDIS_PASSWORD>" --env DB_SSL=True ots
    ```
1. Test with `httpie`
    1. Test write 
        ```bash
        http POST localhost:8080/secrets message="YOUR_MESSAGE" passphrase="YOUR_PASSPHRASE"
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
        http POST localhost:8080/secrets/<id> passphrase="YOUR_PASSPHRASE"
        ```
        1. Sample Response
        ```json
        {
            "message": "Hello there",
            "success": "True"
        }
        ```

1. Create a DO Container Registry 
    ```bash
    doctl registry create <your-registry-name> --region sfo3
    ```

1. Use the registry login command to authenticate Docker with your registry:
    ```bash
    doctl registry login
    ```

1. Use the docker tag command to tag your image with the fully qualified destination path:
    ```bash
    docker tag ots registry.digitalocean.com/<your-registry>/ots:0.0.1
    ```

1. Use the docker push command to upload your image:
    ```bash
    docker push registry.digitalocean.com/<your-registry>/ots:0.0.1
    ```

1. Allow your image to be used with your Kubernetes Cluster
    - Visit the registry page and click the Settings tab.
    - In the DigitalOcean Kubernetes integration section, click Edit to display the available Kubernetes clusters.
    - Select the clusters and click Save.
    - The default service account in each of those namespaces is updated to include the secret in its image pull secret.

### Learn More
- [DigitalOcean Container Registry Quickstart](https://docs.digitalocean.com/products/container-registry/quickstart/)