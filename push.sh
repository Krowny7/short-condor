#!/bin/bash
cd "c:\Users\chaum\Documents\Dossier Code\Projets tests\Short condor" || cd "/c/Users/chaum/Documents/Dossier Code/Projets tests/Short condor" 2>/dev/null

echo "📦 Staging..."
git add .

echo "💾 Committing..."
git commit -m "Refactor Greeks to professional vectorized system - MultiLegGreeksCalculator class + comprehensive documentation"

echo "🚀 Pushing..."
git push

echo "✅ Done!"
