from django import forms

from specifications.models import ProdComponent


class ProdComponentForm(forms.ModelForm):
    class Meta:
        model = ProdComponent
        fields = ('component', 'quantity',)
        widgets = {
            'component': forms.Select(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'step': '1'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        component = cleaned_data.get('component')
        parent_prod = self.instance.parent_prod if self.instance.pk else None
        # Если это новая форма, parent_prod может быть не задан, но мы его получим из instance
        if component and parent_prod and component.pk == parent_prod.pk:
            raise forms.ValidationError("Изделие не может быть компонентом самого себя.")
        if not self.instance.pk:
            cleaned_data["num"] = ProdComponent.objects.filter(parent_prod=parent_prod).count() + 1
        return cleaned_data

    def save(self, commit = True):
        instance = super().save(False)
        if "num" in self.cleaned_data:
            instance.num = self.cleaned_data["num"]
        if commit:
            instance.save()
        return instance
