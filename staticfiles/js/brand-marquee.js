// brand-marquee.js — défilement continu des logos (direction + vitesse aléatoires)
(function(){
  const root = document.getElementById('brand-marquee');
  if (!root) return;

  const track = root.querySelector('.marquee-track');
  if (!track) return;
  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;

  // Duplique la piste pour effet infini
  const clone = track.cloneNode(true);
  clone.classList.add('marquee-track');
  clone.style.left = '100%';
  root.appendChild(clone);

  // Direction & durée aléatoires
  const min = parseInt(root.getAttribute('data-min') || '18', 10);
  const max = parseInt(root.getAttribute('data-max') || '32', 10);
  const dir = Math.random() < 0.5 ? 'left' : 'right';
  const dur = (Math.random() * (max - min) + min).toFixed(1) + 's';

  [track, clone].forEach(el => {
    el.style.animation = `${dir === 'left' ? 'marquee-left' : 'marquee-right'} ${dur} linear infinite`;
  });

  // Pause au survol
  root.addEventListener('mouseenter', ()=> {
    track.style.animationPlayState = 'paused';
    clone.style.animationPlayState = 'paused';
  });
  root.addEventListener('mouseleave', ()=> {
    track.style.animationPlayState = 'running';
    clone.style.animationPlayState = 'running';
  });
})();
