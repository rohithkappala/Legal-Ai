// LegalAI - main.js

// Auto-dismiss flash messages
document.addEventListener('DOMContentLoaded', function () {
  const flashes = document.querySelectorAll('.flash');
  flashes.forEach(function (el) {
    setTimeout(function () {
      el.style.opacity = '0';
      el.style.transition = 'opacity 0.5s';
      setTimeout(function () { el.remove(); }, 500);
    }, 4000);
  });

  // Filter buttons (explore page)
  const filterBtns = document.querySelectorAll('.filter-btn');
  filterBtns.forEach(function (btn) {
    btn.addEventListener('click', function () {
      filterBtns.forEach(b => b.classList.remove('active'));
      this.classList.add('active');
    });
  });

  // Role selector highlight on register
  const roleOptions = document.querySelectorAll('.role-option input');
  roleOptions.forEach(function (input) {
    input.addEventListener('change', function () {
      document.querySelectorAll('.role-option-card').forEach(c => c.classList.remove('selected'));
      this.closest('.role-option').querySelector('.role-option-card').classList.add('selected');
    });
  });
});
