az storage account create \
  --name <STORAGE_ACCOUNT_NAME> \
  --resource-group <RESOURCE_GROUP> \
  --location <LOCATION> \
  --sku Standard_LRS


az aks update \
  --resource-group <RESOURCE_GROUP> \
  --name <AKS_CLUSTER_NAME> \
  --enable-azure-files-csi-driver

kubectl get csinodes

az storage account keys list \
  --resource-group <RESOURCE_GROUP> \
  --account-name <STORAGE_ACCOUNT_NAME> \
  --query "[0].value" --output tsv
  
kubectl create secret generic azure-secret \
  --from-literal=azurestorageaccountname=<STORAGE_ACCOUNT_NAME> \
  --from-literal=azurestorageaccountkey=<STORAGE_ACCOUNT_KEY> \
  --namespace nginx-namespace
