// Voix de la croupière (Fanny) : bulle de dialogue + audio gTTS, partagés
// entre Blackjack et Vidéo Poker. Les textes sources vivent dans
// dealer-dialogue.json (seule source de vérité, lue aussi par le script de
// génération audio ressources/card game/tools/generate_dealer_audio.py :
// ne pas dupliquer les textes ailleurs, modifier uniquement ce JSON puis
// relancer le script pour régénérer les mp3 manquants).

const DIALOGUE_URL = new URL('./dealer-dialogue.json', import.meta.url);
const AUDIO_DIR = new URL('../../assets/dealer_audio/', import.meta.url);
const MUTE_KEY = 'fanny-dealer-muted';

let dialoguePromise = null;
function loadDialogue() {
  if (!dialoguePromise) {
    dialoguePromise = fetch(DIALOGUE_URL).then((r) => r.json());
  }
  return dialoguePromise;
}

export function isMuted() {
  return localStorage.getItem(MUTE_KEY) === '1';
}

function setMuted(muted) {
  localStorage.setItem(MUTE_KEY, muted ? '1' : '0');
}

/**
 * @param {object} opts
 * @param {string} opts.game - 'blackjack' | 'poker'
 * @param {HTMLElement} opts.bubbleEl - conteneur de la bulle (masqué/affiché)
 * @param {HTMLElement} opts.textEl - élément recevant le texte de la réplique
 * @param {HTMLElement} [opts.muteBtn] - bouton toggle mute, optionnel
 */
export function createDealerVoice({ game, bubbleEl, textEl, muteBtn }) {
  let dialogue = null;
  loadDialogue().then((data) => { dialogue = data[game] || {}; });

  const audio = new Audio();
  audio.preload = 'none';
  let hideTimer = null;

  function updateMuteButton() {
    if (!muteBtn) return;
    const muted = isMuted();
    muteBtn.setAttribute('aria-pressed', String(muted));
    muteBtn.textContent = muted ? '🔇' : '🔊';
  }

  function hideBubble() {
    bubbleEl.classList.remove('is-visible');
  }

  function showBubble(text) {
    textEl.textContent = text;
    bubbleEl.classList.remove('is-visible');
    void bubbleEl.offsetWidth;
    bubbleEl.classList.add('is-visible');

    clearTimeout(hideTimer);
    // Filet de sécurité si l'audio ne joue pas (muet, mp3 manquant, autoplay
    // bloqué) : la bulle reste lisible un temps raisonnable puis disparaît.
    hideTimer = setTimeout(hideBubble, 4200);
  }

  function say(event) {
    if (!dialogue) {
      // JSON pas encore chargé (très tôt après l'ouverture de la page) :
      // on retente une fois qu'il est prêt plutôt que de perdre la réplique.
      loadDialogue().then((data) => {
        dialogue = data[game] || {};
        say(event);
      });
      return;
    }
    const lines = dialogue[event];
    if (!lines || lines.length === 0) return;
    const index = Math.floor(Math.random() * lines.length);
    const text = lines[index];

    showBubble(text);

    if (isMuted()) return;
    audio.pause();
    audio.src = new URL(`${game}/${event}_${index}.mp3`, AUDIO_DIR).toString();
    audio.currentTime = 0;
    audio.play().catch(() => {
      // Lecture bloquée (politique autoplay du navigateur) : la bulle
      // affichée ci-dessus reste le seul retour, ce qui est acceptable.
    });
  }

  if (muteBtn) {
    updateMuteButton();
    muteBtn.addEventListener('click', () => {
      setMuted(!isMuted());
      updateMuteButton();
      if (isMuted()) audio.pause();
    });
  }

  audio.addEventListener('ended', () => {
    clearTimeout(hideTimer);
    hideTimer = setTimeout(hideBubble, 900);
  });

  return { say };
}
