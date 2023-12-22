# Velero-API

> [!WARNING]  
**Attention Users:** This project is in active development, and certain tools or features might still be under construction. We kindly urge you to exercise caution while utilizing the tools within this environment. While every effort is being made to ensure the stability and reliability of the project, there could be unexpected behaviors or limited functionalities in some areas.
We highly recommend thoroughly testing the project in non-production or sandbox environments before implementing it in critical or production systems. Your feedback is invaluable to us; if you encounter any issues or have suggestions for improvement, please feel free to [report them](https://github.com/seriohub/velero-api/issues). Your input helps us enhance the project's performance and user experience.
Thank you for your understanding and cooperation.

## Description

This Python project is designed to communicate with the velero client in the Kubernetes environment. Created as a backend project for [Velero-UI](https://github.com/seriohub/velero-ui).

## Configuration

| FIELD                  | TYPE   | DEFAULT                   | DESCRIPTION                                                  |
|------------------------|--------|---------------------------|--------------------------------------------------------------|
| `K8S_INCLUSTER_MODE`   | Bool   |                           | Enable in cluster mode                                       |
| `K8S_VELERO_NAMESPACE` | String |                           | K8s velero namespace                                         |
| `KUBE_CONFIG_FILE`     | String |                           | Path to your kubeconfig file to access cluster               |
| `DEBUG_LEVEL`          | String |                           | Debug level                                                  |
| `ORIGINS`              | String |                           | Array as string containing url origins allowed               |
| `API_ENDPOINT_URL`     | String | 0.0.0.0                   | Bind socket to this host                                     |
| `API_ENDPOINT_PORT`    | Int    | 8001                      | Bind socket to this port                                     |
| `VELERO_CLI_DEST_PATH` | String | /usr/local/bin            | Path where to extract the velero executable file             |
| `VELERO_CLI_PATH`      | String | /app/velero-client        | path where the compressed velero client archives are located |
| `VELERO_CLI_VERSION` * | String | latest available in image | name of the velero client release to be used                 |


*Currently in the image are the archives of binaries v1.11.1, v1.12.1, v1.12.2. Binaries of different releases can be cmq manually loaded within the container.


## Installation

Clone the repository:

  ``` bash
    git clone https://github.com/seriohub/velero-api.git
    cd velero-api
  ```

### Run native

#### Requirements

- Python 3.x
- Velero client

1. Navigate to the [src](src) folder

2. Dependencies installation:

    ``` bash
    pip install -r requirements.txt
    ```

3. Configuration

    Create and edit .env file under src folder, you can start from [.env.template](src/.env.template) under [src](src) folder.
    Setup parameters in the src/.env file if runs it in the native mode

4. Usage

    Under [src](src) folder run the main script:

    ``` bash
    python3 main.py
    ```
   
### Run in Kubernetes

1. Setup docker image:

   1. Navigate to the root folder
   2. Build image

        ``` bash
        docker build --target velero-api -t <your-register>/<your-user>/velero-api:<tag> -f ./docker/Dockerfile .
        ```

   3. Push image

        ``` bash
        docker push <your-register>/<your-user>/velero-api --all-tags
        ```

      >   [!INFO]  
      If you perform custom image creation and use the files within the k8s folder to deploy to kubernetes, remember to update the 30_deployment.yaml file with references to the created image
   
   >   [!INFO]  
   You can skip the *Setup docker image* and use a deployed image published on DockerHub.<br>
   Docker hub: https://hub.docker.com/r/dserio83/velero-api

2. Kubernetes create objects

   1. Navigate to the [k8s](k8s) folder

   2. Create namespace:

        ``` bash
        kubectl create ns velero-api
        ```

   3. Create the ConfigMap:

      >   [!WARNING]  
      Set the parameters in the 10_config_map.yaml file before applying it according to your environment.
   
      ``` bash
       kubectl apply -f 10_config_map.yaml -n velero-api
       ```

   4. Create the RBAC:

       ``` bash
        kubectl apply -f 20_service_account.yaml -n velero-api
       ```
   
   5. Create the RBAC:

       ``` bash
        kubectl apply -f 21_cluster_role.yaml
       ```

   6. Create the RBAC:

      >   [!WARNING]  
      If you use a namespace with name other than **velero-api** update the [*22_cluster_role_binding.yaml*](k8s/22_cluster_role_binding.yaml) file before applying it

      ``` bash
       kubectl apply -f 22_cluster_role_binding.yaml
      ```

   7. Create the Deployment:

       ``` bash
        kubectl apply -f 30_deployment.yaml -n velero-api
       ```
   
   8. Create the Service:

      >   [!WARNING]  
      Customizes the 40_service.yaml file before applying it according to your environment.

       ``` bash
        kubectl apply -f 40_service.yaml -n velero-api
       ```

## Test Environment

The project is developed, tested and put into production on several clusters with the following configuration

1. Kubernetes v1.28.2
2. Velero Server 1.11.1/Client v1.11.1
3. Velero Server 1.12.1/Client v1.12.1

## How to Contribute

1. Fork the project
2. Create your feature branch

    ``` bash
    git checkout -b feature/new-feature
    ```

3. Commit your changes

    ``` bash
   git commit -m 'Add new feature'
   ```

4. Push to the branch

    ``` bash
   git push origin feature/new-feature
   ```

5. Create a new pull request

## License

This project is licensed under the [Apache 2.0 license](LICENSE).

---

Feel free to modify this template according to your project's specific requirements.

In case you need more functionality, create a PR. If you find a bug, open a ticket.
