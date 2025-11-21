(function(){
  function bySel(s){ return document.querySelector(s); }

  function scrollRail(rail, dir=1){
    if(!rail) return;
    const step = rail.clientWidth * 0.9;
    rail.scrollBy({ left: step * dir, behavior: 'smooth' });
  }

  document.querySelectorAll('.carousel-btn').forEach(btn=>{
    btn.addEventListener('click', ()=>{
      const targetSel = btn.getAttribute('data-target');
      const rail = bySel(targetSel);
      if(!rail) return;
      if(btn.classList.contains('prev')) scrollRail(rail, -1);
      else scrollRail(rail, +1);
    });
  });
})();
