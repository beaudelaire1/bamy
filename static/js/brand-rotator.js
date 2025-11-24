(function () {
  const el = document.getElementById("brand-rotator");
  if (!el) return;

  const panels = [...el.querySelectorAll(".rotor-panel")];
  let index = 0;

  const min = parseInt(el.dataset.intervalMin || "5200");
  const max = parseInt(el.dataset.intervalMax || "9000");
  const dur = parseInt(el.dataset.duration || "700");

  function next() {
    panels[index].classList.add("is-hidden");
    index = (index + 1) % panels.length;
    panels[index].classList.remove("is-hidden");

    const nextDelay = Math.floor(Math.random() * (max - min)) + min;
    setTimeout(next, nextDelay);
  }

  setTimeout(next, min);
})();
