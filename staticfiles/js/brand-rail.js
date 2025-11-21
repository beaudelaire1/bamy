(function(){
  const stack = document.getElementById('brand-stack');
  if(!stack) return;

  const items = Array.from(stack.querySelectorAll('.brand-item'));
  if(items.length <= 1) return;

  const visibleMs = Number(stack.getAttribute('data-visible-ms') || 2400);
  const gapMs     = Number(stack.getAttribute('data-gap-ms') || 300);

  let i = 0; // celui qui est visible
  function next(){
    // cacher l'actuel
    items[i].classList.remove('is-active');
    // gap noir (rien ne s'affiche)
    setTimeout(()=>{
      i = (i + 1) % items.length;
      items[i].classList.add('is-active');
      setTimeout(next, visibleMs);
    }, gapMs);
  }
  setTimeout(next, visibleMs);
})();
