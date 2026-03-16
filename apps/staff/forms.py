from django import forms
from django.contrib.auth import get_user_model
from django.db.models import Q
from .models import Staff


class StaffForm(forms.ModelForm):
    """Form nhân viên, kèm trường tài khoản đăng nhập"""

    username = forms.CharField(
        max_length=150,
        required=True,
        label="Tên đăng nhập",
        help_text="Dùng để đăng nhập hệ thống",
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )
    password = forms.CharField(
        max_length=128,
        required=False,
        label="Mật khẩu",
        widget=forms.PasswordInput(render_value=False, attrs={"class": "form-control"}),
        help_text="Để trống nếu không đổi mật khẩu",
    )
    password_confirm = forms.CharField(
        max_length=128,
        required=False,
        label="Xác nhận mật khẩu",
        widget=forms.PasswordInput(render_value=False, attrs={"class": "form-control"}),
    )

    class Meta:
        model = Staff
        fields = [
            "name",
            "phone",
            "email",
            "role",
            "salary",
            "hire_date",
            "is_active",
        ]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "role": forms.Select(attrs={"class": "form-select"}),
            "salary": forms.NumberInput(attrs={"class": "form-control", "step": "1000", "min": "0"}),
            "hire_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "is_active": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_hire_date(self):
        # Cho phép để trống khi edit, giữ nguyên giá trị cũ
        hire_date = self.cleaned_data.get("hire_date")
        if not hire_date and self.instance and self.instance.pk:
            return self.instance.hire_date
        return hire_date

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._linked_user = None
        self._allowed_user_ids = set()
        # Tìm user đã/đang gắn với staff hiện tại để phục vụ kiểm tra trùng username
        User = get_user_model()
        candidates = []
        if self.instance and self.instance.pk:
            candidates.extend([getattr(self.instance, "phone", None), getattr(self.instance, "email", None)])
        # initial có thể truyền username hiện tại của tài khoản
        candidates.append(self.initial.get("username"))
        candidates = [c for c in candidates if c]

        email_match = getattr(self.instance, "email", None) if self.instance else None

        if candidates or email_match:
            query = Q(username__in=candidates)
            if email_match:
                query |= Q(email=email_match)
            users = list(User.objects.filter(query))
            if users:
                self._linked_user = users[0]
                self._allowed_user_ids = {u.id for u in users}

    def clean(self):
        cleaned = super().clean()
        pwd = cleaned.get("password")
        pwd2 = cleaned.get("password_confirm")
        if pwd or pwd2:
            if pwd != pwd2:
                raise forms.ValidationError("Mật khẩu xác nhận không khớp")
            if len(pwd) < 4:
                raise forms.ValidationError("Mật khẩu tối thiểu 4 ký tự")

        # Kiểm tra trùng username với user khác
        username = cleaned.get("username")
        if username:
            User = get_user_model()
            existing = User.objects.filter(username=username).first()
            if existing and existing.id not in self._allowed_user_ids:
                raise forms.ValidationError("Tên đăng nhập đã được sử dụng, vui lòng chọn tên khác")
        return cleaned

    def sync_user(self, staff_obj):
        """Tạo/cập nhật tài khoản Django User cho nhân viên (kể cả đổi username).

        Logic mới:
        - Ưu tiên dùng user đã liên kết (self._linked_user)
        - Nếu username mới đang tồn tại ở user khác và khác staff này -> raise để form báo lỗi
        - Nếu username đã tồn tại và thuộc về user hiện tại -> tái sử dụng, không đổi primary key
        """
        User = get_user_model()
        new_username = self.cleaned_data["username"]
        email = self.cleaned_data.get("email") or ""
        password = self.cleaned_data.get("password")

        # Nếu username đã tồn tại thì tái sử dụng user đó để tránh lỗi unique
        existing = User.objects.filter(username=new_username).first()

        # Dùng user đã liên kết nếu có, hoặc user đã tồn tại với username này
        user = self._linked_user or existing
        if not user:
            # fallback tìm theo initial/phone/email
            old_username = self.initial.get("username") or getattr(staff_obj, "phone", None) or ""
            if old_username:
                user = User.objects.filter(username=old_username).first()
            if not user and staff_obj.phone:
                user = User.objects.filter(username=staff_obj.phone).first()
            if not user and staff_obj.email:
                user = User.objects.filter(username=staff_obj.email).first()

        if user:
            # Nếu đổi username, cập nhật
            user.username = new_username
        else:
            user = User(username=new_username)

        # Cập nhật thông tin chung
        user.email = email
        user.first_name = staff_obj.name
        user.is_staff = True
        user.is_superuser = getattr(user, "is_superuser", False) or False
        user.is_active = staff_obj.is_active
        if password:
            user.set_password(password)
        user.save()
        return user
