workflow "Deploy" {
  on = "push"
  resolves = [
    "GitHub Action for Slack",
  ]
}

action "Build docker image " {
  uses = "actions/docker/cli@aea64bb1b97c42fa69b90523667fef56b90d7cff"
  args = ["build", "-t", "githubactions", "."]
}

action "Get Auth for Google Cloud" {
  uses = "actions/gcloud/auth@df59b3263b6597df4053a74e4e4376c045d9087e"
  secrets = ["GCLOUD_AUTH"]
}

action "Tag Docker for gcloud" {
  uses = "actions/docker/tag@8cdf801b322af5f369e00d85e9cf3a7122f49108"
  needs = [
    "Get Auth for Google Cloud",
    "Build docker image ",
  ]
  args = ["githubactions", "gcr.io/$PROJECT/$APP"]
  secrets = ["PROJECT", "APP"]
}

action "Setup Google Cloud" {
  uses = "actions/gcloud/auth@master"
  needs = [
    "Get Auth for Google Cloud",
    "Tag Docker for gcloud",
  ]
  secrets = ["GCLOUD_AUTH"]
}

action "Get Gcloud Auth" {
  uses = "actions/gcloud/cli@df59b3263b6597df4053a74e4e4376c045d9087e"
  secrets = ["GCLOUD_AUTH"]
  args = ["auth", "configure-docker", "--quiet"]
  needs = ["Tag Docker for gcloud"]
}

action "Push Image to Registery" {
  uses = "actions/gcloud/cli@df59b3263b6597df4053a74e4e4376c045d9087e"
  args = ["docker", "-- push", "gcr.io/$PROJECT/$APP"]
  needs = ["Get Gcloud Auth"]
  secrets = ["PROJECT", "APP"]
}

action "Get K8s Auth" {
  uses = "actions/gcloud/cli@df59b3263b6597df4053a74e4e4376c045d9087e"
  needs = ["Push Image to Registery"]
  secrets = [
    "GCLOUD_AUTH",
    "PROJECT",
    "CLUSTER_NAME",
  ]
  args = "container clusters get-credentials $CLUSTER_NAME --zone us-central1-a --project $PROJECT"
}

action "Update Deployment" {
  uses = "docker://gcr.io/cloud-builders/kubectl"
  runs = "sh -l -c"
  args = ["SHORT_REF=$(echo ${GITHUB_SHA} | head -c7) && cat $GITHUB_WORKSPACE/deploy.yml | sed 's/PROJECT_ID/'\"$PROJECT_ID\"'/' | sed 's/APPLICATION_NAME/'\"$APPLICATION_NAME\"'/' | sed 's/TAG/'\"$SHORT_REF\"'/' | kubectl apply -n $NAMESPACE -f -"]
  needs = ["Get K8s Auth"]
  secrets = ["NAMESPACE", "PROJECT_ID", "APPLICATION_NAME"]
}

action "GitHub Action for Slack" {
  uses = "Ilshidur/action-slack@6286a077a2b77159fcc4f425a9e714173d374616"
  secrets = ["SLACK_WEBHOOK"]
  args = "*Deployment Successful*"
  needs = ["Update Deployment"]
}