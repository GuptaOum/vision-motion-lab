# Deploy the Sudoku API to an EC2 host, mirroring the FaceAttendance workflow:
#   git archive (backend + ocr) -> scp -> docker compose up -d --build
#
# Example:
#   .\deploy.ps1 -Server ec2-user@3.109.177.77 -KeyPath C:\Users\hp\.ssh\face-attendance.pem

param(
    [Parameter(Mandatory = $true)][string]$Server,       # user@host, e.g. ubuntu@1.2.3.4
    [Parameter(Mandatory = $true)][string]$KeyPath,      # path to the .pem private key
    [string]$RemoteDir = "~/sudoku-api",
    [int]$HostPort = 8000
)

$ErrorActionPreference = "Stop"
$archive = Join-Path $env:TEMP "sudoku-api.tar.gz"

Write-Host "Packaging backend + ocr from git HEAD..."
$repoRoot = (git rev-parse --show-toplevel)
git -C $repoRoot archive --format=tar.gz -o $archive HEAD sudoko_flutter_app/backend sudoko_flutter_app/ocr

Write-Host "Copying to $Server ..."
ssh -i $KeyPath $Server "mkdir -p $RemoteDir"
scp -i $KeyPath $archive "${Server}:$RemoteDir/sudoku-api.tar.gz"

Write-Host "Building and starting the container on the remote..."
$remote = "cd $RemoteDir && tar xzf sudoku-api.tar.gz && rm sudoku-api.tar.gz && cd sudoko_flutter_app/backend && HOST_PORT=$HostPort docker compose up -d --build"
ssh -i $KeyPath $Server $remote

$hostOnly = $Server.Split("@")[-1]
Write-Host ""
Write-Host "Done. Health check: http://${hostOnly}:$HostPort/"
Write-Host "Swagger UI:        http://${hostOnly}:$HostPort/docs"
