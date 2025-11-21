// Incrémente / décrémente et soumet le formulaire (fallback SSR OK)
(function () {
  const forms = document.querySelectorAll(".js-qty-form");
  if (forms.length) {
    forms.forEach((form) => {
      const minus = form.querySelector(".js-qty-minus");
      const plus = form.querySelector(".js-qty-plus");
      const input = form.querySelector('input[name="qty"]');
      const submitSafely = () => {
        const buttons = form.querySelectorAll("button");
        buttons.forEach(b => b.disabled = true);
        form.submit();
      };
      if (minus) {
        minus.addEventListener("click", () => {
          let v = parseInt(input.value || "0", 10);
          if (Number.isNaN(v)) v = 0;
          v = Math.max(0, v - 1); // 0 => suppression côté serveur
          input.value = v;
          submitSafely();
        });
      }
      if (plus) {
        plus.addEventListener("click", () => {
          let v = parseInt(input.value || "0", 10);
          if (Number.isNaN(v)) v = 0;
          input.value = v + 1;
          submitSafely();
        });
      }
    });
  }
  // "Continuer vos achats" : si l'utilisateur a une page précédente, on privilégie history.back()
  const backLinks = document.querySelectorAll(".js-continue-shopping");
  backLinks.forEach((a) => {
    a.addEventListener("click", (e) => {
      if (document.referrer && history.length > 1) {
        e.preventDefault();
        history.back();
      }
    });
  });
})();
