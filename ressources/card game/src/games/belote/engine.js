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
//   - Une fois l'atout pris : le distributeur ramasse la carte retournée
//     dans sa main, puis complète les mains (3 cartes aux trois autres
//     joueurs, 2 au distributeur - qui a déjà la carte retournée) : tout
//     le monde termine à 8 cartes.
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
const BID_THRESHOLD_ROUND1 = 6.5;
const BID_THRESHOLD_ROUND2 = 8.5;

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

/** Trie une main pour l'affichage : atout d'abord (du plus faible au plus
 * fort), puis les 3 autres couleurs dans un ordre fixe, chacune triée du
 * plus faible au plus fort. */
export function sortHand(hand, trumpSuit) {
  const groups = [trumpSuit, ...SUITS.filter((s) => s !== trumpSuit)];
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
/* IA (niveau avancé) : enchères et jeu de cartes                       */
/* ------------------------------------------------------------------ */

/** Estime la force d'une main si `suit` devient atout - sert à décider
 * d'annoncer ou de passer. Heuristique (pas un solveur exact) : valorise
 * les gros atouts (Valet, 9, As, 10), la longueur à l'atout, et les As
 * dans les autres couleurs. */
function evaluateHandStrength(hand, suit) {
  let score = 0;
  const trumps = hand.filter((c) => c.suit === suit);
  for (const c of trumps) {
    if (c.rank === 'J') score += 5;
    else if (c.rank === '9') score += 3;
    else if (c.rank === 'A') score += 2;
    else if (c.rank === '10') score += 2;
    else score += 0.5;
  }
  score += Math.max(0, trumps.length - 3) * 1.5;
  for (const c of hand) {
    if (c.suit !== suit && c.rank === 'A') score += 1.5;
  }
  return score;
}

/** Décision d'enchère d'un bot (niveau avancé mais heuristique). */
export function chooseAiBid(hand, round, turnedCard) {
  if (round === 1) {
    const score = evaluateHandStrength(hand, turnedCard.suit);
    if (score >= BID_THRESHOLD_ROUND1) return { type: 'take', suit: turnedCard.suit };
    return { type: 'pass' };
  }
  const candidates = SUITS.filter((s) => s !== turnedCard.suit)
    .map((s) => ({ suit: s, score: evaluateHandStrength(hand, s) }))
    .sort((a, b) => b.score - a.score);
  if (candidates[0].score >= BID_THRESHOLD_ROUND2) return { type: 'take', suit: candidates[0].suit };
  return { type: 'pass' };
}

/** Décision de carte d'un bot (niveau avancé mais heuristique, pas un
 * solveur exact - pas de comptage de cartes des adversaires). En tête de
 * pli : joue son plus fort hors-atout pour écouler ses points en
 * sécurité, sinon un petit atout. En suivant : si son partenaire est
 * déjà maître du pli, ne cherche pas à gagner (défausse la carte la
 * moins chère) ; sinon tente de gagner au moindre coût, et à défaut
 * défausse la carte la moins chère. */
export function chooseAiCard(hand, trick, trumpSuit, mySeat) {
  const options = legalMoves(hand, trick, trumpSuit, mySeat);
  if (trick.length === 0) {
    const nonTrump = options.filter((c) => c.suit !== trumpSuit);
    const pool = nonTrump.length > 0 ? nonTrump : options;
    return pool.reduce((best, c) => (cardRank(c, trumpSuit) > cardRank(best, trumpSuit) ? c : best));
  }

  const winnerSeat = currentTrickWinnerSeat(trick, trumpSuit);
  const partnerWinning = winnerSeat === partnerOf(mySeat);
  if (partnerWinning) {
    return options.reduce((cheapest, c) => (cardPoints(c, trumpSuit) < cardPoints(cheapest, trumpSuit) ? c : cheapest));
  }

  const winnerEntry = trick.find((t) => t.seat === winnerSeat);
  const winningOptions = options.filter((c) => {
    if (c.suit === trumpSuit && winnerEntry.card.suit !== trumpSuit) return true;
    if (c.suit !== winnerEntry.card.suit) return false;
    return cardRank(c, trumpSuit) > cardRank(winnerEntry.card, trumpSuit);
  });
  if (winningOptions.length > 0) {
    return winningOptions.reduce((cheapest, c) => (cardRank(c, trumpSuit) < cardRank(cheapest, trumpSuit) ? c : cheapest));
  }
  return options.reduce((cheapest, c) => (cardPoints(c, trumpSuit) < cardPoints(cheapest, trumpSuit) ? c : cheapest));
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
    this.lastTrick = null;
    this.result = null;
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

  _dealForBidding() {
    const deck = shuffle(buildDeck());
    this.hands = [deck.slice(0, 5), deck.slice(5, 10), deck.slice(10, 15), deck.slice(15, 20)];
    this.turnedCard = deck[20];
    this._remainingDeck = deck.slice(21); // 11 cartes, complétées après enchères
    this.biddingRound = 1;
    this.biddingTurn = nextSeat(this.dealerSeat);
    this.passCount = 0;
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
        this._dealForBidding(); // tout le monde a passé deux fois : redonne
      }
      return { ok: true };
    }
    this.biddingTurn = nextSeat(this.biddingTurn);
    return { ok: true };
  }

  _completeDeal() {
    this.hands[this.dealerSeat].push(this.turnedCard);
    const order = [nextSeat(this.dealerSeat), nextSeat(nextSeat(this.dealerSeat)), nextSeat(nextSeat(nextSeat(this.dealerSeat)))];
    let cursor = 0;
    for (const seat of order) {
      this.hands[seat].push(...this._remainingDeck.slice(cursor, cursor + 3));
      cursor += 3;
    }
    this.hands[this.dealerSeat].push(...this._remainingDeck.slice(cursor, cursor + 2));

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

    if (this.trick.length === 4) {
      const winnerSeat = currentTrickWinnerSeat(this.trick, this.trumpSuit);
      const winnerTeam = teamOf(winnerSeat);
      const isLastTrick = this.trickNum === 7;
      const points = this.trick.reduce((sum, t) => sum + cardPoints(t.card, this.trumpSuit), 0)
        + (isLastTrick ? DIX_DE_DER : 0);
      this.teamScores[winnerTeam] += points;
      this.tricksWonBy[winnerTeam] += 1;
      this.lastTrick = { cards: this.trick.slice(), winnerSeat };
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
    };
    this.phase = 'result';
  }

  nextRound() {
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
      tricksWonBy: this.tricksWonBy,
      lastTrick: this.lastTrick,
      beloteSeat: this.beloteSeat,
      result: this.result,
    };
  }
}
