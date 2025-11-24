(function () {
  // Tous les rubans présents sur la page
  const ribbons = document.querySelectorAll(".promo-ribbon");
  if (!ribbons.length) return;

  ribbons.forEach(ribbon => {
    ribbon.style.transformOrigin = "left";

    // effet d’apparition
    ribbon.animate(
      [
        { transform: "rotate(-50deg) translateX(-40px)", opacity: 0 },
        { transform: "rotate(-40deg) translateX(0)", opacity: 1 }
      ],
      {
        duration: 450,
        easing: "cubic-bezier(.22,.61,.36,1)",
        fill: "forwards"
      }
    );

    // léger pulsation toutes les 2 secondes
    setInterval(() => {
      ribbon.animate(
        [
          { transform: "rotate(-40deg) scale(1)" },
          { transform: "rotate(-40deg) scale(1.05)" },
          { transform: "rotate(-40deg) scale(1)" }
        ],
        {
          duration: 900,
          easing: "ease-in-out"
        }
      );
    }, 2400);
  });
})();
