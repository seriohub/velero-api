# Velero-API

> [!WARNING]  
**Attention Users:** This project is in active development, and certain tools or features might still be under construction. We kindly urge you to exercise caution while utilizing the tools within this environment. While every effort is being made to ensure the stability and reliability of the project, there could be unexpected behaviors or limited functionalities in some areas.
We highly recommend thoroughly testing the project in non-production or sandbox environments before implementing it in critical or production systems. Your feedback is invaluable to us; if you encounter any issues or have suggestions for improvement, please feel free to [report them](https://github.com/seriohub/velero-api/issues). Your input helps us enhance the project's performance and user experience.
Thank you for your understanding and cooperation.

## Description

This Python project, developed as a backend for [Velero-UI](https://github.com/seriohub/velero-ui), is designed to communicate with Kubernetes and the Velero client within the Kubernetes environment.

See [changelog](CHANGELOG.md) for details.

## Configuration

| FIELD                             | TYPE      | DEFAULT                              | DESCRIPTION                                                                                                          |
|-----------------------------------|-----------|--------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| `CONTAINER_MODE`                  | Bool      | False                                | Enabled in is deployed in a container outside k8s cluster                                                            |
| `K8S_IN_CLUSTER_MODE`             | Bool      | False                                | Enabled if is deployed in a cluster                                                                                  |
| `K8S_VELERO_NAMESPACE`            | String    | velero                               | K8s Velero namespace                                                                                                 |
| `K8S_VELERO_UI_NAMESPACE`         | String    | velero-ui                            | K8s Velero namespace                                                                                                 |
| `DEBUG_LEVEL`                     | String    | info                                 | Print level  (Critical, error, warning, info, debug)                                                                 |
| `ORIGINS_1` (1)                   | String    | <http://localhost:3000>              | Allowed origin                                                                                                       |
| `ORIGINS_2` (1)                   | String    | <http://127.0.0.1:3000>              | Allowed origin                                                                                                       |
| `ORIGINS_3` (1)                   | String    | *                                    | Allowed origin                                                                                                       |
| `API_ENDPOINT_URL`                | String    | 0.0.0.0                              | Socket bind host                                                                                                     |
| `API_ENDPOINT_PORT`               | Int       | 8001                                 | Socket bind port                                                                                                     |
| `VELERO_CLI_DEST_PATH`            | String    | /usr/local/bin                       | Path where to extract the velero executable file                                                                     |
| `VELERO_CLI_PATH`                 | String    | /app/velero-client                   | Path where the compressed velero client archives are located                                                         |
| `VELERO_CLI_PATH_CUSTOM`          | String    | /app/velero-client-binary            | Path where the user can store manually the binary file                                                               |
| `VELERO_CLI_VERSION` (2)          | String    | latest available in velero-api-image | Name of the velero client release to be used                                                                         |
| `DOWNLOAD_TMP_FOLDER`             | String    | /tmp/velero-api                      | Destination folder when executing *velero backup download*                                                           |
| `API_ENABLE_DOCUMENTATION`        | BOOL      | True                                 | Enabled/Disabled the fastapi documentation user interfaces                                                           |
| `API_TOKEN_EXPIRATION_MIN`        | Int       | 30                                   | Token validity after the creation (minutes)                                                                          |
| `SECURITY_PATH_DATABASE`          | String    | ./test                               | Path where create the SQL-Lite database used for storing the users credentials                                       |
| `SECURITY_TOKEN_KEY` (3)          | String    |                                      | Secret key used for JWT creation                                                                                     |
| `SECURITY_DISABLE_USERS_PWD_RATE` | Bool      | False                                | If True user can have a weak password, otherwise is required a strong password                                       |
| `API_RATE_LIMITER_L1`             | String    | 60:120                               | Rate limiter: 60 seconds  max requests 10                                                                            |
| `API_RATE_LIMITER_CUSTOM_L1` (4)  | String    | Security:xxx:60:20                   | Rate limiter for specific tag/endpoint: Security (tag) xxx (all endpoints under the tag) 60 seconds  max requests 20 |
| `API_RATE_LIMITER_CUSTOM_L2` (4)  | String    | Info:info:60:500                     | Rate limiter for specific tag/endpoint: Info (tag) xxx (all endpoints under the tag) 60 seconds  max requests 500    |
| `RESTIC_PASSWORD`                 | String    | static-passw0rd                      |                                                                                                                      |
| `AWS_ACCESS_KEY_ID`               | String    |                                      | AWS_ACCESS_KEY_ID                                                                                                    |
| `AWS_SECRET_ACCESS_KEY`           | String    |                                      | AWS_SECRET_ACCESS_KEY                                                                                                |

1. You can define up to 100 allowed origins that should be permitted to make cross-origin requests. An origin is the combination of protocol (http, https), domain (myapp.com, localhost) and port (80, 443, 8001)

2. The Velero client is downloaded when the pod is started according to the environment variable VELERO_CLI_VERSION. In the event of a connection problem, the version 1.12.1 contained within the Velero API image will be utilized.
Set VELERO_CLI_VERSION as the following example: v1.12.2

3. To generate a secure random secret key use the command:
  
   ``` bash
   openssl rand -hex 32
   ```

4. You can define up to 100 custom rate limiters (from the key API_RATE_LIMITER_CUSTOM_L1 to API_RATE_LIMITER_CUSTOM_L99). Rules can be designed for a tag (eg Security, Info, Backup, Schedule, etc) or for a specific endpoint (eg backup/update-expitaration, utils/version, etc).

   >   [!WARNING]  
   Replace the characters **\\** **-** **{** **}** in endpoint urls with the **_**

   The description field of each endpoint describes the key to configure the customized rate limiter and the actual setup.

   - Example : if we want to create a rule for the specific endpoint "/backup/get-storage-classes" (tag: Backup) it will be: </br> Backup:backup_get_storage_classes:60:600

   The default rate limiter is defined by the key **API_RATE_LIMITER_L1**

   To find out all the endpoints exposed by the API project, you can use the Swagger UI documentation **< API IP address >/api/v1/docs**.

   >   [!WARNING]  
   If you disable the api documentation (API_ENABLE_DOCUMENTATION key), you are not able to reach the endpoint /docs.

## In case of Upgrade

In case of upgrades from previous versions, ensure that Kubernetes deployment files are aligned with the latest available version.

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

#### Install with HELM

   See [helm readme](https://github.com/seriohub/velero-helm)

#### Install with Kubernetes YAML

1. Setup docker image:

   >   [!INFO]  
   You can skip the *Setup docker image* step and use a deployed image published on DockerHub.</br>
   Docker hub: <https://hub.docker.com/r/dserio83/velero-api>

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
      If you perform custom image creation and use the files within the k8s folder to deploy to kubernetes, remember to update the 30_deployment.yaml or 30_deployment_no_pvc.yaml file with references to the created image.

2. Kubernetes create objects

   These files are configured assuming that the namespace where Velero is deployed is named "velero," and the namespace where "velero-api" is deployed is named "velero-ui". 
   Please update the following files according to your environment if necessary:
   - [*22_cluster_role_binding.yaml*](k8s/22_cluster_role_binding.yaml)
   - [*23_role.yaml*](k8s/23_role.yaml)
   - [*24_role_binding.yaml*](k8s/24_role_binding.yaml)
   </br>
   </br>
   1. Navigate to the [k8s](k8s) folder

   2. Create namespace:

      ``` bash
      kubectl create ns velero-ui
      ```

   3. Create the ConfigMap:

      >   [!WARNING]  
      Set the parameters in the 10_config_map.yaml file before applying it according to your environment. Set up **SECURITY_TOKEN_KEY**.

      ``` bash
      kubectl apply -f 10_config_map.yaml -n velero-ui
      ```

   4. Create the RBAC Service Account:

      ``` bash
      kubectl apply -f 20_service_account.yaml -n velero-ui
      ```

   5. Create the RBAC Cluster Role:

      ``` bash
      kubectl apply -f 21_cluster_role.yaml
      ```

   6. Create the RBAC Cluster Role Binding:

      ``` bash
      kubectl apply -f 22_cluster_role_binding.yaml
      ```

   7. Create the RBAC Role:

      ``` bash
      kubectl apply -f 23_role.yaml -n velero-ui
      ```

   8. Create the RBAC Role Binding:

      ``` bash
      kubectl apply -f 24_role_binding.yaml -n velero-ui
      ```

   9. Create PVCs (*Optional*)

      1. Database path : By default, the user database is created in the path configured in the SECURITY_PATH_DATABASE parameter of the configuration map. To ensure data persistence, the path can be customized using a PVC.
      2. Custom folder for velero binaries: The user can store the binaries of new versions to avoid downloading the file directly from the code. The env parameter is VELERO_CLI_PATH_CUSTOM.  

      >   [!WARNING]  
      Set storage class name in [25_pvc.yaml](k8s/25_pvc.yaml) before applying it.

      ``` bash
      kubectl apply -f 25_pvc.yaml -n velero-ui
      ```

   10. Create the Deployment:

      If you created a pvc:

      ``` bash
      kubectl apply -f 30_deployment.yaml -n velero-ui
      ```

      otherwise:

      ``` bash
      kubectl apply -f 30_deployment_no_pvc.yaml -n velero-ui
      ```

   11. Create the Service:

       The exposed port must be type of **LoadBalancer** or **Nodeport**
      >   [!WARNING]  
      Customizes the [40_service_lb.yaml](k8s/40_service_lb.yaml) or [40_service_nodeport.yaml](k8s/40_service_nodeport.yaml) file before applying it according to your environment.

      ``` bash
      kubectl apply -f 40_service_lb.yaml -n velero-ui
      ```

      or

      ``` bash
      kubectl apply -f 40_service_nodeport.yaml -n velero-ui
      ```

## Test the API running with the fastapi interface tool

### Check running

  1. Check if the parameter "API_ENABLE_DOCUMENTATION" is set to 1
  2. Open the browser and navigate to the api endpoint url/docs (example http://< ip service >/docs)
  3. Check alive message

### Check API

  1. Check if the parameter "API_ENABLE_DOCUMENTATION" is set to 1
  2. Open the browser and navigate to the api endpoint url/docs (example http://< ip service >/api/v1/docs)
  3. Click the button "Authorize"
  4. The default credential are:
  5. Username: admin
  6. password: admin

## Test Environment

The project is developed, tested and put into production on several clusters with the following configurations:

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
