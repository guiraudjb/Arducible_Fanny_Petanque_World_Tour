import { Deck, Card, SUITS, RANKS } from '../../cards/index.js';

const VALUES = {
  A: 14, K: 13, Q: 12, J: 11, 10: 10, 9: 9, 8: 8, 7: 7, 6: 6, 5: 5, 4: 4, 3: 3, 2: 2,
};

export const HAND_NAMES = {
  'five-of-a-kind': 'Cinq identiques',
  'royal-flush': 'Quinte flush royale',
  'straight-flush': 'Quinte flush',
  'four-of-a-kind': 'Carré',
  'full-house': 'Full',
  flush: 'Couleur',
  straight: 'Quinte',
  'three-of-a-kind': 'Brelan',
  'two-pair': 'Double paire',
  'jacks-or-better': 'Paire de valets ou mieux',
  nothing: 'Rien',
};

/** Paytable "9/6 Jacks or Better" (multiplicateur de la mise), complétée
 * par le palier "cinq identiques" rendu possible par les jokers joker. */
export const PAYTABLE = {
  'five-of-a-kind': 400,
  'royal-flush': 250,
  'straight-flush': 50,
  'four-of-a-kind': 25,
  'full-house': 9,
  flush: 6,
  straight: 4,
  'three-of-a-kind': 3,
  'two-pair': 2,
  'jacks-or-better': 1,
  nothing: 0,
};

// Ordre du meilleur au moins bon, utilisé pour choisir la meilleure
// substitution possible des jokers (cartes folles).
const RANK_ORDER = Object.keys(PAYTABLE);

/** Évalue une main de 5 cartes SANS joker (déjà substitués le cas échéant)
 * et renvoie la catégorie (clé de PAYTABLE/HAND_NAMES). */
function evaluateHandBase(cards) {
  const values = cards.map((c) => VALUES[c.rank]).sort((a, b) => a - b);
  const isFlush = new Set(cards.map((c) => c.suit)).size === 1;

  const uniqueValues = [...new Set(values)];
  let isStraight = false;
  let straightHighForRoyalCheck = null;
  if (uniqueValues.length === 5) {
    if (uniqueValues[4] - uniqueValues[0] === 4) {
      isStraight = true;
      straightHighForRoyalCheck = uniqueValues[4];
    } else if (uniqueValues.join(',') === '2,3,4,5,14') {
      // Quinte "roue" : As-2-3-4-5 (As compte comme 1)
      isStraight = true;
      straightHighForRoyalCheck = 5;
    }
  }

  const countByValue = new Map();
  for (const v of values) countByValue.set(v, (countByValue.get(v) || 0) + 1);
  const counts = [...countByValue.values()].sort((a, b) => b - a);

  // Impossible avec un vrai paquet (4 exemplaires max par rang), mais
  // atteignable une fois qu'un joker a été substitué par un rang déjà présent.
  if (counts[0] === 5) return 'five-of-a-kind';
  if (isStraight && isFlush) {
    return straightHighForRoyalCheck === 14 ? 'royal-flush' : 'straight-flush';
  }
  if (counts[0] === 4) return 'four-of-a-kind';
  if (counts[0] === 3 && counts[1] === 2) return 'full-house';
  if (isFlush) return 'flush';
  if (isStraight) return 'straight';
  if (counts[0] === 3) return 'three-of-a-kind';
  if (counts[0] === 2 && counts[1] === 2) return 'two-pair';
  if (counts[0] === 2) {
    const pairValue = [...countByValue.entries()].find(([, c]) => c === 2)[0];
    if (pairValue >= 11) return 'jacks-or-better';
    return 'nothing';
  }
  return 'nothing';
}

/** Les 52 cartes standard, utilisées comme substitutions possibles d'un
 * joker. Un joker est une notion abstraite ("cette carte compte comme la
 * carte qui m'arrange le mieux"), pas une simulation d'une vraie carte
 * encore dans le paquet : il DOIT pouvoir dupliquer un rang déjà présent
 * dans la main (c'est justement ce qui permet un carré ou un cinq
 * identiques), donc on n'exclut rien ici. */
function allStandardCards() {
  const candidates = [];
  for (const suit of Object.values(SUITS)) {
    for (const rank of RANKS) {
      candidates.push(new Card(rank, suit));
    }
  }
  return candidates;
}

const ALL_CANDIDATES = allStandardCards();

/**
 * Évalue une main de 5 cartes et renvoie la catégorie (clé de
 * PAYTABLE/HAND_NAMES). Les jokers sont des cartes folles : on cherche la
 * meilleure main possible en essayant toutes leurs substitutions.
 */
export function evaluateHand(cards) {
  const wilds = cards.filter((c) => c.isJoker);
  if (wilds.length === 0) return evaluateHandBase(cards);

  const fixed = cards.filter((c) => !c.isJoker);
  const candidates = ALL_CANDIDATES;

  let best = 'nothing';
  const consider = (trialCards) => {
    const rank = evaluateHandBase(trialCards);
    if (RANK_ORDER.indexOf(rank) < RANK_ORDER.indexOf(best)) best = rank;
  };

  if (wilds.length === 1) {
    for (const c of candidates) consider([...fixed, c]);
  } else {
    // 2 jokers (rare, mais possible avec un paquet de 54 cartes) : on
    // teste toutes les paires de substituts distincts.
    for (let i = 0; i < candidates.length; i += 1) {
      for (let j = 0; j < candidates.length; j += 1) {
        if (i === j) continue;
        consider([...fixed, candidates[i], candidates[j]]);
      }
    }
  }
  return best;
}

/**
 * Video poker "Jacks or Better" avec jokers cartes folles (paquet de 54
 * cartes) : mise, distribution de 5 cartes, on garde ce qu'on veut, un
 * seul échange, paiement selon la paytable 9/6 complétée par le palier
 * "cinq identiques" rendu possible par les jokers.
 */
export class VideoPoker {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = 0;
    this.lastBet = 0;
    this.phase = 'betting'; // 'betting' | 'holding' | 'result'
    this.hand = [];
    this.held = [false, false, false, false, false];
    this.handRank = null;
    this.payout = 0;
    this.deck = null;
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  startRound(bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (!Number.isFinite(bet) || bet <= 0 || bet > this.bankroll) {
      return { ok: false, reason: 'bad-bet' };
    }

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= bet;

    this.deck = new Deck({ jokers: 2 });
    this.deck.shuffle();
    this.hand = this.deck.draw(5);
    this.held = [false, false, false, false, false];
    this.handRank = null;
    this.payout = 0;
    this.phase = 'holding';
    return { ok: true };
  }

  toggleHold(index) {
    if (this.phase !== 'holding') return { ok: false, reason: 'wrong-phase' };
    if (index < 0 || index >= this.hand.length) return { ok: false, reason: 'bad-index' };
    this.held[index] = !this.held[index];
    return { ok: true };
  }

  draw() {
    if (this.phase !== 'holding') return { ok: false, reason: 'wrong-phase' };
    for (let i = 0; i < this.hand.length; i += 1) {
      if (!this.held[i]) this.hand[i] = this.deck.draw(1);
    }
    this.handRank = evaluateHand(this.hand);
    this.payout = this.bet * PAYTABLE[this.handRank];
    this.bankroll += this.payout;
    this.phase = 'result';
    return { ok: true };
  }

  nextRound() {
    this.phase = 'betting';
    this.hand = [];
    this.held = [false, false, false, false, false];
    this.handRank = null;
    this.payout = 0;
    this.bet = 0;
  }

  getState() {
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      isGameOver: this.isGameOver,
      hand: this.hand.map((card, i) => ({ card, held: this.held[i] })),
      handRank: this.handRank,
      handName: this.handRank ? HAND_NAMES[this.handRank] : null,
      payout: this.payout,
    };
  }
}
