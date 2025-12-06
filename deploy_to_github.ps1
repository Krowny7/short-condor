# Script de déploiement - Short Condor Analyzer
# Ce script initialise Git et pousse vers GitHub

Write-Host "================================" -ForegroundColor Cyan
Write-Host "🚀 Short Condor - Déploiement GitHub" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Vérifier si Git est installé
$gitVersion = git --version 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Git n'est pas installé!" -ForegroundColor Red
    Write-Host "Installez Git depuis: https://git-scm.com/download/win" -ForegroundColor Yellow
    exit 1
}

Write-Host "✅ Git trouvé: $gitVersion" -ForegroundColor Green
Write-Host ""

# Vérifier si .git existe
if (Test-Path ".git") {
    Write-Host "✅ Dépôt Git détecté" -ForegroundColor Green
    git status
} else {
    Write-Host "⚙️  Initialisation du dépôt Git..." -ForegroundColor Yellow
    git init
    Write-Host "✅ Dépôt initialisé" -ForegroundColor Green
}

Write-Host ""
Write-Host "📝 Configuration Git" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

# Ajouter les fichiers
Write-Host "📦 Ajout des fichiers..."
git add .
Write-Host "✅ Fichiers ajoutés" -ForegroundColor Green

# Commit initial
$commitMsg = "Initial commit: Short Condor Analyzer - Ready for Streamlit Cloud"
Write-Host "💾 Création du commit: '$commitMsg'"
git commit -m $commitMsg
Write-Host "✅ Commit créé" -ForegroundColor Green

Write-Host ""
Write-Host "🔗 Connexion à GitHub" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT - Créez d'abord un dépôt sur GitHub:" -ForegroundColor Yellow
Write-Host "1. Allez sur https://github.com/new" -ForegroundColor White
Write-Host "2. Nommez-le 'short-condor'" -ForegroundColor White
Write-Host "3. Sélectionnez 'Public'" -ForegroundColor White
Write-Host "4. NE sélectionnez PAS 'Initialize this repository'" -ForegroundColor White
Write-Host "5. Cliquez 'Create repository'" -ForegroundColor White
Write-Host ""

$username = Read-Host "📝 Entrez votre username GitHub"
if ([string]::IsNullOrWhiteSpace($username)) {
    Write-Host "❌ Username vide!" -ForegroundColor Red
    exit 1
}

$remoteUrl = "https://github.com/$username/short-condor.git"

Write-Host ""
Write-Host "🔄 Configuration du remote: $remoteUrl" -ForegroundColor Cyan

# Vérifier s'il existe déjà
$existingRemote = git remote get-url origin 2>&1
if ($LASTEXITCODE -eq 0) {
    Write-Host "⚠️  Remote 'origin' existe déjà: $existingRemote" -ForegroundColor Yellow
    git remote remove origin
    Write-Host "✅ Remote existant supprimé" -ForegroundColor Green
}

# Ajouter le remote
git remote add origin $remoteUrl
Write-Host "✅ Remote 'origin' configuré" -ForegroundColor Green

# Renommer la branche en 'main' si nécessaire
git branch -M main
Write-Host "✅ Branche: main" -ForegroundColor Green

Write-Host ""
Write-Host "📤 Push vers GitHub..." -ForegroundColor Cyan
git push -u origin main

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "✅ SUCCÈS! Votre code est sur GitHub!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "📋 Prochaines étapes:" -ForegroundColor Cyan
    Write-Host "1. Allez sur https://share.streamlit.io/" -ForegroundColor White
    Write-Host "2. Cliquez 'Sign in with GitHub'" -ForegroundColor White
    Write-Host "3. Cliquez 'New app'" -ForegroundColor White
    Write-Host "4. Sélectionnez le repo 'short-condor'" -ForegroundColor White
    Write-Host "5. Branch: 'main', File: 'app.py'" -ForegroundColor White
    Write-Host "6. Cliquez 'Deploy'" -ForegroundColor White
    Write-Host ""
    Write-Host "🎉 Votre app sera live dans 2-3 minutes!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Erreur lors du push!" -ForegroundColor Red
    Write-Host "Vérifiez votre connexion GitHub et réessayez" -ForegroundColor Yellow
    exit 1
}
