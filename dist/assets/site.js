(() => {
  'use strict';
  const menu = document.querySelector('.menu-toggle');
  const nav = document.querySelector('#main-navigation');
  const closeMenu = () => { nav?.classList.remove('open'); menu?.setAttribute('aria-expanded','false'); };
  menu?.addEventListener('click', () => { const open = nav.classList.toggle('open'); menu.setAttribute('aria-expanded',String(open)); });
  document.addEventListener('keydown', e => { if(e.key === 'Escape') closeMenu(); });
  document.addEventListener('click', e => { if(!e.target.closest('.header')) closeMenu(); });
  nav?.querySelectorAll('a').forEach(a => a.addEventListener('click',closeMenu));
  const tabs = [...document.querySelectorAll('[role="tab"]')];
  const activateTab = tab => {
    if(tab.dataset.priority) document.dispatchEvent(new CustomEvent('prioritychange',{detail:tab.dataset.priority}));
    tabs.forEach(t => { const active = t === tab; t.setAttribute('aria-selected',String(active)); t.tabIndex = active ? 0 : -1; document.getElementById(t.getAttribute('aria-controls')).hidden = !active; });
  };
  tabs.forEach((tab,i) => {
    tab.addEventListener('click',()=>activateTab(tab));
    tab.addEventListener('keydown',e=>{ let next; if(e.key==='ArrowRight') next=(i+1)%tabs.length; if(e.key==='ArrowLeft') next=(i-1+tabs.length)%tabs.length; if(e.key==='Home') next=0; if(e.key==='End') next=tabs.length-1; if(next!==undefined){e.preventDefault();activateTab(tabs[next]);tabs[next].focus();} });
  });
  const search = document.querySelector('#industry-search');
  search?.addEventListener('input',()=>{
    const term=search.value.toLowerCase().trim(); let count=0;
    document.querySelectorAll('.industry-item').forEach(item=>{item.hidden=!item.textContent.toLowerCase().includes(term);if(!item.hidden)count++;});
    document.querySelector('#directory-count').textContent=`${count} ${count===1?'industry':'industries'}`;
    document.querySelector('#empty-industries').hidden=count!==0;
  });
})();
