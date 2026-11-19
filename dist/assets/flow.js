(() => {
  'use strict';
  const filters = [...document.querySelectorAll('[data-resource-filter]')];
  filters.forEach(button => button.addEventListener('click', () => {
    filters.forEach(b => b.setAttribute('aria-pressed', String(b === button)));
    let count = 0;
    document.querySelectorAll('[data-resource-category]').forEach(card => {
      card.hidden = button.dataset.resourceFilter !== 'All' && card.dataset.resourceCategory !== button.dataset.resourceFilter;
      if (!card.hidden) count++;
    });
    document.querySelector('#resource-count').textContent = `${count} ${count === 1 ? 'workbook' : 'workbooks'}. Choose the one that fits.`;
  }));

  const sections = [...document.querySelectorAll('details.workbook-section')];
  const notes = [...document.querySelectorAll('.workbook-question textarea')];
  let printing = false;
  const syncProgress = () => {
    const count = notes.filter(n => n.value.trim()).length;
    const progress = document.querySelector('.workbook-progress progress');
    if (progress) {
      progress.value = count;
      document.querySelector('#answered-count').textContent = `${count} of ${notes.length}`;
    }
    sections.forEach(section => {
      const fields = [...section.querySelectorAll('textarea')];
      const complete = fields.every(f => f.value.trim());
      const nav = document.querySelector(`[data-section-link="${section.id}"]`);
      nav?.classList.toggle('completed', complete);
      nav?.classList.toggle('current', section.open);
      if (section.open) nav?.setAttribute('aria-current', 'step');
      else nav?.removeAttribute('aria-current');
    });
  };
  const showSection = (id, focus = false) => {
    const section = document.getElementById(id);
    if (!section?.matches('.workbook-section')) return;
    sections.forEach(s => { s.open = s === section; });
    syncProgress();
    if (focus) {
      section.querySelector('summary').focus({preventScroll:true});
      // Wait for closed sections to leave layout before scrolling.
      requestAnimationFrame(() => section.scrollIntoView({behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'instant' : 'smooth', block:'start'}));
    }
  };
  sections.forEach(section => {
    section.querySelector('summary').addEventListener('click', e => {
      e.preventDefault();
      if (section.open) { section.open = false; syncProgress(); }
      else showSection(section.id);
    });
    section.addEventListener('toggle', () => { if (!printing) syncProgress(); });
  });
  document.querySelectorAll('[data-section-link]').forEach(a => a.addEventListener('click', e => {
    e.preventDefault(); showSection(a.dataset.sectionLink, true);
    history.replaceState(null, '', `#${a.dataset.sectionLink}`);
  }));
  document.querySelectorAll('[data-next-section]').forEach(b => b.addEventListener('click', () => showSection(b.dataset.nextSection, true)));
  notes.forEach(n => n.addEventListener('input', () => {
    n.style.height = 'auto'; n.style.height = `${Math.max(78,n.scrollHeight)}px`; syncProgress();
  }));
  if (location.hash.startsWith('#section-')) showSection(location.hash.slice(1));
  syncProgress();

  let printState = [];
  const preparePrint = () => {
    if (printing || !sections.length) return;
    printing = true;
    printState = sections.map(s => s.open);
    sections.forEach(s => { s.open = true; });
    notes.forEach(n => {
      n.parentElement.querySelector('.print-answer').textContent = n.value || 'Notes: _______________________________________________________';
    });
  };
  const restorePrint = () => {
    if (!printing) return;
    sections.forEach((s,i) => { s.open = printState[i]; });
    printing = false;
    syncProgress();
  };
  window.addEventListener('beforeprint', preparePrint);
  window.addEventListener('afterprint', restorePrint);
  document.querySelectorAll('[data-print]').forEach(b => b.addEventListener('click', () => window.print()));
  document.querySelectorAll('[data-download-workbook]').forEach(b => b.addEventListener('click', () => {
    let text = `DIGIATOR | ${document.querySelector('h1').textContent}\n${'='.repeat(55)}\n\n`;
    const setup = document.querySelector('.before-start');
    if (setup) text += 'BEFORE YOU START\n' + [...setup.querySelectorAll('p')].map(p=>p.textContent).join('\n') + '\n\n';
    sections.forEach(s => {
      text += s.querySelector('h2').textContent+'\n\n';
      s.querySelectorAll('.workbook-question').forEach(q => {
        text += q.querySelector('label').textContent+'\n';
        const hint=q.querySelector('.question-hint'); if(hint) text += hint.textContent+'\n';
        text += (q.querySelector('textarea').value || '[Your notes]')+'\n\n';
      });
    });
    text += 'YOUR NEXT STEP\n'+document.querySelector('.keep-notes p').textContent+'\n\n';
    text += 'Digiator · Indore, India\ngrowth@digiator.com · +91 93431 17867\n';
    const url = URL.createObjectURL(new Blob([text], {type:'text/plain;charset=utf-8'}));
    const a = document.createElement('a'); a.href=url; a.download=b.dataset.downloadWorkbook+'.txt'; a.click();
    setTimeout(()=>URL.revokeObjectURL(url),1500);
    document.querySelector('#workbook-status').textContent = 'Downloaded. Your workbook includes all prompts and the notes you added.';
  }));
})();
