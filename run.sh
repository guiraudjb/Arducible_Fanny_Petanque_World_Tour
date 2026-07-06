#!/bin/bash
cat <<- EOF
    _    ____  ____  _   _  ____ ___ ____  _     _____ 
   / \  |  _ \|  _ \| | | |/ ___|_ _| __ )| |   | ____|
  / _ \ | |_) | | | | | | | |    | ||  _ \| |   |  _|  
 / ___ \|  _ <| |_| | |_| | |___ | || |_) | |___| |___ 
/_/   \_\_| \_\____/ \___/ \____|___|____/|_____|_____|
                                                       
EOF
cd "$(dirname "$0")"
if [ ! -d "../pythonvenv" ]; then
    echo "Erreur : environnement Python introuvable. Lancez installdependancy.sh d'abord." >&2
    exit 1
fi
echo "Activation python venv"
source ../pythonvenv/bin/activate
echo "venv chargé. Lancement du jeu"
python3 main.py

