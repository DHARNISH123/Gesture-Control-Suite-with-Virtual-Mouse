document.addEventListener("DOMContentLoaded", function () {
  new Typed('.typing', {
    strings: ["Gesture-Control-Suite-with-Virtual-Mouse"],
    typeSpeed: 60,
    showCursor: true,
    cursorChar: "|",
    loop: false
  });

  const topBtn = document.getElementById("topBtn");
  window.onscroll = function () {
    topBtn.style.display = window.scrollY > 300 ? "block" : "none";
  };
  topBtn.onclick = () => window.scrollTo({ top: 0, behavior: "smooth" });
});
