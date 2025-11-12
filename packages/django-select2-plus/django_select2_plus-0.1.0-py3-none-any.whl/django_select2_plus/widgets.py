# widgets.py
from django import forms
from django.core.exceptions import ValidationError

class Select2PlusWidget(forms.Select):
    template_name = "widgets/smart_select.html"

    class Media:
        
        js = ['django_select2_plus/js/select2-plus.js']
        css = {'all': ['django_select2_plus/css/select2-plus.css']}

    def __init__(self, attrs=None, select_type="simple", model_name=None, depend=None, auto_load=False):
        final_attrs = attrs or {}
        final_attrs["data-select"] = select_type
        final_attrs["data-model"] = model_name
        
        if depend:
            final_attrs["data-depend"] = depend

        if auto_load:
            final_attrs["data-auto-load"] = True 
              
        super().__init__(attrs=final_attrs)


class DeferredModelChoiceField(forms.ModelChoiceField):
    """
    No carga todo el queryset, y acepta un PK en POST.
    Evita que Django use el queryset vacío para resolver el valor.
    """
    def to_python(self, value):
        # Copiado y adaptado de ModelChoiceField.to_python pero usando model.objects.get
        if value in self.empty_values:
            return None

        # Si ya es instancia de modelo, retornarla
        model = self.queryset.model
        if isinstance(value, model):
            return value

        try:
            # Intentar convertir el pk a int/str y traer la instancia directamente desde el modelo
            return model.objects.get(pk=value)
        except (ValueError, TypeError, model.DoesNotExist):
            raise ValidationError(self.error_messages['invalid_choice'], code='invalid_choice')

    def validate(self, value):
        # Mantener la validación estándar (existencia ya comprobada en to_python)
        # Pero permitir None si el campo no es requerido
        if value is None:
            if self.required:
                raise ValidationError(self.error_messages['required'], code='required')
            return
        # No comprobar que esté dentro del queryset: ya resolvimos por PK
        return

def apply_dependent_selects(form):
    """
    Actualiza dinámicamente selects dependientes en formularios Django
    usando los atributos:
    - data-depend="campo_padre"
    - data-auto-load="campo_padre" (para cargar automáticamente al editar)
    """
    instance = getattr(form, "instance", None)

    for field_name, field in form.fields.items():
        if not hasattr(field, "queryset"):
            continue

        depend = field.widget.attrs.get("data-depend")
        autoload = field.widget.attrs.get("data-auto-load")

        # Caso 1: el campo depende de otro
        if depend:
            parent_value = form.data.get(depend) or getattr(instance, f"{depend}_id", None)

            if parent_value:
                model = field.queryset.model
                form.fields[field_name].queryset = model.objects.filter(**{f"{depend}_id": parent_value})
            else:
                form.fields[field_name].queryset = field.queryset.model.objects.none()
            continue

        # Caso 2: el campo se autollenará (cuando se está editando)
        if autoload:
            data_model = field.widget.attrs.get("data-model")
            parent_value = form.data.get(data_model) or getattr(instance, f"{data_model}_id", None)
            
            if parent_value:
                model = field.queryset.model
                form.fields[field_name].queryset = model.objects.filter(**{"id": parent_value})
            continue


