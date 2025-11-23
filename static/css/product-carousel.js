(function(){
  const wrap = document.getElementById('product-carousel');
  if(!wrap) return;

  const track = wrap.querySelector('.pc-track');
  const slides = wrap.querySelectorAll('.pc-slide');
  let index = 0;
  let timer = null;

  function update(){
    const w = wrap.clientWidth;
    track.style.transform = `translateX(-${index * w}px)`;
  }

  function next(){
    index = (index + 1) % slides.length;
    update();
  }

  function start(){
    if(timer) clearInterval(timer);
    timer = setInterval(next, 3500);
  }

  window.addEventListener('resize', update);
  wrap.addEventListener('mouseenter', () => clearInterval(timer));
  wrap.addEventListener('mouseleave', start);

  update();
  start();
})();
