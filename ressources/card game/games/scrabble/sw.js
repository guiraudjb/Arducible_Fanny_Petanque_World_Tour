// Service worker du Scrabble - PWA scopée à ce seul jeu (le SW n'est
// enregistré que depuis games/scrabble/, donc sa portée s'arrête
// naturellement à ce dossier, sans toucher aux autres jeux du casino).
//
// Stratégie mixte :
//   - "coquille applicative" (navigations + .js / .css / .json / .webmanifest
//     de même origine) : NETWORK-FIRST avec repli cache. Le code frais gagne
//     dès qu'on est en ligne - une mise à jour de main.js / engine.js atteint
//     donc les joueurs au prochain chargement, sans dépendre d'un bump de
//     CACHE_VERSION ni du moment où le navigateur revalide sw.js.
//   - reste (dictionnaire .txt/.csv, audio, images) : CACHE-FIRST - lourd et
//     stable, on garde des chargements instantanés et le hors-ligne.
//   - mise en cache opportuniste des requêtes réussies non précachées
//     (ex. pages Wiktionnaire de la recherche approfondie).
//
// CACHE_VERSION sert surtout à purger l'ancien cache à l'activation ;
// l'incrémenter reste utile quand un gros asset cache-first change.
const CACHE_VERSION = 'scrabble-v5';

const PRECACHE_URLS = [
  './',
  './index.html',
  './main.js',
  './best-move-worker.js',
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
  // précachés malgré leur taille (mots.txt ~7,4Mo, definitions.csv ~43Mo).
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

// Coquille applicative (même origine) : navigations + fichiers de code.
const APP_SHELL_RE = /\.(?:js|css|json|webmanifest)$/;

function putInCache(request, response) {
  // Uniquement les réponses saines de même origine (jamais les erreurs ni
  // les réponses opaques cross-origin).
  if (response.ok && response.type === 'basic') {
    const copy = response.clone();
    caches.open(CACHE_VERSION).then((cache) => cache.put(request, copy));
  }
}

self.addEventListener('fetch', (event) => {
  const request = event.request;
  if (request.method !== 'GET') return; // pas de mise en cache des mutations

  const url = new URL(request.url);
  const isShell = request.mode === 'navigate'
    || (url.origin === self.location.origin && APP_SHELL_RE.test(url.pathname));

  if (isShell) {
    // NETWORK-FIRST : code frais si en ligne, cache sinon.
    event.respondWith(
      fetch(request)
        .then((response) => { putInCache(request, response); return response; })
        .catch(() => caches.match(request)),
    );
    return;
  }

  // CACHE-FIRST pour le reste (dictionnaire, audio, images ; + cache
  // opportuniste des pages Wiktionnaire de la recherche approfondie).
  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request)
        .then((response) => { putInCache(request, response); return response; })
        .catch(() => cached);
    }),
  );
});
