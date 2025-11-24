(function(){
  const mq = document.querySelector(".brand-marquee");
  if (!mq) return;

  let scrollAmount = 0;

  function loop(){
    scrollAmount += 1;
    mq.scrollLeft = scrollAmount;
    if (scrollAmount >= mq.scrollWidth - mq.clientWidth) {
      scrollAmount = 0;
    }
    requestAnimationFrame(loop);
  }

  loop();
})();
