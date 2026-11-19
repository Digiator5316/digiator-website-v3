#!/usr/bin/env python3
"""Dependency-free static build. Run: python3 build.py. Source lives beside this file."""
from pathlib import Path
import json, html, re, os, shutil
from urllib.parse import urlsplit
from flow_content import resource_views
from conversion_content import render_home, render_consultation, render_about, lead_section, industry_answers

ROOT=Path(__file__).resolve().parent
DIST=ROOT/'dist'
ORIGIN=os.environ.get('SITE_ORIGIN', 'http://localhost:8352').rstrip('/')
SERVICES=json.loads((ROOT/'services.json').read_text())
INDUSTRIES=json.loads((ROOT/'industries.json').read_text())
CASES=json.loads((ROOT/'cases.json').read_text())
RESOURCES=json.loads((ROOT/'resources.json').read_text())
PAGES=[]
E=lambda x:html.escape(str(x),quote=True)
ARROW='<span class="arrow" aria-hidden="true">↗</span>'
WA='https://wa.me/919343117867'

def link(url,label,cls='line-link'):
    return f'<a class="{cls}" href="{E(url)}">{E(label)}{ARROW}</a>'

def logo(large=False):
    return f'<span class="brand-mark {"emblem" if large else ""}"><img src="/assets/digiator-original.jpg" alt="Digiator — original robot mark and wordmark" width="576" height="576" {"fetchpriority=high" if large else ""}></span>'

def header(active=''):
    items=[('services','Capabilities','/services/'),('industries','Industries','/industries/'),('case-studies','Selected work','/case-studies/'),('about','About','/about/'),('resources','Resources','/resources/')]
    nav=''.join(f'<a href="{url}" class="{"active" if key==active else ""}" {"aria-current=page" if key==active else ""}>{name}</a>' for key,name,url in items)
    return f'''<a href="#main" class="skip">Skip to content</a><header class="header"><div class="wrap nav"><a href="/" class="brand" aria-label="Digiator home">{logo()}<span class="brand-word">Your digital<br>launchpad.</span></a><nav id="main-navigation" class="nav-links" aria-label="Main navigation">{nav}</nav>{link('/consultation/','Let’s talk','btn dark')}<button class="menu-toggle" aria-expanded="false" aria-controls="main-navigation">Menu</button></div></header>'''

def footer():
    cols=[('Explore',[('Capabilities','/services/'),('Industries','/industries/'),('Selected work','/case-studies/'),('About Digiator','/about/')]),('Useful things',[('Workbooks & guides','/resources/'),('Questions & answers','/faq/'),('Start a conversation','/consultation/'),('Contact','/contact/')]),('Say hello',[('growth@digiator.com','mailto:growth@digiator.com'),('+91 93431 17867',WA),('Client support','mailto:operations@digiator.com')])]
    columns=''.join('<div><h3>'+name+'</h3>'+''.join(f'<a href="{url}">{label}</a>' for label,url in items)+'</div>' for name,items in cols)
    return f'''<footer class="footer"><div class="wrap"><div class="footer-top"><div><a href="/" aria-label="Digiator home">{logo()}</a><div class="footer-tag">Your next chapter, built.</div><p>Growth, creative and technology.<br>Based in Indore. Working across India.</p></div>{columns}</div><div class="footer-bottom"><span>© 2026 Digiator. Your Digital Launchpad.</span><div><a href="/privacy/">Privacy</a><a href="/cookies/">Cookies</a><a href="/terms/">Terms</a><span>Indore, Madhya Pradesh</span></div></div></div></footer><a class="whatsapp" href="{WA}" target="_blank" rel="noopener noreferrer" aria-label="Chat with Digiator on WhatsApp"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" aria-hidden="true"><path d="M20.5 11.5a8.5 8.5 0 0 1-12.7 7.4L3 20l1.2-4.5a8.5 8.5 0 1 1 16.3-4Z"/><path d="M8.2 7.5c-.5 1.8 1.8 5.7 4.8 7.2 1.5.7 2.5.2 3-.8l-2.3-1.4-1 .9c-1.4-.6-2.4-1.7-3-3.1l.8-1.1-1.2-2Z"/></svg></a>'''

def cta(title='What would you like to build next?',sub='Bring an ambition, a specific project, or a question worth exploring.'):
    return f'<section class="cta-band"><div class="wrap"><div><h2>{E(title)}</h2><p>{E(sub)} A 20–30 minute conversation with a co-founder.</p></div>{link("/consultation/","Request a Free Consultation","btn dark")}</div></section>'

def page(path,title,description,body,active='',include_cta=True,kind='WebPage'):
    route='/'+path.strip('/')+'/' if path else '/'
    if include_cta:
        body=re.sub(r'href="/consultation/(?:\?[^"]*)?"', 'href="#start"', body)
    data={'@context':'https://schema.org','@type':kind,'name':title,'description':description,'url':ORIGIN+route,'publisher':{'@type':'Organization','name':'Digiator','url':ORIGIN,'logo':ORIGIN+'/assets/digiator-original.jpg'}}
    out=f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{E(title)} | Digiator</title><meta name="description" content="{E(description)}"><meta name="theme-color" content="#102b3b"><meta name="robots" content="noindex,nofollow"><link rel="canonical" href="{ORIGIN+route}"><meta property="og:title" content="{E(title)} | Digiator"><meta property="og:description" content="{E(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{ORIGIN+route}"><meta property="og:image" content="{ORIGIN}/assets/digiator-original.jpg"><link rel="icon" type="image/jpeg" href="/assets/digiator-original.jpg"><link rel="stylesheet" href="/assets/site.css"><link rel="stylesheet" href="/assets/flow.css"><link rel="stylesheet" href="/assets/conversion.css"><script type="application/ld+json">{json.dumps(data).replace('</','<\\/')}</script><script defer src="/assets/site.js"></script><script defer src="/assets/flow.js"></script><script defer src="/assets/conversion.js"></script></head><body data-page="{E(active or path or 'home')}">{header(active)}<main id="main">{body}{lead_section(path,title) if include_cta else ''}</main>{footer()}</body></html>'''
    target=DIST/path/'index.html';target.parent.mkdir(parents=True,exist_ok=True);target.write_text(out)
    PAGES.append({'path':route,'title':title,'description':description})

def pagehero(eyebrow,title,summary,crumbs=(),actions=True,cls=''):
    trail='<a href="/">Home</a>'+''.join(' / '+(f'<a href="{url}">{E(label)}</a>' if url else f'<span>{E(label)}</span>') for label,url in crumbs)
    return f'<section class="page-hero {cls}"><div class="wrap"><div class="breadcrumbs" aria-label="Breadcrumb">{trail}</div><div class="eyebrow">{E(eyebrow)}</div><h1>{E(title)}</h1><p class="lead">{E(summary)}</p>{("<div class=actions>"+link("/consultation/","Request a Free Consultation","btn dark")+link("/case-studies/","Explore the work")+"</div>") if actions else ""}</div></section>'

def flow(kind):
    configs={
      'production':('PRODUCTION / WORKFLOW','One process. Clear responsibilities.',[('Production entry','Capture the shift and calculation inputs'),('Manager review','Review the rules and exceptions'),('HR approval','Use the approved incentive figures')]),
      'healthcare':('PATIENT JOURNEY','From first enquiry to appointment.',[('Relevant enquiry','A message that answers the real question'),('Front-desk follow-up','A clear next step and an assigned owner'),('Appointment outcome','Track what happened after the enquiry')]),
      'brand':('BRAND / EXPERIENCE','Make the value easy to recognise.',[('A clear proposition','Who it is for and why it matters'),('A coherent presence','Identity, website and sales material'),('A considered next step','Help the right visitor start a conversation')]),
      'construction':('PROJECT / ENQUIRY','Context before the conversation.',[('Plot-owner interest','Reach the relevant audience'),('Project context','Understand plot size and the requirement'),('A useful first call','Discuss the right next step')]),
      'property':('PROPERTY / JOURNEY','A coherent path to the site visit.',[('Discover the property','An offer that earns consideration'),('Understand the opportunity','Clear information on a credible website'),('Enquire about a visit','A specific next step for the buyer')]),
      'wellness':('CONCEPT / EXPERIENCE','Make an unfamiliar offer clear.',[('Understand the concept','Explain the experience in human terms'),('Picture the stay','Express the offering through the website'),('Start the conversation','Guide the guest to a relevant enquiry')]),
      'reputation':('CLINIC / JOURNEY','Look beyond the initial enquiry.',[('Interest in the clinic','An enquiry arrives'),('Confidence in the choice','The prospective patient checks the clinic'),('A real-world visit','Review the journey through to arrival')])}
    code,title,steps=configs.get(kind,configs['production'])
    rows=''.join(f'<div class="flow-step"><b>{i:02}</b><div><strong>{a}</strong><small>{b}</small></div></div>' for i,(a,b) in enumerate(steps,1))
    return f'<div class="flow-window"><div class="window-top"><span>{code}</span><span class="window-dots"><i></i><i></i><i></i></span></div><div class="flow-title">{title}</div>{rows}<div class="demo-label">Illustrative workflow · not a client interface</div></div>'

def visual():
    return f'<div class="visual" aria-label="Digiator connects growth, brand and technology"><div class="visual-grid"></div><div class="orbital"></div><span class="orbit-label">Built around your next move</span>{logo(True)}<div class="float-label fl-one"><span class="mini-icon" aria-hidden="true">↗</span><div><small>01 / Growth</small>Reach the right people.</div></div><div class="float-label fl-two"><span class="mini-icon" aria-hidden="true">◇</span><div><small>02 / Brand & experience</small>Make your value visible.</div></div><div class="float-label fl-three"><span class="mini-icon" aria-hidden="true">⌘</span><div><small>03 / Technology</small>Build the way forward.</div></div><span class="visual-caption">STRATEGY → DESIGN → DELIVERY</span></div>'

def workcard(c):
    if c['slug']=='healthcare-growth':
        art='<div class="metric-stages"><div><small>01 / INTEREST</small><strong>670</strong><span>Enquiries</span></div><b aria-hidden="true">→</b><div><small>02 / APPOINTMENT</small><strong>45</strong><span>Appointments</span></div><b aria-hidden="true">→</b><div><small>03 / PATIENT</small><strong>16</strong><span>Patients</span></div></div><span class="chart-note">FIVE-CITY CAMPAIGN · DISTINCT STAGES, ONE JOURNEY</span>'
    else:art=flow(c['diagram'])
    return f'<a class="work-card" href="/case-studies/{c["slug"]}/"><div class="work-art {"healthcare" if c["slug"]=="healthcare-growth" else ""}">{art}</div><div class="work-copy"><div class="work-meta"><span>{E(c["sector"])}</span><span>Case study ↗</span></div><h3>{E(c["title"])}</h3><p>{E(c["summary"])}</p><div class="work-stat"><strong>{E(c["metric"])}</strong><span>{E(c["metricLabel"])}</span></div></div></a>'

def home():
    render_home(globals())


def method_html(items):
    return '<div class="method-grid">'+''.join(f'<div class="method-item"><div class="method-num">{E(num)}</div><h3>{E(title)}</h3><p>{E(body)}</p></div>' for title,body,num in items)+'</div>'

def faq_html(items):
    return '<div class="faq">'+''.join(f'<details><summary>{E(q)}</summary><p>{E(a)}</p></details>' for q,a in items)+'</div>'

def services():
    content=pagehero('Capabilities','What do you need your business to do next?','A stronger presence, better customer conversations or a more dependable way to work. Start with a capability you know—or bring the objective and we’ll shape the brief.',[('Capabilities','')])
    rows=''.join(f'<a class="service-row" href="/services/{s["slug"]}/"><span class="number">0{i+1}</span><div><h3>{E(s["name"])}</h3><p>{E(s["summary"])}</p></div>{ARROW}</a>' for i,s in enumerate(SERVICES))
    content+=f'<section class="section"><div class="wrap page-layout"><aside class="side-note"><h3>Seven connected capabilities</h3><p>Choose the part you need. We connect the disciplines when the project calls for it.</p></aside><div>{rows}</div></div></section>'
    page('services','Capabilities', 'Explore Digiator’s seven capabilities, from strategy and campaigns to websites, automation and custom software.',content,'services')
    for s in SERVICES:
        content=pagehero(s['name'],s['headline'],s['summary'],[('Capabilities','/services/'),(s['name'],'')])
        content+='<nav class="page-jump wrap" aria-label="On this page"><a href="#what-you-get">What you get</a><a href="#how-we-work">How we work</a><a href="#useful-answers">Useful answers</a></nav>'
        fit=''.join(f'<li>{E(x)}</li>' for x in s['fit'])
        deliver=''.join(f'<div class="deliverable"><span class="number">0{i+1}</span><div><h3>{E(a)}</h3><p>{E(b)}</p></div></div>' for i,(a,b) in enumerate(s['deliverables']))
        content+=f'<section class="section"><div class="wrap page-layout"><aside class="side-note"><h3>Useful when you need</h3><ul>{fit}</ul></aside><div class="body-copy"><h2 id="what-you-get">{E(s["introTitle"])}</h2><p>{E(s["intro"])}</p><div class="deliverables">{deliver}</div><div class="proof-note"><div class="eyebrow">Relevant experience</div><p>{E(s["proof"])}</p>{link("/case-studies/"+s["proofSlug"]+"/","Explore the related work")}</div></div></div></section>'
        content+='<section class="section work-section"><div class="wrap"><div class="section-head"><h2 id="how-we-work">How we turn the brief into work.</h2></div>'+method_html([(title,step,f'0{i+1} / THE PROCESS') for i,(title,step) in enumerate(zip(s['stepLabels'],s['steps']))])+'</div></section>'
        content+='<section class="section"><div class="wrap"><div class="section-head"><h2 id="useful-answers">A few useful answers.</h2></div>'+faq_html(s['faq'])+'</div></section>'
        page('services/'+s['slug'],s['name'],s['summary'],content,'services')

def industries():
    content=pagehero('Industries','Your customers have their own reasons to choose.','Your team has its own way of working. Explore how we can shape the presence, customer journey and technology around both.',[('Industries','')],False)
    items=''.join(f'<a class="industry-item" href="/industries/{x["slug"]}/"><span class="number">{i+1:02}</span><div><h3>{E(x["name"])}</h3><p>{E(x["summary"])}</p></div>{ARROW}</a>' for i,x in enumerate(INDUSTRIES))
    content+=f'<section class="section"><div class="wrap"><div class="directory-toolbar"><label class="sr-label" for="industry-search">Find your industry</label><input id="industry-search" class="search-field" type="search" placeholder="Search healthcare, manufacturing, education…"><span class="directory-count" id="directory-count" aria-live="polite">20 industries</span></div><div class="industry-directory">{items}</div><p id="empty-industries" class="empty-state" hidden>No matching industry. Try a broader term, or <a href="/consultation/">tell us about your business</a>.</p></div></section>'
    page('industries','Industries', 'Growth, websites and operational technology shaped around 20 business sectors.',content,'industries')
    for x in INDUSTRIES:
        content=pagehero(x['eyebrow'],x['headline'],x['summary'],[('Industries','/industries/'),(x['name'],'')])
        answer=industry_answers()[x['slug']]
        content+=f'<section class="section reader-insight"><div class="wrap insight-layout"><div class="eyebrow">For {E(x["buyer"])}</div><div><h2>{E(answer["readerQuestion"])}</h2><p>{E(answer["answer"])}</p></div></div></section>'
        tracks=''
        for i,t in enumerate(x['tracks']):
            tracks+=f'<div class="deliverable"><span class="number">0{i+1}</span><div><h3>{E(t["title"])}</h3><p>{E(t["body"])}</p><ul>'+''.join(f'<li>{E(d)}</li>' for d in t['deliverables'])+'</ul></div></div>'
        prooflink=link('/case-studies/'+x['proofSlug']+'/','See the relevant work') if x['proofSlug'] else link('/services/','Explore our capabilities')
        content+=f'<section class="section"><div class="wrap page-layout"><aside class="side-note"><h3>Where we can help</h3><p>The work below can be scoped around your objective. Relevant delivered experience is identified alongside it.</p></aside><div class="body-copy"><h2>What that could involve.</h2><div class="deliverables">{tracks}</div><div class="proof-note"><div class="eyebrow">Experience & scope</div><p>{E(x["proof"])}</p>{prooflink}</div><h2 style="margin-top:50px">What would we look at first?</h2><p>{E(x["firstStep"])}</p><div class="actions">{link('/consultation/?industry='+x['slug'], 'Discuss your project','btn dark')}</div></div></div></section>'
        page('industries/'+x['slug'],x['name'],x['summary'],content,'industries')

CASE_HEADINGS={
 'manufacturing-pims':[('The situation.','One calculation. Several departments to reconcile.'),('The decision that mattered.','Put the rules and approval responsibilities into the system.'),('What the work involved.','Six modules. A five-level approval workflow.'),('The result, in context.','A working platform—and an estimate of capacity released.'),('A lesson worth taking forward.','The process is part of the product.')],
 'healthcare-growth':[('The situation.','An enquiry count could not describe the whole journey.'),('The decision that mattered.','Keep appointments and patient outcomes visible.'),('What the work involved.','Connect the campaign to what happened at the clinic.'),('The result, in context.','670 enquiries. 45 appointments. 16 patients.'),('A lesson worth taking forward.','Measure the decision after the enquiry.')],
 'construction-leadgen':[('The situation.','Reach people planning a construction project.'),('The decision that mattered.','Make the plot part of the first conversation.'),('What the work involved.','Give the campaign a specific project context.'),('The result, in context.','About 400 enquiries, at around ₹60 each.'),('A lesson worth taking forward.','A useful enquiry starts with a relevant question.')],
 'real-estate-sitevisit':[('The situation.','A property needs to be understood before it is visited.'),('The decision that mattered.','Give the identity, website and campaign the same direction.'),('What the work involved.','Build the path toward a site-visit enquiry.'),('The result, in context.','A connected brand and digital journey.'),('A lesson worth taking forward.','Design for the decision a buyer can make next.')],
 'wellness-growth':[('The situation.','Help guests picture an unfamiliar experience.'),('The decision that mattered.','Make the concept understandable before promoting it.'),('What the work involved.','Bring the offer to life through brand and website.'),('The result, in context.','₹2 lakh+ in reported business within one month.'),('A lesson worth taking forward.','Clarity is part of making an experience desirable.')],
 'clinic-reputation-recovery':[('The situation.','Interest in the clinic was not becoming enough visits.'),('The decision that mattered.','Investigate confidence in the clinic after the enquiry.'),('What the work involved.','Address the reputation and the path to a visit.'),('The result, in context.','Recovery began in 15–21 days.'),('A lesson worth taking forward.','Look at what a prospective patient checks next.')],
}

def cases():
    content=pagehero('Selected work','See the decisions behind the results.','What needed to change, what we built, and what happened next. Six engagements with the context behind the reported results.',[('Selected work','')],False)
    content+='<section class="section"><div class="wrap work-grid">'+''.join(workcard(c) for c in CASES)+'</div></section>'
    page('case-studies','Selected work', 'Explore six Digiator case studies in manufacturing software, healthcare, construction, property and wellness.',content,'case-studies')
    for c in CASES:
        content=pagehero(c['sector']+' / Case study',c['title'],c['summary'],[('Selected work','/case-studies/'),(c['sector'],'')],False,'case-hero')
        stats=f'<div class="case-stats"><strong>{E(c["metric"])}</strong><span>{E(c["metricLabel"])}</span><small>{E(c["secondary"])}</small></div>'
        content=content.replace('</div></section>',stats+'</div></section>')
        serv=''.join(f'<li>{E(s)}</li>' for s in c['services'])
        work=''.join(f'<li>{E(s)}</li>' for s in c['work'])
        additional=''
        if c['slug']=='healthcare-growth':
            additional='<div class="proof-note"><div class="eyebrow">Further healthcare experience</div><h3>A five-month digital restructuring result.</h3><p>Digiator’s owner also confirms approximately ₹15 lakh in revenue generated or influenced by approximately ₹3.5 lakh invested in a healthcare business’s digital presence and acquisition system over five months.</p><p>This is a separately reported whole-system result, not an ad-only return. It is presented independently of the five-city campaign figures above.</p></div>'
        content+=f'<section class="section"><div class="wrap page-layout"><aside class="side-note"><h3>Capabilities involved</h3><ul>{serv}</ul></aside><article class="body-copy case-body"><h2>The situation.</h2><p>{E(c["challenge"])}</p><h2>The decision that mattered.</h2><p>{E(c["judgement"])}</p><div style="margin:35px 0">{flow(c["diagram"])}</div><h2>What the work involved.</h2><ul class="text-list">{work}</ul><h2>The result, in context.</h2><p>{E(c["result"])}</p><p class="case-note">{E(c["note"])}</p>{additional}<h2>A lesson worth taking forward.</h2><blockquote>{E(c["lesson"])}</blockquote>{link("/case-studies/","Explore the other case studies")}</article></div></section>'
        for old,new in CASE_HEADINGS.get(c['slug'],[]):
            content=content.replace('>'+old+'</h2>','>'+E(new)+'</h2>')
        page('case-studies/'+c['slug'],c['title'],c['summary'],content,'case-studies',kind='Article')

def about():
    render_about(globals())


def resources():
    resource_views(page, pagehero, link, RESOURCES, E, ARROW)


def consultation(path='consultation'):
    render_consultation(globals(),path)


def faq():
    items=[('What does Digiator do?','We work across strategy, performance marketing, SEO and content, brand and creative, websites, data and automation, and custom software. An engagement can use one capability or a defined combination.'),('Can I come with a specific project?','Yes. A website, a campaign, a brand brief or an internal software process is a useful starting point. We establish the scope and any dependencies with you.'),('Can you work with our existing team or tools?','Yes, subject to the project. Discovery includes what is already working and what should be retained. A new platform or a full rebuild is not always necessary.'),('What happens after the free consultation?','Where there is a fit, we arrange a deeper discussion or meeting and agree what is needed to prepare a proposal. Significant research, audits and technical discovery may be separately scoped.'),('How are price and timelines decided?','They follow the scope, complexity, dependencies and review process. The proposal sets out deliverables, milestones and payment terms. There is no single package suitable for every brief.'),('Who owns the work?','Custom deliverables and access are handed over according to the agreement and payment terms. Your proposal should distinguish those deliverables from third-party software, licences, hosting and subscriptions.'),('What happens if the scope changes?','Changes are documented and assessed for cost and schedule. The revised work is agreed before implementation.'),('Do you provide ongoing support?','Support and maintenance can be scoped separately. The duration and coverage are stated in the proposal rather than assumed across every project.'),('Is every industry page a record of completed client work?','No. Industry pages distinguish delivered experience from proposed applications and adjacent capability. Case studies describe particular engagements.'),('Do you guarantee the results in the case studies?','No. Results belong to their stated engagement and period. Estimates and owner-confirmed figures are identified. Your outcome depends on the project, market and operating conditions.'),('Do we need AI in our project?','Only where it serves a useful, bounded purpose. Many operational requirements are best handled with dependable software and clear rules. Appropriate human review and information handling are part of any AI scope.'),('Can I use the resources without contacting you?','Yes. The workbooks are available to use, print and download. Notes are kept only in your open browser tab unless you download or print them.')]
    content=pagehero('Questions & answers','Know what to expect.','Practical answers about the work, the engagement and the next step.',[('FAQ','')],False)
    content+='<section class="section"><div class="wrap">'+faq_html(items)+'</div></section>'
    page('faq','Questions & answers','Answers about Digiator’s services, consultation, scope, ownership, support and resources.',content)

def legal():
    documents={
      'privacy':('Privacy information','How this website handles the information you choose to share.',[
        ('Who to contact','Digiator — Website Development and Digital Marketing Agency operates from Indore, Madhya Pradesh, India. For questions about website information or an enquiry, contact operations@digiator.com.'),
        ('Enquiry details','The enquiry form prepares a message on your device. It does not send the form to a Digiator website database. Choosing WhatsApp or email opens the selected service; you must complete the send there. Once you send the message, Digiator receives the information included in it and can use it to respond and discuss your project.'),
        ('WhatsApp and email','Your chosen communication service processes messages under its own terms and privacy practices. Share only what is needed for the initial conversation. Do not include patient records, customer lists, passwords or other sensitive project material.'),
        ('Workbook notes','Text you enter in a workbook stays in the current browser tab. This website does not transmit those notes or save them in browser storage. Download or print your notes before closing the tab. A downloaded file is stored on your device.'),
        ('Analytics and hosting','This version does not install advertising pixels, behavioural analytics or session-recording tools. The hosting service may process technical requests and, for a private review site, authentication information to deliver and protect access to the site.'),
        ('Requests about an enquiry','Contact operations@digiator.com to ask about access, correction or deletion of information you have shared with Digiator. The team will consider the request and any applicable record-keeping obligations. This page does not promise a retention period that has not been established for the relevant records.'),
        ('Changes','This information describes the functionality of this website version. It should be updated if hosted forms, analytics, email subscriptions or other data services are introduced. Last updated: 22 October 2026.')]),
      'cookies':('Cookie information','A simple explanation of this website’s browser behaviour.',[
        ('What this site uses','The website code does not set advertising, analytics or preference cookies. It does not use browser local storage or session storage for enquiry or workbook information.'),
        ('Private access and hosting','Where this site is accessed through a private hosting service, that service may use necessary authentication or security mechanisms. Those operate separately from the page interactions described here.'),
        ('External services','Opening WhatsApp or an email application takes you to a separate service with its own settings and practices. Your browser settings can manage cookies and permissions for websites you visit.'),
        ('Future changes','If optional analytics or advertising tools are added, this information and any required choices should be updated to reflect the tools actually used. Last updated: 22 October 2026.')]),
      'terms':('Website terms','The basis for using this website and its resources.',[
        ('About this website','This website introduces Digiator’s capabilities and provides general project-planning resources. Browsing the site or sending an enquiry does not establish a paid engagement.'),
        ('Project agreements','The scope, deliverables, fees, timeline, access, support and ownership terms for a project are set out in the relevant written agreement. General website descriptions do not replace that agreement.'),
        ('Case studies and illustrations','Case-study results relate to specific engagements. Owner-confirmed results and estimates are identified where used. They are not guarantees for a future project. Workflow illustrations are explanatory diagrams rather than representations of a client’s actual interface.'),
        ('Using the resources','You may use the workbooks for your own business planning and share completed copies with your project team. They provide prompts for investigation, not a professional certification, legal opinion or guarantee about an outcome.'),
        ('Appropriate use','Do not misuse the website, attempt unauthorised access, or send confidential third-party information through an initial enquiry. Discuss an appropriate information-sharing arrangement for sensitive project material.'),
        ('Contact','For questions about the website or these terms, contact operations@digiator.com. Last updated: 22 October 2026.')])}
    for slug,(title,summary,sections) in documents.items():
        content=pagehero('Website information',title,summary,[(title,'')],False)
        content+='<section class="section"><article class="wrap legal">'+''.join(f'<h2>{E(a)}</h2><p>{E(b)}</p>' for a,b in sections)+'</article></section>'
        page(slug,title,summary,content,include_cta=False)

def portable_copy():
    """Produce a second export whose pages also work when opened directly from disk."""
    target=ROOT/'offline'
    shutil.copytree(DIST,target,dirs_exist_ok=True)
    for file in target.rglob('*.html'):
        def relative_attribute(match):
            attr,url=match.groups()
            parts=urlsplit(url)
            dest=target/parts.path.lstrip('/')
            if parts.path.endswith('/') or not dest.suffix:
                dest=dest/'index.html'
            relative=os.path.relpath(dest,file.parent)
            if parts.query:relative+='?'+parts.query
            if parts.fragment:relative+='#'+parts.fragment
            return f'{attr}="{relative}"'
        file.write_text(re.sub(r'(href|src)="(/[^\"]*)"',relative_attribute,file.read_text()))
    (ROOT/'Open Digiator Final.html').write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Open Digiator Final</title><meta http-equiv="refresh" content="0;url=offline/index.html"></head><body><p><a href="offline/index.html">Open Digiator Final</a></p></body></html>')

def main():
    home();services();industries();cases();about();resources();consultation();consultation('contact');faq();legal()
    content=pagehero('404 / Page not found','Let’s find the right page.','This address does not match a page on the new Digiator website.',[],False)+'<section class="section"><div class="wrap actions">'+link('/','Back to home','btn dark')+link('/services/','Explore capabilities')+link('/contact/','Contact Digiator')+'</div></section>'
    page('404','Page not found','Find your way back to Digiator.',content,include_cta=False)
    (DIST/'404.html').write_text((DIST/'404'/'index.html').read_text())
    (DIST/'robots.txt').write_text('User-agent: *\nDisallow: /\n# Private review deployment. Update on approved public-domain launch.\n')
    (DIST/'sitemap.xml').write_text('<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'+''.join(f'<url><loc>{ORIGIN+p["path"]}</loc></url>' for p in PAGES if p['path']!='/404/')+'</urlset>')
    (ROOT/'page-manifest.json').write_text(json.dumps(PAGES,indent=2))
    portable_copy()
    print(f'Built {len(PAGES)-1} website pages + 404. All content is rendered in HTML.')

if __name__=='__main__':main()
