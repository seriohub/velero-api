# Velero-API

> [!WARNING]  
**Attention Users:** This project is in active development, and certain tools or features might still be under construction. We kindly urge you to exercise caution while utilizing the tools within this environment. While every effort is being made to ensure the stability and reliability of the project, there could be unexpected behaviors or limited functionalities in some areas.
We highly recommend thoroughly testing the project in non-production or sandbox environments before implementing it in critical or production systems. Your feedback is invaluable to us; if you encounter any issues or have suggestions for improvement, please feel free to [report them](https://github.com/seriohub/velero-api/issues). Your input helps us enhance the project's performance and user experience.
Thank you for your understanding and cooperation.

## Description

This Python project is designed to communicate with the velero client in the Kubernetes environment. Created as a backend project for [Velero-UI](https://github.com/seriohub/velero-ui).

## Configuration

| FIELD                             | TYPE      | DEFAULT                   | DESCRIPTION                                                                                                          |
|-----------------------------------|-----------|---------------------------|----------------------------------------------------------------------------------------------------------------------|
| `CONTAINER_MODE`                  | Bool      | False                     | Enabled in is deployed in a container outside k8s cluster                                                            |
| `K8S_IN_CLUSTER_MODE`             | Bool      | False                     | Enabled if is deployed in a cluster                                                                                  |
| `K8S_VELERO_NAMESPACE`            | String    |                           | K8s Velero namespace                                                                                                 |
| `DEBUG_LEVEL`                     | String    |                           | Debug level                                                                                                          |
| `ORIGINS`                         | String    |                           | Array as string containing url origins allowed                                                                       |
| `API_ENDPOINT_URL`                | String    | 0.0.0.0                   | Socket bind host                                                                                                     |
| `API_ENDPOINT_PORT`               | Int       | 8001                      | Socket bind port                                                                                                     |
| `VELERO_CLI_DEST_PATH`            | String    | /usr/local/bin            | Path where to extract the velero executable file                                                                     |
| `VELERO_CLI_PATH`                 | String    | /app/velero-client        | Path where the compressed velero client archives are located                                                         |
| `VELERO_CLI_VERSION` *            | String    | latest available in image | Name of the velero client release to be used                                                                         |
| `API_ENABLE_DOCUMENTATION`        | BOOL      | True                      | Enabled/Disabled the fastapi documentation user interfaces                                                           |   
| `API_TOKEN_EXPIRATION_MIN`        | Int       | 30                        | Token validity after the creation (minutes)                                                                          |   
| `SECURITY_PATH_DATABASE`          | String    | ./test                    | Path where create the SQL-Lite database used for storing the users credentials                                       |   
| `SECURITY_TOKEN_KEY` **           | String    |                           | Secret key used for JWT creation                                                                                     |   
| `SECURITY_DISABLE_USERS_PWD_RATE` | Bool      | False                     | If True user can have a weak password, otherwise is required a strong password                                       |   
| `API_RATE_LIMITER_L1`             | String    | 60:120                    | Rate limiter: 60 seconds  max requests 10                                                                            |    
| `API_RATE_LIMITER_CUSTOM_L1` ***  | String    | Security:xxx:60:20        | Rate limiter for specific tag/endpoint: Security (tag) xxx (all endpoints under the tag) 60 seconds  max requests 20 |
| `API_RATE_LIMITER_CUSTOM_L2` ***  | String    | Info:info:60:500          | Rate limiter for specific tag/endpoint: Info (tag) xxx (all endpoints under the tag) 60 seconds  max requests 500    |


* *Currently, the docker image contains the binaries **v1.11.1**, **v1.12.1** and **v1.12.2**. Different binaries releases can be manually loaded within the container.

* **To generate a secure random secret key use the command: 
  
  ``` bash
   openssl rand -hex 32
  ```
* ***You can define up to 100 custom rate limiters (from the key API_RATE_LIMITER_CUSTOM_L1 to API_RATE_LIMITER_CUSTOM_L99). Rules can be designed for a tag (eg Security, Info, Backup, Schedule, etc) or for a specific endpoint (eg backup/update-expitaration, utils/version, etc).
>     [!WARNING]  The env keys must be added consecutively (API_RATE_LIMITER_CUSTOM_L1,API_RATE_LIMITER_CUSTOM_L2,API_RATE_LIMITER_CUSTOM_L3...API_RATE_LIMITER_CUSTOM_L99

>     [!WARNING]  Replace the subdomains("\"), the character "-", "{", "}"    with the "_". 
The description field of each endpoint describes the key to configure the customized rate limiter and the actual setup.

- Example : if we want to create a rule for the specific endpoint "/backup/get-storage-classes" (tag: Backup) it will be:<br>Backup:backup_get_storage_classes:60:600

The default rate limiter is defined by the key API_RATE_LIMITER_L1

To find out all the endpoints exposed by the API project, you can use the Swagger UI documentation (<API IP address>/docs).
>     [!WARNING] If you disable the api documentation (API_ENABLE_DOCUMENTATION key), you are not able to reach the endpoint /docs.

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

    Create and edit .env file under [src](src) folder, you can start from [.env.template](src/.env.template) under [src](src) folder.
    Setup parameters (mandatory: SECURITY_TOKEN_KEY and ORIGINS) in the src/.env file if runs it in the native mode.

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

      >   [!WARNING]  
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
      Set the parameters in the 10_config_map.yaml file before applying it according to your environment. Set up SECURITY_TOKEN_KEY and ORIGINS parameters.
   
      ``` bash
       kubectl apply -f 10_config_map.yaml -n velero-api
       ```

   4. Create the RBAC Service Account:

       ``` bash
        kubectl apply -f 20_service_account.yaml -n velero-api
       ```
   
   5. Create the RBAC Cluster Role:

       ``` bash
        kubectl apply -f 21_cluster_role.yaml
       ```

   6. Create the RBAC Cluster Role Binding:

      >   [!WARNING]  
      If you use a namespace with name other than **velero-api** update the [*22_cluster_role_binding.yaml*](k8s/22_cluster_role_binding.yaml) file before applying it

      ``` bash
       kubectl apply -f 22_cluster_role_binding.yaml
      ```

   7. Create PVC (Optional)
      By default, the user database is created in the path configured in the SECURITY_PATH_DATABASE parameter of the configuration map. To ensure data persistence, the path can be customized using a PVC.
   
      >   [!WARNING]  
      Set storage class name in [*25_pvc.yaml*](k8s/25_pvc.yaml) before applying it.
      
      ``` bash
       kubectl apply -f 25_pvc.yaml -n velero-api
      ```
   
   8. Create the Deployment:
      
      If you created a pvc:
   
       ``` bash
        kubectl apply -f 30_deployment.yaml -n velero-api
       ```
      
      otherwise:

      ``` bash
        kubectl apply -f 30_deployment_no_pvc.yaml -n velero-api
      ```      
   
   9. Create the Service:

      >   [!WARNING]  
      Customizes the 40_service.yaml file before applying it according to your environment.

       ``` bash
        kubectl apply -f 40_service.yaml -n velero-api
       ```
## Test the API with the fastapi interface tool

1. Check if the parameter "API_ENABLE_DOCUMENTATION" is set to 1
2. Open the browser and navigate to the api endpoint url/docs (example http://127.0.0.1/docs)
3. Click the button "Authorize"
4. The default credential are:
5. Username: admin
6. password: admin

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
