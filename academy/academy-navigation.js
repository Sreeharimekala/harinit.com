(() => {
  function init() {
    const course = window.HARINIT_COURSE;
    const courseLabel = course ? course.label : 'Microsoft Fabric';
    const courseSlug = course ? course.slug : 'microsoft-fabric';
    const moduleMatch = document.title.match(/Module\s+(\d+)/i);
    const moduleLabel = moduleMatch ? `Module ${moduleMatch[1]}` : courseLabel;
    const header = document.createElement('header');
    header.className = 'academy-global-header';
    header.innerHTML = '<a class="academy-global-brand" href="/">Harin<span>IT</span></a><nav class="academy-global-links" aria-label="HarinIT navigation"><a href="/">Home</a><a href="/platform.html">Platform</a><a href="/services.html">Services</a><a href="/academy/">Academy</a><a href="/about.html">About</a><a href="/contact.html">Contact</a></nav>';
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
