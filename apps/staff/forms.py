from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import ShiftAssignment, Staff


class StaffForm(forms.ModelForm):
    """Staff form with login account fields."""

    username = forms.CharField(
        max_length=150,
        required=True,
        label='Tên đăng nhập',
        help_text='Dùng để đăng nhập hệ thống',
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        max_length=128,
        required=False,
        label='Mật khẩu',
        widget=forms.PasswordInput(render_value=False, attrs={'class': 'form-control'}),
        help_text='Để trống nếu không đổi mật khẩu',
    )
    password_confirm = forms.CharField(
        max_length=128,
        required=False,
        label='Xác nhận mật khẩu',
        widget=forms.PasswordInput(render_value=False, attrs={'class': 'form-control'}),
    )

    class Meta:
        model = Staff
        fields = [
            'name',
            'phone',
            'email',
            'role',
            'salary',
            'hire_date',
            'is_active',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'salary': forms.NumberInput(attrs={'class': 'form-control', 'step': '1000', 'min': '0'}),
            'hire_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._linked_user = None
        self._allowed_user_ids = set()

        user_model = get_user_model()
        candidates = []
        if self.instance and self.instance.pk:
            candidates.extend([getattr(self.instance, 'phone', None), getattr(self.instance, 'email', None)])
        candidates.append(self.initial.get('username'))
        candidates = [item for item in candidates if item]

        email_match = getattr(self.instance, 'email', None) if self.instance else None
        if candidates or email_match:
            query = Q(username__in=candidates)
            if email_match:
                query |= Q(email=email_match)
            users = list(user_model.objects.filter(query))
            if users:
                self._linked_user = users[0]
                self._allowed_user_ids = {user.id for user in users}

    def clean_hire_date(self):
        hire_date = self.cleaned_data.get('hire_date')
        if not hire_date and self.instance and self.instance.pk:
            return self.instance.hire_date
        return hire_date

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get('password')
        pwd2 = cleaned.get('password_confirm')
        if pwd or pwd2:
            if pwd != pwd2:
                raise forms.ValidationError('Mật khẩu xác nhận không khớp')
            if len(pwd) < 4:
                raise forms.ValidationError('Mật khẩu tối thiểu 4 ký tự')

        username = cleaned.get('username')
        if username:
            user_model = get_user_model()
            existing = user_model.objects.filter(username=username).first()
            if existing and existing.id not in self._allowed_user_ids:
                raise forms.ValidationError('Tên đăng nhập đã được sử dụng, vui lòng chọn tên khác')
        return cleaned

    def sync_user(self, staff_obj):
        """Create/update Django user linked with staff."""
        user_model = get_user_model()
        new_username = self.cleaned_data['username']
        email = self.cleaned_data.get('email') or ''
        password = self.cleaned_data.get('password')

        existing = user_model.objects.filter(username=new_username).first()
        user = self._linked_user or existing

        if not user:
            old_username = self.initial.get('username') or getattr(staff_obj, 'phone', None) or ''
            if old_username:
                user = user_model.objects.filter(username=old_username).first()
            if not user and staff_obj.phone:
                user = user_model.objects.filter(username=staff_obj.phone).first()
            if not user and staff_obj.email:
                user = user_model.objects.filter(username=staff_obj.email).first()

        if user:
            user.username = new_username
        else:
            user = user_model(username=new_username)

        user.email = email
        user.first_name = staff_obj.name
        user.is_staff = True
        user.is_superuser = getattr(user, 'is_superuser', False) or False
        user.is_active = staff_obj.is_active
        if password:
            user.set_password(password)
        user.save()
        return user


class ShiftAssignmentForm(forms.ModelForm):
    """Shift assignment form with duplicate validation."""

    class Meta:
        model = ShiftAssignment
        fields = [
            'staff',
            'work_date',
            'shift',
            'start_time',
            'end_time',
            'hourly_rate',
            'note',
        ]
        widgets = {
            'staff': forms.Select(attrs={'class': 'form-select'}),
            'work_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'shift': forms.Select(attrs={'class': 'form-select'}),
            'start_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'hourly_rate': forms.NumberInput(
                attrs={'class': 'form-control', 'step': '1000', 'min': '0', 'placeholder': 'VD: 30000'}
            ),
            'note': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ghi chú (nếu có)'}),
        }

    def clean(self):
        cleaned = super().clean()
        staff = cleaned.get('staff')
        work_date = cleaned.get('work_date')
        shift = cleaned.get('shift')
        if staff and work_date and shift:
            qs = ShiftAssignment.objects.filter(staff=staff, work_date=work_date, shift=shift)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError('Nhân viên này đã được phân cho ca này trong ngày đã chọn.')
        return cleaned
