# ============================================================
# CerveauIA - Démarrage complet de LM Studio
# ============================================================

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "============================================" -ForegroundColor Magenta
Write-Host "       CerveauIA - LM Studio" -ForegroundColor Magenta
Write-Host "============================================" -ForegroundColor Magenta
Write-Host ""

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------

$ProjectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$EnvFile = Join-Path $ProjectRoot ".env"

if (-not (Test-Path $EnvFile)) {
    Write-Host "[ERREUR] Fichier .env introuvable :" -ForegroundColor Red
    Write-Host "         $EnvFile"
    exit 1
}

# Lecture du .env
$EnvContent = Get-Content $EnvFile

foreach ($line in $EnvContent) {

    if ($line -match '^\s*VAULT_PATH=(.*)$') {
        $VAULT_PATH = $Matches[1].Trim()
    }

    if ($line -match '^\s*LM_STUDIO_BASE_URL=(.*)$') {
        $LM_STUDIO_BASE_URL = $Matches[1].Trim()
    }

    if ($line -match '^\s*EMBEDDING_MODEL=(.*)$') {
        $EMBEDDING_MODEL = $Matches[1].Trim()
    }
}

if (-not $LM_STUDIO_BASE_URL) {
    $LM_STUDIO_BASE_URL = "http://localhost:1234/v1"
}

if (-not $EMBEDDING_MODEL) {
    $EMBEDDING_MODEL = "text-embedding-bge-m3"
}

# Extraction du port
$Port = 1234

if ($LM_STUDIO_BASE_URL -match ':(\d+)/v1') {
    $Port = [int]$Matches[1]
}

Write-Host "Configuration .env :" -ForegroundColor Cyan
Write-Host "Modèle : $EMBEDDING_MODEL"
Write-Host "API    : $LM_STUDIO_BASE_URL"
Write-Host "Port   : $Port"
Write-Host ""

# ------------------------------------------------------------
# 1. Vérification de LMS
# ------------------------------------------------------------

Write-Host "[1/5] Vérification de LMS..." -ForegroundColor Cyan

try {
    $lmsVersion = lms --version 2>&1

    if ($LASTEXITCODE -ne 0) {
        throw "LMS ne répond pas correctement."
    }

    Write-Host "[OK] LMS disponible." -ForegroundColor Green
}
catch {
    Write-Host "[ERREUR] LMS introuvable ou inutilisable." -ForegroundColor Red
    Write-Host ""
    Write-Host "Vérifie que LM Studio est installé et que 'lms' est disponible dans le PATH."
    exit 1
}

Write-Host ""

# ------------------------------------------------------------
# 2. Démarrage du serveur LM Studio
# ------------------------------------------------------------

Write-Host "[2/5] Démarrage du serveur LM Studio..." -ForegroundColor Cyan

$ServerRunning = $false

# Vérifie si le serveur est déjà actif
try {
    $response = Invoke-WebRequest `
        -Uri "http://localhost:$Port/v1/models" `
        -Method Get `
        -TimeoutSec 2 `
        -UseBasicParsing `
        -ErrorAction Stop

    if ($response.StatusCode -eq 200) {
        $ServerRunning = $true
    }
}
catch {
    $ServerRunning = $false
}

if ($ServerRunning) {

    Write-Host "[OK] Serveur déjà actif sur le port $Port." -ForegroundColor Green

}
else {

    Write-Host "[INFO] Lancement du serveur en arrière-plan..." -ForegroundColor Yellow

    # Lance LM Studio Server sans bloquer le script
    Start-Process `
        -FilePath "lms" `
        -ArgumentList "server", "start" `
        -WindowStyle Hidden

    # Attendre que le serveur soit disponible
    $MaxAttempts = 30
    $Attempt = 0

    while (-not $ServerRunning -and $Attempt -lt $MaxAttempts) {

        Start-Sleep -Seconds 1
        $Attempt++

        try {
            $response = Invoke-WebRequest `
                -Uri "http://localhost:$Port/v1/models" `
                -Method Get `
                -TimeoutSec 2 `
                -UseBasicParsing `
                -ErrorAction Stop

            if ($response.StatusCode -eq 200) {
                $ServerRunning = $true
            }
        }
        catch {
            $ServerRunning = $false
        }

        if (-not $ServerRunning) {
            Write-Host "." -NoNewline
        }
    }

    Write-Host ""

    if (-not $ServerRunning) {
        Write-Host "[ERREUR] Le serveur ne répond pas après $MaxAttempts secondes." -ForegroundColor Red
        exit 1
    }

    Write-Host "[OK] Serveur LM Studio actif." -ForegroundColor Green
}

Write-Host ""

# ------------------------------------------------------------
# 3. Vérification du modèle
# ------------------------------------------------------------

Write-Host "[3/5] Vérification du modèle..." -ForegroundColor Cyan

$ModelLoaded = $false

try {

    $ModelsResponse = Invoke-RestMethod `
        -Uri "http://localhost:$Port/v1/models" `
        -Method Get `
        -TimeoutSec 5

    foreach ($model in $ModelsResponse.data) {

        if ($model.id -eq $EMBEDDING_MODEL) {
            $ModelLoaded = $true
            break
        }
    }

}
catch {
    Write-Host "[INFO] Impossible de lire les modèles via l'API." -ForegroundColor Yellow
}

if ($ModelLoaded) {

    Write-Host "[OK] Modèle déjà chargé : $EMBEDDING_MODEL" -ForegroundColor Green

}
else {

    Write-Host "[INFO] Modèle non chargé." -ForegroundColor Yellow
    Write-Host "[INFO] Chargement de : $EMBEDDING_MODEL" -ForegroundColor Cyan
    Write-Host ""

    lms load $EMBEDDING_MODEL --gpu=max

    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "[ERREUR] Impossible de charger le modèle." -ForegroundColor Red
        exit 1
    }

    Write-Host ""
    Write-Host "[OK] Modèle chargé : $EMBEDDING_MODEL" -ForegroundColor Green
}

Write-Host ""

# ------------------------------------------------------------
# 4. Vérification finale de l'API
# ------------------------------------------------------------

Write-Host "[4/5] Vérification de l'API..." -ForegroundColor Cyan

try {

    $response = Invoke-WebRequest `
        -Uri "http://localhost:$Port/v1/models" `
        -Method Get `
        -TimeoutSec 5 `
        -UseBasicParsing `
        -ErrorAction Stop

    if ($response.StatusCode -ne 200) {
        throw "HTTP $($response.StatusCode)"
    }

    Write-Host "[OK] API disponible : http://localhost:$Port/v1" -ForegroundColor Green

}
catch {

    Write-Host "[ERREUR] L'API LM Studio ne répond pas." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}

Write-Host ""

# ------------------------------------------------------------
# 5. Vérification finale du modèle
# ------------------------------------------------------------

Write-Host "[5/5] Vérification finale du modèle..." -ForegroundColor Cyan

try {

    $FinalModelsResponse = Invoke-RestMethod `
        -Uri "http://localhost:$Port/v1/models" `
        -Method Get `
        -TimeoutSec 5

    $FinalModelFound = $false

    foreach ($model in $FinalModelsResponse.data) {

        if ($model.id -eq $EMBEDDING_MODEL) {
            $FinalModelFound = $true
            break
        }
    }

    if (-not $FinalModelFound) {
        throw "Le modèle $EMBEDDING_MODEL n'est pas disponible dans l'API."
    }

    Write-Host "[OK] Modèle disponible : $EMBEDDING_MODEL" -ForegroundColor Green

}
catch {

    Write-Host "[ERREUR] Le modèle n'est pas disponible." -ForegroundColor Red
    Write-Host $_.Exception.Message
    exit 1
}
Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "       CERVEAUIA - PRÊT" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "LM Studio : OK"
Write-Host "Serveur   : OK"
Write-Host "Modèle    : $EMBEDDING_MODEL"
Write-Host "API       : http://localhost:$Port/v1"
Write-Host ""
Write-Host "CerveauIA peut maintenant utiliser les embeddings."
Write-Host ""