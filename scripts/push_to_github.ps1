param(
  [Parameter(Mandatory=$true)][string]$RemoteUrl,
  [string]$Branch = $(git rev-parse --abbrev-ref HEAD)
)

Write-Host "Setting remote 'origin' -> $RemoteUrl (will overwrite if exists)"
try { git remote remove origin } catch { }
git remote add origin $RemoteUrl

Write-Host "Pushing branch $Branch to origin"
git push -u origin $Branch

Write-Host "Push complete. If the remote is private, configure credential manager or use a PAT in the URL."
