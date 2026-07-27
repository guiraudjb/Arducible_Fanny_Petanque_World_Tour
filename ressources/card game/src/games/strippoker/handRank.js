const RANK_VALUES = {
  A: 14, K: 13, Q: 12, J: 11, 10: 10, 9: 9, 8: 8, 7: 7, 6: 6, 5: 5, 4: 4, 3: 3, 2: 2,
};

export const HAND_CATEGORY_NAMES = {
  'royal-flush': 'Quinte flush royale',
  'straight-flush': 'Quinte flush',
  'four-of-a-kind': 'Carré',
  'full-house': 'Full',
  flush: 'Couleur',
  straight: 'Quinte',
  'three-of-a-kind': 'Brelan',
  'two-pair': 'Double paire',
  'one-pair': 'Paire',
  'high-card': 'Carte haute',
};

/**
 * Classe une main de 5 cartes (poker standard, tous les rangs de paire comptent,
 * contrairement au video poker Jacks or Better). Renvoie la catégorie et un
 * vecteur de départage (kickers) pour comparer deux mains de même catégorie.
 */
export function rankHand(cards) {
  const values = cards.map((c) => RANK_VALUES[c.rank]).sort((a, b) => b - a);
  const isFlush = new Set(cards.map((c) => c.suit)).size === 1;

  const uniqueDesc = [...new Set(values)].sort((a, b) => b - a);
  let isStraight = false;
  let straightHigh = null;
  if (uniqueDesc.length === 5) {
    if (uniqueDesc[0] - uniqueDesc[4] === 4) {
      isStraight = true;
      straightHigh = uniqueDesc[0];
    } else if (uniqueDesc.join(',') === '14,5,4,3,2') {
      isStraight = true; // quinte "roue" As-2-3-4-5
      straightHigh = 5;
    }
  }

  const countMap = new Map();
  for (const v of values) countMap.set(v, (countMap.get(v) || 0) + 1);
  const groups = [...countMap.entries()].sort((a, b) => b[1] - a[1] || b[0] - a[0]);

  if (isStraight && isFlush) {
    return straightHigh === 14
      ? { category: 'royal-flush', categoryIndex: 9, tiebreak: [14] }
      : { category: 'straight-flush', categoryIndex: 8, tiebreak: [straightHigh] };
  }
  if (groups[0][1] === 4) {
    return { category: 'four-of-a-kind', categoryIndex: 7, tiebreak: [groups[0][0], groups[1][0]] };
  }
  if (groups[0][1] === 3 && groups[1][1] === 2) {
    return { category: 'full-house', categoryIndex: 6, tiebreak: [groups[0][0], groups[1][0]] };
  }
  if (isFlush) {
    return { category: 'flush', categoryIndex: 5, tiebreak: values };
  }
  if (isStraight) {
    return { category: 'straight', categoryIndex: 4, tiebreak: [straightHigh] };
  }
  if (groups[0][1] === 3) {
    return {
      category: 'three-of-a-kind',
      categoryIndex: 3,
      tiebreak: [groups[0][0], groups[1][0], groups[2][0]],
    };
  }
  if (groups[0][1] === 2 && groups[1][1] === 2) {
    return {
      category: 'two-pair',
      categoryIndex: 2,
      tiebreak: [Math.max(groups[0][0], groups[1][0]), Math.min(groups[0][0], groups[1][0]), groups[2][0]],
    };
  }
  if (groups[0][1] === 2) {
    return {
      category: 'one-pair',
      categoryIndex: 1,
      tiebreak: [groups[0][0], groups[1][0], groups[2][0], groups[3][0]],
    };
  }
  return { category: 'high-card', categoryIndex: 0, tiebreak: values };
}

/** Renvoie 1 si la main A gagne, -1 si B gagne, 0 en cas d'égalité parfaite. */
export function compareHands(handA, handB) {
  const rankA = rankHand(handA);
  const rankB = rankHand(handB);
  if (rankA.categoryIndex !== rankB.categoryIndex) {
    return rankA.categoryIndex > rankB.categoryIndex ? 1 : -1;
  }
  for (let i = 0; i < rankA.tiebreak.length; i += 1) {
    if (rankA.tiebreak[i] !== rankB.tiebreak[i]) {
      return rankA.tiebreak[i] > rankB.tiebreak[i] ? 1 : -1;
    }
  }
  return 0;
}
