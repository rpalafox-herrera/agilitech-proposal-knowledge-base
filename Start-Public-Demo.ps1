$ErrorActionPreference = 'Stop'
$ProjectDir = $PSScriptRoot
$WorkspaceDir = [System.IO.Path]::GetFullPath((Join-Path $ProjectDir '..\..\work'))
$Python = Join-Path $WorkspaceDir '.venv\Scripts\python.exe'
$Cloudflared = Join-Path $WorkspaceDir 'cloudflared.exe'
$TunnelLog = Join-Path $WorkspaceDir 'cloudflared-presentation.log'
$LinkFile = Join-Path $ProjectDir 'PUBLIC_LINK.txt'

Write-Host ''
Write-Host 'Agilitech Proposal Knowledge Base Public Demo' -ForegroundColor Cyan
Write-Host 'This demo has no login. Use only public or fictional documents.' -ForegroundColor Yellow
Write-Host ''

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Python environment not found at $Python. Run the first-time setup in README.md."
}
if (-not (Test-Path -LiteralPath $Cloudflared)) {
    throw "The signed Cloudflare tunnel program was not found at $Cloudflared."
}

try {
    $health = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8501/_stcore/health' -TimeoutSec 2
} catch {
    Write-Host 'Starting the local website...' -ForegroundColor Green
    $app = Start-Process -FilePath $Python `
        -ArgumentList '-m','streamlit','run','app.py','--server.headless','true','--server.port','8501' `
        -WorkingDirectory $ProjectDir -WindowStyle Hidden -PassThru
    Set-Content -LiteralPath (Join-Path $WorkspaceDir 'streamlit-public-demo.pid') -Value $app.Id
    $ready = $false
    for ($attempt = 0; $attempt -lt 25; $attempt++) {
        Start-Sleep -Seconds 1
        try {
            $health = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:8501/_stcore/health' -TimeoutSec 2
            if ($health.StatusCode -eq 200) { $ready = $true; break }
        } catch { }
    }
    if (-not $ready) { throw 'The local website did not start. Run Start App.cmd and review its error message.' }
}

if (Test-Path -LiteralPath $TunnelLog) { Remove-Item -LiteralPath $TunnelLog -Force }
Write-Host 'Creating an encrypted public presentation link...' -ForegroundColor Green
$tunnel = Start-Process -FilePath $Cloudflared `
    -ArgumentList 'tunnel','--url','http://127.0.0.1:8501','--no-autoupdate','--logfile',$TunnelLog,'--loglevel','info' `
    -WorkingDirectory $WorkspaceDir -WindowStyle Hidden -PassThru
Set-Content -LiteralPath (Join-Path $WorkspaceDir 'cloudflared-public-demo.pid') -Value $tunnel.Id

$publicUrl = $null
for ($attempt = 0; $attempt -lt 35; $attempt++) {
    Start-Sleep -Seconds 1
    if ($tunnel.HasExited) { throw "The public tunnel stopped before producing a link. See $TunnelLog" }
    if (Test-Path -LiteralPath $TunnelLog) {
        $logText = Get-Content -LiteralPath $TunnelLog -Raw
        $match = [regex]::Match($logText, 'https://[a-z0-9-]+\.trycloudflare\.com')
        if ($match.Success) { $publicUrl = $match.Value; break }
    }
}
if (-not $publicUrl) { throw "No public link was produced. See $TunnelLog" }

Set-Content -LiteralPath $LinkFile -Value $publicUrl
try { Set-Clipboard -Value $publicUrl } catch { }

Write-Host ''
Write-Host 'PUBLIC LINK READY' -ForegroundColor Green
Write-Host $publicUrl -ForegroundColor Cyan
Write-Host ''
Write-Host 'The link was copied to the clipboard and saved in PUBLIC_LINK.txt.'
Write-Host 'Keep this laptop awake, connected to the internet, and powered on during class.'
Write-Host 'If you restart the launcher, use the newest link in PUBLIC_LINK.txt.'
Write-Host ''
Start-Process $publicUrl
