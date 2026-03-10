from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Product, ProductType

class ProductSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_available=True).select_related('product_type')

    def location(self, obj):
        return f'/all-products/{obj.product_type.slug}/{obj.custom_url}'



class ProductTypeSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return ProductType.objects.all()

    def location(self, obj):
        return f'/all-products/{obj.slug}'


class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return ['home', 'delivery', 'about', 'contacts', 'faq']

    def location(self, item):
        urls = {
            'home':     '/',
            'delivery': '/delivery',
            'about':    '/about',
            'contacts': '/contacts',
            'faq':      '/faq',
        }
        return urls[item]