# django-select2-plus

`django-select2-plus` es una implementación mejorada de widgets **Select2** para Django, permitiendo cargar opciones dinámicamente mediante AJAX, manejar **selects dependientes** y ofrecer una integración simple con **Bootstrap 5**.

Este paquete nace como solución práctica cuando se necesitan selects que cambien según otros campos, sin recargar la página y con buen rendimiento.

---

## 🚀 Características

- ✅ Compatible con Django >=3.8
- ✅ Integración mejorada con Bootstrap 5
- ✅ Soporte para dependencias dinámicas (`depend_*`)
- ✅ Carga remota mediante API / AJAX
- ✅ Compatible con formularios Django regulares y CBV
- ✅ Fácil de extender y personalizar

---
## 📦 Instalación

```python
pip install django-select2-plus

INSTALLED_APPS = [
    ...
    "django_select2_plus",
]

urlpatterns = [
    ...
    path("select2-plus/", include("django_select2_plus.urls")),
]
```
## 🔗 Uso

```python
from django_select2_plus.widgets import Select2PlusWidget, DeferredModelChoiceField, apply_dependent_selects

class PersonaForm(forms.Form):
    class PersonaForm(forms.ModelForm):
    departamento = forms.ModelChoiceField(
        queryset=Departamento.objects.all(),
        widget=Select2PlusWidget(select_type='search', model_name='departamento')
    )

    provincia = DeferredModelChoiceField(
        queryset=Provincia.objects.none(),
        widget=Select2PlusWidget(select_type='search', model_name='provincia', depend='departamento')
    )

    distrito = DeferredModelChoiceField(
        queryset=Distrito.objects.none(),
        widget=Select2PlusWidget(select_type='source', model_name='distrito', depend='provincia')
    )

    etnia = DeferredModelChoiceField(
        queryset=Etnia.objects.all(),
        widget=Select2PlusWidget(select_type='simple', model_name='etnia', auto_load=True)
    )

    class Meta:
        model = Persona
        fields = ['nombre', 'departamento', 'provincia', 'distrito', 'etnia']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        apply_dependent_selects(self)

```
## 🎨 Incluir en la plantilla(muy importante)
{{ form.media }}
