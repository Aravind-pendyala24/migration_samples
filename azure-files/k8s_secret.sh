kubectl create secret generic azure-file-secret \
  --from-literal=azurestorageaccountname=<STORAGE_ACCOUNT> \
  --from-literal=azurestorageaccountkey=<STORAGE_ACCOUNT_KEY>
