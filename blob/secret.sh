kubectl create secret generic blobfuse-secret \
  --from-literal=azurestorageaccountname=<STORAGE_ACCOUNT> \
  --from-literal=azurestorageaccountkey=<STORAGE_KEY>
