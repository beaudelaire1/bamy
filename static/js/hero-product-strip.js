(function(){
  const strip = document.querySelector(".hero-product-strip");
  if (!strip) return;

  let x = 0;

  function loop(){
    x -= 0.5;
    strip.style.transform = `translateX(${x}px)`;
    if (Math.abs(x) > strip.clientWidth) x = 0;
    requestAnimationFrame(loop);
  }

  loop();
})();
