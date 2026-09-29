from django import forms
from django.db.models import Q
from django.shortcuts import get_object_or_404

from products.models import Prod
from ei.models import Ei

from specifications.models import ProdComponent


class ProdComponentForm(forms.ModelForm):
    class Meta:
        model = ProdComponent
        fields = (
            "component",
            "quantity",
        )
        widgets = {
            "component": forms.Select(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control", "step": "1"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        component = cleaned_data.get("component")
        parent_prod = self.instance.parent_prod if self.instance.pk else None
        # Если это новая форма, parent_prod может быть не задан, но мы его получим из instance
        if component and parent_prod and component.pk == parent_prod.pk:
            raise forms.ValidationError(
                "Изделие не может быть компонентом самого себя."
            )
        if not self.instance.pk:
            cleaned_data["num"] = (
                ProdComponent.objects.filter(parent_prod=parent_prod).count() + 1
            )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(False)
        if "num" in self.cleaned_data:
            instance.num = self.cleaned_data["num"]
        if commit:
            instance.save()
        return instance


class TotalCostRatioForm(forms.Form):
    quantity = forms.DecimalField(
        min_value=0.0,
        initial=1.0,
        required=True,
        label="Количество изделия",
    )

    def __init__(self, ei: Ei | None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if ei:
            ei = get_object_or_404(Ei, pk=ei.pk)
            queryset = Ei.objects.filter(
                Q(main_class=ei.main_class)
                | Q(pk=ei.pk)
                | Q(pk=ei.main_class_id)
            )
            self.fields["ei"] = forms.ModelChoiceField(
                queryset=queryset,
                required=False,
                initial=ei,
                label="Единица измерения",
            )


ProdComponentFormSet = forms.inlineformset_factory(
    Prod,
    ProdComponent,
    form=ProdComponentForm,
    fk_name="parent_prod",
    fields=(
        "component",
        "quantity",
    ),
    extra=1,
    can_delete=True,
)