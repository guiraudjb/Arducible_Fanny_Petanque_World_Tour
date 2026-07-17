#!/bin/bash
cat <<- EOF
    ___        _       __________
   / _ \ _   _(_)_______|__  /__  /
  | | | | | | | |_  /_  / / /  / /
  | |_| | |_| | |/ / / /_/ /__/ /
   \__\_\\__,_|_/___/____/____/____|
     FANNY WORLD TOUR QUIZZ - 5 questions par pays
EOF
cd "$(dirname "$0")"
if [ ! -d "../pythonvenv" ]; then
    echo "Erreur : environnement Python introuvable. Lancez installdependancy.sh d'abord." >&2
    exit 1
fi
echo "Activation python venv"
source ../pythonvenv/bin/activate
echo "venv chargé. Lancement du jeu"
python3 main_quizz.py
