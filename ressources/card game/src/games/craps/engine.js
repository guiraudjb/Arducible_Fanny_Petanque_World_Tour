// Craps simplifié : seule la mise "Ligne Pass" (Pass Line) et son
// opposé "Ne Pass Pas" (Don't Pass) sont proposées - ce sont les deux
// mises fondamentales du craps, celles que tout le monde joue en
// premier. Les mises annexes du vrai tapis (Field, Come, Place, Odds...)
// sont volontairement absentes pour garder un mini-jeu simple.
//
// Règles standard :
//  - Sortie ("come-out roll") : 7 ou 11 => Ligne Pass gagne (Ne Pass Pas perd) ;
//    2 ou 3 => Ligne Pass perd (Ne Pass Pas gagne) ;
//    12 => Ligne Pass perd, mais Ne Pass Pas est nul (mise remboursée -
//    c'est le "12 barré", règle officielle qui évite que la banque perde
//    systématiquement sur le pire tirage) ;
//    tout autre total (4,5,6,8,9,10) => devient le "point".
//  - Une fois le point établi, on relance jusqu'à faire soit le point à
//    nouveau (Ligne Pass gagne), soit un 7 ("seven-out", Ligne Pass perd).
//  - Les deux mises paient 1:1.

function rollDie() {
  return 1 + Math.floor(Math.random() * 6);
}

export function rollDice() {
  const d1 = rollDie();
  const d2 = rollDie();
  return { d1, d2, total: d1 + d2 };
}

export const SIDE_LABELS = { pass: 'Ligne Pass', dontpass: 'Ne Pass Pas' };

export class Craps {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = 0;
    this.lastBet = 0;
    this.side = null; // 'pass' | 'dontpass'
    this.lastSide = null;
    this.phase = 'betting'; // 'betting' | 'rolling' | 'result'
    this.point = null;
    this.rolls = [];
    this.outcome = null; // 'win' | 'lose' | 'push'
    this.payout = 0;
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  startRound(side, bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (!SIDE_LABELS[side]) return { ok: false, reason: 'no-side' };
    if (!Number.isFinite(bet) || bet <= 0 || bet > this.bankroll) return { ok: false, reason: 'bad-bet' };

    this.side = side;
    this.lastSide = side;
    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= bet;
    this.point = null;
    this.rolls = [];
    this.outcome = null;
    this.payout = 0;
    this.phase = 'rolling';
    return { ok: true };
  }

  roll() {
    if (this.phase !== 'rolling') return { ok: false, reason: 'wrong-phase' };
    const r = rollDice();
    this.rolls.push(r);

    if (this.point === null) {
      if (r.total === 7 || r.total === 11) this._settle(this.side === 'pass' ? 'win' : 'lose');
      else if (r.total === 2 || r.total === 3) this._settle(this.side === 'pass' ? 'lose' : 'win');
      else if (r.total === 12) this._settle(this.side === 'pass' ? 'lose' : 'push');
      else this.point = r.total;
    } else if (r.total === this.point) {
      this._settle(this.side === 'pass' ? 'win' : 'lose');
    } else if (r.total === 7) {
      this._settle(this.side === 'pass' ? 'lose' : 'win');
    }
    return { ok: true };
  }

  _settle(outcome) {
    this.outcome = outcome;
    if (outcome === 'win') this.payout = this.bet * 2;
    else if (outcome === 'push') this.payout = this.bet;
    else this.payout = 0;
    this.bankroll += this.payout;
    this.phase = 'result';
  }

  nextRound() {
    this.phase = 'betting';
    this.side = null;
    this.point = null;
    this.rolls = [];
    this.outcome = null;
    this.payout = 0;
    this.bet = 0;
  }

  getState() {
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      lastSide: this.lastSide,
      isGameOver: this.isGameOver,
      side: this.side,
      point: this.point,
      rolls: this.rolls,
      lastRoll: this.rolls.length ? this.rolls[this.rolls.length - 1] : null,
      outcome: this.outcome,
      payout: this.payout,
    };
  }
}
