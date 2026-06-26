$ErrorActionPreference = "Stop"

docker run --rm `
  -e AWS_ENDPOINT `
  -e SP_TENANT_ID `
  -e SP_CLIENT_ID `
  -e SP_CLIENT_SECRET `
  -e SP_SITE_ID `
  -e SP_COMMAND_LIMITS_LIST_ID `
  -e SP_BLOCK_COMMANDS_LIST_ID `
  -v "${PWD}:/work" `
  --workdir /work `
  $env:E2E_CONTAINER `
  robot TestScenes.robot

if ($LASTEXITCODE -ne 0) {
    throw "Robot test failed with exit code $LASTEXITCODE"
}
