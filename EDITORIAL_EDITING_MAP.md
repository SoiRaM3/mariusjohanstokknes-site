# Website Editorial Editing Map — v4.5

## Authoritative structured files

- `content/books.json`
  - status, language, series, KDP formats, ASINs, prices, cover paths
  - `editorial` blocks used as the long-form source for each public English book
- `content/public-links.json`
  - split contact address
  - author profiles
  - retailer directory

## Main editorial pages

- `about.html`
- `framework.html`
- `fragments.html`
- `publishing-house.html`
- `press.html`
- `contact.html`
- `retailers.html`
- `spanish-editions.html`
- `review-copies.html`

## Visual assets added in v4.5

- `assets/images/editorial/zorro-about.webp`
- `assets/images/editorial/framework-editorial.webp`
- `assets/images/editorial/fragments-editorial.webp`
- `assets/images/editorial/publishing-editorial.webp`
- `assets/images/editorial/contact-editorial.webp`

## Contact privacy

The address is not written as one clear string in HTML. It is assembled from:

```javascript
window.STOKKNES_CONTACT={user:"marius_johan_stokknes",domain:"live.no"};
```

`assets/js/site.js` creates the mail link locally when a visitor clicks or submits a form.

## Public naming

Use `M. J. Stokknes` or `Stokknes` in editorial copy.
Use `Marius Johan Stokknes` for legal and bibliographic records.
