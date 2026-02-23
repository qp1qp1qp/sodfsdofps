from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required
from .models import CharacteristicValue

@staff_member_required
def get_characteristic_values(request):
    """API для получения значений характеристик"""
    characteristic_id = request.GET.get('characteristic_id')
    if not characteristic_id:
        return JsonResponse([], safe=False)
    
    values = CharacteristicValue.objects.filter(characteristic_id=characteristic_id).values('id', 'value')
    return JsonResponse(list(values), safe=False) 