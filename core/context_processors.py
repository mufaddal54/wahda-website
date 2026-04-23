
from .i18n import get_lang


def site_defaults(request):
    return {
        "site_name": "Al Wahda Building Materials Trading",
        "brand_name": "Al Wahda",
        "company_phone": "+971525376406",
        "company_email": "wahdabm52@gmail.com",
        "company_whatsapp": "https://wa.me/971525376406",
        "company_address": "New Salama, Fruit & Vegetable Market, Umm Al Quwain, UAE",
        "instagram_handle": "alwahdabmt",
        "current_lang": get_lang(request),
        "site_url": "https://alwahdabmt.com",
    }
