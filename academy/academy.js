(() => {
  const course = window.HARINIT_COURSE;
  if (!course) return;
  const keyFor = (module, id) => `${module.file}#${id}`;
  const read = () => { try { const value = JSON.parse(localStorage.getItem(course.storageKey) || '{}'); return value && typeof value === 'object' ? value : {}; } catch (_) { return {}; } };
  const write = value => { try { localStorage.setItem(course.storageKey, JSON.stringify(value)); return true; } catch (_) { return false; } };
  const moduleForPage = () => course.modules.find(module => location.pathname.endsWith(module.file));
  const lessonIds = module => Array.from({ length: module.count }, (_, index) => `${module.prefix}${index + 1}`);
  const counts = (module, progress = read()) => { const total = module.count; const done = lessonIds(module).filter(id => progress[keyFor(module, id)]).length; return { total, done, percent: total ? Math.round(done / total * 100) : 0 }; };
  const overall = progress => course.modules.reduce((total, module) => { const value = counts(module, progress); total.done += value.done; total.total += value.total; return total; }, { done: 0, total: 0 });
  window.getNextIncompleteLesson = () => { const progress = read(); for (const module of course.modules) { const incomplete = lessonIds(module).find(id => !progress[keyFor(module, id)]); if (incomplete) return `${module.file}#${incomplete}`; } return null; };

  function updateButton(button, done) { button.classList.toggle('is-complete', done); button.textContent = done ? '✓ Completed — Mark Incomplete' : 'Mark Lesson Complete'; button.setAttribute('aria-pressed', String(done)); }
  const cleanTitle = section => (section.querySelector('h2, h1')?.textContent || 'Lesson').replace(/\s+/g, ' ').trim() || 'Lesson';
  const numberFor = section => document.querySelector(`#sidebar a[href="#${section.id}"] .nav-num`)?.textContent.trim() || '';

  function setupLessonPage() {
    const module = moduleForPage(); if (!module) return;
    const sections = [...document.querySelectorAll('.lesson[id], .chapter[id]')];
    sections.forEach((section, index) => {
      const id = section.id; const key = keyFor(module, id); const actions = document.createElement('div'); actions.className = 'lesson-completion';
      const button = document.createElement('button'); button.type = 'button'; button.className = 'lesson-completion-button'; updateButton(button, Boolean(read()[key]));
      button.addEventListener('click', () => { const progress = read(); if (progress[key]) delete progress[key]; else progress[key] = true; write(progress); updateButton(button, Boolean(progress[key])); updateSidebar(); }); actions.append(button); section.append(actions);
      const existing = section.querySelector('.lesson-pagination'); if (existing) existing.remove();
      const pagination = document.createElement('nav'); pagination.className = 'lesson-pagination'; pagination.setAttribute('aria-label', 'Lesson navigation');
      const links = [];
      if (index > 0) { const num = numberFor(sections[index - 1]); links.push(`<a href="#${sections[index - 1].id}">← Previous: ${num ? num + ' ' : ''}${cleanTitle(sections[index - 1])}</a>`); }
      else { const previousModule = course.modules[module.number - 2]; if (previousModule) links.push(`<a href="${previousModule.file}#${previousModule.prefix}${previousModule.count}">← Previous: Module ${previousModule.number} — ${previousModule.title}</a>`); }
      if (index < sections.length - 1) { const num = numberFor(sections[index + 1]); links.push(`<a href="#${sections[index + 1].id}">Next: ${num ? num + ' ' : ''}${cleanTitle(sections[index + 1])} →</a>`); }
      else { const nextModule = course.modules[module.number]; if (nextModule) links.push(`<a href="${nextModule.file}#${nextModule.prefix}1">Next: Module ${nextModule.number} — ${nextModule.title} →</a>`); }
      if (links.length) { pagination.innerHTML = links.join(''); section.append(pagination); }
    });
    function updateSidebar() {
      const progress = read(); const current = location.hash || `#${sections[0] && sections[0].id}`;
      document.querySelectorAll('#sidebar a[href^="#"]').forEach(link => {
        const id = link.getAttribute('href').slice(1); const complete = Boolean(progress[keyFor(module, id)]); const isCurrent = `#${id}` === current;
        link.classList.toggle('is-complete', complete); link.classList.toggle('is-current', isCurrent);
        link.dataset.progress = complete ? '✓' : (isCurrent ? '→' : '○');
        const state = complete ? 'Completed' : (isCurrent ? 'Current lesson' : 'Not completed');
        link.setAttribute('aria-label', `${state}: ${link.textContent.trim()}`);
        if (isCurrent) link.setAttribute('aria-current', 'true'); else link.removeAttribute('aria-current');
      });
    }
    window.addEventListener('hashchange', updateSidebar); updateSidebar();

    // Mobile: keep the toggle's aria-expanded state honest and close the
    // panel once a lesson is chosen so it never sits over half the screen.
    const navToggle = document.getElementById('navToggle'); const sidebarEl = document.getElementById('sidebar');
    if (navToggle && sidebarEl) {
      navToggle.setAttribute('aria-controls', 'sidebar');
      navToggle.setAttribute('aria-expanded', String(sidebarEl.classList.contains('open')));
      navToggle.addEventListener('click', () => navToggle.setAttribute('aria-expanded', String(sidebarEl.classList.contains('open'))));
      sidebarEl.querySelectorAll('.nav-link').forEach(link => link.addEventListener('click', () => {
        if (window.matchMedia('(max-width: 900px)').matches) { sidebarEl.classList.remove('open'); navToggle.setAttribute('aria-expanded', 'false'); }
      }));
    }

    const search = document.createElement('div'); search.className = 'fabric-search'; document.querySelector('main')?.prepend(search); window.HarinitFabricSearch?.mount(search);
  }

  function confirmReset(onConfirm) {
    const overlay = document.createElement('div'); overlay.className = 'reset-confirm-overlay';
    overlay.innerHTML = '<div class="reset-confirm-dialog" role="alertdialog" aria-modal="true" aria-labelledby="resetConfirmTitle" aria-describedby="resetConfirmBody"><h3 id="resetConfirmTitle">Reset all course progress?</h3><p id="resetConfirmBody">Are you sure you want to reset all course progress? This clears every completed lesson and cannot be undone.</p><div class="reset-confirm-actions"><button type="button" class="reset-confirm-cancel">Cancel</button><button type="button" class="reset-confirm-ok">Reset Progress</button></div></div>';
    document.body.append(overlay);
    const close = () => { overlay.remove(); document.removeEventListener('keydown', onKey); };
    function onKey(event) { if (event.key === 'Escape') close(); }
    overlay.addEventListener('click', event => { if (event.target === overlay) close(); });
    overlay.querySelector('.reset-confirm-cancel').addEventListener('click', close);
    overlay.querySelector('.reset-confirm-ok').addEventListener('click', () => { close(); onConfirm(); });
    document.addEventListener('keydown', onKey);
    overlay.querySelector('.reset-confirm-cancel').focus();
  }

  function setupDashboard() {
    const progress = read(); const total = overall(progress); const host = document.querySelector('#course-progress');
    const percent = total.total ? Math.round(total.done / total.total * 100) : 0;
    if (host) host.innerHTML = `<div class="progress-card"><div><span class="eyebrow">Course Progress</span><h2>Overall Progress</h2><p>${total.done} / ${total.total} Lessons Completed</p></div><div class="progress-meter" aria-label="${percent}% complete"><span style="width:${percent}%"></span></div><strong>${percent}%</strong><button class="reset-progress" type="button">Reset Progress</button></div>`;
    host?.querySelector('.reset-progress')?.addEventListener('click', () => { confirmReset(() => { try { localStorage.removeItem(course.storageKey); } catch (_) {} location.reload(); }); });
    document.querySelectorAll('.module-card').forEach(card => {
      const href = card.getAttribute('href') || ''; const module = course.modules.find(item => href.includes(item.file)); if (!module) return;
      const value = counts(module, progress); const status = value.done === 0 ? 'Not Started' : value.done === value.total ? '✓ Completed' : 'In Progress';
      const action = card.querySelector('span:last-of-type'); if (action) action.textContent = 'Continue →';
      const detail = document.createElement('div'); detail.className = 'module-progress';
      detail.dataset.status = value.done === 0 ? 'not-started' : value.done === value.total ? 'completed' : 'in-progress';
      detail.innerHTML = `<div class="mini-progress"><span style="width:${value.percent}%"></span></div><small>${value.done} / ${value.total} lessons · ${status}</small>`;
      card.append(detail);
    });
    const continueButton = document.querySelector('[data-continue-learning]'); if (continueButton) { const next = window.getNextIncompleteLesson(); continueButton.textContent = next ? 'Continue Learning →' : 'Course Completed ✓'; if (!next) { continueButton.removeAttribute('href'); continueButton.setAttribute('aria-disabled', 'true'); } else continueButton.href = next; }
    const search = document.querySelector('#fabric-search-host'); window.HarinitFabricSearch?.mount(search);
  }
  document.addEventListener('DOMContentLoaded', () => { if (moduleForPage()) setupLessonPage(); else if (document.querySelector('#course-progress')) setupDashboard(); });
})();
