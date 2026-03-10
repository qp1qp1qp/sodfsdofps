from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Product
from .serializers import ProductDetailSerializer

@api_view(['GET'])
def product_detail(request, custom_url):
    try:
        product = Product.objects.get(custom_url=custom_url)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({"error": "Product not found"}, status=404)