// Belote à quatre, en deux équipes de deux (vous + Fanny contre deux
// adversaires) - une donne par mise. Règles classiques françaises :
//   - Paquet de 32 cartes (7 à As), 8 cartes chacun (32 = 4x8).
//   - Sièges (dans l'ordre du tour de table) : PLAYER, OPP1, FANNY, OPP2.
//     PLAYER et FANNY sont partenaires (équipe A), OPP1 et OPP2 forment
//     l'équipe B - les partenaires sont toujours assis en face l'un de
//     l'autre, jamais côte à côte.
//   - Donne : 5 cartes à chacun, puis une carte est retournée. Le joueur
//     à gauche du distributeur parle en premier.
//   - Enchères : au premier tour, chacun peut "prendre" la couleur de la
//     carte retournée (comme atout) ou passer. Si tout le monde passe,
//     second tour : chacun peut annoncer n'importe quelle AUTRE couleur
//     comme atout, ou passer. Si tout le monde passe deux fois, on
//     redistribue (nouvelle donne, même mise).
//   - Une fois l'atout pris : celui qui a pris ramasse la carte retournée
//     dans sa main (pas systématiquement le distributeur), puis on
//     complète les mains (3 cartes aux trois autres joueurs, 2 seulement
//     au preneur qui a déjà la carte retournée) : tout le monde termine à
//     8 cartes. Le premier pli est toujours entamé par le joueur à
//     gauche du distributeur, que ce soit lui le preneur ou non.
//   - Suivi du pli : obligation de fournir la couleur demandée ; à
//     défaut, obligation de couper à l'atout ; obligation de monter
//     (sur-couper) si on le peut - SAUF si le partenaire est déjà maître
//     du pli (ces deux exceptions n'existaient pas dans une variante à 2
//     joueurs sans partenaire).
//   - Belote-Rebelote (Roi+Dame d'atout dans la même main) : +20 points
//     à l'équipe qui les détient, annoncée automatiquement.
//   - "Dix de der" : +10 points à l'équipe qui remporte le dernier pli.
//   - Chute : si l'équipe preneuse (celle qui a annoncé l'atout) ne
//     totalise pas au moins 82 points aux plis, elle marque 0 et
//     l'équipe adverse rafle la totalité des points de la donne (162),
//     chacune gardant malgré tout son bonus belote-rebelote éventuel.
//   - Victoire de la donne : l'équipe qui totalise le plus de points
//     (après application de la chute) l'emporte.
//   - Le paquet n'est JAMAIS rebattu entre deux mènes (seulement mélangé
//     une fois, au tout premier coup d'une nouvelle partie) : entre deux
//     mènes, on ramasse les cartes dans leur ordre de chute exact et on
//     coupe une seule fois. C'est cette règle qui rend une vraie mémoire
//     des plis de la mène précédente utile (voir ai.js) - contrairement à
//     un paquet rebattu à fond, une simple coupe ne détruit pas l'ordre
//     relatif des cartes.

export const SUITS = ['coeur', 'carreau', 'trefle', 'pique'];
export const SUIT_SYMBOLS = { coeur: '♥', carreau: '♦', trefle: '♣', pique: '♠' };
export const SUIT_COLORS = { coeur: 'red', carreau: 'red', trefle: 'black', pique: 'black' };
const RANKS = ['7', '8', '9', '10', 'J', 'Q', 'K', 'A'];

export const SEATS = ['player', 'opp1', 'fanny', 'opp2'];
export const PLAYER = 0;
export const OPP1 = 1;
export const FANNY = 2;
export const OPP2 = 3;
export const BOTS = [OPP1, FANNY, OPP2];

export function teamOf(seat) {
  return seat % 2 === 0 ? 'A' : 'B';
}
export function partnerOf(seat) {
  return (seat + 2) % 4;
}
function nextSeat(seat) {
  return (seat + 1) % 4;
}

const TRUMP_ORDER = ['7', '8', 'Q', 'K', '10', 'A', '9', 'J']; // du plus faible au plus fort
const TRUMP_POINTS = { J: 20, 9: 14, A: 11, 10: 10, K: 4, Q: 3, 8: 0, 7: 0 };
const NONTRUMP_ORDER = ['7', '8', '9', 'J', 'Q', 'K', '10', 'A'];
const NONTRUMP_POINTS = { A: 11, 10: 10, K: 4, Q: 3, J: 2, 9: 0, 8: 0, 7: 0 };

const DIX_DE_DER = 10;
const BELOTE_REBELOTE = 20;
const CONTRACT_THRESHOLD = 82;
const TOTAL_TRICK_POINTS = 162; // 152 (valeur des cartes) + 10 (dix de der)

function makeCard(rank, suit) {
  return { rank, suit, id: `${rank}-${suit}` };
}

function buildDeck() {
  const cards = [];
  for (const suit of SUITS) for (const rank of RANKS) cards.push(makeCard(rank, suit));
  return cards;
}

function shuffle(array) {
  for (let i = array.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
  return array;
}

export function cardPoints(card, trumpSuit) {
  return card.suit === trumpSuit ? TRUMP_POINTS[card.rank] : NONTRUMP_POINTS[card.rank];
}

function cardRank(card, trumpSuit) {
  return card.suit === trumpSuit ? TRUMP_ORDER.indexOf(card.rank) : NONTRUMP_ORDER.indexOf(card.rank);
}

// Cycle des enseignes qui alterne rouge/noir/rouge/noir (et boucle
// proprement : pique->coeur alterne aussi) - voir sortHand ci-dessous.
const SUIT_CYCLE = ['coeur', 'trefle', 'carreau', 'pique'];

/** Trie une main pour l'affichage : atout d'abord (du plus faible au plus
 * fort) s'il y en a un, puis les 3 autres enseignes en poursuivant le cycle
 * rouge/noir à partir de l'atout - deux enseignes de même couleur ne se
 * suivent donc jamais. Sans atout encore connu (avant l'enchère), utilise
 * le cycle tel quel à partir de cœur. */
export function sortHand(hand, trumpSuit) {
  const start = trumpSuit ? SUIT_CYCLE.indexOf(trumpSuit) : 0;
  const groups = [...SUIT_CYCLE.slice(start), ...SUIT_CYCLE.slice(0, start)];
  return hand.slice().sort((a, b) => {
    const ga = groups.indexOf(a.suit);
    const gb = groups.indexOf(b.suit);
    if (ga !== gb) return ga - gb;
    return cardRank(a, trumpSuit) - cardRank(b, trumpSuit);
  });
}

function currentTrickWinnerSeat(trick, trumpSuit) {
  const trumpsPlayed = trick.filter((t) => t.card.suit === trumpSuit);
  const pool = trumpsPlayed.length > 0 ? trumpsPlayed : trick.filter((t) => t.card.suit === trick[0].card.suit);
  return pool.reduce((best, t) => (cardRank(t.card, trumpSuit) > cardRank(best.card, trumpSuit) ? t : best)).seat;
}

/** Cartes jouables depuis `hand` compte tenu du pli en cours (voir
 * commentaire d'en-tête). `trick`: [{ card, seat }]. */
export function legalMoves(hand, trick, trumpSuit, mySeat) {
  if (trick.length === 0) return hand.slice();
  const ledSuit = trick[0].card.suit;
  const sameSuit = hand.filter((c) => c.suit === ledSuit);
  const partnerWinning = currentTrickWinnerSeat(trick, trumpSuit) === partnerOf(mySeat);

  if (sameSuit.length > 0) {
    if (ledSuit === trumpSuit) {
      if (partnerWinning) return sameSuit;
      const trumpsInTrick = trick.filter((t) => t.card.suit === trumpSuit);
      const bestRank = Math.max(...trumpsInTrick.map((t) => cardRank(t.card, trumpSuit)));
      const overtrumps = sameSuit.filter((c) => cardRank(c, trumpSuit) > bestRank);
      return overtrumps.length > 0 ? overtrumps : sameSuit;
    }
    return sameSuit;
  }

  const trumps = hand.filter((c) => c.suit === trumpSuit);
  if (trumps.length === 0) return hand.slice();
  if (partnerWinning) return hand.slice();

  const trumpsInTrick = trick.filter((t) => t.card.suit === trumpSuit);
  if (trumpsInTrick.length > 0) {
    const bestRank = Math.max(...trumpsInTrick.map((t) => cardRank(t.card, trumpSuit)));
    const overtrumps = trumps.filter((c) => cardRank(c, trumpSuit) > bestRank);
    return overtrumps.length > 0 ? overtrumps : trumps;
  }
  return trumps;
}

/* ------------------------------------------------------------------ */
/* L'IA (mémoire, probabilités, enchères, jeu de carte) vit dans        */
/* ./ai.js - elle a besoin d'un accès à cardRank/currentTrickWinnerSeat, */
/* exportés ci-dessous pour cet usage interne au module Belote.         */
/* ------------------------------------------------------------------ */
export { cardRank, currentTrickWinnerSeat };

/** Distribution initiale : 5 cartes à chacun (indices de sièges fixes,
 * PLAYER=deck[0:5], OPP1=deck[5:10], ...), puis carte retournée = deck[20].
 * Fonction pure, partagée entre le vrai moteur et la reconstruction de
 * l'IA (reconstructDeal) pour ne jamais désynchroniser les deux. */
function dealInitialHands(deck) {
  return [deck.slice(0, 5), deck.slice(5, 10), deck.slice(10, 15), deck.slice(15, 20)];
}

/** Complète les mains après l'enchère : la carte retournée + le talon
 * vont au preneur (3 cartes aux trois autres, dans l'ordre du tour de
 * table à partir du joueur à gauche du distributeur ; 2 seulement au
 * preneur qui a déjà la carte retournée). Fonction pure, voir ci-dessus. */
function completeHands(initialHands, remainingDeck, turnedCard, dealerSeat, preneur) {
  const hands = initialHands.map((h) => h.slice());
  hands[preneur].push(turnedCard);
  const order = [];
  for (let s = nextSeat(dealerSeat), i = 0; i < 4; s = nextSeat(s), i += 1) {
    if (s !== preneur) order.push(s);
  }
  let cursor = 0;
  for (const seat of order) {
    hands[seat].push(...remainingDeck.slice(cursor, cursor + 3));
    cursor += 3;
  }
  hands[preneur].push(...remainingDeck.slice(cursor, cursor + 2));
  return hands;
}

/** Étant donné l'ordre exact de chute des cartes de la DERNIÈRE mène
 * réellement jouée (`previousSequence`, 32 cartes, voir Belote.lastRealSequence)
 * et sachant qu'une seule coupe (jamais un mélange) a eu lieu depuis,
 * cherche la (ou les) rotation(s) du paquet cohérente(s) avec la main que
 * `mySeat` a réellement reçue cette donne (`myOriginalHand`, ses 8 cartes
 * d'origine, jouées ou non). Comme les 32 cartes sont toutes différentes,
 * une seule rotation colle presque toujours en pratique : c'est la
 * mémoire "absolue" d'un joueur qui a suivi toute la mène précédente et
 * sait qu'on ne fait que couper entre deux mènes. Ne fuite aucune
 * information cachée : ne s'appuie que sur des faits publics (l'ordre de
 * chute déjà vu par tout le monde, ma propre main, le distributeur, le
 * preneur). Retourne un tableau de reconstructions cohérentes (0, 1, ou
 * rarement plus d'une), chacune `{ hands, turnedCard }`. */
export function reconstructDeal({ previousSequence, mySeat, myOriginalHand, dealerSeat, preneur }) {
  if (!previousSequence || previousSequence.length !== 32) return [];
  const myIds = myOriginalHand.map((c) => c.id).slice().sort().join(',');
  const matches = [];
  for (let k = 0; k < 32; k += 1) {
    const rotated = [...previousSequence.slice(k), ...previousSequence.slice(0, k)];
    const initial = dealInitialHands(rotated);
    const turnedCard = rotated[20];
    const remainingDeck = rotated.slice(21);
    const hands = completeHands(initial, remainingDeck, turnedCard, dealerSeat, preneur);
    const simIds = hands[mySeat].map((c) => c.id).slice().sort().join(',');
    if (simIds === myIds) matches.push({ hands, turnedCard });
  }
  return matches;
}

export const TIERS = [
  { key: 'legendaire', name: 'Manche légendaire', min: 152, mult: 15 },
  { key: 'exceptionnel', name: 'Manche exceptionnelle', min: 130, mult: 8 },
  { key: 'remarquable', name: 'Manche remarquable', min: 110, mult: 5 },
  { key: 'beau', name: 'Belle manche', min: 100, mult: 3 },
  { key: 'bon', name: 'Bonne manche', min: 92, mult: 2 },
  { key: 'correct', name: 'Manche gagnée', min: 82, mult: 1 },
  { key: 'perdu', name: 'Manche perdue', min: 0, mult: 0 },
];

export function tierForScore(score) {
  return TIERS.find((t) => score >= t.min);
}

// Une "partie" (au sens traditionnel de la belote) se joue en 500 points,
// cumulés manche après manche - indépendamment des mises/du bankroll du
// casino, qui continuent sans interruption d'une partie à l'autre.
const PARTIE_TARGET = 500;

export class Belote {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.dealerSeat = Math.floor(Math.random() * 4);
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = 0;
    this.lastBet = 0;
    this.phase = 'betting'; // 'betting' | 'bidding' | 'playing' | 'result'
    // Ordre de chute exact de la dernière mène réellement jouée (32
    // cartes) - null tant qu'aucune mène de CETTE session n'est encore
    // allée à son terme. Sert à la fois à reconstituer le paquet réel de
    // la donne suivante (jamais rebattu, seulement coupé) et de mémoire à
    // l'IA (voir ai.js / reconstructDeal). Remis à null uniquement ici :
    // une nouvelle session = un nouveau paquet, mélangé pour de vrai.
    this.lastRealSequence = null;
    // Score cumulé de la partie en cours (500 points), remis à zéro ici
    // (nouvelle session = nouvelle partie) et quand une partie est gagnée
    // (voir _finishRound / nextRound) - distinct de teamScores, qui ne
    // compte que la mène en cours.
    this.matchScores = { A: 0, B: 0 };
    this._pendingPartieReset = false;
    this._resetHandState();
  }

  _resetHandState() {
    this.hands = [[], [], [], []];
    this.turnedCard = null;
    this.biddingRound = 1;
    this.biddingTurn = null;
    this.passCount = 0;
    this.trumpSuit = null;
    this.preneur = null;
    this.trick = [];
    this.leader = null;
    this.trickNum = 0;
    this.teamScores = { A: 0, B: 0 };
    this.tricksWonBy = { A: 0, B: 0 };
    this.beloteSeat = null;
    // null tant qu'aucune des deux cartes n'a été jouée ; 'belote' dès que
    // le siège qui a Roi+Dame d'atout en joue une des deux (peu importe
    // laquelle, peu importe le pli) ; 'rebelote' dès qu'il joue l'autre.
    this.beloteState = null;
    this.lastTrick = null;
    this.result = null;
    // Historique complet des plis déjà complétés dans LA MÈNE EN COURS,
    // pour que l'IA puisse compter les cartes tombées et détecter les
    // coupes (voir ai.js) - remis à zéro à chaque nouvelle donne. Son
    // contenu final est capturé dans `lastRealSequence` par
    // `_finishRound()` juste avant d'être écrasé ici, pour rester
    // disponible comme mémoire de "la mène précédente" à la donne
    // suivante (voir reconstructDeal ci-dessus).
    this.trickHistory = [];
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  startRound(bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (!Number.isFinite(bet) || bet <= 0 || bet > this.bankroll) return { ok: false, reason: 'bad-bet' };

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= bet;
    this._resetHandState();
    this._dealForBidding();
    this.phase = 'bidding';
    return { ok: true };
  }

  /** Une seule coupe (jamais un mélange) : scinde le paquet à un point
   * aléatoire et échange les deux tas. */
  _cut(deck) {
    const margin = 4; // évite une coupe dégénérée trop proche d'un bord
    const cutPoint = margin + Math.floor(Math.random() * (deck.length - margin * 2));
    return [...deck.slice(cutPoint), ...deck.slice(0, cutPoint)];
  }

  _dealForBidding({ isRedeal = false } = {}) {
    let baseDeck;
    if (isRedeal) {
      // Personne n'a pris : aucun pli n'a été joué, on regroupe
      // simplement ce qui avait déjà été distribué pour cette tentative
      // (la mémoire de l'IA, elle, reste basée sur `lastRealSequence` -
      // rien de nouveau n'a été révélé par cette enchère ratée).
      baseDeck = [
        ...this.hands[PLAYER], ...this.hands[OPP1], ...this.hands[FANNY], ...this.hands[OPP2],
        ...(this.turnedCard ? [this.turnedCard] : []),
        ...(this._remainingDeck || []),
      ];
    } else if (this.lastRealSequence === null) {
      baseDeck = shuffle(buildDeck()); // tout premier paquet de la session : seul vrai mélange
    } else {
      baseDeck = this.lastRealSequence; // ordre de chute exact de la dernière mène jouée
    }

    const deck = this._cut(baseDeck);
    this.hands = dealInitialHands(deck);
    this.hands[PLAYER] = sortHand(this.hands[PLAYER], null); // pas d'atout connu avant l'enchère
    this.turnedCard = deck[20];
    this._remainingDeck = deck.slice(21); // 11 cartes, complétées après enchères
    this.biddingRound = 1;
    this.biddingTurn = nextSeat(this.dealerSeat);
    this.passCount = 0;
    // Historique des annonces de CETTE enchère (remis à zéro à chaque
    // redonne) - permet à l'IA de savoir ce que son partenaire a déjà dit
    // ce tour-ci (voir "soutien" dans ai.js).
    this.biddingHistory = [];
  }

  get turn() {
    if (this.phase === 'bidding') return this.biddingTurn;
    if (this.phase !== 'playing') return null;
    return (this.leader + this.trick.length) % 4;
  }

  legalMovesForSeat(seat) {
    if (this.phase !== 'playing' || this.turn !== seat) return [];
    return legalMoves(this.hands[seat], this.trick, this.trumpSuit, seat);
  }

  bid(seat, action) {
    if (this.phase !== 'bidding' || seat !== this.biddingTurn) return { ok: false, reason: 'wrong-phase' };
    this.biddingHistory.push({ seat, round: this.biddingRound, action });

    if (action.type === 'take') {
      const suit = this.biddingRound === 1 ? this.turnedCard.suit : action.suit;
      if (this.biddingRound === 2 && suit === this.turnedCard.suit) return { ok: false, reason: 'bad-suit' };
      if (!SUITS.includes(suit)) return { ok: false, reason: 'bad-suit' };
      this.trumpSuit = suit;
      this.preneur = seat;
      this._completeDeal();
      return { ok: true };
    }

    if (action.type !== 'pass') return { ok: false, reason: 'bad-action' };
    this.passCount += 1;
    if (this.passCount === 4) {
      if (this.biddingRound === 1) {
        this.biddingRound = 2;
        this.passCount = 0;
        this.biddingTurn = nextSeat(this.dealerSeat);
      } else {
        this._dealForBidding({ isRedeal: true }); // tout le monde a passé deux fois : redonne
      }
      return { ok: true };
    }
    this.biddingTurn = nextSeat(this.biddingTurn);
    return { ok: true };
  }

  _completeDeal() {
    // La carte retournée revient à celui qui prend (pas systématiquement
    // au distributeur) : il termine donc à 6 cartes avant le complément,
    // pendant que les trois autres n'en ont que 5.
    this.hands = completeHands(this.hands, this._remainingDeck, this.turnedCard, this.dealerSeat, this.preneur);
    this.hands[PLAYER] = sortHand(this.hands[PLAYER], this.trumpSuit);

    for (const seat of [PLAYER, OPP1, FANNY, OPP2]) {
      const hasK = this.hands[seat].some((c) => c.suit === this.trumpSuit && c.rank === 'K');
      const hasQ = this.hands[seat].some((c) => c.suit === this.trumpSuit && c.rank === 'Q');
      if (hasK && hasQ) this.beloteSeat = seat;
    }

    this.trick = [];
    this.leader = nextSeat(this.dealerSeat);
    this.trickNum = 0;
    this.phase = 'playing';
  }

  playCard(seat, cardId) {
    if (this.phase !== 'playing' || this.turn !== seat) return { ok: false, reason: 'wrong-phase' };
    const hand = this.hands[seat];
    const idx = hand.findIndex((c) => c.id === cardId);
    if (idx === -1) return { ok: false, reason: 'not-in-hand' };
    const card = hand[idx];
    const legal = legalMoves(hand, this.trick, this.trumpSuit, seat);
    if (!legal.some((c) => c.id === cardId)) return { ok: false, reason: 'illegal-move' };

    hand.splice(idx, 1);
    this.trick.push({ card, seat });

    if (seat === this.beloteSeat && card.suit === this.trumpSuit && (card.rank === 'K' || card.rank === 'Q')) {
      this.beloteState = this.beloteState === null ? 'belote' : 'rebelote';
    }

    if (this.trick.length === 4) {
      const winnerSeat = currentTrickWinnerSeat(this.trick, this.trumpSuit);
      const winnerTeam = teamOf(winnerSeat);
      const isLastTrick = this.trickNum === 7;
      const points = this.trick.reduce((sum, t) => sum + cardPoints(t.card, this.trumpSuit), 0)
        + (isLastTrick ? DIX_DE_DER : 0);
      this.teamScores[winnerTeam] += points;
      this.tricksWonBy[winnerTeam] += 1;
      this.lastTrick = { cards: this.trick.slice(), winnerSeat };
      this.trickHistory.push({ cards: this.trick.slice(), ledSuit: this.trick[0].card.suit, winnerSeat });
      this.trick = [];
      this.leader = winnerSeat;
      this.trickNum += 1;

      if (this.trickNum === 8) this._finishRound();
    }
    return { ok: true };
  }

  _finishRound() {
    const preneurTeam = teamOf(this.preneur);
    const defenderTeam = preneurTeam === 'A' ? 'B' : 'A';
    const beloteTeam = this.beloteSeat !== null ? teamOf(this.beloteSeat) : null;
    const beloteBonus = { A: beloteTeam === 'A' ? BELOTE_REBELOTE : 0, B: beloteTeam === 'B' ? BELOTE_REBELOTE : 0 };

    const preneurRaw = this.teamScores[preneurTeam];
    const made = preneurRaw >= CONTRACT_THRESHOLD;

    const finalScores = { A: 0, B: 0 };
    if (made) {
      finalScores.A = this.teamScores.A + beloteBonus.A;
      finalScores.B = this.teamScores.B + beloteBonus.B;
    } else {
      finalScores[preneurTeam] = beloteBonus[preneurTeam];
      finalScores[defenderTeam] = TOTAL_TRICK_POINTS + beloteBonus[defenderTeam];
    }

    const teamAScore = finalScores.A;
    const tier = tierForScore(teamAScore);
    const payout = this.bet * tier.mult;
    this.bankroll += payout;

    const capotTeam = this.tricksWonBy.A === 8 ? 'A' : (this.tricksWonBy.B === 8 ? 'B' : null);

    // Cumul de la partie (500 points, voir PARTIE_TARGET) : si le seuil est
    // atteint, la partie est gagnée et repartira de zéro à la manche
    // suivante (voir nextRound) - le score affiché ici, lui, reste celui
    // qui a fait gagner la partie, jusqu'à ce que la manche suivante démarre.
    this.matchScores.A += finalScores.A;
    this.matchScores.B += finalScores.B;
    const partieWinner = this.matchScores.A >= PARTIE_TARGET || this.matchScores.B >= PARTIE_TARGET
      ? (this.matchScores.A > this.matchScores.B ? 'A' : 'B')
      : null;
    if (partieWinner) this._pendingPartieReset = true;

    this.result = {
      teamAScore,
      teamBScore: finalScores.B,
      tier,
      payout,
      made,
      chute: !made,
      preneurTeam,
      capotTeam,
      beloteTeam,
      won: teamAScore > finalScores.B,
      matchScores: { ...this.matchScores },
      partieWinner,
    };
    // Ordre de chute exact des 32 cartes cette mène - devient la mémoire
    // "mène précédente" pour l'IA à la prochaine donne (voir ai.js) et la
    // base réelle du paquet qui sera coupé (jamais rebattu) pour la
    // prochaine mène (voir _dealForBidding).
    this.lastRealSequence = this.trickHistory.flatMap((t) => t.cards.map((e) => e.card));
    this.phase = 'result';
  }

  nextRound() {
    if (this._pendingPartieReset) {
      this.matchScores = { A: 0, B: 0 };
      this._pendingPartieReset = false;
    }
    this.phase = 'betting';
    this.dealerSeat = nextSeat(this.dealerSeat);
    this._resetHandState();
    this.bet = 0;
  }

  getState() {
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      isGameOver: this.isGameOver,
      dealerSeat: this.dealerSeat,
      turnedCard: this.turnedCard,
      biddingRound: this.biddingRound,
      biddingTurn: this.biddingTurn,
      trumpSuit: this.trumpSuit,
      preneur: this.preneur,
      playerHand: this.hands[PLAYER],
      handCounts: this.hands.map((h) => h.length),
      trick: this.trick,
      turn: this.turn,
      legalCardIds: this.legalMovesForSeat(PLAYER).map((c) => c.id),
      trickNum: this.trickNum,
      teamScores: this.teamScores,
      matchScores: this.matchScores,
      tricksWonBy: this.tricksWonBy,
      lastTrick: this.lastTrick,
      beloteSeat: this.beloteSeat,
      beloteState: this.beloteState,
      result: this.result,
    };
  }
}
