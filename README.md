# ☕ Smart Coffee Shop Management System

Hệ thống quản lý quán cafe thông minh với tích hợp AI cho dự đoán kinh doanh.

## 🌟 Tính năng nổi bật

### 📊 AI & Analytics
- **Dự đoán doanh thu**: Sử dụng Linear Regression để dự đoán doanh thu 7-30 ngày tới
- **Dự đoán tồn kho**: Tính toán mức tiêu thụ và đề xuất nhập hàng tự động
- **Phân tích xu hướng**: Sản phẩm bán chạy, giờ cao điểm, phân tích khách hàng

### 💼 Quản lý nghiệp vụ
- **POS System**: Giao diện bán hàng trực quan, hỗ trợ tùy chỉnh sản phẩm
- **Quản lý sản phẩm**: CRUD đầy đủ, quản lý công thức pha chế
- **Quản lý kho**: Tự động trừ nguyên liệu, cảnh báo sắp hết hàng
- **Quản lý khách hàng**: Hệ thống tích điểm và nâng cấp hạng tự động
- **Quản lý nhân viên**: Chấm công, phân quyền theo vai trò

### 🤖 Tự động hóa
- ✅ Tự động tạo mã đơn hàng: `ORD{YYYYMMDD}{001}`
- ✅ Tự động cập nhật điểm khách hàng khi hoàn thành đơn
- ✅ Tự động nâng cấp hạng thành viên (Đồng → Bạc → Vàng → Kim cương)
- ✅ Tự động trừ nguyên liệu khi hoàn thành đơn
- ✅ Tự động cập nhật thống kê hàng ngày

## 🛠️ Công nghệ sử dụng

### Backend
- **Django 4.2.26 (security patched)**: Web framework
- **PostgreSQL/SQLite**: Database
- **Django REST Framework**: API

### AI & Data Science
- **scikit-learn**: Machine Learning (Linear Regression)
- **pandas**: Data manipulation
- **numpy**: Numerical computing

### Frontend
- **Bootstrap 5**: UI Framework
- **Chart.js**: Data visualization
- **Bootstrap Icons**: Icon library

## 📁 Cấu trúc dự án

```
smart-coffee-shop/
├── manage.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── config/                 # Django settings
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/                   # Django apps
│   ├── products/          # Quản lý sản phẩm
│   ├── ingredients/       # Quản lý nguyên liệu
│   ├── customers/         # Quản lý khách hàng
│   ├── staff/            # Quản lý nhân viên
│   ├── orders/           # Quản lý đơn hàng & POS
│   ├── analytics/        # Phân tích & AI
│   │   └── ml_models/    # AI models
│   │       ├── revenue_predictor.py
│   │       ├── stock_predictor.py
│   │       └── trend_analyzer.py
│   └── core/             # Utilities
├── templates/            # HTML templates
├── static/              # Static files (CSS, JS)
├── media/               # User uploads
└── database/            # SQL schema
```

## 🚀 Cài đặt & Chạy

### 1. Clone repository

```bash
git clone https://github.com/DUT-NgoTanQuoc/smart-coffee-shop.git
cd smart-coffee-shop
```

### 2. Tạo môi trường ảo và cài đặt dependencies

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Cài đặt packages
pip install -r requirements.txt
```

### 3. Cấu hình Database

#### Option A: SQLite (Đơn giản, cho development)
```bash
# Sử dụng SQLite mặc định, không cần cấu hình gì
python manage.py migrate
```

#### Option B: PostgreSQL (Khuyến nghị cho production)

1. Cài đặt PostgreSQL
2. Tạo database:
```sql
CREATE DATABASE coffee_shop;
CREATE USER postgres WITH PASSWORD 'password';
GRANT ALL PRIVILEGES ON DATABASE coffee_shop TO postgres;
```

3. Uncomment phần PostgreSQL trong `config/settings.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'coffee_shop',
        'USER': 'postgres',
        'PASSWORD': 'password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

4. Chạy migration:
```bash
python manage.py migrate
```

### 4. Tạo superuser

```bash
python manage.py createsuperuser
```

### 5. Chạy development server

```bash
python manage.py runserver
```

Truy cập: `http://127.0.0.1:8000`

## 📚 Hướng dẫn sử dụng

### 1. Đăng nhập Admin
- URL: `http://127.0.0.1:8000/admin/`
- Đăng nhập bằng superuser đã tạo

### 2. Thêm dữ liệu mẫu
1. **Thêm Categories**: Cà phê, Trà, Smoothie, Bánh ngọt
2. **Thêm Ingredients**: Cà phê, Sữa, Đường, Đá, v.v.
3. **Thêm Products**: Với giá theo size S/M/L
4. **Thêm Recipes**: Định nghĩa nguyên liệu cho mỗi sản phẩm
5. **Thêm Customizations**: Đường, Đá, Topping
6. **Thêm Customers**: Khách hàng với số điện thoại
7. **Thêm Staff**: Nhân viên với role

### 3. Sử dụng POS
1. Truy cập: `http://127.0.0.1:8000/orders/create/`
2. Click vào sản phẩm để thêm vào giỏ
3. Nhập số điện thoại khách hàng (nếu có)
4. Chọn phương thức thanh toán
5. Click "Thanh toán"

### 4. Xem Analytics
- **Dashboard**: Tổng quan hệ thống
- **Dự đoán doanh thu**: AI dự đoán doanh thu tương lai
- **Dự đoán tồn kho**: Cảnh báo nguyên liệu sắp hết
- **Xu hướng**: Phân tích sản phẩm bán chạy, giờ cao điểm

## 🤖 Chi tiết AI Models

### 1. Revenue Predictor
**File**: `apps/analytics/ml_models/revenue_predictor.py`

**Thuật toán**: Linear Regression (scikit-learn)

**Chức năng**:
- Huấn luyện trên dữ liệu lịch sử từ `DailyStat`
- Dự đoán doanh thu 7-30 ngày tới
- Trả về dữ liệu cho Chart.js

**Cách sử dụng**:
```python
from apps.analytics.ml_models import RevenuePredictor

predictor = RevenuePredictor()
prediction = predictor.predict(days_ahead=7)
summary = predictor.get_summary()
```

### 2. Stock Predictor
**File**: `apps/analytics/ml_models/stock_predictor.py`

**Chức năng**:
- Tính mức tiêu thụ trung bình theo ngày
- Dự đoán ngày hết hàng
- Phân loại mức độ ưu tiên: HIGH (≤3 ngày), MEDIUM (≤7 ngày), LOW (>7 ngày)
- Đề xuất số lượng cần nhập

**Cách sử dụng**:
```python
from apps.analytics.ml_models import StockPredictor

predictor = StockPredictor()
predictions = predictor.predict_all_ingredients()
alerts = predictor.get_low_stock_alerts()
```

### 3. Trend Analyzer
**File**: `apps/analytics/ml_models/trend_analyzer.py`

**Chức năng**:
- Top sản phẩm bán chạy
- Phân tích giờ cao điểm (heatmap)
- Top khách hàng
- Phân bố hạng thành viên
- Hiệu suất theo danh mục
- Doanh số theo size

**Cách sử dụng**:
```python
from apps.analytics.ml_models import TrendAnalyzer

analyzer = TrendAnalyzer()
bestsellers = analyzer.get_bestselling_products(limit=10)
peak_hours = analyzer.get_peak_hours()
customer_insights = analyzer.get_customer_insights()
```

## 🔐 Phân quyền

Hệ thống có 4 vai trò nhân viên:

1. **Manager**: Toàn quyền quản lý
2. **Cashier**: Thu ngân, tạo đơn hàng
3. **Barista**: Pha chế
4. **Server**: Phục vụ

Sử dụng decorator `@role_required`:
```python
from apps.core.decorators import role_required

@role_required('manager', 'cashier')
def my_view(request):
    # Chỉ manager và cashier mới truy cập được
    pass
```

## 📊 Database Schema

Hệ thống có 13 bảng chính:

1. **categories**: Danh mục sản phẩm
2. **products**: Sản phẩm (với 3 size)
3. **recipes**: Công thức pha chế
4. **customizations**: Tùy chỉnh (đường, đá, topping)
5. **ingredients**: Nguyên liệu
6. **customers**: Khách hàng (với điểm và hạng)
7. **favorite_drinks**: Đồ uống yêu thích
8. **staff**: Nhân viên
9. **work_logs**: Chấm công
10. **orders**: Đơn hàng
11. **order_items**: Chi tiết đơn hàng
12. **payments**: Thanh toán
13. **daily_stats**: Thống kê hàng ngày

Chi tiết xem file: `database/schema.sql`

## 🎯 Hệ thống tích điểm

### Quy tắc tích điểm:
- 1 điểm = 10,000đ
- Điểm được cộng tự động khi đơn hàng hoàn thành

### Hạng thành viên:
| Hạng | Điểm yêu cầu | Giảm giá |
|------|--------------|----------|
| Đồng | 0 - 499 | 0% |
| Bạc | 500 - 1,999 | 5% |
| Vàng | 2,000 - 4,999 | 10% |
| Kim cương | ≥ 5,000 | 15% |

Hạng được nâng cấp tự động thông qua Django Signals.

## 🔧 API Endpoints (Optional)

Nếu sử dụng Django REST Framework:

```
GET  /api/products/              # Danh sách sản phẩm
GET  /api/products/{id}/         # Chi tiết sản phẩm
GET  /api/customers/             # Danh sách khách hàng
GET  /api/orders/                # Danh sách đơn hàng
POST /api/orders/                # Tạo đơn hàng
GET  /api/analytics/revenue/     # Dữ liệu doanh thu
GET  /api/analytics/stock/       # Dự đoán tồn kho
```

## 📸 Screenshots

_(Sẽ được thêm sau khi triển khai)_

- Dashboard
- POS Interface
- Revenue Forecast
- Stock Prediction
- Trends Analysis

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📝 License

This project is licensed under the MIT License.

## 👨‍💻 Author

**Ngo Tan Quoc**
- GitHub: [@DUT-NgoTanQuoc](https://github.com/DUT-NgoTanQuoc)
- Email: your-email@example.com

## 🙏 Acknowledgments

- Django Documentation
- scikit-learn Documentation
- Bootstrap Team
- Chart.js Team

---

**Phát triển cho đồ án tốt nghiệp - 2024**