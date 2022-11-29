kubectl exec -i vault-0 -- vault auth enable kubernetes
kubectl exec -it vault-0 -- sh -c '
vault write auth/kubernetes/config \
    kubernetes_host="https://$KUBERNETES_PORT_443_TCP_ADDR:443"
'

kubectl exec -it vault-0 -- sh -c '
vault policy write dev - <<EOF
path "*" {
  capabilities = ["read"]
}
'

kubectl exec -it vault-0 -- sh -c '
vault write auth/kubernetes/role/dev \
    bound_service_account_names=default \
    bound_service_account_namespaces=default \
    policies=dev \
    ttl=20m
'

kubectl exec -it vault-0 -- sh -c '
vault kv put secret/app \
  oidc-rp-client-id=1337 \
  oidc-rp-client-secret=supersecret \
  secret-key=dev \
  debug=true \
  postgresql-main-host=database \
  postgresql-main-admin=dev \
  postgresql-main-password=dev \
  postgresql-main-database=dev

vault kv get secret/app
'
