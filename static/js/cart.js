(function(){
  const btn = document.querySelector("#nav-cart a.icon-btn");
  const panel = document.getElementById("cart-panel");

  if (!btn || !panel) return;

  btn.addEventListener("mouseenter", () => {
    panel.style.display = "block";
  });

  btn.addEventListener("mouseleave", () => {
    panel.style.display = "none";
  });
})();
