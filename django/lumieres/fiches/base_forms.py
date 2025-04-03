from django import forms

class NoteFormBase(forms.ModelForm):
    class Meta:
        model = None
        fields = '__all__'
