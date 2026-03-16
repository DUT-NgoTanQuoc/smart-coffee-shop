# ☕ Smart Coffee Shop POS - Hướng dẫn sử dụng

## 🚀 Bắt đầu

### Server đang chạy
- **URL**: http://127.0.0.1:8000
- **Port**: 8000
- **Database**: PostgreSQL (coffee_shop)

## 📝 Tài khoản Test

| Role | Username | Password | Quyền |
|------|----------|----------|-------|
| **Admin** | admin | 123456 | Quản lý toàn bộ hệ thống |
| **Cashier** | cashier1<br>cashier2 | 123456 | Tạo đơn hàng, xem danh sách |
| **Barista** | barista1<br>barista2<br>barista3<br>barista4 | 123456 | Xử lý đơn hàng, quản lý nguyên liệu |
| **Part-time** | parttime | 123456 | Quản lý nguyên liệu |

## 🔐 Quy trình Đăng nhập

1. **Truy cập trang chủ**
   ```
   http://127.0.0.1:8000
   ```

2. **Thấy sidebar với nút Đăng nhập**
   - Sidebar hiển thị ngay cả khi chưa login
   - Click nút "Đăng nhập" hoặc truy cập link bất kỳ sẽ chuyển về login

3. **Nhập thông tin đăng nhập**
   - Username: Chọn từ bảng trên
   - Password: 123456
   - Click "Đăng nhập"

4. **Menu tự động thay đổi theo role**
   - **Admin**: Thấy toàn bộ menu
   - **Cashier**: Chỉ thấy menu "THU NGÂN"
   - **Barista**: Chỉ thấy menu "BARISTA"
   - **Part-time**: Chỉ thấy menu "PART-TIME"

## 📱 Menu theo Role

### 👤 Admin
```
┌─ Trang chủ
├─ DASHBOARDS
│  └─ Admin Dashboard
├─ QUẢN LÝ HỆ THỐNG
│  ├─ Tất cả đơn hàng
│  ├─ Sản phẩm
│  ├─ Nguyên liệu
│  ├─ Khách hàng
│  └─ Nhân viên
└─ PHÂN TÍCH AI
   ├─ Dự đoán doanh thu
   ├─ Dự đoán tồn kho
   └─ Xu hướng
```

### 💵 Cashier (Thu Ngân)
```
┌─ Trang chủ
└─ THU NGÂN
   ├─ Bảng điều khiển (Dashboard)
   ├─ Tạo đơn hàng (POS)
   └─ Danh sách đơn hàng
```

### ☕ Barista (Pha chế)
```
┌─ Trang chủ
└─ BARISTA
   ├─ Hàng chờ đơn hàng (Queue)
   ├─ Quản lý nguyên liệu (Tracking)
   └─ Chi tiết nguyên liệu (Inventory)
```

### 🕐 Part-time
```
┌─ Trang chủ
└─ PART-TIME
   └─ Quản lý nguyên liệu
```

## 🎯 Chức năng chính

### 1️⃣ Tạo Đơn Hàng (Cashier)
**Menu**: THU NGÂN → Tạo đơn hàng

1. Chọn sản phẩm từ danh sách
2. Chọn size (S/M/L)
3. Nhập số lượng
4. Click "Thêm vào giỏ"
5. Nhập thông tin khách hàng
6. Click "Hoàn thành đơn hàng"

**Trạng thái đơn**: Pending → Preparing → Completed

### 2️⃣ Xử lý Đơn Hàng (Barista)
**Menu**: BARISTA → Hàng chờ đơn hàng

1. Xem danh sách đơn hàng pending
2. Click vào đơn để xem chi tiết
3. Cập nhật trạng thái:
   - Pending → Preparing (bắt đầu pha)
   - Preparing → Completed (hoàn thành)
4. Xem công thức pha (recipe)
5. Quản lý nguyên liệu sử dụng

### 3️⃣ Quản lý Nguyên liệu
**Menu**: BARISTA → Quản lý nguyên liệu

#### Xem tồn kho
- Danh sách tất cả nguyên liệu
- Tồn kho hiện tại
- Mức tối thiểu
- Giá/đơn vị
- Trạng thái (Còn hàng/Sắp hết)

#### Nhập kho
- Click nút "+" để nhập thêm
- Nhập số lượng
- Ghi nhận tự động

#### Sửa thông tin
- Click nút "Sửa" để cập nhật:
  - Tên, đơn vị
  - Số lượng hiện tại
  - Mức tối thiểu
  - Giá

### 4️⃣ Quản lý Sản phẩm (Admin)
**Menu**: QUẢN LÝ HỆ THỐNG → Sản phẩm

1. **Xem danh sách**: Tất cả sản phẩm hiện có
2. **Thêm mới**: 
   - Tên, mô tả, category
   - Giá S/M/L
   - Upload hình ảnh
3. **Sửa thông tin**: Click vào sản phẩm, chỉnh sửa
4. **Xóa**: Xóa sản phẩm khỏi hệ thống

**Lưu ý**: Mô tả sản phẩm không được mất khi sửa (đã fix!)

## 🔧 Tính năng đã sửa

### 1. ✅ Lỗi NoReverseMatch (ingredient_edit)
- **Vấn đề**: Template gọi URL name sai
- **Fix**: Cập nhật URL name từ 'ingredient_edit' → 'ingredient_update'
- **Kết quả**: Barista dashboard không còn báo lỗi

### 2. ✅ Sidebar ẩn khi chưa login
- **Vấn đề**: Sidebar bị ẩn trên trang login
- **Fix**: Cập nhật template để luôn hiển thị sidebar
- **Kết quả**: Sidebar visible với nút "Đăng nhập" rõ ràng

### 3. ✅ Role-Based Menu
- **Vấn đề**: Menu hiển thị không đúng theo role
- **Fix**: Thêm context processor để lấy user account role
- **Kết quả**: Mỗi role chỉ thấy menu dành cho mình

### 4. ✅ Form sản phẩm - Mô tả không mất
- **Vấn đề**: Sửa sản phẩm không thay đổi → mô tả bị mất
- **Fix**: Dùng Django ModelForm thay vì POST thủ công
- **Kết quả**: Chỉ cập nhật các field thay đổi, giữ lại cũ

## 💾 Dữ liệu có sẵn

| Tập dữ liệu | Số lượng |
|------------|---------|
| Sản phẩm | 20 |
| Đơn hàng | 150 |
| Khách hàng | 50 |
| Nguyên liệu | 26 |
| Tài khoản | 8 |

## 🆘 Gặp sự cố?

### 1. Không thể đăng nhập
- **Kiểm tra**: Username/password từ bảng
- **Thử lại**: Refresh trang, xóa cache
- **Mật khẩu**: Luôn là 123456 cho tất cả test account

### 2. Lỗi 404 - Trang không tìm thấy
- **Kiểm tra**: Server có đang chạy không?
- **Start lại**: `python manage.py runserver 0.0.0.0:8000`
- **Xem logs**: Kiểm tra terminal nơi server chạy

### 3. Lỗi 403 - Forbidden
- **Nguyên nhân**: Tài khoản không có quyền truy cập
- **Giải pháp**: Đăng nhập bằng tài khoản khác với quyền phù hợp

### 4. Menu không thay đổi sau login
- **Thử**: Refresh trang (F5 hoặc Ctrl+R)
- **Logout rồi login lại**
- **Clear browser cache**

### 5. Mô tả sản phẩm bị mất
- **Đã fix**: Dùng Django Forms
- **Cách dùng**: Click sản phẩm → sửa → không thay đổi mô tả → lưu
- **Kết quả**: Mô tả sẽ được giữ lại

## 📊 Thống kê

### Hôm nay
- Xem trên Admin Dashboard
- Doanh thu
- Số đơn hàng
- Số khách hàng

### Xu hướng
- Menu: PHÂN TÍCH AI → Xu hướng
- Xem biểu đồ bán hàng theo thời gian

### Dự đoán
- **Doanh thu**: Dự đoán doanh thu tương lai
- **Tồn kho**: Dự đoán nguyên liệu cần mua

## 🔒 Bảo mật

- ✅ Tất cả chức năng yêu cầu đăng nhập
- ✅ Menu tự động ẩn theo role
- ✅ Backend kiểm tra permission
- ✅ Session timeout
- ✅ Password hashing

## 📞 Hỗ trợ

- **Server**: http://0.0.0.0:8000
- **Ngôn ngữ**: Tiếng Việt
- **Framework**: Django 4.2.26
- **Database**: PostgreSQL

---

**Chúc bạn sử dụng hệ thống thành công! ☕**
