# Pull request comment

This action used for comment a pull request based on reference job.

## Inputs

| key                      | required | default                                                         | description                                           |
|--------------------------|----------|-----------------------------------------------------------------|-------------------------------------------------------|
| vault-auth-path          | `false`  | `jwt/github`                                                    | Vault auth backend path to use (default usually okay) |
| vault-auth-role          | `false`  | `common-action`                                                 | Vault auth role to use for common action              |
| vault-url                | `true`   | *none*                                                          | Vault API URL (default okay in almost all cases)      |
| vault-path-dynamic-token | `false`  | `github/token/common-action`                                    | Vault path of dynamic token                           |
| job-reference            | `true`   | *none*                                                          | Reference job to get result                           |
| comment                  | `false`  | `### ${action} ${status} ${emoji}\n\nSee full output at ${url}` | Comment template                                      |
| delete-bot-comment       | `false`  | `true`                                                          | Delete bot comment                                    |
| pr-number                | `false`  | `context.issue.number`                                          | Number of PR to comment                               |
| repo-owner               | `false`  | `context.repo.owner`                                            | Owner of the repository                               |
| repo                     | `false`  | `context.repo.repo`                                             | Repository name                                       |


## Example usage

```
---
name: Run build and comment pull request

on: [pull_request]

jobs:
  build-job:
    runs-on: ubuntu-latest
    steps:
      - name: validate script
        id: validate
        shell: bash
        run: |
          echo "Build job"
  pr-comment:
    permissions:
      # Allow requesting/creating OIDC token
      id-token: write
    # run on our self-hosted runner to ensure Vault access
    runs-on: ubuntu-latest
    if: always()
    needs: [build-job]
    steps:
      - name: Comment to pull request
        uses: gooddata/github-actions-public/pr-comment@master
        with:
          vault-auth-role: "common-action"
          job-reference: "build-job"
```
