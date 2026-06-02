from django import forms
from .models import Product, Category


class ProductForm(forms.ModelForm):
    """Form tạo/cập nhật sản phẩm"""
    
    class Meta:
        model = Product
        fields = [
            'name',
            'description',
            'category',
            'price_small',
            'price_medium',
            'price_large',
            'image',
            'is_available',
        ]
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True,
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
            }),
            'category': forms.Select(attrs={
                'class': 'form-select',
            }),
            'price_small': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '100',
            }),
            'price_medium': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '100',
            }),
            'price_large': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '0',
                'step': '100',
            }),
            'image': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*',
            }),
            'is_available': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Thêm label để template sử dụng
        self.fields['category'].label = "Danh mục"
        self.fields['category'].empty_label = "-- Chọn danh mục --"
        # Description có thể trống
        self.fields['description'].required = False
    
    def clean_description(self):
        """Đảm bảo description không bị set thành chuỗi rỗng"""
        description = self.cleaned_data.get('description')
        # Nếu người dùng không nhập gì, trả về None thay vì chuỗi rỗng
        if description == '':
            return None
        return description

    def clean(self):
        cleaned_data = super().clean()
        prices = [
            cleaned_data.get('price_small'),
            cleaned_data.get('price_medium'),
            cleaned_data.get('price_large'),
        ]

        if not any(price is not None and price > 0 for price in prices):
            raise forms.ValidationError('Vui lòng nhập ít nhất một giá lớn hơn 0.')

        return cleaned_data
