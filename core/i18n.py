from __future__ import annotations


def get_lang(request) -> str:
    lang = (request.GET.get("lang") or request.COOKIES.get("lang") or "en").lower()
    return "ar" if lang == "ar" else "en"


def is_ar(request) -> bool:
    return get_lang(request) == "ar"
