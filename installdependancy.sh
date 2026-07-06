#!/bin/bash
set -e

if ! python3 -c "import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)" 2>/dev/null; then
    echo "Erreur : Python 3.8 ou supérieur requis." >&2
    exit 1
fi

python3 -m venv ../pythonvenv
source ../pythonvenv/bin/activate

pip install --upgrade pip
pip install "opencv-python>=4.8,<5" "numpy>=1.24,<2" "mediapipe>=0.10" pygame

echo "Téléchargement du modèle MediaPipe Pose..."
if command -v wget &>/dev/null; then
    wget -q --show-progress \
      -O assets/pose_landmarker_lite.task \
      "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
elif command -v curl &>/dev/null; then
    curl -L --progress-bar \
      -o assets/pose_landmarker_lite.task \
      "https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task"
else
    echo "Erreur : wget ou curl requis pour télécharger le modèle." >&2
    exit 1
fi
echo "Modèle téléchargé."
echo "Installation terminée. Lancez le jeu avec ./run.sh"
