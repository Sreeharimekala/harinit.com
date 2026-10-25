// Adapts the standalone Databricks chapter pages to the shared Academy
// scripts (academy.js / academy-navigation.js / search-index.js).
//
// Those scripts expect each lesson to be a `.lesson[id]` element. The
// chapter pages instead mark each lesson with an `<h2 id="sN-M">` followed
// by its content. This script wraps every such heading and the content
// after it (up to the next h2) in `<section class="lesson" id="sN-M">`,
// moving the id from the h2 to the section so existing links and the
// page's own table of contents keep working.
//
// Must be loaded with `defer` BEFORE academy-navigation.js and academy.js,
// so the wrapping is done before their DOMContentLoaded handlers run.
(() => {
  const containsH2 = node => node.nodeType === 1 && (node.tagName === 'H2' || node.querySelector('h2'));
  document.querySelectorAll('h2[id]').forEach(heading => {
    if (!/^s\d+-\d+$/.test(heading.id)) return;
    if (heading.closest('.lesson')) return;
    const section = document.createElement('section');
    section.className = 'lesson';
    section.id = heading.id;
    heading.removeAttribute('id');
    heading.parentNode.insertBefore(section, heading);
    let node = heading;
    while (node) {
      const next = node.nextSibling;
      section.appendChild(node);
      node = next;
      if (node && containsH2(node)) break;
      if (node && node.nodeType === 1 && node.matches('nav.pager, footer')) break;
    }
  });
})();
