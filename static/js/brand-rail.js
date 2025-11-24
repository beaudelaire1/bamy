(function () {
  const stack = document.getElementById("brand-stack");
  if (!stack) return;

  const items = [...stack.querySelectorAll(".brand-item")];
  const dots = [...document.querySelectorAll(".brand-pagination .brand-dot")];

  if (items.length <= 1) {
    items.forEach(el => el.classList.add("is-active"));
    return;
  }

  let index = 0;
  const interval = parseInt(stack.dataset.interval || "3500");

  function show(i) {
    items.forEach((el, idx) => {
      el.classList.toggle("is-active", idx === i);
    });
    dots.forEach((el, idx) => {
      el.classList.toggle("is-active", idx === i);
    });
  }

  function next() {
    index = (index + 1) % items.length;
    show(index);
  }

  // initial
  show(0);
  setInterval(next, interval);
})();
