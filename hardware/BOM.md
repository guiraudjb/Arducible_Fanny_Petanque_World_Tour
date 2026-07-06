# Nomenclature (BOM) — Fanny Pétanque World Tour

Borne à 3 cibles physiques. Quantités données **par cible** puis **totales pour
les 3 cibles**, plus les pièces du châssis (non dupliquées) et le contrôleur
central. Les pièces mécaniques et leurs quantités sont extraites directement
de l'assemblage FreeCAD (`ressources/modélisation/Doc final/ChassisV7/`), pas
estimées.

## Électronique — par cible (×3)

| Réf. | Composant | Qté/cible | Qté totale | Fichier |
|---|---|---|---|---|
| U1 | Capteur à effet Hall **OH37** (Nanjing Ouzhuo Tech, SOT-23) | 1 | 3 | [BOM JLCPCB](pcb/bom-jlcpcb.png) |
| R1 | Résistance **10 kΩ** (CMS 0603) | 1 | 3 | [BOM JLCPCB](pcb/bom-jlcpcb.png) |
| — | PCB détection (Gerber `arduciblesmd`, 2 couches) | 1 | 3 | [Gerber](pcb/gerber-pcb-detection.zip) · [modèle 3D](pcb/pcb-detection-3d-model.zip) |
| — | Aimant néodyme cylindrique **∅4×2 mm, N80** (solidaire de la boule, déclenche le capteur) | 1 | 3 | [FCStd](cad/aimant-neodyme-4x2.FCStd) |

*Source composants : capture "Bill of Material" JLCPCB
(`ressources/archives/PCB pour détection/composantssmd.png`) —
OH37 commandé ×25, résistance 10k ×30 (quantités de lot, pas la
consommation réelle de 1/cible).*

## Électronique — contrôleur central (×1)

| Composant | Détail | Fichier |
|---|---|---|
| Arduino Leonardo | ATmega32u4, USB HID natif — reconnu par l'ordinateur comme un clavier. Reçoit les 3 signaux de cible et envoie les touches `E`/`R`/`T`. | — |
| Connecteurs RJ45 (×3) + câble Ethernet Cat5/6 | Un câble réseau par cible ramène le signal du capteur + alimentation vers le boîtier Leonardo. | [Schéma de câblage](schematics/arduino-leonardo-rj45-wiring.png) |
| Câble Micro-USB | Liaison Leonardo ↔ PC. | — |

> Le schéma de câblage montre aussi 4 boutons "Key up/left/right/down" :
> **obsolètes**, hérités d'un prototype antérieur — le jeu actuel n'utilise
> que les 3 cibles (`E`/`R`/`T`).

## Mécanique — par cible / articulation (×3)

Nomenclature exacte de `assemblageArticulation.FCStd` :

| Pièce | Qté/cible | Qté totale | Fichier |
|---|---|---|---|
| Plaque d'articulation milieu (découpe laser 140×40×5 mm) | 1 | 3 | [STEP](cad/plaque-milieu.step) · [FCStd](cad/plaque-milieu.FCStd) |
| Plaque d'articulation sup (idem) | 1 | 3 | [STEP](cad/plaque-sup.step) · [FCStd](cad/plaque-sup.FCStd) |
| Plaque d'articulation inf (idem) | 1 | 3 | [STEP](cad/plaque-inf.step) · [FCStd](cad/plaque-inf.FCStd) |
| Vis métaux tête fraisée TF Pozi M4×50, acier zingué blanc | 2 | 6 | [FCStd](cad/vis-m4x50-tf-pozi.FCStd) |
| Écrou frein M4 | 6 | 18 | [FCStd](cad/ecrou-frein-m4.FCStd) |
| Vis métaux M4×30 | 4 | 12 | [FCStd](cad/vis-m4x30.FCStd) |
| Rotule radiale **GE8C** (rotule à rotule, alésage 8 mm) | 1 | 3 | [FCStd](cad/rotule-ge8c.FCStd) |
| Entretoise carte électronique (H31, sur-mesure) | 1 | 3 | [FCStd](cad/entretoise-h31.FCStd) |
| Rondelle plate épaisse M8×21×4 série L (DIN 7349) | 2 | 6 | [FCStd](cad/rondelle-epaisse-din7349-m8.FCStd) |
| Rondelle 8×22×1,5 mm | 1 | 3 | *(non modélisée séparément)* |
| Tampon ressort silicone **CR60, ∅20, 8,5×15 mm, 60 SHA** (amortisseur de rebond) | 1 | 3 | [FCStd](cad/tampon-ressort-cr60.FCStd) · [STL](cad/tampon-ressort-cr60.stl) |
| Vis métaux CHC BTR (clé de 6) M8×70, filetée sur 22, classe 12.9, acier brut | 1 | 3 | [FCStd](cad/vis-chc-m8x70.FCStd) |
| Écrou frein M8 | 1 | 3 | [FCStd](cad/ecrou-frein-m8.FCStd) |
| Boule de pétanque (pleine, ∅70 mm) | 1 | 3 | [FCStd](cad/boule-petanque-pleine.FCStd) |
| Interface axe-aimant (sur-mesure, ∅4 mm) | 1 | 3 | [FCStd](cad/interface-axe-aimant-4mm.FCStd) |
| Aimant néodyme ∅4×2 mm N80 | 1 | 3 | *(doublon avec la ligne électronique ci-dessus — même aimant, à ne compter qu'une fois)* |

Sous-assemblage complet : [assemblage-articulation.FCStd](cad/assemblage-articulation.FCStd).

## Mécanique — châssis (×1, non dupliqué)

Nomenclature exacte de `ChassisAssemblageV7.FCStd` :

| Pièce | Dimensions | Qté | Fichier |
|---|---|---|---|
| Plateau V7 (base, tôle pliée) | 800×343×86 mm | 1 | [STEP](cad/plateau-v7.step) |
| Équerre V7 (fixation plateau ↔ supports/articulations) | ~38×30–48×30–48 mm | 6 | [STEP](cad/equaire-v7.step) |
| Support V7 (rail de maintien) | 8×328,7×77,8 mm | 2 | [STEP](cad/support-v7.step) |
| Sous-assemblage articulation (voir tableau ci-dessus) | 70×140×136,3 mm | 3 | [FCStd](cad/assemblage-articulation.FCStd) |

Assemblage complet : [chassis-assemblage-v7.FCStd](cad/chassis-assemblage-v7.FCStd).

## Sources

- Assemblages FreeCAD inspectés directement (FreeCAD 1.0.2, mode console) :
  `ChassisAssemblageV7.FCStd` (82 objets) et `assemblageArticulation.FCStd`
  (110 objets), dans `ressources/modélisation/Doc final/ChassisV7/`.
- BOM électronique : `ressources/archives/PCB pour détection/composantssmd.png`
  (export JLCPCB).
- Schéma de câblage : `ressources/archives/Contrôleurs de jeu/arduino leonardo/arducibleLeonardoschéma_bb.png`.

*Les quantités "hors châssis" (visserie de fixation plateau/équerre/support,
si non modélisée dans l'assemblage) ne sont pas incluses ici : l'assemblage
FreeCAD ne modélise pas de pièce de fixation explicite à ce niveau.*
