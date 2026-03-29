param(
  [Parameter(Mandatory=$true)]
  [string]$ImagePath,

  [string]$Prompt = "Recreate this UI. Make it responsive.",
  [string]$McpBrainUrl = "http://127.0.0.1:8000"
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path $ImagePath)) {
  throw "ImagePath not found: $ImagePath"
}

$uri = "$McpBrainUrl/generator/from-screenshot?prompt=$([uri]::EscapeDataString($Prompt))"

Write-Host "POST $uri"

$resp = Invoke-RestMethod `
  -Method Post `
  -Uri $uri `
  -Form @{ screenshot = Get-Item $ImagePath }

$resp | ConvertTo-Json -Depth 10

if ($resp.template_name) {
  Write-Host ""
  Write-Host "Preview:"
  Write-Host "  http://localhost:4000/template-preview/$($resp.template_name)"
}

