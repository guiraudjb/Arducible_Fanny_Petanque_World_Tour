// Bandit manchot à 3 rouleaux, une seule ligne de paiement (classique).
// Aucune carte à jouer ici : les symboles sont des glyphes (voir main.js),
// ce moteur ne connaît que leurs identifiants texte.

/** Bande de symboles pondérée : plus un symbole apparaît de fois dans ce
 * tableau, plus il a de chances de sortir sur un rouleau (probabilité par
 * duplication, pas de table de poids séparée à maintenir en synchronisation). */
const SYMBOL_STRIP = [
  'cherry', 'cherry', 'cherry', 'cherry', 'cherry',
  'lemon', 'lemon', 'lemon', 'lemon',
  'bell', 'bell', 'bell',
  'diamond', 'diamond',
  'star', 'star',
  'seven',
  'crown',
];

export const SYMBOL_GLYPHS = {
  cherry: '🍒',
  lemon: '🍋',
  bell: '🔔',
  diamond: '💎',
  star: '⭐',
  // Volontairement du texte simple, pas l'emoji "sept encadré" (7️⃣) : cette
  // séquence combinée (chiffre + variation selector + keycap) s'est révélée
  // invisible avec certaines polices emoji (Twemoji Mozilla notamment),
  // alors que les émojis à un seul point de code ci-dessus s'affichent
  // partout sans problème. Un "7" stylé en CSS est fiable sur tout appareil.
  seven: '7',
  crown: '👑',
};

export const SYMBOL_NAMES = {
  cherry: 'Cerises',
  lemon: 'Citrons',
  bell: 'Cloches',
  diamond: 'Diamants',
  star: 'Étoiles',
  seven: 'Sept',
  crown: 'Couronnes',
};

/** Multiplicateur de RETOUR TOTAL (pas de profit) pour 3 symboles identiques :
 * bankroll += bet * multiplier. Un multiplicateur de 0 = perte totale, 1 =
 * on récupère juste sa mise. Convention volontairement différente de
 * Blackjack/Poker (qui ajoutent la mise rendue + le gain séparément) car
 * c'est la façon dont un vrai bandit manchot annonce ses gains ("3 cerises
 * paient x4" signifie 4 fois la mise au total, pas 4 fois en plus). */
export const PAYTABLE = {
  crown: 100,
  seven: 50,
  star: 20,
  diamond: 10,
  bell: 6,
  lemon: 4,
  cherry: 3,
};

/** Bonus classique "2 cerises" : si exactement 2 des 3 rouleaux affichent
 * une cerise (le troisième étant autre chose), on double la mise. Une
 * mécanique traditionnelle des bandits manchots, indépendante du tableau
 * des combos à 3 symboles identiques ci-dessus. */
const TWO_CHERRY_MULTIPLIER = 2;

function spinReel() {
  const index = Math.floor(Math.random() * SYMBOL_STRIP.length);
  return SYMBOL_STRIP[index];
}

/** Catégorise un résultat pour le choix de la réplique de la croupière. */
export function winTier(multiplier) {
  if (multiplier >= 50) return 'jackpot';
  if (multiplier >= 10) return 'big';
  if (multiplier > 0) return 'small';
  return 'none';
}

export class SlotMachine {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = 0;
    this.lastBet = 0;
    this.phase = 'betting'; // 'betting' | 'result'
    this.reels = ['cherry', 'cherry', 'cherry'];
    this.payoutMultiplier = 0;
    this.payout = 0;
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  spin(bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (!Number.isFinite(bet) || bet <= 0 || bet > this.bankroll) {
      return { ok: false, reason: 'bad-bet' };
    }

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= bet;

    this.reels = [spinReel(), spinReel(), spinReel()];

    const [a, b, c] = this.reels;
    let multiplier = 0;
    if (a === b && b === c) {
      multiplier = PAYTABLE[a];
    } else {
      const cherryCount = this.reels.filter((s) => s === 'cherry').length;
      if (cherryCount === 2) multiplier = TWO_CHERRY_MULTIPLIER;
    }

    this.payoutMultiplier = multiplier;
    this.payout = bet * multiplier;
    this.bankroll += this.payout;
    this.phase = 'result';
    return { ok: true };
  }

  nextSpin() {
    this.phase = 'betting';
    this.payoutMultiplier = 0;
    this.payout = 0;
  }

  getState() {
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      isGameOver: this.isGameOver,
      reels: this.reels,
      payoutMultiplier: this.payoutMultiplier,
      payout: this.payout,
      winTier: this.phase === 'result' ? winTier(this.payoutMultiplier) : 'none',
    };
  }
}
