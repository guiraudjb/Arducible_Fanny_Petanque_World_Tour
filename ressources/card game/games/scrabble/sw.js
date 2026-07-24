// Service worker du Scrabble - PWA scopée à ce seul jeu (le SW n'est
// enregistré que depuis games/scrabble/, donc sa portée s'arrête
// naturellement à ce dossier, sans toucher aux autres jeux du casino).
//
// Stratégie : cache-first sur tout, avec mise en cache opportuniste des
// requêtes réussies qui ne sont pas déjà précachées (ex. les pages
// Wiktionnaire consultées via la recherche approfondie).
//
// Incrémenter CACHE_VERSION à chaque changement de cette liste ou du
// contenu des fichiers précachés, pour forcer une nouvelle installation.
const CACHE_VERSION = 'scrabble-v1';

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
  '../../src/games/scrabble/engine.js',
  '../../src/dealer/dealerVoice.js',
  '../../src/dealer/dealer-dialogue.json',
  '../../assets/table/fanny-dealer-scene.jpg',
  // Dictionnaire + définitions : sans eux le jeu est injouable, donc
  // précachés malgré leur taille (mots.txt ~550Ko, definitions.csv ~4,7Mo).
  '../../assets/scrabble/mots.txt',
  '../../assets/scrabble/definitions.csv',
  // Répliques de Fanny (voir src/dealer/dealer-dialogue.json).
  '../../assets/dealer_audio/scrabble/bankruptcy_0.mp3',
  '../../assets/dealer_audio/scrabble/bingo_0.mp3',
  '../../assets/dealer_audio/scrabble/bingo_1.mp3',
  '../../assets/dealer_audio/scrabble/dealing_0.mp3',
  '../../assets/dealer_audio/scrabble/dealing_1.mp3',
  '../../assets/dealer_audio/scrabble/greeting_0.mp3',
  '../../assets/dealer_audio/scrabble/greeting_1.mp3',
  '../../assets/dealer_audio/scrabble/lose_0.mp3',
  '../../assets/dealer_audio/scrabble/lose_1.mp3',
  '../../assets/dealer_audio/scrabble/timeout_0.mp3',
  '../../assets/dealer_audio/scrabble/timeout_1.mp3',
  '../../assets/dealer_audio/scrabble/win_big_0.mp3',
  '../../assets/dealer_audio/scrabble/win_big_1.mp3',
  '../../assets/dealer_audio/scrabble/win_jackpot_0.mp3',
  '../../assets/dealer_audio/scrabble/win_jackpot_1.mp3',
  '../../assets/dealer_audio/scrabble/win_small_0.mp3',
  '../../assets/dealer_audio/scrabble/win_small_1.mp3',
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
        // Mise en cache opportuniste (ex. une page Wiktionnaire consultée
        // via la recherche approfondie) : uniquement les réponses saines
        // et de même origine, jamais les erreurs ni les réponses opaques
        // cross-origin (Wiktionnaire, chargé dans une frame, n'est de
        // toute façon pas concerné : c'est une requête cross-origin faite
        // par le navigateur pour l'iframe, pas par ce service worker).
        if (response.ok && response.type === 'basic') {
          const copy = response.clone();
          caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
        }
        return response;
      }).catch(() => cached);
    }),
  );
});
