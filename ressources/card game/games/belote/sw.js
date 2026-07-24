// Service worker de la Belote - PWA scopée à ce seul jeu (le SW n'est
// enregistré que depuis games/belote/, donc sa portée s'arrête naturellement
// à ce dossier, sans toucher aux autres jeux du casino).
//
// Stratégie : cache-first sur tout, avec mise en cache opportuniste des
// requêtes réussies qui ne sont pas déjà dans la liste précachée (ex. les
// jeux de cartes à thème du sélecteur de deck : seul le deck par défaut est
// précaché à l'installation, les autres sont mis en cache la première fois
// qu'on les choisit, pour rester jouable hors-ligne ensuite).
//
// Incrémenter CACHE_VERSION à chaque changement de cette liste ou du
// contenu des fichiers précachés, pour forcer une nouvelle installation.
const CACHE_VERSION = 'belote-v2';

const PRECACHE_URLS = [
  './',
  './index.html',
  './main.js',
  './style.css',
  './manifest.webmanifest',
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png',
  './icons/apple-touch-icon.png',
  '../../src/games/belote/engine.js',
  '../../src/games/belote/ai.js',
  '../../src/dealer/dealerVoice.js',
  '../../src/dealer/dealer-dialogue.json',
  '../../src/cards/deckSelector.js',
  // Deck par défaut : uniquement les 32 cartes utilisées par la belote
  // (7 à As, les 2-6 et les jokers ne servent qu'aux autres jeux du casino).
  '../../assets/cards/back.png',
  '../../assets/cards/7-hearts.png', '../../assets/cards/8-hearts.png', '../../assets/cards/9-hearts.png',
  '../../assets/cards/10-hearts.png', '../../assets/cards/J-hearts.png', '../../assets/cards/Q-hearts.png',
  '../../assets/cards/K-hearts.png', '../../assets/cards/A-hearts.png',
  '../../assets/cards/7-diamonds.png', '../../assets/cards/8-diamonds.png', '../../assets/cards/9-diamonds.png',
  '../../assets/cards/10-diamonds.png', '../../assets/cards/J-diamonds.png', '../../assets/cards/Q-diamonds.png',
  '../../assets/cards/K-diamonds.png', '../../assets/cards/A-diamonds.png',
  '../../assets/cards/7-clubs.png', '../../assets/cards/8-clubs.png', '../../assets/cards/9-clubs.png',
  '../../assets/cards/10-clubs.png', '../../assets/cards/J-clubs.png', '../../assets/cards/Q-clubs.png',
  '../../assets/cards/K-clubs.png', '../../assets/cards/A-clubs.png',
  '../../assets/cards/7-spades.png', '../../assets/cards/8-spades.png', '../../assets/cards/9-spades.png',
  '../../assets/cards/10-spades.png', '../../assets/cards/J-spades.png', '../../assets/cards/Q-spades.png',
  '../../assets/cards/K-spades.png', '../../assets/cards/A-spades.png',
  // Répliques de Fanny (voir src/dealer/dealer-dialogue.json).
  '../../assets/dealer_audio/belote/bankruptcy_0.mp3',
  '../../assets/dealer_audio/belote/belote_call_0.mp3',
  '../../assets/dealer_audio/belote/dealing_0.mp3',
  '../../assets/dealer_audio/belote/dealing_1.mp3',
  '../../assets/dealer_audio/belote/greeting_0.mp3',
  '../../assets/dealer_audio/belote/greeting_1.mp3',
  '../../assets/dealer_audio/belote/last_trick_bernard_0.mp3',
  '../../assets/dealer_audio/belote/last_trick_fanny_0.mp3',
  '../../assets/dealer_audio/belote/last_trick_marcel_0.mp3',
  '../../assets/dealer_audio/belote/last_trick_vous_0.mp3',
  '../../assets/dealer_audio/belote/lose_0.mp3',
  '../../assets/dealer_audio/belote/lose_1.mp3',
  '../../assets/dealer_audio/belote/partie_lost_0.mp3',
  '../../assets/dealer_audio/belote/partie_lost_1.mp3',
  '../../assets/dealer_audio/belote/partie_won_0.mp3',
  '../../assets/dealer_audio/belote/partie_won_1.mp3',
  '../../assets/dealer_audio/belote/rebelote_call_0.mp3',
  '../../assets/dealer_audio/belote/take_bernard_carreau_0.mp3',
  '../../assets/dealer_audio/belote/take_bernard_coeur_0.mp3',
  '../../assets/dealer_audio/belote/take_bernard_pique_0.mp3',
  '../../assets/dealer_audio/belote/take_bernard_trefle_0.mp3',
  '../../assets/dealer_audio/belote/take_fanny_carreau_0.mp3',
  '../../assets/dealer_audio/belote/take_fanny_coeur_0.mp3',
  '../../assets/dealer_audio/belote/take_fanny_pique_0.mp3',
  '../../assets/dealer_audio/belote/take_fanny_trefle_0.mp3',
  '../../assets/dealer_audio/belote/take_marcel_carreau_0.mp3',
  '../../assets/dealer_audio/belote/take_marcel_coeur_0.mp3',
  '../../assets/dealer_audio/belote/take_marcel_pique_0.mp3',
  '../../assets/dealer_audio/belote/take_marcel_trefle_0.mp3',
  '../../assets/dealer_audio/belote/trick_win_bernard_0.mp3',
  '../../assets/dealer_audio/belote/trick_win_bernard_1.mp3',
  '../../assets/dealer_audio/belote/trick_win_bernard_2.mp3',
  '../../assets/dealer_audio/belote/trick_win_fanny_0.mp3',
  '../../assets/dealer_audio/belote/trick_win_fanny_1.mp3',
  '../../assets/dealer_audio/belote/trick_win_fanny_2.mp3',
  '../../assets/dealer_audio/belote/trick_win_marcel_0.mp3',
  '../../assets/dealer_audio/belote/trick_win_marcel_1.mp3',
  '../../assets/dealer_audio/belote/trick_win_marcel_2.mp3',
  '../../assets/dealer_audio/belote/trick_win_vous_0.mp3',
  '../../assets/dealer_audio/belote/trick_win_vous_1.mp3',
  '../../assets/dealer_audio/belote/trick_win_vous_2.mp3',
  '../../assets/dealer_audio/belote/win_big_0.mp3',
  '../../assets/dealer_audio/belote/win_big_1.mp3',
  '../../assets/dealer_audio/belote/win_jackpot_0.mp3',
  '../../assets/dealer_audio/belote/win_jackpot_1.mp3',
  '../../assets/dealer_audio/belote/win_small_0.mp3',
  '../../assets/dealer_audio/belote/win_small_1.mp3',
  // Annonce vocale de la carte retournée (une par carte, voir
  // tools/generate_card_audio.py).
  '../../assets/cards_audio/belote/10-carreau.mp3', '../../assets/cards_audio/belote/10-coeur.mp3',
  '../../assets/cards_audio/belote/10-pique.mp3', '../../assets/cards_audio/belote/10-trefle.mp3',
  '../../assets/cards_audio/belote/7-carreau.mp3', '../../assets/cards_audio/belote/7-coeur.mp3',
  '../../assets/cards_audio/belote/7-pique.mp3', '../../assets/cards_audio/belote/7-trefle.mp3',
  '../../assets/cards_audio/belote/8-carreau.mp3', '../../assets/cards_audio/belote/8-coeur.mp3',
  '../../assets/cards_audio/belote/8-pique.mp3', '../../assets/cards_audio/belote/8-trefle.mp3',
  '../../assets/cards_audio/belote/9-carreau.mp3', '../../assets/cards_audio/belote/9-coeur.mp3',
  '../../assets/cards_audio/belote/9-pique.mp3', '../../assets/cards_audio/belote/9-trefle.mp3',
  '../../assets/cards_audio/belote/A-carreau.mp3', '../../assets/cards_audio/belote/A-coeur.mp3',
  '../../assets/cards_audio/belote/A-pique.mp3', '../../assets/cards_audio/belote/A-trefle.mp3',
  '../../assets/cards_audio/belote/J-carreau.mp3', '../../assets/cards_audio/belote/J-coeur.mp3',
  '../../assets/cards_audio/belote/J-pique.mp3', '../../assets/cards_audio/belote/J-trefle.mp3',
  '../../assets/cards_audio/belote/K-carreau.mp3', '../../assets/cards_audio/belote/K-coeur.mp3',
  '../../assets/cards_audio/belote/K-pique.mp3', '../../assets/cards_audio/belote/K-trefle.mp3',
  '../../assets/cards_audio/belote/Q-carreau.mp3', '../../assets/cards_audio/belote/Q-coeur.mp3',
  '../../assets/cards_audio/belote/Q-pique.mp3', '../../assets/cards_audio/belote/Q-trefle.mp3',
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_VERSION)
      .then((cache) => cache.addAll(PRECACHE_URLS))
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((k) => k !== CACHE_VERSION).map((k) => caches.delete(k))))
      .then(() => self.clients.claim()),
  );
});

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return; // pas de mise en cache des mutations

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request).then((response) => {
        // Mise en cache opportuniste (ex. un jeu de cartes à thème choisi
        // dans le sélecteur) : uniquement les réponses saines et de même
        // origine, jamais les erreurs ni les réponses opaques cross-origin.
        if (response.ok && response.type === 'basic') {
          const copy = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
        }
        return response;
      }).catch(() => cached);
    }),
  );
});
