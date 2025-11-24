(function(){
  const wrap = document.getElementById('product-carousel');
  if (!wrap) return;

  const track = wrap.querySelector('.pc-track');
  const prevBtn = wrap.querySelector('[data-pc-prev]');
  const nextBtn = wrap.querySelector('[data-pc-next]');
  const cards = [...track.children];

  let idx = 0;
  let timer = null;

  const speed = parseInt(wrap.dataset.speed || '450');
  const interval = parseInt(wrap.dataset.interval || '3500');
  const auto = wrap.dataset.auto !== 'false';

  function visibleCount() {
    const w = wrap.clientWidth;
    if (w >= 1200) return 4;
    if (w >= 992) return 3;
    if (w >= 640) return 2;
    return 1;
  }

  function cardWidth() {
    const c = cards[0];
    return c.getBoundingClientRect().width + 24;
  }

  function update(){
    track.style.transform = `translateX(${-idx * cardWidth()}px)`;
  }

  function go(n){
    const max = Math.max(0, cards.length - visibleCount());
    idx = Math.max(0, Math.min(n, max));
    track.style.transition = `transform ${speed}ms ease`;
    update();
    setTimeout(() => track.style.transition = 'none', speed);
  }

  function next() { go(idx + 1); }
  function prev() { go(idx - 1); }

  if (nextBtn) nextBtn.onclick = () => { next(); start(); };
  if (prevBtn) prevBtn.onclick = () => { prev(); start(); };

  function start(){
    stop();
    if (!auto) return;
    timer = setInterval(() => {
      if (idx >= cards.length - visibleCount()) idx = -1;
      next();
    }, interval);
  }

  function stop(){
    if (timer) clearInterval(timer);
  }

  wrap.addEventListener("mouseenter", stop);
  wrap.addEventListener("mouseleave", start);

  update();
  start();
})();
