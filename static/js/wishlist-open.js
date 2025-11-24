(function(){
  const btn = document.querySelector("#nav-wishlist button");
  const panel = document.getElementById("wishlist-panel");

  if (!btn || !panel) return;

  btn.addEventListener("click", () => {
    panel.style.display = panel.style.display === "block" ? "none" : "block";
  });

  document.addEventListener("click", (e) => {
    if (!panel.contains(e.target) && !btn.contains(e.target)) {
      panel.style.display = "none";
    }
  });
})();
