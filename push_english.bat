@echo off
REM Translate app to English terminology
cd /d "c:\Users\chaum\Documents\Dossier Code\Projets tests\Short condor"

echo.
echo ========================================
echo TRANSLATING APP TO ENGLISH TERMINOLOGY
echo ========================================
echo.

echo [1/3] Staging app.py...
git add app.py
echo OK

echo [2/3] Committing translation...
git commit -m "Translate UI to use English financial terminology (Mode, Real, Manual, Strike, Interest Rate, Greeks, Delta, Gamma, Theta, Vega, Payoff, P&L, etc.)"

echo [3/3] Pushing to GitHub...
git push

echo.
echo ========================================
echo ✅ TRANSLATION COMPLETE!
echo ========================================
echo.
echo All international finance terms are now in English
echo while keeping French descriptions where appropriate
echo.
pause
