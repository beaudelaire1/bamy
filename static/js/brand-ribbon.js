document.addEventListener('DOMContentLoaded', () => {
  const ribbon = document.getElementById('brand-ribbon');
  if (!ribbon) return;

  const track = ribbon.querySelector('.brand-track');
  const clone = track.cloneNode(true);
  clone.classList.add('clone');
  ribbon.appendChild(clone);

  // Animation infinie
  let pos = 0;
  const speed = 0.5;

  function animate() {
    pos -= speed;
    if (pos <= -track.offsetWidth) pos = 0;
    track.style.transform = `translateX(${pos}px)`;
    clone.style.transform = `translateX(${pos + track.offsetWidth}px)`;
    requestAnimationFrame(animate);
  }

  animate();
});
