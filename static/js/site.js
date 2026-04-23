document.addEventListener("DOMContentLoaded", () => {
  const body = document.body;
  if (window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
    body.classList.add("reduced-motion");
  }
});
