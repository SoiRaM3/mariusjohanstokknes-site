# M. J. Stokknes Website Platform v5.1

Public source for **mariusjohanstokknes.com**.

## Brand structure

- **M. J. Stokknes** — author and reader-facing front door.
- **Stokknes Publishing House** — independent imprint and publishing operation.
- **The shield** — browser, app, site, and press identity.

## Replace the final balcony photo

The website is already wired to stable files:

```text
assets/images/editorial/hero-balcony-web.webp
assets/images/editorial/hero-balcony-web.jpg
assets/images/editorial/hero-balcony-mobile.webp
```

Replace those files with the same names, validate, preview, and publish. No HTML editing is required.

## Local workflow

```text
PREVIEW → EDIT → VALIDATE → BACKUP → GIT STATUS → PUBLISH
```

The Author Machine controls the local Git repository under:

```text
06_WEBSITE_PLATFORM\mj-stokknes-platform-v3
```


Current editorial patch: **v5.1 Policy & Publishing Standards**.


Version: v5.1 Policy & Publishing Standards


## Policy and publishing standards

The public site now includes canonical AI/editorial, legal, privacy, cookie, and corrections pages. Every book page contains an official publication record and homepage route. The old v4 HTML generator is preserved as `scripts/build_legacy_v4.py`. The normal `scripts/build.py` is now a compatibility guard so an old validation launcher cannot silently rebuild the finished v5 site from an obsolete generator.
