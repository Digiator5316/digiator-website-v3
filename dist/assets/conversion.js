(() => {
  'use strict';
  const form = document.querySelector('#consultation-form');
  if (!form) return;
  const need = form.elements.need;
  document.addEventListener('prioritychange', e => {
    if ([...need.options].some(o => o.value === e.detail)) need.value = e.detail;
  });
  const params = new URLSearchParams(location.search);
  if (params.has('need') && [...need.options].some(o => o.value === params.get('need'))) need.value = params.get('need');
  const contact = form.elements.contact;
  contact.addEventListener('input', () => contact.setCustomValidity(''));
  const valid = () => {
    const value = contact.value.trim();
    const email = /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value);
    const phone = /^[+()\d\s.-]+$/.test(value) && value.replace(/\D/g,'').length >= 8 && value.replace(/\D/g,'').length <= 15;
    contact.setCustomValidity(email || phone ? '' : 'Enter an email address or a phone number, including its country code.');
    return form.reportValidity();
  };
  const enquiryText = () => {
    const d = new FormData(form);
    let message = `Hello Digiator, I'd like to request a free consultation.\n\nName: ${d.get('name')}\nBusiness: ${d.get('company')}\nContact: ${d.get('contact')}\nStarting point: ${d.get('need')}\n\n${d.get('message')}\n\nEnquiry from: ${d.get('page') || 'Digiator website'}`;
    // Campaign context travels with an explicitly sent enquiry; it is not stored or transmitted on page view.
    const campaign = ['utm_source','utm_medium','utm_campaign'].filter(key => params.has(key));
    if (campaign.length) message += '\n'+campaign.map(key=>`${key}: ${params.get(key).slice(0,200)}`).join('\n');
    return message;
  };
  const compose = channel => {
    if (!valid()) return;
    const a = document.createElement('a');
    if (channel === 'WhatsApp') {
      a.href = 'https://wa.me/919343117867?text='+encodeURIComponent(enquiryText());
      a.target = '_blank'; a.rel = 'noopener noreferrer';
    } else {
      a.href = 'mailto:growth@digiator.com?subject='+encodeURIComponent('Project enquiry — '+form.elements.company.value)+'&body='+encodeURIComponent(enquiryText());
    }
    a.click();
    document.querySelector('#enquiry-status').textContent = `Your message is ready in ${channel === 'WhatsApp' ? 'WhatsApp' : 'your email app'}. Complete the send there to share it with Digiator. This page has not sent or stored your enquiry.`;
  };
  form.addEventListener('submit', e => { e.preventDefault(); compose('WhatsApp'); });
  document.querySelector('#email-enquiry')?.addEventListener('click', () => compose('email'));
})();
