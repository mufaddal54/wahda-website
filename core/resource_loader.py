from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
import html

import bleach
import frontmatter
import markdown

from django.conf import settings


@dataclass
class ResourceItem:
    slug: str
    title: str
    title_ar: str
    description: str
    description_ar: str
    category: str
    tags: list[str]
    date: datetime
    reading_time: str
    body_html: str
    body_html_ar: str
    source_file: Path


RESOURCE_DIR = Path(settings.BASE_DIR) / "resources" / "content"


def _to_html(md_text: str) -> str:
    rendered = markdown.markdown(
        md_text,
        extensions=["extra", "tables", "toc", "fenced_code"],
        output_format="html5",
    )
    allowed_tags = set(bleach.sanitizer.ALLOWED_TAGS).union(
        {"p", "h2", "h3", "h4", "ul", "ol", "li", "pre", "code", "table", "thead", "tbody", "tr", "th", "td", "blockquote"}
    )
    allowed_attrs = {
        "a": ["href", "title", "rel"],
        "th": ["colspan", "rowspan"],
        "td": ["colspan", "rowspan"],
    }
    return bleach.clean(rendered, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def _safe_text(value: str) -> str:
    return html.escape(str(value)).strip()


def load_resources() -> list[ResourceItem]:
    items: list[ResourceItem] = []
    if not RESOURCE_DIR.exists():
        return items

    for md_file in sorted(RESOURCE_DIR.glob("*.md")):
        post = frontmatter.load(md_file)
        slug = _safe_text(post.get("slug") or md_file.stem)
        title = _safe_text(post.get("title") or slug.replace("-", " ").title())
        title_ar = _safe_text(post.get("title_ar") or title)
        description = _safe_text(post.get("description") or "")
        description_ar = _safe_text(post.get("description_ar") or description)
        category = _safe_text(post.get("category") or "General")
        tags = [
            _safe_text(tag)
            for tag in post.get("tags", [])
            if str(tag).strip()
        ]
        date_str = post.get("date") or "2026-01-01"
        try:
            date = datetime.fromisoformat(str(date_str))
        except ValueError:
            date = datetime(2026, 1, 1)

        reading_time = _safe_text(post.get("reading_time") or "4 min read")
        body_html = _to_html(post.content)
        body_ar = str(post.get("content_ar") or post.content)
        body_html_ar = _to_html(body_ar)

        items.append(
            ResourceItem(
                slug=slug,
                title=title,
                title_ar=title_ar,
                description=description,
                description_ar=description_ar,
                category=category,
                tags=tags,
                date=date,
                reading_time=reading_time,
                body_html=body_html,
                body_html_ar=body_html_ar,
                source_file=md_file,
            )
        )

    items.sort(key=lambda x: x.date, reverse=True)
    return items
