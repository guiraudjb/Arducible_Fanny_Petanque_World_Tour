// Keno : on choisit de 1 à 10 numéros parmi 80, 20 sont tirés au sort.
// Le gain dépend du nombre de numéros choisis ET du nombre de bons
// numéros parmi eux (comme au vrai keno, chaque "type" de grille - pick
// 1, pick 2... - a sa propre table de gains). Cette grille de
// multiplicateurs est un choix de la maison (comme n'importe quel
// casino fixe la sienne) - ni l'ODS ni une norme officielle, juste un
// barème pensé pour rester amusant sans dénaturer les probabilités
// réelles du tirage.

export const MAX_NUMBER = 80;
export const DRAWN_COUNT = 20;
export const MAX_PICKS = 10;

// PAYTABLE[nombre de numéros choisis][nombre de bons numéros] = multiplicateur
export const PAYTABLE = {
  1: { 1: 3 },
  2: { 2: 12 },
  3: { 2: 1, 3: 40 },
  4: { 2: 1, 3: 4, 4: 100 },
  5: { 3: 1, 4: 10, 5: 300 },
  6: { 3: 1, 4: 3, 5: 30, 6: 500 },
  7: { 4: 1, 5: 5, 6: 50, 7: 1000 },
  8: { 5: 2, 6: 12, 7: 200, 8: 2000 },
  9: { 5: 1, 6: 5, 7: 50, 8: 500, 9: 3000 },
  10: { 5: 2, 6: 5, 7: 20, 8: 100, 9: 1000, 10: 5000 },
};

export function multiplierFor(picksCount, hits) {
  const table = PAYTABLE[picksCount];
  if (!table) return 0;
  return table[hits] || 0;
}

export function drawNumbers() {
  const pool = Array.from({ length: MAX_NUMBER }, (_, i) => i + 1);
  for (let i = pool.length - 1; i > 0; i -= 1) {
    const j = Math.floor(Math.random() * (i + 1));
    [pool[i], pool[j]] = [pool[j], pool[i]];
  }
  return pool.slice(0, DRAWN_COUNT).sort((a, b) => a - b);
}

export class Keno {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = 0;
    this.lastBet = 0;
    this.picks = [];
    this.phase = 'betting'; // 'betting' | 'result'
    this.drawn = [];
    this.hits = 0;
    this.multiplier = 0;
    this.payout = 0;
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  togglePick(number) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (number < 1 || number > MAX_NUMBER) return { ok: false, reason: 'bad-number' };
    const idx = this.picks.indexOf(number);
    if (idx >= 0) {
      this.picks.splice(idx, 1);
    } else {
      if (this.picks.length >= MAX_PICKS) return { ok: false, reason: 'too-many-picks' };
      this.picks.push(number);
    }
    return { ok: true };
  }

  clearPicks() {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    this.picks = [];
    return { ok: true };
  }

  draw(bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (this.picks.length === 0) return { ok: false, reason: 'no-picks' };
    if (!Number.isFinite(bet) || bet <= 0 || bet > this.bankroll) return { ok: false, reason: 'bad-bet' };

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= bet;

    this.drawn = drawNumbers();
    const drawnSet = new Set(this.drawn);
    this.hits = this.picks.filter((n) => drawnSet.has(n)).length;
    this.multiplier = multiplierFor(this.picks.length, this.hits);
    this.payout = bet * this.multiplier;
    this.bankroll += this.payout;
    this.phase = 'result';
    return { ok: true };
  }

  nextRound() {
    this.phase = 'betting';
    this.drawn = [];
    this.hits = 0;
    this.multiplier = 0;
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
      picks: [...this.picks],
      drawn: this.drawn,
      hits: this.hits,
      multiplier: this.multiplier,
      payout: this.payout,
      paytableRow: PAYTABLE[this.picks.length] || null,
    };
  }
}
