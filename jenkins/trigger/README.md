# Trigger Jenkins job

This action triggers Jenkins job through Jenkins API with given parameters

## Inputs

| key           | default | description                                                                                                        |
|---------------|---------|--------------------------------------------------------------------------------------------------------------------|
| comment-pr    | "false" | Specifies whether the PR should be commented with job result                                                       |
| slack-channel | *none*  | Specifies which Slack channel should be used to notify in case of failure. If left empty, notification is not sent |
| slack-token   | *none*  | Slack bot token that needs to be passed from secrets                                                               |
| server        | *none*  | Url of server the job should be run on                                                                             |
| folder        | *none*  | Path to folder containing the job to run                                                                           |
| job-name      | *none*  | Name of the job to run                                                                                             |
| vault-url     | *none*  | Vault API URL                                                                                                      |
| params        | *none*  | Job build parameters in dict syntax                                                                                |

## Outputs

| key              | description                                   |
|------------------|-----------------------------------------------|
| job-build-status | Job build status ('SUCCESS' if job succeeded) |
| job-build-url    | Job build URL                                 |



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
    # run on our self-hosted runner to ensure Vault access
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Jenkins job
        id: trigger-jenkins-job
        uses: gooddata/github-actions-public/jenkins/trigger@master
        with:
          slack-channel: channel-for-report
          slack-token: ${{ secrets.SLACK_BOT_TOKEN }}
          server: "jenkins-server.com"
          folder: "github"
          job-name: "basic-test-job"
          params: '{"repo":"test-repo","branch":"test-branch"}'

```
