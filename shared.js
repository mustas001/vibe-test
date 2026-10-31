/* Small helpers shared by the arcade pages: PWA plumbing and phone niceties. */
(() => {
'use strict';
const A = window.Arcade = {};
const mq = q => matchMedia(q).matches;
const isGame = document.body.hasAttribute('data-game');

A.touch = mq('(pointer: coarse)');
A.standalone = mq('(display-mode: standalone)') || mq('(display-mode: fullscreen)') || navigator.standalone === true;
A.buzz = ms => { try { if (A.touch && navigator.vibrate) navigator.vibrate(ms); } catch {} };

// offline support (needs https or localhost; silently skipped otherwise)
if ('serviceWorker' in navigator && /^https?:$/.test(location.protocol)) {
  addEventListener('load', () => navigator.serviceWorker.register('sw.js').catch(() => {}));
}

// stop iOS pinch-zoom gestures
['gesturestart', 'gesturechange', 'gestureend'].forEach(t => document.addEventListener(t, e => e.preventDefault()));

if (!isGame) return;

// ask phones held upright to rotate; games pause themselves via the event
const rot = document.createElement('div');
rot.id = 'rotate';
rot.innerHTML = '<div class="phone"></div><div class="msg">ROTATE YOUR PHONE</div><div class="sub">This game plays in landscape</div>';
document.body.appendChild(rot);
const portrait = matchMedia('(pointer: coarse) and (orientation: portrait)');
const onTurn = () => { if (portrait.matches) dispatchEvent(new Event('arcade:portrait')); };
portrait.addEventListener ? portrait.addEventListener('change', onTurn) : portrait.addListener(onTurn);

// block the long-press menu on the playfield
document.addEventListener('contextmenu', e => { if (e.target.closest && e.target.closest('.stage')) e.preventDefault(); });

// fullscreen toggle (not available on iPhone Safari, which needs "Add to Home Screen")
const fs = document.getElementById('fsBtn');
const root = document.documentElement;
if (fs && root.requestFullscreen && !A.standalone) {
  fs.hidden = false;
  fs.addEventListener('click', async () => {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else {
        await root.requestFullscreen({ navigationUI: 'hide' });
        try { await screen.orientation.lock('landscape'); } catch {}
      }
    } catch {}
    fs.blur();
  });
  document.addEventListener('fullscreenchange', () => { fs.textContent = document.fullscreenElement ? 'EXIT FULL' : 'FULLSCREEN'; });
}

// keep the screen awake while playing
let lock = null;
const keepAwake = async () => {
  try {
    if (!('wakeLock' in navigator) || lock || document.visibilityState !== 'visible') return;
    lock = await navigator.wakeLock.request('screen');
    lock.addEventListener('release', () => { lock = null; });
  } catch {}
};
addEventListener('pointerdown', keepAwake);
document.addEventListener('visibilitychange', keepAwake);
})();
