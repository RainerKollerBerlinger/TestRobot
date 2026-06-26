$ErrorActionPreference = "Stop"

docker run --rm `
  -v "${PWD}:/work" `
  --workdir /work `
  rainerk123/e2etesting:v0.3 `
  robot TestScenes.robot

if ($LASTEXITCODE -ne 0) {
    throw "Robot test failed with exit code $LASTEXITCODE"
}