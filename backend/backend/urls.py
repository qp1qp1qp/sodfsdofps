from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve as static_serve
from django.views.decorators.cache import cache_control
from rest_framework.routers import DefaultRouter
from products.views import submit_quiz, FavoriteViewSet, subscribe_newsletter, ProductViewSet, CharacteristicViewSet, HeroImageViewSet, GalleryImageViewSet, OrderViewSet, PageViewSet, ProductTypeViewSet, receive_analytics_events
from products import views as product_views
from django.contrib.sitemaps.views import sitemap
from products.admin_views import get_characteristic_values
from products.sitemaps import ProductSitemap, ProductTypeSitemap, StaticSitemap

router = DefaultRouter()
router.register(r'product-types', ProductTypeViewSet, basename='producttype')
router.register(r'products', ProductViewSet, basename='product')
router.register(r'characteristics', CharacteristicViewSet, basename='characteristic')
router.register(r'hero-images', HeroImageViewSet, basename='heroimage')
router.register(r'gallery-images', GalleryImageViewSet, basename='galleryimage')
router.register(r'orders', OrderViewSet, basename='order')
router.register(r'pages', PageViewSet, basename='page')
router.register(r'favorites', FavoriteViewSet, basename='favorite')

sitemaps = {
    'products':      ProductSitemap,
    'product_types': ProductTypeSitemap,
    'static':        StaticSitemap,
}

urlpatterns = [
    path('admin_new_wooddon_site_ru_test/', admin.site.urls),
    path('api/', include(router.urls)),
    path('api/newsletter/subscribe/', subscribe_newsletter, name='subscribe_newsletter'),
    path('api/analytics/events/', receive_analytics_events, name='receive_analytics_events'),
    path('api/quiz/submit/', submit_quiz, name='quiz_submit'),
    path('admin_new_wooddon_site_ru_test/api/characteristic-values/', get_characteristic_values, name='admin-characteristic-values'),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
]

if settings.DEBUG:
    cached_serve = cache_control(max_age=86400)(static_serve)
    urlpatterns += [
        path('media/<path:path>', cached_serve, {'document_root': settings.MEDIA_ROOT}),
    ]