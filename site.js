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
