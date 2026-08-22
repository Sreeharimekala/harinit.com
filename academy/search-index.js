window.HarinitFabricSearch = (() => {
  let index = null;
  let building = null;
  const course = () => window.HARINIT_FABRIC_COURSE;
  const clean = value => (value || '').replace(/\s+/g, ' ').trim();
  async function buildIndex() {
    if (index) return index;
    if (building) return building;
    building = (async () => {
    const entries = course().modules.map(module => ({ title: module.title, module, href: module.file, context: `Module ${module.number} — ${module.title}` }));
    const documents = await Promise.all(course().modules.map(async module => {
      try {
        const response = await fetch(module.file);
        if (!response.ok) return [];
        const doc = new DOMParser().parseFromString(await response.text(), 'text/html');
        return [...doc.querySelectorAll('.lesson[id], .chapter[id]')].map(section => {
          const heading = section.querySelector('h2, h1');
          const title = clean(heading && heading.textContent) || `Lesson ${section.id.replace(/\D/g, '')}`;
          const context = clean(section.querySelector('p') && section.querySelector('p').textContent).slice(0, 120);
          return { title, module, href: `${module.file}#${section.id}`, context: context || `Module ${module.number} — ${module.title}` };
        });
      } catch (_) { return []; }
    }));
    index = entries.concat(...documents);
    return index;
    })();
    return building;
  }
  function mount(target) {
    if (!target || target.dataset.searchMounted) return;
    target.dataset.searchMounted = 'true';
    target.innerHTML = '<label class="fabric-search-label" for="fabricSearch">Search Microsoft Fabric</label><input id="fabricSearch" class="fabric-search-input" type="search" autocomplete="off" placeholder="🔍 Search Microsoft Fabric..." aria-expanded="false"><div class="fabric-search-results" role="listbox" aria-label="Search results"></div>';
    const input = target.querySelector('input'); const results = target.querySelector('.fabric-search-results'); let matches = []; let selected = -1;
    const render = () => { results.innerHTML = matches.length ? matches.map((item, i) => `<a role="option" aria-selected="${i === selected}" class="fabric-search-result" href="${item.href}"><strong>${item.title}</strong><span>${item.context}</span><em>Open lesson →</em></a>`).join('') : `<p class="fabric-search-empty">No lessons found for: “${input.value}”</p>`; input.setAttribute('aria-expanded', 'true'); };
    input.addEventListener('input', async () => {
      const query = clean(input.value).toLowerCase(); selected = -1;
      if (!query) { results.innerHTML = ''; input.setAttribute('aria-expanded', 'false'); return; }
      results.innerHTML = '<p class="fabric-search-empty">Building lesson search index…</p>';
      const source = await buildIndex();
      matches = source.filter(item => `${item.title} ${item.module.title} ${item.context}`.toLowerCase().includes(query)).slice(0, 12); render();
    });
    input.addEventListener('keydown', event => { const options = [...results.querySelectorAll('a')]; if (event.key === 'Escape') { results.innerHTML = ''; input.value = ''; input.setAttribute('aria-expanded', 'false'); input.blur(); } if (event.key === 'ArrowDown' && options.length) { event.preventDefault(); selected = Math.min(selected + 1, options.length - 1); render(); } if (event.key === 'ArrowUp' && options.length) { event.preventDefault(); selected = Math.max(selected - 1, 0); render(); } if (event.key === 'Enter' && selected >= 0 && options[selected]) options[selected].click(); });
  }
  return { mount, buildIndex };
})();
