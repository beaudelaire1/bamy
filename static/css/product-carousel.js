(function(){
  const wrap = document.getElementById('product-carousel');
  if (!wrap) return;
  const track = wrap.querySelector('.pc-track');
  const cards = Array.from(track.children);
  if (cards.length < 1) return;

  const prevBtn = wrap.querySelector('[data-pc-prev]');
  const nextBtn = wrap.querySelector('[data-pc-next]');
  const speed = parseInt(wrap.getAttribute('data-speed')||'450',10);
  const auto = wrap.getAttribute('data-auto') !== 'false';
  const interval = parseInt(wrap.getAttribute('data-interval')||'3500',10);

  let idx = 0, timer = null;

  function visibleCount(){
    const w = wrap.clientWidth;
    if (w >= 1200) return 4;
    if (w >= 992)  return 3;
    if (w >= 640)  return 2;
    return 1;
  }
  function cardWidth(){
    const first = cards[0];
    const style = window.getComputedStyle(first);
    const gap = 24; // gap dans le template
    return first.getBoundingClientRect().width + gap;
  }
  function update(){
    track.style.transform = `translateX(${-idx * cardWidth()}px)`;
  }
  function go(n){
    const max = Math.max(0, cards.length - visibleCount());
    idx = Math.max(0, Math.min(n, max));
    track.style.transition = `transform ${speed}ms cubic-bezier(.2,.7,.3,1)`;
    update();
    setTimeout(()=> track.style.transition = 'none', speed);
  }
  function next(){ go(idx + 1); }
  function prev(){ go(idx - 1); }

  function start(){ if(!auto) return; stop(); timer = setInterval(()=>{ if (idx >= cards.length - visibleCount()) idx = -1; next(); }, interval); }
  function stop(){ if(timer) clearInterval(timer); }

  nextBtn && nextBtn.addEventListener('click', ()=>{ next(); start(); });
  prevBtn && prevBtn.addEventListener('click', ()=>{ prev(); start(); });

  window.addEventListener('resize', ()=> go(idx));
  wrap.addEventListener('mouseenter', stop);
  wrap.addEventListener('mouseleave', start);

  update();
  start();
})();
