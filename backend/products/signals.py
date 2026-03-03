import os
import logging
from io import BytesIO

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.files.base import ContentFile

logger = logging.getLogger('products')

WEBP_QUALITY = 85
MAX_WIDTH    = 1920
MAX_PRODUCT  = 1200


def convert_to_webp(image_field, max_width=MAX_WIDTH, quality=WEBP_QUALITY):
    """
    Конвертирует ImageField в WebP на месте.
    Возвращает True если конвертация произошла, иначе False.
    Не делает ничего если файл уже .webp или поле пустое.
    """
    try:
        from PIL import Image

        if not image_field or not image_field.name:
            return False

        if image_field.name.lower().endswith('.webp'):
            return False

        image_field.open('rb')
        raw = image_field.read()
        image_field.close()

        img = Image.open(BytesIO(raw))

        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGBA')
        else:
            img = img.convert('RGB')

        if img.width > max_width:
            ratio  = max_width / img.width
            new_h  = int(img.height * ratio)
            img    = img.resize((max_width, new_h), Image.LANCZOS)

        buffer = BytesIO()
        img.save(buffer, format='WEBP', quality=quality, method=6)
        buffer.seek(0)

        old_name   = os.path.basename(image_field.name)
        base_name  = os.path.splitext(old_name)[0]
        new_name   = f"{base_name}.webp"

        old_path = image_field.path if hasattr(image_field, 'path') else None
        image_field.save(new_name, ContentFile(buffer.read()), save=False)

        if old_path and os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError as e:
                logger.warning(f'Could not delete old image {old_path}: {e}')

        logger.info(f'Converted {old_name} → {new_name}')
        return True

    except Exception as e:
        logger.error(f'WebP conversion error for {getattr(image_field, "name", "unknown")}: {e}')
        return False



@receiver(post_save, sender='products.Product')
def convert_product_main_image(sender, instance, **kwargs):
    """Конвертирует основное изображение Product.imageUrl"""
    if not instance.imageUrl:
        return
    if instance.imageUrl.name.lower().endswith('.webp'):
        return

    changed = convert_to_webp(instance.imageUrl, max_width=MAX_PRODUCT)
    if changed:
        type(instance).objects.filter(pk=instance.pk).update(imageUrl=instance.imageUrl.name)


@receiver(post_save, sender='products.ProductImage')
def convert_product_extra_image(sender, instance, **kwargs):
    """Конвертирует дополнительные фото ProductImage.image"""
    if not instance.image:
        return
    if instance.image.name.lower().endswith('.webp'):
        return

    changed = convert_to_webp(instance.image, max_width=MAX_PRODUCT)
    if changed:
        type(instance).objects.filter(pk=instance.pk).update(image=instance.image.name)


@receiver(post_save, sender='products.HeroImage')
def convert_hero_image(sender, instance, **kwargs):
    """Конвертирует HeroImage.image"""
    if not instance.image:
        return
    if instance.image.name.lower().endswith('.webp'):
        return

    changed = convert_to_webp(instance.image, max_width=MAX_WIDTH)
    if changed:
        type(instance).objects.filter(pk=instance.pk).update(image=instance.image.name)


@receiver(post_save, sender='products.GalleryImage')
def convert_gallery_image(sender, instance, **kwargs):
    """Конвертирует GalleryImage.image"""
    if not instance.image:
        return
    if instance.image.name.lower().endswith('.webp'):
        return

    changed = convert_to_webp(instance.image, max_width=MAX_WIDTH)
    if changed:
        type(instance).objects.filter(pk=instance.pk).update(image=instance.image.name)