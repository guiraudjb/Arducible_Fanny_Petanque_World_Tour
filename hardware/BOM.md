# Nomenclature (BOM) — Fanny Pétanque World Tour

Borne à 3 cibles physiques. Quantités données **par cible** puis **totales pour
les 3 cibles**, plus les pièces du châssis (non dupliquées) et le contrôleur
central. Les pièces mécaniques et leurs quantités sont extraites directement
de l'assemblage FreeCAD (`ressources/modélisation/Doc final/ChassisV7/`), pas
estimées.

## Électronique — par cible (×3)

| Réf. | Composant | Qté/cible | Qté totale | Fichier |
|---|---|---|---|---|
| U1 | Capteur à effet Hall **OH37** (Nanjing Ouzhuo Tech, SOT-23) | 1 | 3 | [BOM JLCPCB](pcb/bom-jlcpcb-v3.csv) |
| R1 | Résistance **10 kΩ** (CMS 0603) | 1 | 3 | [BOM JLCPCB](pcb/bom-jlcpcb-v3.csv) |
| J1 | Connecteur **JST-XH 3 points** (DATA/-/+, LCSC C2316) | 1 | 3 | [BOM JLCPCB](pcb/bom-jlcpcb-v3.csv) |
| — | PCB détection v3 (Gerber `arduciblesmdv3`, 2 couches) | 1 | 3 | [Gerber](pcb/gerber-pcb-detection-v3.zip) · [BOM](pcb/bom-jlcpcb-v3.csv) · [Pick & Place](pcb/pick-and-place-v3.csv) · [modèle 3D](pcb/OBJ_arduciblesmdv3_2026-07-19.zip) · [FCStd](cad/detection-pcb-v3.FCStd) · [Fritzing](fritzing/PetanqueDetection_Board_v3.fzpz) |
| — | Aimant néodyme cylindrique **∅4×2 mm, grade indiqué N80** (solidaire de la boule, déclenche le capteur) | 1 | 3 | [FCStd](cad/aimant-neodyme-4x2.FCStd) · [Fournisseur](https://www.supermagnete.fr/aimants-disques-neodyme/disque-magnetique-diametre-4mm-hauteur-2mm-neodyme-n45-nickele_S-04-02-N) — voir note grade N80 en section Mécanique — articulation |

*Fichiers de commande JLCPCB (Gerber/BOM/Pick & Place, prêts à l'import)
générés le 2026-07-17, à jour dans `pcb/*-v3.*`. Connecteur JST-XH replacé en
face arrière le 2026-07-19 (voir `pcb/pcb.readme`). Source des
quantités de lot (pas la consommation réelle de 1/cible) : capture
"Bill of Material" JLCPCB (`ressources/archives/PCB pour détection/composantssmd.png`)
— OH37 commandé ×25, résistance 10k ×30.*

## Électronique — contrôleur central (×1)

| Composant | Détail | Fichier |
|---|---|---|
| Carte Pro Micro (ATmega32U4) | Même puce qu'un Arduino Leonardo, dont elle reprend le brochage — reconnue comme tel par l'ordinateur (USB HID natif, clavier). Reçoit les 3 signaux de cible et envoie les touches `E`/`R`/`T`. | [Photo fournisseur](renders/vendor/pro-micro-board.png) · [Pièce Fritzing](fritzing/pro-micro-jeremylee-sparkfun.fzpz) |
| Sketch Arduino | Boucle de lecture des 3 broches cible + retranscription clavier via `Keyboard.h`. | [littlepromicro.ino](firmware/littlepromicro.ino) |
| Boîtier de protection (prototype) | Petit boîtier imprimé en 3D pour la carte nue, antérieur au boîtier de la borne ci-dessous. | [FCStd](enclosure/promicrousbcv1.FCStd) |
| Connecteurs RJ45 (×3) + câble Ethernet Cat5/6 | Un câble réseau par cible ramène le signal du capteur + alimentation vers la carte Pro Micro. | [Schéma Fritzing](schematics/pro-micro-wiring.png) ([source](fritzing/cablage-pro-micro.fzz)) · [Pièce Fritzing RJ45](fritzing/rj45-8-jack-sparkfun.fzpz) (déjà incluse nativement dans Fritzing : Core Parts → « RJ45 Jack ») · [Ancien schéma Leonardo](schematics/arduino-leonardo-rj45-wiring.png) |
| Câble Micro-USB | Liaison Leonardo ↔ PC. | — |
| Boîtier imprimé en 3D (façade, fermeture, casquette, support WS2812) | Réutilise le design du contrôleur Pro Micro, adapté pour loger le Leonardo. | [FCStd](enclosure/boitierJeufreecad020.FCStd) · [Façade STL](enclosure/boitierJeu-facade.stl) · [Fermeture STL](enclosure/boitierJeu-fermeture.stl) · [Casquette STL](enclosure/boitierJeufreecad020-casquette.stl) · [Support WS2812 STL](enclosure/boitierJeu-supportws2812.stl) |

> Le schéma de câblage montre aussi 4 boutons "Key up/left/right/down" :
> **obsolètes**, hérités d'un prototype antérieur — le jeu actuel n'utilise
> que les 3 cibles (`E`/`R`/`T`).

## Mécanique — par cible / articulation (×3)

Nomenclature exacte de `assemblageArticulation.FCStd` :

| Pièce | Qté/cible | Qté totale | Fichier |
|---|---|---|---|
| Plaque d'articulation milieu (découpe laser 140×40×5 mm) | 1 | 3 | [STEP](cad/plaque-milieu.step) · [FCStd](cad/plaque-milieu.FCStd) · [Plan coté](plans/plaque-milieu.pdf) |
| Plaque d'articulation sup (idem) | 1 | 3 | [STEP](cad/plaque-sup.step) · [FCStd](cad/plaque-sup.FCStd) · [Plan coté](plans/plaque-sup.pdf) |
| Plaque d'articulation inf (idem) | 1 | 3 | [STEP](cad/plaque-inf.step) · [FCStd](cad/plaque-inf.FCStd) · [Plan coté](plans/plaque-inf.pdf) |
| Vis métaux tête fraisée TF Pozi M4×50, acier zingué blanc | 2 | 6 | [FCStd](cad/vis-m4x50-tf-pozi.FCStd) · [Fournisseur](https://www.vis-express.fr/vis-metaux-tete-fraisee-tf-pozi-din-965/26698-vis-metaux-tete-fraisee-tf-pozi-2-m4x50-acier-zingue.html) |
| Écrou frein M4 (nylstop, DIN 985, acier zingué blanc) | 6 | 18 | [FCStd](cad/ecrou-frein-m4.FCStd) · [Fournisseur](https://www.vis-express.fr/ecrou-frein-din-985-din-985vs4325/31291-ecrou-frein-m4-acier-zingue.html) |
| Vis métaux M4×30 (tête fraisée Pozi n°2, DIN 965, acier zingué blanc) | 4 | 12 | [FCStd](cad/vis-m4x30.FCStd) · [Fournisseur](https://www.vis-express.fr/vis-metaux-tete-fraisee-tf-pozi-din-965/26679-vis-metaux-tete-fraisee-tf-pozi-n2-m4x30-acier-zingue.html) |
| Rotule radiale **GE8C** (rotule à rotule, alésage 8 mm) | 1 | 3 | [FCStd](cad/rotule-ge8c.FCStd) · variante articulée (chape + bille réelles, utilisée dans l'assemblage) : [FCStd](cad/rotule-ge8-articulee.FCStd) · [Fournisseur](https://www.lebonroulement.com/rotule-serie-ge-gek-gedo-geuk/147702-rotule-radiale-ge8c-kml.html) |
| Entretoise carte électronique (H31, sur-mesure) | 1 | 3 | [FCStd](cad/entretoise-h31.FCStd) |
| Rondelle plate épaisse M8×21×4 série L (DIN 7349) | 2 | 6 | [FCStd](cad/rondelle-epaisse-din7349-m8.FCStd) · [Fournisseur](https://www.vis-express.fr/rondelle-plate-serie-l-large-din-7349/5153-rondelle-plate-m8x21x4-serie-l-large-acier-zingue-blanc.html) |
| Rondelle 8×22×1,5 mm | 1 | 3 | [FCStd](cad/rondelle-8x22x1-5.FCStd) · [Fournisseur](https://www.vis-express.fr/rondelle-plate-l-nfe-25513-nfe-25513vs-nfe25513-grade-c/29545-rondelle-plate-m8x22x15-l-acier-zingue.html) |
| Tampon ressort **polychloroprène (CR) 60 SHA, ∅20, 8,5×15 mm** (amortisseur de rebond) | 1 | 3 | [FCStd](cad/tampon-ressort-cr60.FCStd) · [STL](cad/tampon-ressort-cr60.stl) · variante déformable (utilisée dans l'assemblage) : [FCStd](cad/tampon-ressort-cr60-deformable.FCStd) |
| Vis métaux CHC BTR (clé de 6) M8×70, filetée sur 28, classe 12.9, acier brut | 1 | 3 | [FCStd](cad/vis-chc-m8x70.FCStd) · [Fournisseur](https://www.vis-express.fr/vis-metaux-chc-btr-filetage-total-classe-129-hexagonal-creux-din-912-din-912-iso-4762/14889-vis-metaux-chc-btr-cle-de-6-hc6-m8x70-filetee-sur-28-classe-129-acier-brut.html) |
| Écrou frein M8 (nylstop, DIN 985, acier zingué blanc) | 1 | 3 | [FCStd](cad/ecrou-frein-m8.FCStd) · [Fournisseur](https://www.vis-express.fr/ecrou-frein-din-985-din-985vs4325/31317-ecrou-frein-m8-acier-zingue.html) |
| Boule de pétanque (∅70 mm — modélisée pleine par simplification CAO ; une vraie boule est toujours une coque creuse) | 1 | 3 | [FCStd](cad/boule-petanque-pleine.FCStd) · [Ébauche testée (Décathlon)](https://www.decathlon.fr/p/jeu-de-3-boules-de-petanque-100-loisir-lisses/324055/c231c5m8579726) — perçage/taraudage M8 validé malgré la coque fine ; remplissage terre/gravier → corrosion de l'axe, graissage recommandé ; piste non résolue pour une meilleure coque perçable/taraudable : [boule inox ∅60×2 mm insert M8](https://www.metalenstock.fr/boules-et-bagues-en-inox/542-boule-decorative-inox-creuse-diametre-60-epaisseur-2-mm-insert-m8.html) · [boule inox ∅80×2 mm insert M8](https://www.metalenstock.fr/boules-et-bagues-en-inox/543-boule-decorative-inox-creuse-diametre-80-epaisseur-2-mm-insert-m8.html) (non testées) ; recherche d'un ∅70 mm prêt-à-l'emploi (percé+taraudé M8) infructueuse chez les fournisseurs inox spécialisés (Metalenstock, Esse, Oxynov — gamme standard 60→80 mm, rien à 70 mm) ; piste la plus proche : [boule acier brut ∅70×3 mm non taraudée (decoferforge.com)](https://www.decoferforge.com/rubrique/boules-acier/boules-creuses), à percer/tarauder soi-même et non inox (anticorrosion à ajouter) ; Metalenstock propose sinon un devis sur mesure |
| Interface axe-aimant (sur-mesure, ∅4 mm) | 1 | 3 | [FCStd](cad/interface-axe-aimant-4mm.FCStd) |
| Aimant néodyme ∅4×2 mm, grade indiqué N80 | 1 | 3 | *(doublon avec la ligne électronique ci-dessus — même aimant, à ne compter qu'une fois)* · [Fournisseur](https://www.supermagnete.fr/aimants-disques-neodyme/disque-magnetique-diametre-4mm-hauteur-2mm-neodyme-n45-nickele_S-04-02-N) — **N80 n'est pas un grade néodyme standard** (grades réels : N35 à N52), probable confusion avec la température de fonctionnement max. (80 °C) ; la référence la plus proche en ∅4×2 mm est un grade N45 |

Sous-assemblage complet : [assemblage-articulation.FCStd](cad/assemblage-articulation.FCStd).

*Depuis le 2026-07-20, `assemblage-articulation.FCStd` affiche les variantes
articulée/déformable de la rotule GE8 et du tampon ressort (géométrie réelle
en deux corps pour la rotule — chape fixe + bille solidaire de l'axe — et
profil de révolution pour le tampon) au lieu des pièces figées d'origine.
Les objets d'origine (`RotuleGE8_001`, `tamponressort_001`) sont conservés
dans le fichier mais masqués, pour ne pas casser les contraintes A2plus qui
s'y réfèrent. Achat/nomenclature inchangés — même rotule GE8C, même tampon
CR60 du commerce ; seule la représentation CAD change.*

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
