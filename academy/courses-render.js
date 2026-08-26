// Renders the course cards on the Academy landing page from the course
// data in courses-data.js (window.HARINIT_COURSES) into the empty
// #course-list container in academy/index.html.
//
// This produces the exact same markup/classes that used to be hand-coded
// per course directly in the HTML (see git history of academy/index.html
// prior to this change) -- it's a refactor of how the cards get built,
// not a visual or structural redesign.
(() => {
  const courses = window.HARINIT_COURSES;
  const host = document.getElementById('course-list');
  if (!Array.isArray(courses) || !host) return;

  courses.forEach((course, index) => {
    const article = document.createElement('article');
    article.className = 'course-card';
    // The original hand-coded markup only added this gap on cards after
    // the first one (the cards aren't in a grid, so spacing between them
    // is manual). Preserve that exactly for any number of courses.
    if (index > 0) article.style.marginTop = '1.5rem';
    if (course.accent) {
      if (course.accent.accent) article.style.setProperty('--accent', course.accent.accent);
      if (course.accent.accent2) article.style.setProperty('--accent2', course.accent.accent2);
    }

    const left = document.createElement('div');

    const eyebrow = document.createElement('span');
    eyebrow.className = 'eyebrow';
    eyebrow.textContent = course.badge;

    const title = document.createElement('h3');
    title.textContent = course.title;

    const subtitle = document.createElement('h4');
    subtitle.textContent = course.subtitle;

    const description = document.createElement('p');
    description.textContent = course.description;

    const link = document.createElement('a');
    link.className = 'button';
    link.href = course.button.href;
    link.append(document.createTextNode(course.button.label + ' '));
    const arrow = document.createElement('span');
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '→';
    link.append(arrow);

    left.append(eyebrow, title, subtitle, description, link);

    const info = document.createElement('div');
    info.className = 'course-info';
    info.setAttribute('aria-label', 'Course highlights');
    course.stats.forEach(stat => {
      const tile = document.createElement('div');
      tile.className = 'stat';
      const strong = document.createElement('strong');
      strong.textContent = stat.label;
      const sub = document.createElement('span');
      sub.textContent = stat.sub;
      tile.append(strong, sub);
      info.append(tile);
    });

    article.append(left, info);
    host.append(article);
  });
})();
