# Obtain Vault client certificate

This action obtains a Vault client x509 certificate.

A separate action is needed for this as the standard upstream [vault-action](https://github.com/hashicorp/vault-action)
only supports `GET` requests against Vault, while obtaining a PKI certificate
is a `POST` operation. Therefore, that action is only used here for Vault login,
and we then make a certificate request via `curl`.

## Inputs

| key             | default        | description                                             |
|-----------------|----------------|---------------------------------------------------------|
| backend         | `client/alpha` | Vault certificate backend to use (default usually okay) |
| cn              | *none*         | Vault certificate common name                           |
| role            | *none*         | Vault certificate backend role to use                   |
| ttl             | `14400`        | Certificate TTL (in seconds; maximum 1 day)             |
| vault-auth-path | `jwt/github`   | Vault auth backend path to use (default usually okay)   |
| vault-auth-role | *none*         | Vault auth role to use for obtaining certificate        |
| vault-url       | *none*         | Vault API URL                                           |

## Outputs

| key         | description                                            |
|-------------|--------------------------------------------------------|
| ca_chain    | Certificate chain returned by Vault (PEM format)       |
| certificate | Certificate (public part) issued by Vault (PEM format) |
| private_key | Private key for the issued certificate (PEM format)    |


## Example usage

```
---
name: Run action using Vault cert

"on":
  push:
    branches: [develop]

jobs:
  testing:
    permissions:
      contents: read
      # Allow requesting/creating OIDC token
      id-token: write
    runs-on: ubuntu-latest
    steps:
      - name: Get certificate from Vault
        id: cert
        uses: gooddata/github-actions-public/vault/cert@master
        with:
          cn: localhost
          role: test
          vault-auth-role: testing
```
