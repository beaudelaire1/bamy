// Gestion du thème sombre/clair.
// Ce script ajoute ou retire une classe `dark-theme` sur le body et
// persiste le choix dans localStorage. Lorsque la page se charge,
// l'état enregistré est restauré.

function applyTheme(saved) {
  if (saved === "dark") {
    document.body.classList.add("dark-theme");
  } else {
    document.body.classList.remove("dark-theme");
  }
}

document.addEventListener("DOMContentLoaded", function () {
  try {
    const saved = localStorage.getItem("site_theme");
    applyTheme(saved);
    const toggle = document.getElementById("theme-toggle");
    if (toggle) {
      toggle.addEventListener("click", function () {
        const isDark = document.body.classList.toggle("dark-theme");
        localStorage.setItem("site_theme", isDark ? "dark" : "light");
      });
    }
  } catch (e) {
    // Gracefully fail if localStorage is unavailable
  }
});