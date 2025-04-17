from django import forms
from .models.person import Person

# class PersonField(forms.Field):
#     """
#     A stub for PersonField. Extend this as needed.
#     """
#     pass

# class PersonWidget(forms.Widget):
#     """
#     A stub for PersonWidget. Extend this as needed.
#     """
#     def render(self, name, value, attrs=None, renderer=None):
#         return super().render(name, value, attrs, renderer)

# from django import forms
# #from .models import Person  # Assuming Person is the model you want to reference

class MultiplePersonField(forms.ModelMultipleChoiceField):
    """
    A custom field for handling multiple person-related data.
    """

    def __init__(self, *args, **kwargs):
        # Ensure you pass the queryset here, assuming you want to use the Person model
        if 'queryset' not in kwargs:
            kwargs['queryset'] = Person.objects.all()
        kwargs.setdefault('widget', forms.CheckboxSelectMultiple)
        super().__init__(*args, **kwargs)

    def clean(self, value):
        """
        Custom cleaning logic for the field.
        """
        cleaned_value = super().clean(value)
        if not cleaned_value:
            raise forms.ValidationError("You must select at least one person.")
        return cleaned_value

