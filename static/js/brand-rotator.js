(function () {
  const root = document.getElementById("brand-rotator");
  if (!root) return;
  const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  const panels = Array.from(root.querySelectorAll(".rotor-panel"));
  if (panels.length <= 1 || reduce) { panels.forEach((p,i)=>p.classList.toggle("is-hidden",i!==0)); return; }

  const minInt = parseInt(root.getAttribute("data-interval-min") || "5000", 10);
  const maxInt = parseInt(root.getAttribute("data-interval-max") || "9000", 10);
  const durMs  = parseInt(root.getAttribute("data-duration") || "700", 10);

  let idx = 0, timer = null;
  panels.forEach((p,i)=>p.classList.toggle("is-hidden", i!==idx));

  const randDir = () => (Math.random() < 0.5 ? "left" : "right");
  const randLag = () => Math.floor(Math.random() * (maxInt - minInt + 1)) + minInt;

  function go(next, dir){
    const cur = panels[idx], inn = panels[next];
    cur.classList.remove("enter-from-left","enter-from-right");
    cur.classList.add(dir==="left"?"exit-to-left":"exit-to-right");

    inn.classList.remove("is-hidden","exit-to-left","exit-to-right");
    inn.classList.add(dir==="left"?"enter-from-right":"enter-from-left");

    setTimeout(()=> {
      cur.classList.add("is-hidden");
      cur.classList.remove("exit-to-left","exit-to-right");
      inn.classList.remove("enter-from-left","enter-from-right");
      idx = next;
      schedule();
    }, durMs);
  }

  function schedule(){
    clearTimeout(timer);
    timer = setTimeout(()=>{
      const d = randDir();
      const n = (idx + 1) % panels.length;
      go(n, d);
    }, randLag());
  }

  root.addEventListener("mouseenter", ()=> clearTimeout(timer));
  root.addEventListener("mouseleave", schedule);

  schedule();
})();
