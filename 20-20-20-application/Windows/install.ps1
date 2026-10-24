$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
function Find-Python {
    $candidates = @()
    $py = Get-Command py.exe -ErrorAction SilentlyContinue
    if ($py) { $candidates += ,@('py.exe','-3.11'); $candidates += ,@('py.exe','-3') }
    $candidates += ,@('python.exe')
    $candidates += ,@("$env:LOCALAPPDATA\Programs\Python\Python311\python.exe")
    $candidates += ,@("$env:LOCALAPPDATA\Microsoft\WindowsApps\python3.11.exe")
    foreach ($candidate in $candidates) {
        try {
            $argsList = @($candidate | Select-Object -Skip 1) + @('-c','import sys; assert sys.version_info >= (3, 11); print(sys.executable)')
            $path = & $candidate[0] @argsList 2>$null
            if ($LASTEXITCODE -eq 0 -and $path -and (Test-Path ($path | Select-Object -Last 1))) {
                return ($path | Select-Object -Last 1).Trim()
            }
        } catch { }
    }
    return $null
}
$python = Find-Python
if (-not $python) {
    Write-Host 'Python 3.11+ not found. Trying Microsoft Store first...'
    $winget = Get-Command winget.exe -ErrorAction SilentlyContinue
    if ($winget) {
        # Store package IDs may change; query the Store source rather than assuming the winget community ID.
        Write-Host 'Searching Microsoft Store for Python 3.11...'
        & winget.exe search 'Python 3.11' --source msstore --accept-source-agreements
        Write-Host 'Opening Microsoft Store Python listing. Install Python 3.11 or newer, then return here.'
        Start-Process 'ms-windows-store://search/?query=Python%203.11'
        Read-Host 'Press Enter after installing Python from Microsoft Store'
        $python = Find-Python
    } else {
        Write-Warning 'Windows Package Manager is unavailable; Microsoft Store may be blocked.'
        try { Start-Process 'ms-windows-store://search/?query=Python%203.11' } catch { }
        Read-Host 'Press Enter after attempting Microsoft Store installation'
        $python = Find-Python
    }
}
if (-not $python) {
    Write-Warning 'Microsoft Store installation was not detected.'
    $answer = Read-Host 'Download Python 3.11 from official python.org as fallback? [y/N]'
    if ($answer -notmatch '^(y|yes)$') { throw 'Python installation cancelled.' }
    $version = '3.11.9'
    $url = "https://www.python.org/ftp/python/$version/python-$version-amd64.exe"
    $target = Join-Path $env:TEMP "python-$version-amd64.exe"
    Write-Host "Downloading $url"
    Invoke-WebRequest -Uri $url -OutFile $target
    $proc = Start-Process -FilePath $target -ArgumentList '/quiet','InstallAllUsers=0','PrependPath=0','Include_pip=1' -Wait -PassThru
    if ($proc.ExitCode -ne 0) { throw "Python installer exited with $($proc.ExitCode)" }
    $python = Find-Python
}
if (-not $python) { throw 'Python 3.11+ not detected. Reopen terminal or rerun setup after installation.' }
Write-Host "Using Python: $python"
& $python -m venv (Join-Path $PSScriptRoot '.venv')
if ($LASTEXITCODE -ne 0) { throw 'Virtual environment creation failed.' }
$venvPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
& $venvPython -m pip install --upgrade pip pywin32 pystray pillow
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& $venvPython -c 'import win32api, pystray, PIL'
if ($LASTEXITCODE -ne 0) { throw 'Dependency verification failed.' }
Write-Host 'Setup complete. Run run.bat to start EyeGuard.'
