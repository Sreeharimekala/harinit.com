(() => {
  function init() {
    const course = window.HARINIT_COURSE;
    const courseLabel = course ? course.label : 'Microsoft Fabric';
    const courseSlug = course ? course.slug : 'microsoft-fabric';
    const moduleMatch = document.title.match(/Module\s+(\d+)/i);
    const moduleLabel = moduleMatch ? `Module ${moduleMatch[1]}` : courseLabel;
    const header = document.createElement('header');
    header.className = 'academy-global-header';
    header.innerHTML = '<a class="academy-global-brand" href="/" style="display:flex;align-items:center;gap:8px"><span style="position:relative;width:32px;height:32px;flex-shrink:0"><svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" style="width:100%;height:100%"><defs><linearGradient id="glg1" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#1A6FD4"/><stop offset="100%" style="stop-color:#00C48C"/></linearGradient><linearGradient id="glg2" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" style="stop-color:#00C48C"/><stop offset="100%" style="stop-color:#00E0A0"/></linearGradient></defs><path d="M18 10 L18 55 Q18 72 35 72 L42 72 L42 58 L35 58 Q32 58 32 55 L32 10 Z" fill="url(#glg1)"/><path d="M42 38 Q50 28 62 32 L62 72 L48 72 L48 46 Q46 40 42 38 Z" fill="url(#glg2)"/><circle cx="72" cy="32" r="5" fill="#00E0A0"/><circle cx="85" cy="24" r="4" fill="#00E0A0"/><circle cx="85" cy="40" r="4" fill="#00E0A0"/><line x1="72" y1="32" x2="81" y2="25" stroke="#00E0A0" stroke-width="2.5"/><line x1="72" y1="32" x2="81" y2="39" stroke="#00E0A0" stroke-width="2.5"/><line x1="62" y1="32" x2="67" y2="32" stroke="#00E0A0" stroke-width="2.5"/></svg></span><span>Harin<span>IT</span></span></a><nav class="academy-global-links" aria-label="HarinIT navigation"><a href="/">Home</a><a href="/platform.html">Platform</a><a href="/services.html">Services</a><a href="/academy/">Academy</a><a href="/about.html">About</a><a href="/contact.html">Contact</a></nav>';
    document.body.prepend(header);

    const sidebar = document.getElementById('sidebar');
    if (sidebar) {
      const back = document.createElement('a');
      back.className = 'academy-back-link';
      back.href = '/';
      back.textContent = '← Back to HarinIT';
      sidebar.prepend(back);
    }

    const main = document.querySelector('main');
    if (main) {
      const crumbs = document.createElement('nav');
      crumbs.className = 'academy-breadcrumbs';
      crumbs.setAttribute('aria-label', 'Breadcrumb');
      crumbs.innerHTML = `<a href="/">HarinIT</a><span>›</span><a href="/academy/">Academy</a><span>›</span><a href="/academy/${courseSlug}/">${courseLabel}</a><span>›</span><span aria-current="page">${moduleLabel}</span>`;
      main.prepend(crumbs);

      const lessons = [...main.querySelectorAll('.lesson[id]')];
      lessons.forEach((lesson, index) => {
        if (lesson.querySelector('.lesson-pagination')) return;
        const pagination = document.createElement('nav');
        pagination.className = 'lesson-pagination';
        pagination.setAttribute('aria-label', 'Lesson navigation');
        const links = [];
        if (index > 0) links.push(`<a href="#${lessons[index - 1].id}">← Previous Lesson</a>`);
        if (index < lessons.length - 1) links.push(`<a href="#${lessons[index + 1].id}">Next Lesson →</a>`);
        if (links.length) {
          pagination.innerHTML = links.join('');
          lesson.append(pagination);
        }
      });
    }

    const shell = document.querySelector('.shell');
    if (shell) {
      const footer = document.createElement('footer');
      footer.className = 'academy-lesson-footer';
      footer.innerHTML = '<div class="academy-lesson-footer-inner"><strong>HarinIT</strong><nav aria-label="Footer navigation"><a href="/">Home</a><a href="/platform.html">Platform</a><a href="/services.html">Services</a><a href="/academy/">Academy</a><a href="/about.html">About</a><a href="/contact.html">Contact</a></nav></div>';
      shell.insertAdjacentElement('afterend', footer);
    }
  }
  document.addEventListener('DOMContentLoaded', init);
})();
