from django.apps import apps
from django.http import JsonResponse
from django.views.decorators.http import require_GET


# Create your views here.
@require_GET
def select2plus_api(request):
    model_name = request.GET.get("model")
    app_name = name_app(model_name)
    term = request.GET.get("term", "")
    filters = {k.replace("depend_", ""): v for k, v in request.GET.items() if k.startswith("depend_")}

    if not model_name:
        return JsonResponse({"results": []})

    Model = apps.get_model(app_name, model_name)

    qs = Model.objects.all()

    # aplicar filtros dependientes
    if filters:
        qs = qs.filter(**filters)

    # búsqueda si hay término
    if term:
        qs = qs.filter(nombre__icontains=term)

    results = [{"id": obj.id, "text": str(obj)} for obj in qs]
    return JsonResponse({"results": results})

def name_app(model_name):
    for app in apps.get_app_configs():
        for model in app.get_models():
            if model_name in model._meta.model_name.lower():
                return app.label