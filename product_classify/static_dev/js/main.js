// Toggle mobile menu
document.querySelector('.nav-toggle').addEventListener('click', function() {
  this.classList.toggle('open');
  document.querySelector('.nav-menu').classList.toggle('open');
});

// Close mobile menu on link click
document.querySelectorAll('.nav-menu a').forEach(link => {
  link.addEventListener('click', () => {
    document.querySelector('.nav-toggle').classList.remove('open');
    document.querySelector('.nav-menu').classList.remove('open');
  });
});

// Toggle dropdown on mobile
document.querySelectorAll('.nav-dropdown > a').forEach(link => {
  link.addEventListener('click', function(e) {
    if (window.innerWidth <= 768) {
      e.preventDefault();
      this.parentElement.classList.toggle('open');
    }
  });
});