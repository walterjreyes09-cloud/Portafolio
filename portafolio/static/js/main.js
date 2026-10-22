// Menú móvil
const btn = document.querySelector('.menu-btn');
const nav = document.querySelector('.nav');
if (btn && nav) {
  btn.addEventListener('click', () => {
    const open = nav.classList.toggle('open');
    btn.setAttribute('aria-expanded', open);
  });
  nav.addEventListener('click', e => { if (e.target.tagName === 'A') nav.classList.remove('open'); });
}

// Visor de imágenes
const box = document.getElementById('lightbox');
if (box) {
  const img = box.querySelector('img');
  const cap = box.querySelector('p');
  document.querySelectorAll('[data-lightbox]').forEach(el => {
    el.addEventListener('click', () => {
      img.src = el.dataset.lightbox;
      img.alt = cap.textContent = el.dataset.caption || '';
      box.showModal();
    });
  });
  box.querySelector('.lb-close').addEventListener('click', () => box.close());
  box.addEventListener('click', e => { if (e.target === box) box.close(); });
}

// Confirmación al eliminar
document.querySelectorAll('form[data-confirm]').forEach(f => {
  f.addEventListener('submit', e => { if (!confirm(f.dataset.confirm)) e.preventDefault(); });
});
