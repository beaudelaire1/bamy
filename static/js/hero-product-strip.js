// Défilement continu des produits dans l'encadré du Héro (direction & vitesse aléatoires)
(function(){
  const root = document.getElementById('hero-product-strip');
  if (!root) return;
  const strip = root.querySelector('.strip');
  if (!strip) return;

  const reduce = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  if (reduce) return;

  // Clone pour effet infini
  const clone = strip.cloneNode(true);
  clone.classList.add('strip-clone');
  root.appendChild(clone);

  // Durée & direction aléatoires
  const min = parseInt(root.getAttribute('data-min') || '18', 10);
  const max = parseInt(root.getAttribute('data-max') || '28', 10);
  const dir = Math.random() < 0.5 ? 'strip-left' : 'strip-right';
  const dur = (Math.random() * (max - min) + min).toFixed(1) + 's';

  [strip, clone].forEach(el => {
    el.style.animation = `${dir} ${dur} linear infinite`;
  });

  // Pause au survol (UX premium)
  root.addEventListener('mouseenter', ()=> {
    strip.style.animationPlayState = 'paused';
    clone.style.animationPlayState = 'paused';
  });
  root.addEventListener('mouseleave', ()=> {
    strip.style.animationPlayState = 'running';
    clone.style.animationPlayState = 'running';
  });
})();
