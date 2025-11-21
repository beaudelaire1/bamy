// Ouvre /catalog/wishlist/ avec les IDs de localStorage (fallback: lien simple sans IDs).
(function(){
  function getIds(){
    try { return JSON.parse(localStorage.getItem('wishlist_ids') || '[]'); }
    catch(e){ return []; }
  }

  const link = document.getElementById('wishlist-open');
  if (!link) return;

  link.addEventListener('click', function(e){
    e.preventDefault();
    const ids = getIds().map(String).filter(Boolean);
    // base = href déjà présent => robustesse si le site n'est pas à la racine
    const base = link.getAttribute('href') || '/catalog/wishlist/';
    const url = ids.length ? (base + (base.includes('?') ? '&' : '?') + 'ids=' + ids.join(',')) : base;
    window.location.href = url;
  });
})();
