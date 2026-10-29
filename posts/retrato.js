/* Se o retrato não estiver em ../retratos/, o post cai na versão tipográfica. */
for (const img of document.querySelectorAll('.retrato img')) {
  const semRetrato = () => {
    img.closest('.post').classList.add('sem-retrato');
    img.remove();
  };
  if (img.complete && img.naturalWidth === 0) semRetrato();
  else img.addEventListener('error', semRetrato);
}
