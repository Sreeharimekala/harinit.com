// Single source of truth for the course cards on the HarinIT Academy
// landing page (academy/index.html). Rendered by courses-render.js.
//
// This is deliberately separate from fabric-course-data.js /
// ai-ml-course-data.js: those files hold per-module lesson-progress data
// for a single course's own dashboard/lesson pages (module file names,
// lesson counts, localStorage keys) and are consumed by academy.js on the
// per-course pages. This file holds per-course *summary* data for the
// Academy hub card grid — a different shape for a different page — so it
// stays a separate list rather than being bolted onto that structure.
//
// To add a new course: copy the EXAMPLE block at the bottom into this
// array, fill in your values, and it will appear on the Academy landing
// page automatically — no HTML edits required.
window.HARINIT_COURSES = [
  {
    id: 'microsoft-fabric',
    badge: 'Microsoft Fabric',
    title: 'Microsoft Fabric',
    subtitle: 'Data Engineering',
    description: 'Build practical data engineering skills across Microsoft Fabric, from foundational concepts to end-to-end projects.',
    stats: [
      { label: '12 Modules', sub: 'A clear learning path' },
      { label: '100+ Lessons', sub: 'Focused practical learning' },
      { label: 'Hands-on Learning', sub: 'Build as you learn' },
      { label: 'End-to-End Projects', sub: 'Apply your knowledge' }
    ],
    button: { label: 'Explore Microsoft Fabric', href: 'microsoft-fabric/' }
    // No accent override -> uses the default --accent/--accent2 palette
    // already defined in academy.css (:root).
  },
  {
    id: 'ai-ml',
    badge: 'AI & ML',
    title: 'AI & ML',
    subtitle: 'Artificial Intelligence & Machine Learning',
    description: 'Learn Python, SQL, Mathematics, Data Structures, Statistics, Data Analysis, Machine Learning, Deep Learning, NLP, MLOps, Generative AI, LLMs, and real-world AI/ML projects.',
    stats: [
      { label: '12 Modules', sub: 'Beginner → Advanced' },
      { label: '270 Lessons', sub: 'Focused practical learning' },
      { label: 'Hands-on Learning', sub: 'Build as you learn' },
      { label: 'Capstone Projects', sub: 'Apply your knowledge' }
    ],
    button: { label: 'Explore AI & ML', href: 'ai-ml/' }
  }

  // -------------------------------------------------------------------
  // EXAMPLE — copy this block (uncomment it), add a comma after the
  // course above it, fill in your own values, and you're done. This is
  // the exact shape every course entry follows.
  // -------------------------------------------------------------------
  // ,{
  //   id: 'your-course-slug',            // internal id, not shown anywhere
  //   badge: 'Your Badge Label',          // small eyebrow tag above the title
  //   title: 'Course Title',              // large heading (h3)
  //   subtitle: 'Course Subtitle',        // accent-colored subheading (h4)
  //   description: 'One or two sentences describing what this course teaches.',
  //   stats: [                            // exactly 4 stat tiles, in order
  //     { label: '12 Modules', sub: 'A clear learning path' },
  //     { label: '100+ Lessons', sub: 'Focused practical learning' },
  //     { label: 'Hands-on Learning', sub: 'Build as you learn' },
  //     { label: 'End-to-End Projects', sub: 'Apply your knowledge' }
  //   ],
  //   button: { label: 'Explore Your Course', href: 'your-course-folder/' },
  //   accent: { accent: '#5eb1ff', accent2: '#8b7cf6' } // optional; omit to
  //     // use the default palette above. When set, only overrides the
  //     // --accent/--accent2 custom properties for this card (its eyebrow,
  //     // subtitle, and glow accent), leaving every other card and the
  //     // rest of the page untouched.
  // }
];
