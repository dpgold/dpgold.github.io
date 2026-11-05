// Publication theme filter + sort; op-ed outlet filter + title search.
(function () {
  const list = document.getElementById('publist');
  const chips = document.querySelectorAll('.chip');
  const sort = document.getElementById('pubsort');
  chips.forEach(c => c.addEventListener('click', () => {
    chips.forEach(x => x.classList.toggle('on', x === c));
    const f = c.dataset.f;
    list.querySelectorAll('.pub').forEach(li => li.classList.toggle('hidden', f !== 'all' && li.dataset.theme !== f));
  }));
  sort.addEventListener('change', () => {
    const k = sort.value;
    [...list.children]
      .sort((a, b) => (+b.dataset[k] - +a.dataset[k]) || (+b.dataset.year - +a.dataset.year))
      .forEach(li => list.appendChild(li));
  });

  const outlet = document.getElementById('outlet');
  const q = document.getElementById('oq');
  function filterOpeds() {
    const o = outlet.value, s = q.value.trim().toLowerCase();
    document.querySelectorAll('#opeds .year').forEach(y => {
      let any = false;
      y.querySelectorAll('li').forEach(li => {
        const ok = (!o || li.dataset.outlet === o) && (!s || li.textContent.toLowerCase().includes(s));
        li.classList.toggle('hidden', !ok);
        any = any || ok;
      });
      y.classList.toggle('hidden', !any);
    });
  }
  outlet.addEventListener('change', filterOpeds);
  q.addEventListener('input', filterOpeds);
})();

// Tabs: show one section at a time, keyed by the URL hash; highlight its nav link.
(function () {
  const links = [...document.querySelectorAll('nav.top .links a')];
  const ids = links.map(a => a.getAttribute('href').slice(1));
  function show() {
    const id = ids.includes(location.hash.slice(1)) ? location.hash.slice(1) : 'about';
    document.body.classList.add('tabbed');
    document.body.dataset.tab = id;
    document.querySelectorAll('main > section').forEach(s => s.classList.toggle('active', s.id === id));
    links.forEach(a => {
      const on = a.getAttribute('href') === '#' + id;
      a.classList.toggle('active', on);
      if (on) { a.setAttribute('aria-current', 'page'); a.scrollIntoView({ block: 'nearest', inline: 'nearest' }); }
      else a.removeAttribute('aria-current');
    });
    window.scrollTo(0, 0);
  }
  window.addEventListener('hashchange', show);
  show();
})();

// Personal fees: keep "None in the last N months" current between rebuilds.
document.querySelectorAll('.recent[data-end]').forEach(p => {
  const d = new Date(p.dataset.end + 'T00:00:00'), t = new Date();
  const m = (t.getFullYear() - d.getFullYear()) * 12 + t.getMonth() - d.getMonth() - (t.getDate() < d.getDate() ? 1 : 0);
  if (m > 0) p.innerHTML = '<strong>None in the last ' + m + ' months.</strong>';
});
