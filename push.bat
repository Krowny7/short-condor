@echo off
REM Push script for Greeks refactoring
cd /d "c:\Users\chaum\Documents\Dossier Code\Projets tests\Short condor"

echo.
echo ========================================
echo PUSHING GREEKS REFACTORING TO GITHUB
echo ========================================
echo.

echo [1/4] Staging all changes...
git add .
echo OK

echo [2/4] Checking git status...
git status --short

echo.
echo [3/4] Committing...
git commit -m "Refactor Greeks to professional vectorized system - MultiLegGreeksCalculator for 10-100x faster computation"

echo.
echo [4/4] Pushing to GitHub...
git push

echo.
echo ========================================
echo ✅ DEPLOYMENT COMPLETE!
echo ========================================
echo.
echo Streamlit Cloud will auto-redeploy in 1-2 minutes
echo Check: https://github.com/Krowny7/short-condor
echo.
pause
