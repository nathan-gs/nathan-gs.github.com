---
title: Serving TensorFlow models on Azure
tags: 
 - azure
 - tensorflow

---
https://blogs.msdn.microsoft.com/wesleyb/2018/02/21/serving-tensorflow-models-on-azure/

1. model download + extract on smb volume
2. start tensorflow image

### Assumptions & requirements
- A running Docker installation

## Steps
1. Create Resource Group `tfonazure`

    ```bash
    az group create --name tfonazure --location westeurope
    ```
2. Create Container Registry (ACR) & login
    ```bash
    az acr create -g tfonazure --name tfonazure --sku Basic
    az acr login --name tfonazure
    az acr update -n tfonazure --admin-enabled true
    ```

3. Build Docker image
    ```bash
        docker build -t "sugyan-tensorflow-mnist:latest" .
        docker tag sugyan-tensorflow-mnist:latest  tfonazure.azurecr.io/sugyan-tensorflow-mnist:latest
        docker push  tfonazure.azurecr.io/sugyan-tensorflow-mnist:latest

    ```

4. Start the container
    ```bash
        az group create --name tfonazure-aci --location westeurope
        ACR_PASSWORD=`az acr credential show --name tfonazure --query "passwords[0].value"`
        az container create \
            -g tfonazure-aci \
            --name mnist \
            --image tfonazure.azurecr.io/sugyan-tensorflow-mnist:latest \
            --cpu 2 \
            --memory 2 \
            --registry-password `az acr credential show --name tfonazure --query "passwords[0].value" | sed 's/"//g'` \
            --ip-address public \
            --ports 80 \
            --location westeurope
    ```