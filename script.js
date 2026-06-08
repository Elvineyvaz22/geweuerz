const buttons = document.querySelectorAll('.lang-btn');

function setLanguage(lang) {
  document.documentElement.lang = lang;

  document.querySelectorAll('[data-tr]').forEach((el) => {
    const value = lang === 'de' ? el.dataset.de : el.dataset.tr;
    if (value) el.textContent = value;
  });

  buttons.forEach(btn => btn.classList.toggle('active', btn.dataset.lang === lang));
  localStorage.setItem('siteLang', lang);
}

buttons.forEach(btn => {
  btn.addEventListener('click', () => setLanguage(btn.dataset.lang));
});

setLanguage(localStorage.getItem('siteLang') || 'tr');
document.getElementById('year').textContent = new Date().getFullYear();
