# Function app that processes image using HTTP triggers
func azure functionapp fetch-app-settings <APP_NAME>
func azure functionapp publish <APP_NAME>
@Microsoft.KeyVault(SecretUri=https://<YourVaultName>.vault.azure.net/secrets/<SecretName>/<SecretVersion>)
