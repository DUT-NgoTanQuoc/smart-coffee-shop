## 🚀 Hướng dẫn sử dụng Smart Coffee Shop POS

### ✅ Server đang chạy
- **URL**: http://192.168.1.8:8000 hoặc http://127.0.0.1:8000
- **Port**: 8000

---

## 📋 Tài khoản test

### Admin (Quản lý)
- **Username**: admin
- **Password**: 123456
- **Quyền**: Toàn quyền quản lý hệ thống

### Cashier (Thu Ngân)
- **Username**: cashier1 hoặc cashier2
- **Password**: 123456
- **Quyền**: 
  - ✅ Tạo đơn hàng
  - ✅ Xem danh sách đơn hàng
  - ✅ Bảng điều khiển thu ngân

### Barista (Pha chế)
- **Username**: barista1, barista2, barista3, hoặc barista4
- **Password**: 123456
- **Quyền**:
  - ✅ Hàng chờ đơn hàng
  - ✅ Quản lý nguyên liệu
  - ✅ Chi tiết nguyên liệu

### Part-Time
- **Username**: parttime
- **Password**: 123456
- **Quyền**:
  - ✅ Quản lý nguyên liệu

---

## 🔐 Quy trình đăng nhập

1. **Truy cập trang chủ**: Bất kỳ link nào cũng sẽ redirect về trang login
2. **Nhập thông tin**: Username và Password
3. **Xem menu**: Sau đăng nhập, chỉ thấy menu dành cho role của bạn
4. **Sử dụng chức năng**: Mỗi role chỉ có quyền truy cập các chức năng riêng

---

## 📱 Menu theo Role

### Admin Dashboard
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

### Cashier Dashboard
```
┌─ Trang chủ
└─ THU NGÂN
   ├─ Bảng điều khiển
   ├─ Tạo đơn hàng
   └─ Danh sách đơn hàng
```

### Barista Dashboard
```
┌─ Trang chủ
└─ BARISTA
   ├─ Hàng chờ đơn hàng
   ├─ Quản lý nguyên liệu
   └─ Chi tiết nguyên liệu
```

---

## 🎯 Chức năng chính

### ☕ Tạo Đơn Hàng (Cashier)
1. Click "Tạo đơn hàng" trên sidebar
2. Chọn sản phẩm
3. Chọn size (S, M, L)
4. Nhập số lượng
5. Hoàn thành đơn hàng

### 🚀 Xử lý Đơn Hàng (Barista)
1. Click "Hàng chờ đơn hàng"
2. Xem các đơn hàng pending
3. Cập nhật trạng thái: pending → preparing → completed

### 📦 Quản lý Nguyên Liệu
1. Xem danh sách nguyên liệu
2. Thêm nguyên liệu mới
3. Nhập kho khi hết
4. Theo dõi tồn kho

---

## 🔒 Bảo mật

- ✅ Tất cả chức năng đều yêu cầu đăng nhập
- ✅ Menu tự động hiển thị theo role
- ✅ Không thể truy cập chức năng của role khác
- ✅ Logout để kết thúc phiên

---

## 💾 Dữ liệu

- **Cơ sở dữ liệu**: PostgreSQL (coffee_shop)
- **Dữ liệu test**: 20 sản phẩm, 150 đơn hàng, 50 khách hàng
- **Nguyên liệu**: 26 loại nguyên liệu

---

## 🆘 Gặp sự cố?

1. **Không thể đăng nhập**: Kiểm tra username/password ở danh sách trên
2. **Không thấy menu**: Refresh trang hoặc logout → login lại
3. **Lỗi 404**: Đảm bảo server đang chạy
4. **Lỗi 403 (Forbidden)**: Tài khoản này không có quyền truy cập

---

## 📞 Hỗ trợ

- Server đang chạy trên: **http://0.0.0.0:8000**
- Ngôn ngữ giao diện: **Tiếng Việt**
- Hệ thống: **Django 4.2.26 + PostgreSQL**

Chúc bạn sử dụng hệ thống thành công! ☕
