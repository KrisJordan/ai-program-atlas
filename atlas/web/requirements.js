/* Reveal the exact target and its ancestors; keep other branches collapsed. */
(() => {
  const reveal = () => {
    let target;
    try { target = document.getElementById(decodeURIComponent(location.hash.slice(1))); } catch { return; }
    if (!target) return;
    for (let node = target; node; node = node.parentElement) {
      if (node.tagName === 'DETAILS') node.open = true;
    }
    const own = target.querySelector(':scope > details.requirement-disclosure, :scope > details.requirement-bundle-disclosure');
    if (own) own.open = true;
    requestAnimationFrame(() => target.scrollIntoView({block:'start'}));
  };
  window.addEventListener('hashchange', reveal);
  reveal();
})();
