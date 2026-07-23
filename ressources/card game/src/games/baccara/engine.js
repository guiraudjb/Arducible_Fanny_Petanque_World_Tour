import { Deck } from '../../cards/index.js';

// Baccara (Punto Banco), règles casino standard : le joueur mise sur
// "Joueur", "Banque" ou "Égalité" - il ne joue aucune carte lui-même,
// les deux mains (Joueur / Banque) sont tirées automatiquement selon le
// tableau des tirages officiel.

function cardPoint(card) {
  if (card.rank === 'A') return 1;
  if (['10', 'J', 'Q', 'K'].includes(card.rank)) return 0;
  return Number(card.rank);
}

export function handTotal(cards) {
  return cards.reduce((sum, c) => sum + cardPoint(c), 0) % 10;
}

function isNatural(cards) {
  return cards.length === 2 && handTotal(cards) >= 8;
}

// Le joueur tire une 3e carte si son total est 0-5, reste sur 6-7.
function playerShouldDraw(total) {
  return total <= 5;
}

// Tableau officiel du tirage de la banque, en fonction de son propre
// total et de la valeur de la 3e carte du joueur (null si le joueur n'a
// pas tiré).
function bankerShouldDraw(bankerTotal, playerThirdValue) {
  if (bankerTotal <= 2) return true;
  if (bankerTotal >= 7) return false;
  if (playerThirdValue === null) return bankerTotal <= 5;
  switch (bankerTotal) {
    case 3: return playerThirdValue !== 8;
    case 4: return playerThirdValue >= 2 && playerThirdValue <= 7;
    case 5: return playerThirdValue >= 4 && playerThirdValue <= 7;
    case 6: return playerThirdValue === 6 || playerThirdValue === 7;
    default: return false;
  }
}

// Cotes de paiement (gain en plus de la mise rendue). La Banque paie
// 1:1 moins 5% de commission (odds officielles), simplifiée ici en un
// gain net de 0.95x plutôt qu'en jetons de commission séparés.
export const ODDS = { player: 1, banker: 0.95, tie: 8 };

export const SIDE_LABELS = { player: 'Joueur', banker: 'Banque', tie: 'Égalité' };

export class Baccara {
  constructor({ startingBankroll = 500 } = {}) {
    this.startingBankroll = startingBankroll;
    this.newSession();
  }

  newSession() {
    this.bankroll = this.startingBankroll;
    this.bet = null; // { side: 'player'|'banker'|'tie', amount }
    this.lastBet = null;
    this.phase = 'betting'; // 'betting' | 'result'
    this.playerHand = [];
    this.bankerHand = [];
    this.winner = null; // 'player' | 'banker' | 'tie'
    this.payout = 0;
  }

  get isGameOver() {
    return this.phase === 'betting' && this.bankroll <= 0;
  }

  deal(bet) {
    if (this.phase !== 'betting') return { ok: false, reason: 'wrong-phase' };
    if (!bet || !SIDE_LABELS[bet.side]) return { ok: false, reason: 'no-bet-type' };
    const amount = bet.amount;
    if (!Number.isFinite(amount) || amount <= 0 || amount > this.bankroll) {
      return { ok: false, reason: 'bad-bet' };
    }

    this.bet = bet;
    this.lastBet = bet;
    this.bankroll -= amount;

    const deck = new Deck({ jokers: 0 });
    deck.shuffle();
    this.playerHand = [deck.draw(1), deck.draw(1)];
    this.bankerHand = [deck.draw(1), deck.draw(1)];

    if (!isNatural(this.playerHand) && !isNatural(this.bankerHand)) {
      let playerThirdValue = null;
      if (playerShouldDraw(handTotal(this.playerHand))) {
        const card = deck.draw(1);
        this.playerHand.push(card);
        playerThirdValue = cardPoint(card);
      }
      if (bankerShouldDraw(handTotal(this.bankerHand), playerThirdValue)) {
        this.bankerHand.push(deck.draw(1));
      }
    }

    const playerTotal = handTotal(this.playerHand);
    const bankerTotal = handTotal(this.bankerHand);
    this.winner = playerTotal === bankerTotal ? 'tie' : (playerTotal > bankerTotal ? 'player' : 'banker');

    let payout = 0;
    if (this.winner === bet.side) {
      payout = bet.side === 'tie'
        ? amount * (ODDS.tie + 1)
        : amount + Math.floor(amount * ODDS[bet.side]);
    } else if (bet.side !== 'tie' && this.winner === 'tie') {
      // Règle standard : une mise Joueur/Banque est remboursée (push) en cas d'égalité.
      payout = amount;
    }
    this.payout = payout;
    this.bankroll += payout;
    this.phase = 'result';
    return { ok: true };
  }

  nextRound() {
    this.phase = 'betting';
    this.playerHand = [];
    this.bankerHand = [];
    this.winner = null;
    this.payout = 0;
    this.bet = null;
  }

  getState() {
    return {
      phase: this.phase,
      bankroll: this.bankroll,
      bet: this.bet,
      lastBet: this.lastBet,
      isGameOver: this.isGameOver,
      playerHand: this.playerHand,
      bankerHand: this.bankerHand,
      playerTotal: handTotal(this.playerHand),
      bankerTotal: handTotal(this.bankerHand),
      winner: this.winner,
      payout: this.payout,
    };
  }
}
