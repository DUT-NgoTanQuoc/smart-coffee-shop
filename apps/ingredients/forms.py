from decimal import Decimal

from django import forms

from .models import Ingredient


class IngredientForm(forms.ModelForm):
    """Form tạo/cập nhật nguyên liệu với validation số không âm"""

    class Meta:
        model = Ingredient
        fields = [
            'name',
            'unit',
            'quantity',
            'min_quantity',
            'price_per_unit',
            'supplier',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'required': True}),
            'unit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'g, ml, cái,...', 'required': True}),
            'supplier': forms.TextInput(attrs={'class': 'form-control'}),
            'quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'min_quantity': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '0.01'}),
            'price_per_unit': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'step': '100'}),
        }

    def clean_quantity(self):
        value = self.cleaned_data.get('quantity')
        if value is None:
            value = Decimal('0')
        if value < 0:
            raise forms.ValidationError('Số lượng không được âm')
        return value

    def clean_min_quantity(self):
        value = self.cleaned_data.get('min_quantity')
        if value is None:
            value = Decimal('0')
        if value < 0:
            raise forms.ValidationError('Mức tối thiểu không được âm')
        return value

    def clean_price_per_unit(self):
        value = self.cleaned_data.get('price_per_unit')
        if value is None:
            value = Decimal('0')
        if value < 0:
            raise forms.ValidationError('Giá không được âm')
        return value


class IngredientRestockForm(forms.Form):
    quantity = forms.DecimalField(
        min_value=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'min': '0.01', 'step': '0.01'}),
        label='Số lượng nhập thêm'
    )

    def clean_quantity(self):
        value = self.cleaned_data['quantity']
        if value <= 0:
            raise forms.ValidationError('Số lượng nhập phải lớn hơn 0')
        return value
