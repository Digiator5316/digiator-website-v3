# Digiator website — Version 3

The standalone Digiator marketing website, Version 3 (the Final revision). This repository contains only this website's source, content, logo, styles, browser scripts and static exports. It contains no Digiator AI Studio, Ronin application, other website versions, credentials or private research files.

## Open locally

Run `python3 serve.py`, or double-click **Open Digiator Final.command** on a Mac. Open **http://127.0.0.1:8352/**. Keep the terminal running while browsing. If that port is occupied, use `python3 serve.py --port 8354` and open the displayed address.

For a preview without a server, double-click **Open Digiator Final.html**. Keep the `offline` folder beside it so all pages, assets and links work.

Python 3 is needed for the local server and rebuilds. The site itself is plain HTML, CSS and JavaScript; no framework, Node.js installation, package installation or AI service is required.

## Website contents

- Homepage, About, consultation, contact and FAQ.
- Seven services and twenty industry pages.
- Six case studies and seven interactive workbooks.
- Privacy, cookies, terms and the error page.

There are 52 content routes plus the error route. The static export also includes a root `404.html` for hosts that support a custom error page.

## Edit and rebuild

- `build.py`: shared page templates, page families and export generation.
- `conversion_content.py`: homepage, About, consultation and enquiry presentation.
- `flow_content.py`: resource library and workbook layouts.
- `services.json`, `industries.json`, `industry_answers.json`, `cases.json`, `resources.json`: the website's content inputs.
- `dist/assets/`: the original logo and editable CSS/JavaScript assets.
- `dist/`: complete static website for a local server or hosting at a domain root.
- `offline/`: the same website with relative links for direct opening from disk.
- `page-manifest.json`: generated route inventory.

After editing templates, content or assets, run:

```sh
python3 build.py
python3 check_site.py
```

The build regenerates pages and the offline export; the tracked assets in `dist/assets/` are also source files and should be kept. Direct HTML edits in `dist/` should be reflected in the generator before rebuilding.

## Hosting and enquiry behaviour

This repository is private source storage. Pushing a commit does not publish a website; GitHub Pages is not enabled. To deploy later, serve only `dist/` at the site root and configure directory `index.html` routes and the custom error page. Hosting under a path prefix needs the root-relative links adapted first.

The original local canonical origin and review-only `noindex` metadata are preserved. Set `SITE_ORIGIN` when rebuilding for a confirmed hosting destination, and review indexing settings separately before public launch.

The enquiry form prepares a WhatsApp or email message for the visitor to review and send in that application. This version has no server-side lead storage or direct submission backend. Workbook notes stay in the current tab until downloaded or printed. No test enquiry is sent as part of repository verification.

## Ownership

Digiator branding and content are retained. No open-source licence is granted by storing this project on GitHub.
