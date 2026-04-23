from __future__ import annotations

import json
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring

from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.text import slugify

from .i18n import get_lang
from .resource_loader import load_resources


PRODUCT_CATEGORIES = [
    {
        "slug": "building-materials",
        "name_en": "Building Materials",
        "name_ar": "مواد البناء",
        "summary_en": "Complete day-to-day construction materials for contracting sites and maintenance teams.",
        "summary_ar": "تشكيلة شاملة من مواد البناء اليومية لمواقع المقاولات وفرق الصيانة.",
        "items_en": [
            "Screws",
            "Nails",
            "Cutting discs",
            "Welding accessories",
            "Hand tools",
            "Wrenches & sockets",
            "Measuring tools",
            "Binding wire",
        ],
        "items_ar": [
            "براغي",
            "مسامير",
            "أقراص قطع",
            "مستلزمات لحام",
            "أدوات يدوية",
            "مفاتيح وربطات",
            "أدوات قياس",
            "سلك ربط",
        ],
    },
    {
        "slug": "power-tools",
        "name_en": "Power Tools",
        "name_ar": "الأدوات الكهربائية",
        "summary_en": "Professional power tools for precision work in construction, industrial, and workshop environments.",
        "summary_ar": "أدوات كهربائية احترافية لأعمال دقيقة في البناء والصناعة والورش.",
        "items_en": [
            "Drill machines",
            "Angle grinders",
            "Rotary jack hammers",
            "Circular saws",
            "Jigsaw machines",
            "Heat guns",
        ],
        "items_ar": [
            "مثاقب كهربائية",
            "جلاخات زاوية",
            "شاكوش تكسير دوار",
            "منشار دائري",
            "منشار أركت",
            "مسدس هواء ساخن",
        ],
    },
    {
        "slug": "sanitary-ware",
        "name_en": "Sanitary Ware",
        "name_ar": "الأدوات الصحية",
        "summary_en": "Reliable sanitary products for residential and commercial projects.",
        "summary_ar": "منتجات صحية موثوقة للمشاريع السكنية والتجارية.",
        "items_en": [
            "Wash basins",
            "Water closets",
            "Shower mixers",
            "Sink mixers",
            "Water heaters",
            "Accessories & fittings",
        ],
        "items_ar": [
            "أحواض غسيل",
            "مراحيض",
            "خلاطات دش",
            "خلاطات مغاسل",
            "سخانات مياه",
            "إكسسوارات ووصلات",
        ],
    },
    {
        "slug": "electrical-plumbing",
        "name_en": "Electrical & Plumbing",
        "name_ar": "الكهرباء والسباكة",
        "summary_en": "Curated electrical and plumbing supplies designed for durable project performance.",
        "summary_ar": "مواد كهرباء وسباكة مختارة بعناية لأداء طويل الأمد في المشاريع.",
        "items_en": [
            "Ducab wire",
            "LED lighting",
            "Electrical accessories",
            "Electrical panels",
            "PPR pipes & fittings",
            "Cable trays & C-channels",
            "Conduits and DD pipes",
            "Water pumps",
            "Exhaust fans",
        ],
        "items_ar": [
            "أسلاك دوكاب",
            "إضاءة LED",
            "إكسسوارات كهربائية",
            "لوحات كهربائية",
            "أنابيب ووصلات PPR",
            "مسارات كابلات وقنوات C",
            "مواسير كونديت وDD",
            "مضخات مياه",
            "مراوح شفط",
        ],
    },
    {
        "slug": "safety-items",
        "name_en": "Safety Items",
        "name_ar": "مستلزمات السلامة",
        "summary_en": "Workforce protection products for sites, factories, and industrial operations.",
        "summary_ar": "مستلزمات حماية الأفراد لمواقع العمل والمصانع والعمليات الصناعية.",
        "items_en": [
            "Safety harnesses",
            "First aid kits",
            "Safety equipment",
            "Safety accessories",
            "Safety coveralls",
            "Safety shoes",
        ],
        "items_ar": [
            "أحزمة أمان",
            "حقائب إسعافات أولية",
            "معدات سلامة",
            "إكسسوارات سلامة",
            "أفرول سلامة",
            "أحذية سلامة",
        ],
    },
    {
        "slug": "general-items",
        "name_en": "General Items",
        "name_ar": "منتجات عامة",
        "summary_en": "Everyday support items that complete practical construction and maintenance workflows.",
        "summary_ar": "منتجات دعم يومية تكمل سير العمل العملي في البناء والصيانة.",
        "items_en": [
            "Paint, abrasives & adhesives",
            "Castor wheels",
            "Ladders",
            "Polythene sheets",
            "Tools & accessories",
            "Corrugated rolls",
        ],
        "items_ar": [
            "دهانات وصنفرة ولاصق",
            "عجلات كاستر",
            "سلالم",
            "أغطية بوليثين",
            "أدوات وإكسسوارات",
            "لفائف مموجة",
        ],
    },
]

INDUSTRIES_EN = [
    "Residential and commercial construction",
    "Infrastructure and civil works",
    "MEP contracting",
    "Industrial maintenance",
    "Factories and workshops",
    "Facilities management",
]

INDUSTRIES_AR = [
    "الإنشاءات السكنية والتجارية",
    "البنية التحتية والأعمال المدنية",
    "مقاولات الميكانيكا والكهرباء والسباكة",
    "الصيانة الصناعية",
    "المصانع والورش",
    "إدارة المرافق",
]

FAQS_EN = [
    {
        "question": "Do you deliver building materials outside Umm Al Quwain?",
        "answer": "Yes. Al Wahda supplies and delivers construction and industrial materials across Dubai and the UAE.",
    },
    {
        "question": "Can I request bulk pricing for contractors?",
        "answer": "Yes. We support contractor and industrial bulk requirements with fast quotation support.",
    },
    {
        "question": "What products do you stock?",
        "answer": "From building materials and power tools to sanitary ware, electrical/plumbing, safety items, and general products.",
    },
]

FAQS_AR = [
    {
        "question": "هل توفرون التوصيل خارج أم القيوين؟",
        "answer": "نعم، نخدم دبي ومختلف إمارات الدولة بتوريد وتسليم مواد البناء والمواد الصناعية.",
    },
    {
        "question": "هل يمكن طلب أسعار خاصة للكميات الكبيرة؟",
        "answer": "نعم، نقدم عروض أسعار سريعة للمقاولين وطلبات المشاريع والكميات.",
    },
    {
        "question": "ما هي الفئات المتوفرة لديكم؟",
        "answer": "نوفر مواد البناء، الأدوات الكهربائية، الأدوات الصحية، مستلزمات الكهرباء والسباكة، منتجات السلامة، ومنتجات عامة.",
    },
]

NAV_PAGES = [
    ("", "daily", "1.0"),
    ("products/", "weekly", "0.9"),
    ("industries/", "weekly", "0.8"),
    ("resources/", "weekly", "0.8"),
    ("contact/", "monthly", "0.8"),
]


def _schema_json(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False)


def _meta(*, title: str, description: str, keywords: str, canonical_path: str, og_type: str = "website") -> dict[str, str]:
    return {
        "meta_title": title,
        "meta_description": description,
        "meta_keywords": keywords,
        "canonical_path": canonical_path,
        "og_type": og_type,
    }


def _lang_suffix(lang: str) -> str:
    return "?lang=ar" if lang == "ar" else ""


def home(request):
    lang = get_lang(request)
    ar = lang == "ar"

    context = {
        "lang": lang,
        "dir": "rtl" if ar else "ltr",
        "lang_suffix": _lang_suffix(lang),
        **_meta(
            title="شركة مواد بناء في الإمارات | الوحدة لمواد البناء" if ar else "Building Materials Supplier in UAE | Al Wahda",
            description=(
                "الوحدة لمواد البناء في أم القيوين توفر مواد البناء والأدوات الكهربائية والمواد الصناعية وتخدم دبي وجميع الإمارات."
                if ar
                else "Al Wahda Building Materials Trading supplies building materials, tools, sanitary ware, and industrial products across Umm Al Quwain, Dubai, and the UAE."
            ),
            keywords=(
                "مواد بناء الإمارات, مواد بناء دبي, أدوات كهربائية الإمارات, مورد صناعي أم القيوين"
                if ar
                else "building materials UAE, construction materials Dubai, industrial supplies UAE, power tools supplier"
            ),
            canonical_path="/",
        ),
        "hero_keywords": (
            ["مواد بناء الإمارات", "أدوات كهربائية دبي", "مورد صناعي أم القيوين"]
            if ar
            else ["building materials supplier UAE", "construction tools Dubai", "industrial supplies Umm Al Quwain"]
        ),
        "product_categories": PRODUCT_CATEGORIES,
        "faqs": FAQS_AR if ar else FAQS_EN,
        "home_copy": {
            "eyebrow": "أم القيوين | توريد إلى جميع الإمارات" if ar else "Umm Al Quwain Based | UAE-Wide Supply",
            "title": "جاهزون لخدمة مشاريعك اليومية في البناء والصناعة." if ar else "Built for fast-moving projects. Supplied by Al Wahda.",
            "lead": "أكثر من 17 سنة خبرة في توريد مواد البناء والأدوات للمقاولين والمصانع وفرق الصيانة." if ar else "Over 17 years of expertise in supplying building materials, tools, and industrial items for contractors, factories, and maintenance teams.",
            "cta1": "استعرض المنتجات" if ar else "Explore Products",
            "cta2": "اطلب عرض سعر" if ar else "Request a Quote",
            "panel_title": "لماذا تختارنا الشركات" if ar else "Why teams choose Al Wahda",
            "panel_points": (
                [
                    "تنوع كبير في المواد والأدوات",
                    "دعم سريع لطلبات المشاريع والكميات",
                    "خدمة موثوقة وسرعة في الاستجابة",
                ]
                if ar
                else [
                    "Wide catalog aligned with real UAE project demand",
                    "Fast support for contractor and bulk requirements",
                    "Reliable service built on long-term supply experience",
                ]
            ),
            "breadth_eyebrow": "تنوع المنتجات" if ar else "Product Breadth",
            "breadth_title": "فئات رئيسية تغطي احتياجات الموقع والقطاع الصناعي" if ar else "Core categories for daily site and industrial operations",
            "faq_eyebrow": "الأسئلة المتكررة" if ar else "Frequently Asked Questions",
            "faq_title": "إجابات سريعة للمقاولين وفرق المشتريات" if ar else "Answers for contractors and procurement teams",
            "cta_band_title": "هل لديك طلب مواد عاجل لمشروعك؟" if ar else "Need urgent material support for a UAE project?",
            "cta_band_text": "أرسل قائمة المواد وسنخدمك بسرعة." if ar else "Share your requirement list and get assisted quickly.",
            "cta_band_btn": "ابدأ عبر واتساب" if ar else "Start on WhatsApp",
        },
        "schema": _schema_json(
            {
                "@context": "https://schema.org",
                "@graph": [
                    {
                        "@type": "Organization",
                        "name": "Al Wahda Building Materials Trading",
                        "url": request.build_absolute_uri("/"),
                        "email": "wahdabm52@gmail.com",
                        "telephone": "+971525376406",
                        "address": {
                            "@type": "PostalAddress",
                            "streetAddress": "New Salama, Fruit & Vegetable Market",
                            "addressLocality": "Umm Al Quwain",
                            "addressCountry": "AE",
                        },
                        "areaServed": ["Umm Al Quwain", "Dubai", "UAE"],
                    },
                    {
                        "@type": "WebSite",
                        "name": "Al Wahda Building Materials Trading",
                        "url": request.build_absolute_uri("/"),
                        "potentialAction": {
                            "@type": "SearchAction",
                            "target": request.build_absolute_uri("/resources/?q={search_term_string}"),
                            "query-input": "required name=search_term_string",
                        },
                    },
                    {
                        "@type": "FAQPage",
                        "mainEntity": [
                            {
                                "@type": "Question",
                                "name": item["question"],
                                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
                            }
                            for item in (FAQS_AR if ar else FAQS_EN)
                        ],
                    },
                ],
            }
        ),
    }
    return render(request, "pages/home.html", context)


def products(request):
    lang = get_lang(request)
    ar = lang == "ar"

    context = {
        "lang": lang,
        "dir": "rtl" if ar else "ltr",
        "lang_suffix": _lang_suffix(lang),
        **_meta(
            title="المنتجات | الوحدة لمواد البناء" if ar else "Products | Construction & Industrial Supplies UAE | Al Wahda",
            description=(
                "استعرض فئات منتجات الوحدة لمواد البناء: مواد بناء، أدوات كهربائية، أدوات صحية، كهرباء وسباكة، سلامة، ومنتجات عامة."
                if ar
                else "Browse Al Wahda categories: building materials, power tools, sanitary ware, electrical/plumbing, safety items, and general products."
            ),
            keywords=(
                "مواد بناء دبي, أدوات كهربائية الإمارات, مورد سباكة وكهرباء الإمارات"
                if ar
                else "construction tools supplier UAE, power tools Dubai, sanitary ware supplier UAE, electrical plumbing supplies"
            ),
            canonical_path="/products/",
        ),
        "product_categories": PRODUCT_CATEGORIES,
        "page_copy": {
            "eyebrow": "المنتجات" if ar else "Products",
            "title": "فئات منتجات البناء والصناعة" if ar else "Construction and industrial product categories",
            "lead": "منتجات منظمة حسب احتياج المشاريع اليومية لتسهيل الشراء والتوريد." if ar else "Catalog structured around practical project requirements for easier procurement.",
            "callout_title": "متطلبات المشاريع والكميات" if ar else "Bulk requirements and recurring procurement",
            "callout_text": "شاركنا قائمة المواد والكميات المطلوبة وسنجهز لك عرضًا مناسبًا." if ar else "Share your BOQ or item list and we will support your sourcing plan quickly.",
            "callout_btn": "احصل على عرض سعر" if ar else "Get a Product Quote",
        },
        "schema": _schema_json(
            {
                "@context": "https://schema.org",
                "@type": "ItemList",
                "name": "Al Wahda Product Categories",
                "itemListElement": [
                    {
                        "@type": "ListItem",
                        "position": index,
                        "name": category["name_ar"] if ar else category["name_en"],
                        "url": request.build_absolute_uri(f"/products/#{category['slug']}"),
                    }
                    for index, category in enumerate(PRODUCT_CATEGORIES, start=1)
                ],
            }
        ),
    }
    return render(request, "pages/products.html", context)


def industries(request):
    lang = get_lang(request)
    ar = lang == "ar"

    context = {
        "lang": lang,
        "dir": "rtl" if ar else "ltr",
        "lang_suffix": _lang_suffix(lang),
        **_meta(
            title="القطاعات التي نخدمها | الوحدة" if ar else "Industries We Serve in UAE | Al Wahda",
            description=(
                "ندعم المقاولين والمصانع وفرق الصيانة في مختلف إمارات الدولة بتوريد مواد وأدوات موثوقة."
                if ar
                else "Al Wahda supports construction, MEP, maintenance, and industrial teams across UAE with reliable supply."
            ),
            keywords=(
                "توريد صناعي الإمارات, مورد مواد مقاولات" if ar else "industrial supplier UAE, MEP tools supplier Dubai, construction procurement UAE"
            ),
            canonical_path="/industries/",
        ),
        "industries": INDUSTRIES_AR if ar else INDUSTRIES_EN,
        "page_copy": {
            "eyebrow": "القطاعات" if ar else "Industries",
            "title": "نخدم مشاريع البناء والصناعة بكفاءة" if ar else "Supply support for construction and industrial operations",
            "lead": "نوائم التوريد مع سرعة عملك ومتطلبات الموقع." if ar else "Our product mix is aligned with real-world pace on sites, workshops, and maintenance operations.",
            "card_text": "دعم توريد منظم بما يتناسب مع سرعة التنفيذ واحتياجات التشغيل." if ar else "Practical supply support aligned with field schedules and continuity needs.",
            "cta_title": "هل تحتاج شريك توريد موثوق لمشروعك القادم؟" if ar else "Need a dependable material partner for your next package?",
            "cta_text": "تواصل معنا وحدد احتياجاتك لنقترح الأنسب." if ar else "Share your scope and timeline. We will guide suitable categories and supply options.",
            "cta_btn": "تواصل مع المبيعات" if ar else "Talk to Sales",
        },
    }
    return render(request, "pages/industries.html", context)


def resources(request):
    lang = get_lang(request)
    ar = lang == "ar"
    all_resources = load_resources()
    q = (request.GET.get("q") or "").strip().lower()
    tag = (request.GET.get("tag") or "").strip().lower()

    filtered = all_resources
    if q:
        filtered = [
            r
            for r in filtered
            if q in r.title.lower() or q in r.description.lower() or q in r.body_html.lower()
        ]

    if tag:
        filtered = [
            r
            for r in filtered
            if any(tag == existing.lower() for existing in r.tags)
        ]

    tags = sorted({tag_name for item in all_resources for tag_name in item.tags})

    context = {
        "lang": lang,
        "dir": "rtl" if ar else "ltr",
        "lang_suffix": _lang_suffix(lang),
        **_meta(
            title="الموارد | أدلة الشراء والمشاريع" if ar else "Resources | Construction Insights UAE | Al Wahda",
            description=(
                "مكتبة أدلة عملية للمقاولين والمشترين في مجالات مواد البناء والأدوات في الإمارات."
                if ar
                else "Practical buying guides, product explainers, and field insights for contractors and industrial buyers in UAE."
            ),
            keywords=(
                "دليل شراء مواد البناء الإمارات, أدلة المقاولين" if ar else "construction materials guide UAE, industrial tools buying guide Dubai, contractor resources UAE"
            ),
            canonical_path="/resources/",
        ),
        "resources": filtered,
        "localized_resources": [
            {
                "slug": r.slug,
                "title": r.title_ar if ar else r.title,
                "description": r.description_ar if ar else r.description,
                "date": r.date,
                "reading_time": r.reading_time,
                "tags": r.tags,
            }
            for r in filtered
        ],
        "all_tags": tags,
        "active_q": q,
        "active_tag": tag,
        "page_copy": {
            "eyebrow": "الموارد" if ar else "Resources",
            "title": "أدلة عملية لمشتريات البناء والصناعة" if ar else "Practical guides for construction and industrial buyers",
            "lead": "محتوى منظم لاستهداف الأسئلة الفعلية للمشترين وتحسين الظهور في نتائج البحث." if ar else "Knowledge hub designed for real buyer questions and long-tail UAE search capture.",
            "search_placeholder": "ابحث في المواضيع" if ar else "Search guide topics",
            "all_tags": "كل الوسوم" if ar else "All tags",
            "filter_btn": "تصفية" if ar else "Filter",
            "empty_title": "لا توجد نتائج" if ar else "No resources found",
            "empty_text": "جرّب كلمة أخرى أو أزل التصفية لعرض جميع الأدلة." if ar else "Try another keyword or clear your filter to browse all guides.",
        },
    }
    return render(request, "pages/resources.html", context)


def resource_detail(request, slug: str):
    lang = get_lang(request)
    ar = lang == "ar"
    all_resources = load_resources()
    item = next((resource for resource in all_resources if resource.slug == slug), None)
    if not item:
        raise Http404("Resource not found")

    similar_items = [r for r in all_resources if r.slug != item.slug and r.category == item.category][:3]
    breadcrumb_schema = {
        "@context": "https://schema.org",
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Home", "item": request.build_absolute_uri("/")},
            {"@type": "ListItem", "position": 2, "name": "Resources", "item": request.build_absolute_uri("/resources/")},
            {"@type": "ListItem", "position": 3, "name": item.title, "item": request.build_absolute_uri(f"/resources/{item.slug}/")},
        ],
    }

    context = {
        "lang": lang,
        "dir": "rtl" if ar else "ltr",
        "lang_suffix": _lang_suffix(lang),
        **_meta(
            title=f"{item.title} | {'موارد الوحدة' if ar else 'Al Wahda Resources'}",
            description=item.description,
            keywords=", ".join(item.tags) if item.tags else "construction resources UAE",
            canonical_path=f"/resources/{item.slug}/",
            og_type="article",
        ),
        "resource": item,
        "resource_title": item.title_ar if ar else item.title,
        "resource_description": item.description_ar if ar else item.description,
        "resource_body_html": item.body_html_ar if ar else item.body_html,
        "similar_items": [
            {
                "slug": s.slug,
                "title": s.title_ar if ar else s.title,
                "description": s.description_ar if ar else s.description,
            }
            for s in similar_items
        ],
        "page_copy": {
            "home": "الرئيسية" if ar else "Home",
            "resources": "الموارد" if ar else "Resources",
            "related": "موارد ذات صلة" if ar else "Related resources",
            "empty_related": "سيتم إضافة المزيد من الأدلة قريبًا." if ar else "More guides are coming soon.",
        },
        "schema": _schema_json(breadcrumb_schema),
    }
    return render(request, "pages/resource_detail.html", context)


def contact(request):
    lang = get_lang(request)
    ar = lang == "ar"
    context = {
        "lang": lang,
        "dir": "rtl" if ar else "ltr",
        "lang_suffix": _lang_suffix(lang),
        **_meta(
            title="تواصل معنا | الوحدة لمواد البناء" if ar else "Contact Al Wahda | Building Materials Trading UAE",
            description=(
                "تواصل مع الوحدة لمواد البناء لطلبات المواد والمشاريع في الإمارات."
                if ar
                else "Contact Al Wahda Building Materials Trading for product inquiries, contractor requirements, and industrial supply support across UAE."
            ),
            keywords=(
                "تواصل مواد بناء الإمارات, عرض سعر مواد بناء" if ar else "contact building materials supplier UAE, construction materials quote Dubai"
            ),
            canonical_path="/contact/",
        ),
        "page_copy": {
            "eyebrow": "تواصل" if ar else "Contact",
            "title": "تواصل مع فريق المبيعات والدعم" if ar else "Talk to Al Wahda sales and procurement support",
            "lead": "أرسل قائمة المواد أو متطلبات المشروع وسنقوم بخدمتك بسرعة." if ar else "Send your requirement list for construction and industrial supplies. We assist teams across UAE.",
            "quick": "بيانات التواصل" if ar else "Quick Contact",
            "send": "أرسل الطلب عبر الإيميل" if ar else "Send Requirement by Email",
            "format": "لخدمة أسرع، أرسل المعلومات التالية:" if ar else "Use this format for faster support:",
            "points": (
                ["موقع المشروع", "قائمة المواد أو الأدوات", "الكميات المطلوبة", "موعد التسليم المتوقع"]
                if ar
                else ["Project location", "Material or tool list", "Required quantities", "Target delivery date"]
            ),
            "email_btn": "راسل فريق المبيعات" if ar else "Email Sales Team",
            "phone": "الهاتف" if ar else "Phone",
            "email": "البريد" if ar else "Email",
            "whatsapp": "واتساب" if ar else "WhatsApp",
            "address": "العنوان" if ar else "Address",
        },
        "schema": _schema_json(
            {
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                "name": "Al Wahda Building Materials Trading",
                "telephone": "+971525376406",
                "email": "wahdabm52@gmail.com",
                "address": {
                    "@type": "PostalAddress",
                    "streetAddress": "New Salama, Fruit & Vegetable Market",
                    "addressLocality": "Umm Al Quwain",
                    "addressCountry": "AE",
                },
                "areaServed": ["Umm Al Quwain", "Dubai", "UAE"],
            }
        ),
    }
    return render(request, "pages/contact.html", context)


def robots_txt(request):
    base = request.build_absolute_uri("/").rstrip("/")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        f"Sitemap: {base}/sitemap.xml",
        f"Sitemap: {base}/sitemap-ar.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")


def sitemap_xml(request):
    base = request.build_absolute_uri("/").rstrip("/")
    now = datetime.now(tz=timezone.utc).date().isoformat()

    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for path, changefreq, priority in NAV_PAGES:
        url = SubElement(urlset, "url")
        loc = f"{base}/{path}" if path else f"{base}/"
        SubElement(url, "loc").text = loc
        SubElement(url, "lastmod").text = now
        SubElement(url, "changefreq").text = changefreq
        SubElement(url, "priority").text = priority

    for article in load_resources():
        url = SubElement(urlset, "url")
        loc = f"{base}/resources/{slugify(article.slug)}/"
        SubElement(url, "loc").text = loc
        SubElement(url, "lastmod").text = article.date.date().isoformat()
        SubElement(url, "changefreq").text = "monthly"
        SubElement(url, "priority").text = "0.7"

    xml_data = tostring(urlset, encoding="utf-8", method="xml")
    return HttpResponse(xml_data, content_type="application/xml")


def sitemap_ar_xml(request):
    base = request.build_absolute_uri("/").rstrip("/")
    now = datetime.now(tz=timezone.utc).date().isoformat()

    urlset = Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")

    for path, changefreq, priority in NAV_PAGES:
        url = SubElement(urlset, "url")
        loc = f"{base}/{path}" if path else f"{base}/"
        SubElement(url, "loc").text = f"{loc}?lang=ar"
        SubElement(url, "lastmod").text = now
        SubElement(url, "changefreq").text = changefreq
        SubElement(url, "priority").text = priority

    for article in load_resources():
        url = SubElement(urlset, "url")
        loc = f"{base}/resources/{slugify(article.slug)}/?lang=ar"
        SubElement(url, "loc").text = loc
        SubElement(url, "lastmod").text = article.date.date().isoformat()
        SubElement(url, "changefreq").text = "monthly"
        SubElement(url, "priority").text = "0.7"

    xml_data = tostring(urlset, encoding="utf-8", method="xml")
    return HttpResponse(xml_data, content_type="application/xml")
