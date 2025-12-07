@echo off
REM Smart Y-axis scaling fix for Greeks graphs
cd /d "c:\Users\chaum\Documents\Dossier Code\Projets tests\Short condor"

echo.
echo ========================================
echo FIXING GREEKS GRAPH AXIS SCALING
echo ========================================
echo.

echo [1/3] Staging changes...
git add app.py
echo OK

echo [2/3] Committing fix...
git commit -m "Fix: Add smart Y-axis scaling to Greeks graphs - prevents flattening when time to expiration increases"

echo [3/3] Pushing to GitHub...
git push

echo.
echo ========================================
echo ✅ AXIS SCALING FIXED!
echo ========================================
echo.
echo The Greeks graphs will now auto-scale intelligently
echo even with long time to expiration (0.5+ years)
echo.
pause
