# setup.ps1 - one-time setup for the Learning system (Windows)
#
# Run from PowerShell inside the Learning folder:
#   powershell -ExecutionPolicy Bypass -File .\setup.ps1
#
# What it does:
#   0. Moves the tutor files from _setup\claude into .claude
#   1. Checks git, Python, and Claude Code are installed
#   2. Creates a private Python environment (.claude\.venv) with the review engine (fsrs)
#   3. Tests the review engine
#   4. Turns this folder into a git repo on branch "main" and makes the first commit
#   5. Creates a PUBLIC GitHub repo and pushes (if the GitHub CLI "gh" is installed)
# Safe to run again: every step skips itself if already done.

$ErrorActionPreference = "Continue"   # native tools (git) write to stderr; we check $LASTEXITCODE instead
Set-Location -Path $PSScriptRoot

function Say($msg)  { Write-Host "`n==> $msg" -ForegroundColor Cyan }
function Ok($msg)   { Write-Host "    OK: $msg" -ForegroundColor Green }
function Warn($msg) { Write-Host "    WARNING: $msg" -ForegroundColor Yellow }
function Fail($msg) { Write-Host "    PROBLEM: $msg" -ForegroundColor Red; exit 1 }
function Has($cmd)  { return [bool](Get-Command $cmd -ErrorAction SilentlyContinue) }

# ---------------------------------------------------------------- 0. tutor files
# Claude's remote tools may not write into .claude (a safety rule), so the tutor's
# skills/hooks/scripts ship in _setup\claude and this script moves them into place.
Say "Installing tutor files into .claude"
if (Test-Path "_setup\claude") {
  New-Item -ItemType Directory -Force -Path ".claude" | Out-Null
  Copy-Item -Path "_setup\claude\*" -Destination ".claude" -Recurse -Force
  Remove-Item -Recurse -Force "_setup"
  Ok "Skills, hooks and review engine installed in .claude"
} elseif (Test-Path ".claude\scripts\srs.py") {
  Ok "Already installed"
} else {
  Fail "Tutor files not found (_setup\claude is missing)."
}

# ---------------------------------------------------------------- 1. tools
Say "Checking tools"

if (Has "git") { Ok (git --version) } else {
  Fail "git not found. Install Git for Windows (also gives Git Bash, which Claude Code needs): winget install Git.Git"
}

if (Has "claude") { Ok "Claude Code found" } else {
  Warn "Claude Code ('claude') not found on PATH. Install it from https://code.claude.com before your first session."
}

# Find a real Python 3 (the Microsoft Store 'python' alias is a fake stub, so test it).
$python = $null
foreach ($candidate in @("py -3", "python", "python3")) {
  $parts = $candidate.Split(" ")
  $exe = $parts[0]
  $pyArgs = @($parts | Select-Object -Skip 1)
  if (-not (Has $exe)) { continue }
  try {
    $v = & $exe @pyArgs -c "import sys; print('%d.%d' % sys.version_info[:2])" 2>$null
    if ($LASTEXITCODE -eq 0 -and "$v" -match '^3\.(\d+)$' -and [int]$Matches[1] -ge 10) {
      $python = $candidate; Ok "Python $v ($candidate)"; break
    }
  } catch { }
}
if (-not $python) {
  Fail "Python 3.10+ not found. Install it: winget install Python.Python.3.12  (then open a NEW PowerShell window and re-run)"
}

# ---------------------------------------------------------------- 2. venv + fsrs
Say "Setting up the review engine (private Python environment)"
$venvPy = Join-Path $PSScriptRoot ".claude\.venv\Scripts\python.exe"
if (-not (Test-Path $venvPy)) {
  $parts = $python.Split(" ")
  $pyExe = $parts[0]
  $pyArgs = @($parts | Select-Object -Skip 1)
  & $pyExe @pyArgs -m venv ".claude\.venv"
  if ($LASTEXITCODE -ne 0) { Fail "Could not create the Python environment." }
}
& $venvPy -m pip install --quiet --upgrade pip
& $venvPy -m pip install --quiet -r ".claude\requirements.txt"
if ($LASTEXITCODE -ne 0) { Fail "pip install failed (no internet?)." }
Ok "fsrs installed"

# ---------------------------------------------------------------- 3. test
Say "Testing the review engine"
& $venvPy ".claude\scripts\srs.py" stats --write | Out-Null
if ($LASTEXITCODE -ne 0) { Fail "Review engine test failed." }
Ok "Review engine works (_system\stats.md written)"

# ---------------------------------------------------------------- 4. git
Say "Setting up git"
if (-not (Test-Path ".git")) {
  git init -b main | Out-Null
  Ok "Created git repo on branch main"
} else {
  Ok "Git repo already exists"
}

$email = (git config user.email) 2>$null
$name  = (git config user.name) 2>$null
if (-not $name) {
  $name = Read-Host "    Your name for git commits"
  git config user.name "$name"
}
if (-not $email) {
  $email = Read-Host "    Your GitHub email (MUST match your GitHub account or Beeminder won't count commits)"
  git config user.email "$email"
} else {
  Write-Host "    Git email is: $email"
  Write-Host "    This MUST be an email on your GitHub account (github.com/settings/emails), or Beeminder won't count your commits."
  $change = Read-Host "    Press Enter to keep it, or type a different email"
  if ($change) { git config user.email "$change"; $email = $change }
}

$hasCommit = $true
git rev-parse --verify HEAD 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) { $hasCommit = $false }
if (-not $hasCommit) {
  git add -A
  git commit -q -m "setup: learning system"
  Ok "First commit made"
} else {
  Ok "Repo already has commits"
}

# ---------------------------------------------------------------- 5. GitHub
Say "Connecting to GitHub"
$remote = (git remote get-url origin) 2>$null
if ($remote) {
  Ok "Remote already set: $remote"
  git push -u origin main
} elseif (Has "gh") {
  gh auth status 2>$null | Out-Null
  if ($LASTEXITCODE -ne 0) {
    Write-Host "    Logging in to GitHub (a browser window will open)..."
    gh auth login --web --git-protocol https
  }
  $repoName = Read-Host "    Name for the new PUBLIC GitHub repo (Enter = learning)"
  if (-not $repoName) { $repoName = "learning" }
  gh repo create $repoName --public --source . --remote origin --push --description "My AI-tutored learning system: lessons, review cards, and exercises. One commit per daily session."
  if ($LASTEXITCODE -ne 0) { Fail "Could not create the GitHub repo (name taken?). Re-run with another name." }
  Ok "Pushed to GitHub"
} else {
  Warn "GitHub CLI (gh) not found. Either install it (winget install GitHub.cli) and re-run this script, or do it by hand:"
  Write-Host "      1. Create an EMPTY public repo at https://github.com/new (no README)"
  Write-Host "      2. git remote add origin https://github.com/<you>/<repo>.git"
  Write-Host "      3. git push -u origin main"
}

# ---------------------------------------------------------------- done
Say "Done! Next steps"
Write-Host "    1. Obsidian: Settings -> Community plugins -> turn off Restricted mode -> Browse -> 'Dataview' -> Install -> Enable"
Write-Host "       Then open Learning\_system\Dashboard.md"
Write-Host "    2. Beeminder: create a GitHub goal tracking THIS repo's commits on main"
Write-Host "    3. Start learning, in this folder:"
Write-Host "         claude"
Write-Host "         /new-subject"
Write-Host ""
