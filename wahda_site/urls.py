from django.contrib import admin
from django.urls import path
from core import views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("products/", views.products, name="products"),
    path("industries/", views.industries, name="industries"),
    path("resources/", views.resources, name="resources"),
    path("resources/<slug:slug>/", views.resource_detail, name="resource_detail"),
    path("contact/", views.contact, name="contact"),
    path("robots.txt", views.robots_txt, name="robots_txt"),
    path("sitemap.xml", views.sitemap_xml, name="sitemap_xml"),
    path("sitemap-ar.xml", views.sitemap_ar_xml, name="sitemap_ar_xml"),
]
