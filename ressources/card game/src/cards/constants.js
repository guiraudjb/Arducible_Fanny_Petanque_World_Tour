// Constantes du jeu de 54 cartes (52 + 2 jokers)

export const SUITS = Object.freeze({
  HEARTS: 'hearts',
  DIAMONDS: 'diamonds',
  CLUBS: 'clubs',
  SPADES: 'spades',
});

export const SUIT_SYMBOLS = Object.freeze({
  [SUITS.HEARTS]: '♥',
  [SUITS.DIAMONDS]: '♦',
  [SUITS.CLUBS]: '♣',
  [SUITS.SPADES]: '♠',
});

export const SUIT_COLORS = Object.freeze({
  [SUITS.HEARTS]: 'red',
  [SUITS.DIAMONDS]: 'red',
  [SUITS.CLUBS]: 'black',
  [SUITS.SPADES]: 'black',
});

// Ordre des rangs du plus bas au plus haut (as bas par défaut)
export const RANKS = Object.freeze([
  'A', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K',
]);

export const JOKER_COLORS = Object.freeze({
  RED: 'red',
  BLACK: 'black',
});
