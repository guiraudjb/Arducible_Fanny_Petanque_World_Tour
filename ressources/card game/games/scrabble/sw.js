// Service worker du Scrabble - PWA scopée à ce seul jeu (le SW n'est
// enregistré que depuis games/scrabble/, donc sa portée s'arrête
// naturellement à ce dossier, sans toucher aux autres jeux du casino).
//
// Stratégie mixte :
//   - "coquille applicative" (navigations + .js / .css / .json / .webmanifest
//     de même origine) : NETWORK-FIRST avec repli cache. Le code frais gagne
//     dès qu'on est en ligne.
//   - reste (dictionnaire .txt/.csv, audio, images) : CACHE-FIRST - lourd et
//     stable, chargements instantanés + hors-ligne.
//   - requêtes réussies non précachées : cache opportuniste dans un cache
//     RUNTIME séparé et plafonné (jamais dans le cache versionné, pour ne
//     pas risquer d'évincer un fichier critique).
//
// Durcissement (v6) :
//   - le pré-cache n'est plus atomique : un .mp3 manquant ou definitions.csv
//     qui coupe ne bloque plus l'installation. Avant, cache.addAll rejetait
//     en bloc -> install en échec -> skipWaiting jamais appelé -> l'ancien
//     SW (et son ancien dictionnaire) restait actif indéfiniment. Désormais :
//     Promise.allSettled + skipWaiting inconditionnel.
//   - à l'activation, contrôle de vraisemblance du mots.txt en cache (dans
//     TOUS les caches) : trop court = vieille copie (76 k mots) ou tronquée
//     -> on la supprime, le prochain fetch la rechargera sur le réseau.
//   - on ne purge les anciens caches que si le nouveau cache est viable
//     (index.html + main.js présents), sinon on les garde comme filet.
//   - putInCache rejette un mots.txt dont le corps est plus court que son
//     Content-Length annoncé (téléchargement coupé en plein flux).
//   - message {type:'PURGE_DICT'} : purge le dictionnaire à la demande
//     (bouton "recharger le dictionnaire" côté jeu).
//
// CACHE_VERSION purge les anciens caches à l'activation ; l'incrémenter
// reste nécessaire quand un gros asset cache-first change.
const CACHE_VERSION = 'scrabble-v6';
const RUNTIME_CACHE = 'scrabble-runtime-v6';
const RUNTIME_MAX = 60; // nombre max d'entrées du cache opportuniste (éviction FIFO)

// mots.txt fait ~645 000 lignes aujourd'hui ; en-dessous de ce plancher la
// copie en cache est forcément une vieille version ou une copie tronquée.
const DICT_MIN_WORDS = 500000;

const DICT_URL = new URL('../../assets/scrabble/mots.txt', self.location).href;
const DEFS_URL = new URL('../../assets/scrabble/definitions.csv', self.location).href;

// Sans ces fichiers le jeu est injouable : on essaie de les pré-cacher, mais
// même en cas d'échec on installe quand même (le fetch réseau prendra le
// relais au premier besoin).
const CRITICAL_URLS = [
  './',
  './index.html',
  './main.js',
  './best-move-worker.js',
  './style.css',
  './manifest.webmanifest',
  '../../src/games/scrabble/engine.js',
  '../../src/dealer/dealerVoice.js',
  '../../src/dealer/dealer-dialogue.json',
  '../../assets/scrabble/mots.txt',
];

// Confort (icônes, définitions, voix de Fanny, décor) : pré-cachés au mieux,
// jamais bloquants.
const OPTIONAL_URLS = [
  './icons/icon-192.png',
  './icons/icon-512.png',
  './icons/icon-512-maskable.png',
  './icons/apple-touch-icon.png',
  '../../assets/table/fanny-dealer-scene.jpg',
  // definitions.csv ~43 Mo : lourd, et le jeu tourne sans (repli sur le
  // dico complet) -> optionnel, jamais bloquant pour l'installation.
  '../../assets/scrabble/definitions.csv',
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

const PRECACHE_SET = new Set(
  [...CRITICAL_URLS, ...OPTIONAL_URLS].map((u) => new URL(u, self.location).href),
);

// Pré-cache tolérant : chaque URL est tentée indépendamment, un échec
// n'entraîne pas les autres (contrairement à cache.addAll qui rejette en
// bloc et fait alors échouer toute l'installation).
async function precache() {
  const cache = await caches.open(CACHE_VERSION);
  await Promise.allSettled(OPTIONAL_URLS.map((u) => cache.add(u)));
  await Promise.allSettled(CRITICAL_URLS.map((u) => cache.add(u)));
}

self.addEventListener('install', (event) => {
  event.waitUntil(precache().then(() => self.skipWaiting()));
});

/** Le nouveau cache contient-il au moins le code du jeu ? Sert de garde-fou
 * avant de purger les anciens caches : si le pré-cache a totalement échoué
 * (mise à jour lancée hors-ligne...), on garde les anciens comme filet. */
async function newCacheIsViable() {
  const cache = await caches.open(CACHE_VERSION);
  const [html, js] = await Promise.all([
    cache.match('./index.html'),
    cache.match('./main.js'),
  ]);
  return Boolean(html && js);
}

/** Supprime toute copie de mots.txt manifestement périmée (vieille version
 * courte) ou tronquée, dans TOUS les caches - y compris un ancien cache
 * conservé comme filet, qui sinon masquerait la copie fraîche
 * (CacheStorage.match parcourt les caches du plus ancien au plus récent).
 * Le prochain fetch ira chercher la bonne version sur le réseau. */
async function ensureFreshDictionary() {
  for (const name of await caches.keys()) {
    const cache = await caches.open(name);
    const cached = await cache.match(DICT_URL);
    if (!cached) continue;
    try {
      const text = await cached.text();
      let lines = 0;
      for (let i = 0; i < text.length; i += 1) {
        if (text.charCodeAt(i) === 10) lines += 1;
      }
      if (lines < DICT_MIN_WORDS) await cache.delete(DICT_URL);
    } catch (_) {
      await cache.delete(DICT_URL);
    }
  }
}

self.addEventListener('activate', (event) => {
  event.waitUntil((async () => {
    if (await newCacheIsViable()) {
      const keep = new Set([CACHE_VERSION, RUNTIME_CACHE]);
      const keys = await caches.keys();
      await Promise.all(keys.filter((k) => !keep.has(k)).map((k) => caches.delete(k)));
    }
    await ensureFreshDictionary();
    await self.clients.claim();
  })());
});

// Purge du dictionnaire à la demande du jeu (ex. bouton "recharger le
// dictionnaire", ou déclenchée si un mot censé valide est refusé). Le client
// recharge la page ensuite pour re-télécharger la version fraîche.
self.addEventListener('message', (event) => {
  if (!event.data || event.data.type !== 'PURGE_DICT') return;
  event.waitUntil(
    caches.open(CACHE_VERSION).then((cache) => Promise.all([
      cache.delete(DICT_URL),
      cache.delete(DEFS_URL),
    ])),
  );
});

// Coquille applicative (même origine) : navigations + fichiers de code.
const APP_SHELL_RE = /\.(?:js|css|json|webmanifest)$/;

/** Éviction FIFO du cache opportuniste (cache.keys() rend les entrées dans
 * leur ordre d'insertion). */
function trimCache(cacheName, max) {
  caches.open(cacheName).then((cache) => cache.keys().then((keys) => {
    if (keys.length <= max) return;
    Promise.all(keys.slice(0, keys.length - max).map((k) => cache.delete(k)));
  }));
}

/** Met en cache une réponse saine de même origine. Pour le dictionnaire
 * uniquement : rejette un corps plus court que le Content-Length annoncé
 * (connexion coupée en plein téléchargement - on préfère re-fetch plus tard
 * qu'un mots.txt tronqué servi comme référence ; une troncature de
 * definitions.csv, elle, n'est que cosmétique). */
function putInCache(request, response, cacheName) {
  if (!response.ok || response.type !== 'basic') return;
  const forStore = response.clone();
  const finish = () => caches.open(cacheName).then((cache) =>
    cache.put(request, forStore).then(() => {
      if (cacheName === RUNTIME_CACHE) trimCache(RUNTIME_CACHE, RUNTIME_MAX);
    }));

  const declared = Number(response.headers.get('content-length'));
  if (request.url === DICT_URL && declared > 0) {
    response.clone().arrayBuffer()
      .then((buf) => { if (buf.byteLength >= declared) finish(); })
      .catch(() => {});
    return;
  }
  finish();
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
        .then((response) => { putInCache(request, response, CACHE_VERSION); return response; })
        .catch(() => caches.match(request)),
    );
    return;
  }

  // CACHE-FIRST pour le reste. Un asset connu (précaché ou coquille) va dans
  // le cache versionné ; tout le reste (pages Wiktionnaire de la recherche
  // approfondie, etc.) dans le cache RUNTIME plafonné.
  const versioned = PRECACHE_SET.has(url.href)
    || (url.origin === self.location.origin && APP_SHELL_RE.test(url.pathname));
  const cacheName = versioned ? CACHE_VERSION : RUNTIME_CACHE;

  event.respondWith(
    caches.match(request).then((cached) => {
      if (cached) return cached;
      return fetch(request)
        .then((response) => { putInCache(request, response, cacheName); return response; })
        .catch(() => cached);
    }),
  );
});
