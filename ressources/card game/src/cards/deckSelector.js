// Choix du jeu de cartes (thème visuel) - partagé entre tous les jeux de
// cartes du casino (Belote, Solitaire, Vidéo Poker, Blackjack, Baccara).
// Persisté dans localStorage sous une clé unique et commune : changer de
// deck dans un jeu le garde pour les autres, comme un vrai jeu de cartes
// qu'on apporterait d'une table à l'autre.

const STORAGE_KEY = 'fanny-deck-theme';

export const DECKS = [
  { id: 'default', label: 'Classique', folder: null },
  { id: 'theme-sexy', label: 'Sexy', folder: 'theme-sexy' },
  { id: 'theme-plage-ville', label: 'Plage / Ville', folder: 'theme-plage-ville' },
  { id: 'theme-outfits', label: 'Outfits', folder: 'theme-outfits' },
  { id: 'theme-decennies', label: 'Décennies vintage', folder: 'theme-decennies' },
  { id: 'theme-couture', label: 'Haute Couture', folder: 'theme-couture' },
  { id: 'theme-souscultures', label: 'Sous-cultures', folder: 'theme-souscultures' },
  { id: 'theme-voyage', label: 'Voyage & Vacances', folder: 'theme-voyage' },
  { id: 'theme-soiree', label: 'Soirée & Gala', folder: 'theme-soiree' },
  { id: 'theme-sport', label: 'Sport & Loisirs', folder: 'theme-sport' },
  { id: 'theme-fanny-vol1', label: 'Fanny World Tour — Vol. 1', folder: 'theme-fanny-vol1' },
  { id: 'theme-fanny-vol2', label: 'Fanny World Tour — Vol. 2', folder: 'theme-fanny-vol2' },
];

export function getSelectedDeckId() {
  const stored = localStorage.getItem(STORAGE_KEY);
  return DECKS.some((d) => d.id === stored) ? stored : DECKS[0].id;
}

function setSelectedDeckId(id) {
  localStorage.setItem(STORAGE_KEY, id);
}

/** Dossier de sprites pour un deck donné, à partir du dossier de base du
 * jeu appelant (toujours `../../assets/cards/` dans ce projet, mais laissé
 * paramétrable plutôt que codé en dur ici). */
export function spriteDirFor(deckId, baseSpriteDir = '../../assets/cards/') {
  const deck = DECKS.find((d) => d.id === deckId) || DECKS[0];
  return deck.folder ? `${baseSpriteDir}${deck.folder}/` : baseSpriteDir;
}

/**
 * Câble un <select> existant : le remplit avec les 12 decks, sélectionne
 * celui déjà choisi (localStorage), et appelle `onChange(spriteDir)` à
 * chaque changement - y compris une fois immédiatement à l'initialisation,
 * pour que l'appelant reçoive le dossier de sprites de départ sans dupliquer
 * la lecture du localStorage de son côté.
 */
export function createDeckSelector({ selectEl, baseSpriteDir = '../../assets/cards/', onChange }) {
  selectEl.innerHTML = '';
  for (const deck of DECKS) {
    const opt = document.createElement('option');
    opt.value = deck.id;
    opt.textContent = deck.label;
    selectEl.appendChild(opt);
  }
  const current = getSelectedDeckId();
  selectEl.value = current;

  selectEl.addEventListener('change', () => {
    setSelectedDeckId(selectEl.value);
    onChange(spriteDirFor(selectEl.value, baseSpriteDir));
  });

  onChange(spriteDirFor(current, baseSpriteDir));
}
