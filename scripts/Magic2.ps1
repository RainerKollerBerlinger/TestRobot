$ErrorActionPreference = "Stop"

docker run --rm `
  -v "${PWD}:/work" `
  --workdir /work `
  $env:E2E_CONTAINER `
  robot TestScenes.robot

if ($LASTEXITCODE -ne 0) {
    throw "Robot test failed with exit code $LASTEXITCODE"
}