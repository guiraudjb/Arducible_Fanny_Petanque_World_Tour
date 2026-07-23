// Moteur cognitif des bots de Belote (Fanny, Marcel, Bernard) : bidding et
// jeu de carte "niveau avancé", au-delà d'une simple heuristique réactive.
//
// Mémoire à deux niveaux :
//   1. Mène en cours (buildMemory/estimateCardProbabilities) : couleurs déjà
//      coupées par chaque siège, cartes déjà tombées. Toujours disponible.
//   2. Mène PRÉCÉDENTE (reconstructDeal, dans engine.js) : le paquet n'est
//      jamais rebattu entre deux mènes (voir engine.js), seulement coupé une
//      fois - un joueur qui a suivi tous les plis de la mène précédente et
//      voit sa propre main cette donne peut donc, en pratique, retrouver la
//      coupe exacte et reconstituer TOUTES les mains (les 32 cartes sont
//      toutes différentes : sa main, contiguë dans le paquet coupé, ne colle
//      qu'à une seule rotation). C'est la "mémorisation absolue" demandée -
//      un vrai effet du fait qu'on ne fait QUE couper, jamais mélanger.
//      N'existe pas à la toute première mène d'une session (aucune mène
//      précédente) : on retombe alors sur l'estimation proportionnelle du
//      niveau 1 uniquement.
//
// Ce n'est pas un solveur exact au sens "énumération de toutes les donnes
// compatibles avec les enchères" (pas de Monte-Carlo sur les enchères) :
// c'est une IA heuristique qui va nettement plus loin que "joue son plus
// fort / défausse le moins cher" - elle track les couleurs coupées, exploite
// la non-repousse du paquet pour prédire les mains adverses avec une
// confiance très élevée dès la 2e mène, et pondère ses décisions par
// sièges/profils.

import {
  SUITS, PLAYER, OPP1, FANNY, OPP2, teamOf, partnerOf, cardPoints, legalMoves,
  cardRank, currentTrickWinnerSeat, reconstructDeal,
} from './engine.js';

const SEATS_ALL = [PLAYER, OPP1, FANNY, OPP2];
const RANKS = ['7', '8', '9', '10', 'J', 'Q', 'K', 'A'];
// Table résolument agressive à la prise (cf. module 3) : un "bon jeu" doit
// suffire à prendre, sans sur-analyser - le seuil est donc bas. Exemples de
// référence qui doivent passer isGoodHand : [Valet d'atout + 1 As extérieur]
// (5 + 2 = 7) et [9 d'atout + 1 As extérieur + 1 Dix extérieur] (3+2+1 = 6).
const TAKE_THRESHOLD_ROUND1 = 6;
const TAKE_THRESHOLD_ROUND2 = 6.5; // un peu plus prudent : couleur non montrée par la retourne

function allCardIds() {
  const ids = [];
  for (const suit of SUITS) for (const rank of RANKS) ids.push(`${rank}-${suit}`);
  return ids;
}
const ALL_CARD_IDS = allCardIds();

/* ------------------------------------------------------------------ */
/* Module 1 : Mémoire et tracking                                       */
/* ------------------------------------------------------------------ */
/** Reconstruit la mémoire de la mène EN COURS à partir de `trickHistory`
 * (les plis déjà complétés cette donne - voir Belote.trickHistory). Track :
 * les cartes déjà tombées, et pour chaque siège les couleurs où il a
 * "coupé" (n'a pas fourni la couleur demandée -> il n'en a plus du tout,
 * probabilité 0 pour le reste de la mène).
 *
 * Recalculée à neuf à chaque décision plutôt que mise à jour de proche en
 * proche : plus simple, ne peut pas se désynchroniser de l'état réel. */
export function buildMemory(trickHistory) {
  const seenIds = new Set();
  const voidSuits = { [PLAYER]: new Set(), [OPP1]: new Set(), [FANNY]: new Set(), [OPP2]: new Set() };

  for (const trick of trickHistory) {
    const ledSuit = trick.ledSuit;
    for (const { seat, card } of trick.cards) {
      seenIds.add(card.id);
      if (card.suit !== ledSuit) voidSuits[seat].add(ledSuit);
    }
  }
  return { seenIds, voidSuits };
}

/* ------------------------------------------------------------------ */
/* Module 2 : Lecture du paquet (carte de probabilités)                 */
/* ------------------------------------------------------------------ */
/** Pour chaque carte non encore vue et absente de ma main, estime une
 * probabilité de présence chez chacun des 3 autres sièges : répartition
 * proportionnelle à la taille de main restante de chaque siège, à zéro
 * pour toute couleur où ce siège a démontré un vide (module 1). Ce n'est
 * pas une énumération combinatoire exacte des donnes compatibles (trop
 * coûteux pour un jeu casual) mais une approximation simple et honnête,
 * suffisante pour guider des impasses raisonnables. */
export function estimateCardProbabilities({ myHand, mySeat, handCounts, memory }) {
  const myIds = new Set(myHand.map((c) => c.id));
  const otherSeats = SEATS_ALL.filter((s) => s !== mySeat);
  const probabilities = new Map(); // cardId -> { seat: probabilité }

  for (const id of ALL_CARD_IDS) {
    if (myIds.has(id) || memory.seenIds.has(id)) continue;
    const suit = id.slice(id.indexOf('-') + 1);
    const eligible = otherSeats.filter((s) => handCounts[s] > 0 && !memory.voidSuits[s].has(suit));
    const weightTotal = eligible.reduce((sum, s) => sum + handCounts[s], 0);
    const dist = {};
    if (weightTotal === 0) {
      // Cas dégénéré (tous les sièges restants sont flagués vides dans
      // cette couleur, ce qui ne devrait arriver que si notre suivi a une
      // incohérence) : on retombe sur une équirépartition défensive.
      const fallback = otherSeats.filter((s) => handCounts[s] > 0);
      fallback.forEach((s) => { dist[s] = 1 / fallback.length; });
    } else {
      eligible.forEach((s) => { dist[s] = handCounts[s] / weightTotal; });
    }
    probabilities.set(id, dist);
  }
  return probabilities;
}

/** Version "mémoire de la mène précédente" de la carte de probabilités :
 * à partir des reconstructions cohérentes retournées par `reconstructDeal`
 * (voir engine.js - généralement une seule, exacte), calcule pour chaque
 * carte encore non vue la fraction des reconstructions où elle se trouve
 * chez chaque adversaire. Avec une seule reconstruction cohérente, ça
 * revient à connaître la main adverse avec certitude (0 ou 1) - c'est
 * volontaire : c'est la mémorisation absolue demandée, pas une approximation. */
function probMapFromReconstructions(reconstructions, memory, mySeat) {
  const otherSeats = SEATS_ALL.filter((s) => s !== mySeat);
  const probabilities = new Map();
  const n = reconstructions.length;
  for (const id of ALL_CARD_IDS) {
    if (memory.seenIds.has(id)) continue; // déjà jouée cette mène : plus dans aucune main
    const dist = {};
    let anyFound = false;
    for (const s of otherSeats) {
      const count = reconstructions.reduce((sum, rec) => sum + (rec.hands[s].some((c) => c.id === id) ? 1 : 0), 0);
      if (count > 0) anyFound = true;
      dist[s] = count / n;
    }
    // Si la carte n'apparaît jamais chez un adversaire dans nos
    // reconstructions cohérentes, c'est qu'elle est dans NOTRE propre main
    // simulée - on ne l'ajoute pas (même convention que "carte connue").
    if (anyFound) probabilities.set(id, dist);
  }
  return probabilities;
}

/** Probabilité que `seat` détienne encore une carte capable de battre
 * `card` dans `suit` (utilisé pour jauger le risque d'une impasse). Une
 * carte déjà vue ou dans notre main ne compte jamais comme "en vie". */
function probSeatHoldsBetter(probMap, card, suit, seat, trumpSuit) {
  const myRank = cardRank(card, trumpSuit);
  let total = 0;
  for (const id of ALL_CARD_IDS) {
    const cardSuit = id.slice(id.indexOf('-') + 1);
    if (cardSuit !== suit) continue;
    const dist = probMap.get(id);
    if (!dist) continue; // déjà vue / dans une main connue : pas un risque
    const rank = id.slice(0, id.indexOf('-'));
    if (cardRank({ rank, suit }, trumpSuit) > myRank) total += dist[seat] || 0;
  }
  return total;
}

/* ------------------------------------------------------------------ */
/* Module 3 : Évaluation et prise - agressivité systématique            */
/* ------------------------------------------------------------------ */
/** Cartes hors-atout capables de "reprendre la main" : un As (+2, une vraie
 * garantie d'entrée), un Roi protégé par au moins une carte plus basse de
 * la même couleur (+1), ou un Dix isolé (+1, moins fiable mais compte pour
 * de l'agressivité). */
function outsideStrength(hand, trumpSuit) {
  let strength = 0;
  for (const suit of SUITS) {
    if (suit === trumpSuit) continue;
    const ofSuit = hand.filter((c) => c.suit === suit);
    if (ofSuit.some((c) => c.rank === 'A')) strength += 2;
    else if (ofSuit.some((c) => c.rank === 'K') && ofSuit.length >= 2) strength += 1;
    if (ofSuit.some((c) => c.rank === '10')) strength += 1;
  }
  return strength;
}

/** Force d'une main si `suit` devient atout : honneurs d'atout + longueur +
 * force hors-atout (retours), plus le soutien éventuel du partenaire (a-t-il
 * déjà annoncé/passé ce tour-ci ?). Volontairement PAS pondérée par la
 * position à la parole - la table est agressive à la prise, un bon jeu se
 * prend quel que soit l'ordre de parole, même en premier sans garantie. */
function evaluateHandStrength(hand, suit, { support = 0 } = {}) {
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
  score += outsideStrength(hand, suit);
  score += support;
  return score;
}

/** `isGoodHand` de référence (sans ajustement de profil) : un booléen net,
 * pas juste un score continu - c'est la règle stricte demandée : SI bon jeu
 * ALORS prise. Exemples qui doivent renvoyer `true` : Valet d'atout + 1 As
 * extérieur (5+2=7 ≥ 6) ; 9 d'atout + 1 As extérieur + 1 Dix extérieur
 * (3+2+1=6 ≥ 6). */
export function isGoodHand(hand, suit, round = 1) {
  const threshold = round === 1 ? TAKE_THRESHOLD_ROUND1 : TAKE_THRESHOLD_ROUND2;
  return evaluateHandStrength(hand, suit) >= threshold;
}

/** Décision d'enchère d'un bot : agressive et déterministe - SI la main est
 * jugée bonne (score ≥ seuil, ajusté par l'audace du profil), le bot prend
 * IMMÉDIATEMENT, sans tenir compte de sa position de parole. `ctx` :
 * { support, profile }. */
export function chooseAiBid(hand, round, turnedCard, ctx = {}) {
  const { support = 0, profile = DEFAULT_PROFILE } = ctx;
  const threshold1 = TAKE_THRESHOLD_ROUND1 - profile.biddingBoldness;
  const threshold2 = TAKE_THRESHOLD_ROUND2 - profile.biddingBoldness;

  if (round === 1) {
    const score = evaluateHandStrength(hand, turnedCard.suit, { support });
    if (score >= threshold1) return { type: 'take', suit: turnedCard.suit };
    return { type: 'pass' };
  }
  const candidates = SUITS.filter((s) => s !== turnedCard.suit)
    .map((s) => ({ suit: s, score: evaluateHandStrength(hand, s, { support }) }))
    .sort((a, b) => b.score - a.score);
  if (candidates[0].score >= threshold2) return { type: 'take', suit: candidates[0].suit };
  return { type: 'pass' };
}

/** Calcule le soutien du partenaire pour le siège qui va enchérir, à partir
 * de l'historique de l'enchère en cours (Belote.biddingHistory). La
 * position à la parole n'entre plus en jeu (voir chooseAiBid ci-dessus). */
export function biddingContext({ seat, biddingRound, biddingHistory, profile }) {
  const partner = partnerOf(seat);
  const partnerEntry = biddingHistory.find((e) => e.seat === partner && e.round === biddingRound);
  let support = 0;
  if (partnerEntry) {
    support = partnerEntry.action.type === 'take' ? 0 : -0.3 * profile.synergyWeight;
  }
  return { support };
}

/* ------------------------------------------------------------------ */
/* Module 4 : Jeu de la carte (atout, impasses, défausse, dix de der)   */
/* ------------------------------------------------------------------ */
/** Carte "maîtresse" probable d'une couleur : le plus haut rang qui n'a
 * encore été ni vu (mémoire), ni déjà dans notre main. Sert à décider si
 * une carte qu'on tient est déjà maîtresse (utile pour le dix de der). */
function isLikelyMaster(card, hand, trumpSuit, memory) {
  const myIds = new Set(hand.map((c) => c.id));
  for (const id of ALL_CARD_IDS) {
    const suit = id.slice(id.indexOf('-') + 1);
    if (suit !== card.suit || myIds.has(id) || memory.seenIds.has(id)) continue;
    const rank = id.slice(0, id.indexOf('-'));
    if (cardRank({ rank, suit }, trumpSuit) > cardRank(card, trumpSuit)) return false;
  }
  return true;
}

function chooseLead(hand, options, trumpSuit, mySeat, ctx) {
  const { memory, isEndgame, profile, defending } = ctx;

  // Dix de der : dans les deux derniers plis, on garde une carte
  // maîtresse identifiée pour sécuriser le dernier pli plutôt que de
  // l'entamer trop tôt - sauf si c'est la seule option restante.
  if (isEndgame && options.length > 1) {
    const masters = options.filter((c) => isLikelyMaster(c, hand, trumpSuit, memory));
    const nonMasters = options.filter((c) => !masters.includes(c));
    if (masters.length > 0 && nonMasters.length > 0) {
      return nonMasters.reduce((best, c) => (cardRank(c, trumpSuit) > cardRank(best, trumpSuit) ? c : best));
    }
  }

  // Défense affûtée (module 4) : la table prend agressivement des
  // contrats parfois limites (module 3), donc en défense on cherche à
  // épuiser l'atout du preneur au plus vite pour l'empêcher de couper nos
  // gagnants plus tard et le pousser à la chute. Tous les défenseurs le
  // font désormais, pas seulement Marcel - son profil "aggression" élevé
  // le fait juste dès une poignée plus courte (2 atouts) que les autres (3).
  const trumpsInHand = hand.filter((c) => c.suit === trumpSuit);
  if (defending) {
    const minTrumps = profile.aggression > 0.6 ? 2 : 3;
    if (trumpsInHand.length >= minTrumps) {
      const leadTrump = options.filter((c) => c.suit === trumpSuit);
      if (leadTrump.length > 0) {
        return leadTrump.reduce((best, c) => (cardRank(c, trumpSuit) < cardRank(best, trumpSuit) ? c : best));
      }
    }
  }

  const nonTrump = options.filter((c) => c.suit !== trumpSuit);
  const pool = nonTrump.length > 0 ? nonTrump : options;
  return pool.reduce((best, c) => (cardRank(c, trumpSuit) > cardRank(best, trumpSuit) ? c : best));
}

function chooseFollow(hand, options, trick, trumpSuit, mySeat, ctx) {
  const { memory, probMap, profile } = ctx;
  const winnerSeat = currentTrickWinnerSeat(trick, trumpSuit);
  const partnerWinning = winnerSeat === partnerOf(mySeat);

  // Bernard (synergie) : cède la main dès que son partenaire est maître,
  // et défausse alors dans la couleur la plus utile à l'appel (la plus
  // longue chez lui hors-atout, pour ne pas gâcher un futur appel).
  if (partnerWinning) {
    return options.reduce((cheapest, c) => (cardPoints(c, trumpSuit) < cardPoints(cheapest, trumpSuit) ? c : cheapest));
  }

  const winnerEntry = trick.find((t) => t.seat === winnerSeat);
  const seatsYetToPlay = SEATS_ALL.filter((s) => !trick.some((t) => t.seat === s) && s !== mySeat);

  const winningOptions = options.filter((c) => {
    if (c.suit === trumpSuit && winnerEntry.card.suit !== trumpSuit) return true;
    if (c.suit !== winnerEntry.card.suit) return false;
    return cardRank(c, trumpSuit) > cardRank(winnerEntry.card, trumpSuit);
  });

  if (winningOptions.length > 0) {
    // Impasse : parmi les cartes qui gagnent CE pli, certaines peuvent
    // encore se faire reprendre par un joueur qui parle après nous (une
    // carte plus haute qui n'est pas encore tombée). On préfère la moins
    // chère qui reste "raisonnablement sûre" plutôt que de sur-jouer par
    // prudence si le risque estimé est faible.
    const scored = winningOptions.map((c) => {
      const risk = probMap && seatsYetToPlay.length > 0
        ? seatsYetToPlay.reduce((sum, s) => sum + probSeatHoldsBetter(probMap, c, c.suit, s, trumpSuit), 0)
        : 0;
      return { card: c, risk };
    });
    const riskTolerance = 0.35 + profile.impasseBoldness * 0.25;
    const safe = scored.filter((s) => s.risk <= riskTolerance);
    const pool = safe.length > 0 ? safe : scored;
    return pool.reduce((cheapest, s) => (cardRank(s.card, trumpSuit) < cardRank(cheapest.card, trumpSuit) ? s : cheapest)).card;
  }

  return options.reduce((cheapest, c) => (cardPoints(c, trumpSuit) < cardPoints(cheapest, trumpSuit) ? c : cheapest));
}

/** Décision de carte d'un bot. `ctx` : { memory, probMap, profile,
 * trickNum, defending }. `memory`/`probMap` sont optionnels (retombent sur
 * un jeu sûr mais moins fin sans eux). `defending` : le bot n'est PAS dans
 * l'équipe du preneur (voir module 4 - défense affûtée). */
export function chooseAiCard(hand, trick, trumpSuit, mySeat, ctx = {}) {
  const {
    memory = { seenIds: new Set(), voidSuits: { [PLAYER]: new Set(), [OPP1]: new Set(), [FANNY]: new Set(), [OPP2]: new Set() } },
    probMap = null,
    profile = DEFAULT_PROFILE,
    trickNum = 0,
    defending = false,
  } = ctx;
  const options = legalMoves(hand, trick, trumpSuit, mySeat);
  const isEndgame = trickNum >= 6;

  if (trick.length === 0) return chooseLead(hand, options, trumpSuit, mySeat, { memory, isEndgame, profile, defending });
  return chooseFollow(hand, options, trick, trumpSuit, mySeat, { memory, probMap, profile });
}

/* ------------------------------------------------------------------ */
/* Profils des bots                                                     */
/* ------------------------------------------------------------------ */
// Les 3 bots partagent le même moteur (modules 1-4 ci-dessus) mais avec des
// pondérations différentes, pour un style de jeu distinct :
//   - Fanny (la calculatrice) : quasi tout sur la lecture du paquet
//     (probabilités) - peu d'audace en enchères, des impasses très
//     prudentes.
//   - Bernard (le stratège) : synergie maximale - cède vite la main dès
//     que son partenaire est maître, ajuste ses enchères au comportement
//     de son partenaire.
//   - Marcel (l'agressif) : pousse l'atout en défense pour épuiser le
//     preneur, prend plus de risques dans ses impasses et ses enchères.
export const DEFAULT_PROFILE = { biddingBoldness: 0, synergyWeight: 0.5, aggression: 0.3, impasseBoldness: 0.3 };
export const BOT_PROFILES = {
  [FANNY]: { name: 'Fanny', biddingBoldness: 0, synergyWeight: 0.4, aggression: 0.2, impasseBoldness: 0.15 },
  [OPP1]: { name: 'Marcel', biddingBoldness: 0.8, synergyWeight: 0.3, aggression: 0.9, impasseBoldness: 0.7 },
  [OPP2]: { name: 'Bernard', biddingBoldness: 0.2, synergyWeight: 1.0, aggression: 0.25, impasseBoldness: 0.2 },
};

/* ------------------------------------------------------------------ */
/* DecisionEngine : orchestre les 4 modules pour un bot donné            */
/* ------------------------------------------------------------------ */
/** Un DecisionEngine par bot (construit une fois, réutilisé toute la
 * partie). Il ne conserve aucun état d'une mène à l'autre : à chaque
 * décision, il reconstruit sa mémoire/ses probabilités à partir de l'état
 * réel du moteur de jeu (trickHistory/biddingHistory de la mène en cours),
 * ce qui évite tout risque de désynchronisation - moins "performant" en
 * théorie qu'un état incrémental, invisible en pratique vu le volume. */
export class DecisionEngine {
  constructor(seat, profile = BOT_PROFILES[seat] || DEFAULT_PROFILE) {
    this.seat = seat;
    this.profile = profile;
  }

  /** `game` : instance Belote. Retourne une action { type: 'take'|'pass', suit? }. */
  decideBid(game) {
    const { support } = biddingContext({
      seat: this.seat,
      biddingRound: game.biddingRound,
      biddingHistory: game.biddingHistory,
      profile: this.profile,
    });
    return chooseAiBid(game.hands[this.seat], game.biddingRound, game.turnedCard, {
      support, profile: this.profile,
    });
  }

  /** `game` : instance Belote. Retourne la carte (objet Card) à jouer. */
  decideCard(game) {
    const memory = buildMemory(game.trickHistory);
    const probMap = this._buildProbMap(game, memory);
    const defending = game.preneur !== null && teamOf(this.seat) !== teamOf(game.preneur);
    return chooseAiCard(game.hands[this.seat], game.trick, game.trumpSuit, this.seat, {
      memory, probMap, profile: this.profile, trickNum: game.trickNum, defending,
    });
  }

  /** Tente d'abord la reconstruction "mémoire de la mène précédente" (voir
   * l'en-tête du fichier) ; si aucune mène précédente n'est disponible
   * (toute première donne de la session) ou qu'aucune rotation ne colle
   * (ne devrait pas arriver, filet de sécurité), retombe sur l'estimation
   * proportionnelle de la mène en cours. */
  _buildProbMap(game, memory) {
    const myOriginalHand = [
      ...game.hands[this.seat],
      ...game.trickHistory.flatMap((t) => t.cards.filter((e) => e.seat === this.seat).map((e) => e.card)),
      ...game.trick.filter((e) => e.seat === this.seat).map((e) => e.card),
    ];
    const reconstructions = reconstructDeal({
      previousSequence: game.lastRealSequence,
      mySeat: this.seat,
      myOriginalHand,
      dealerSeat: game.dealerSeat,
      preneur: game.preneur,
    });
    if (reconstructions.length > 0) return probMapFromReconstructions(reconstructions, memory, this.seat);

    const handCounts = game.hands.map((h) => h.length);
    return estimateCardProbabilities({ myHand: game.hands[this.seat], mySeat: this.seat, handCounts, memory });
  }
}
