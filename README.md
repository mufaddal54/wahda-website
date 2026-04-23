# Al Wahda Building Materials Trading Website

A high-performance Django website for **Al Wahda Building Materials Trading**, optimized for Vercel Hobby deployment.

## Stack
- Django 5
- Alpine.js for lightweight interactions
- Markdown-based resources (file-driven content)
- WhiteNoise static handling
- Bilingual interface (English + Arabic, RTL-ready)

## Local setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## Deployment (Vercel Hobby)

1. Import the repository into Vercel.
2. Set environment variables:
   - `DJANGO_SECRET_KEY`
   - `DEBUG=False`
   - `ALLOWED_HOSTS=your-domain.com,.vercel.app`
3. Deploy.

## SEO implementation highlights

- Page-level metadata and canonical tags
- JSON-LD for Organization, LocalBusiness, WebSite/SearchAction, FAQPage, ItemList, BreadcrumbList
- Dynamic XML sitemap with resource URLs
- Robots.txt with sitemap declaration
- Keyword cluster integration across primary pages and resource guides
- Semantic heading structure + crawlable internal linking

## Content source for Resources page

Resources are loaded from markdown files in:

`resources/content/*.md`

Each file uses front matter:

```md
---
slug: sample-slug
title: Sample Title
description: Short summary
category: Tools
tags:
  - tag one
  - tag two
date: 2026-03-10
reading_time: 5 min read
---
Article body...
```

## Notes on Wagtail

Given Vercel Hobby constraints and to avoid paid infrastructure lock-in, this build uses markdown content instead of Wagtail CMS.
If needed later, Wagtail can be integrated with managed Postgres + external media storage.

## Current business contact details

- Email: `wahdabm52@gmail.com`
- Phone: `+971525376406`
- WhatsApp: `+971525376406`
