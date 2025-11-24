(function(){
  const btn = document.getElementById("theme-toggle");
  if (!btn) return;

  const html = document.documentElement;

  function apply(){
    if (localStorage.getItem("theme") === "dark") {
      html.setAttribute("data-theme", "dark");
    } else {
      html.removeAttribute("data-theme");
    }
  }

  btn.addEventListener("click", () => {
    const now = localStorage.getItem("theme") === "dark" ? "light" : "dark";
    localStorage.setItem("theme", now);
    apply();
  });

  apply();
})();
