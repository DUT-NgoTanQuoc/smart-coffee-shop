# HUONG DAN CAI DAT - CHAY - TEST DAY DU SMART COFFEE SHOP

Tai lieu nay dung de ban cua ban clone project, chay duoc ngay, va test day du tat ca chuc nang hien co.

## 1) Moi truong va cai dat

Yeu cau:
- Python 3.10+ (khuyen nghi 3.11)
- Git
- Windows PowerShell hoac Terminal bat ky

Cac buoc:

```bash
git clone https://github.com/DUT-NgoTanQuoc/smart-coffee-shop.git
cd smart-coffee-shop

python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
# source .venv/bin/activate

pip install -r requirements.txt
python manage.py migrate
```

Luu y:
- Project dang cau hinh `USE_SQLITE=true` mac dinh trong `config/settings.py`.
- Repo da co san `db.sqlite3` voi du lieu demo. Khong can tao data tu dau neu chi can test nhanh.

## 2) Chay chuong trinh

```bash
python manage.py runserver 127.0.0.1:8000
```

Mo trinh duyet:
- `http://127.0.0.1:8000`

Khong dung `http://0.0.0.0:8000` tren browser vi co the bao loi khong hop le dia chi.

## 3) Tai khoan test co san

Tai khoan custom (dang nhap qua `/accounts/login/`):
- `admin` / `123456`
- `cashier1` / `123456`
- `barista1` / `123456`
- `barista2` / `123456`

Neu mat khau bi lech, reset tat ca password ve `123456`:

```bash
python reset_passwords.py
```

Neu gap loi CSRF luc dang nhap:
- Tai lai trang login bang `Ctrl+F5`
- Dang nhap lai

## 4) Kiem tra du lieu truoc khi test

Chay lenh nhanh:

```bash
python manage.py shell -c "from apps.products.models import Product; from apps.ingredients.models import Ingredient; from apps.customers.models import Customer; from apps.staff.models import Staff, ShiftAssignment; from apps.orders.models import Order, DiscountCode; from apps.core.models import Account; print('products', Product.objects.count()); print('ingredients', Ingredient.objects.count()); print('customers', Customer.objects.count()); print('staff', Staff.objects.count()); print('assignments', ShiftAssignment.objects.count()); print('orders', Order.objects.count()); print('discount_codes', DiscountCode.objects.count()); print('accounts', Account.objects.count())"
```

Neu ban muon them rat nhieu du lieu giong that:

```bash
python scripts/seed_realistic_data.py
```

## 5) Danh sach tinh nang hien co (de doi chieu khi test)

- Dang nhap/dang xuat theo role
- Dashboard admin hop nhat (Tong quan + AI phan tich + Ton kho)
- POS tao don + ap ma giam gia theo code
- Tim khach hang theo SDT
- Quan ly don hang + chi tiet don
- Cap nhat trang thai don qua API
- Barista dashboard (hang doi, mon trong don, cong thuc, hoan thanh don)
- Quan ly san pham (CRUD)
- Quan ly nguyen lieu (list/filter/create/update/restock)
- Trang Goi y & Du bao nguyen lieu thang sau
- Quan ly khach hang (list/filter/search/create/detail)
- Quan ly nhan vien (list/filter/create/update/delete/detail)
- Lich phan ca FullCalendar (month/week/day, filter nhan vien, CRUD JSON)
- Canh bao du nguoi/thieu nguoi theo ca
- Cham cong theo thang
- Tong hop luong theo gio theo thang
- Trang analytics legacy: revenue forecast, stock prediction, trends
- Signal tu dong khi don chuyen completed:
  - Cong diem khach hang
  - Tru ton kho theo recipe
  - Cap nhat daily stats

## 6) Test case chi tiet (UI + API)

### 6.1 Authentication va phan quyen

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| AUTH-01 | Dang nhap admin | Login `admin/123456` | Dang nhap thanh cong, redirect `/'` |
| AUTH-02 | Dang nhap cashier | Login `cashier1/123456` | Redirect sang `/orders/create/` |
| AUTH-03 | Dang nhap barista | Login `barista1/123456` | Redirect sang `/orders/dashboard/barista/` |
| AUTH-04 | Dang xuat | Bam Dang xuat | Ve `/accounts/login/` |
| AUTH-05 | Sai mat khau | Nhap sai password | Bao loi dang nhap khong dung |
| AUTH-06 | CSRF login | Login o tab cu sau khi dang nhap tab khac | He thong huong dan reload login (khong vo trang 403 tho) |

### 6.2 Dashboard admin hop nhat

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| DASH-01 | Load dashboard | Login admin, vao `/` | Hien card tong quan + bieu do doanh thu |
| DASH-02 | Tab AI | Chuyen tab `AI phan tich` | Hien cac chart gio cao diem, danh muc, tier KH |
| DASH-03 | Tab Ton kho | Chuyen tab `Ton kho` | Hien bang canh bao + chart so sanh ton/khuyen nghi |
| DASH-04 | Legacy admin dashboard | Vao `/orders/dashboard/admin/` | Redirect ve dashboard hop nhat `/` |

### 6.3 POS va don hang

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| POS-01 | Tao don co 1 mon | Vao `/orders/create/`, chon mon, bam Thanh toan | Tao don thanh cong, co ma `ORD...` |
| POS-02 | Tang/giam so luong | Tang so luong trong gio | Tong tien cap nhat dung |
| POS-03 | Tim KH co ton tai | Nhap SDT KH co san, bam tim | Hien ten/tier/diem KH |
| POS-04 | Tim KH khong ton tai | SDT la | Bao khong tim thay |
| POS-05 | Ma giam gia hop le | Nhap code VD `KHAITRUONG10` | Hien % giam, tien giam, final amount dung |
| POS-06 | Ma giam gia sai | Nhap code sai | Bao loi ma khong hop le |
| POS-07 | Ma giam gia khong du dieu kien min order | Gio nho hon min_order_amount cua ma | Bao loi dung dieu kien |
| POS-08 | Cart rong | Bam Thanh toan khi cart rong | He thong chan va bao loi |
| POS-09 | Don vua tao hien o danh sach | Vao `/orders/list/` | Don moi xuat hien dau list |
| POS-10 | Chi tiet don | Bam xem chi tiet don | Hien item, payment, tong/discount/final |

### 6.4 API don hang quan trong

| ID | Muc tieu | Endpoint | Ky vong |
|---|---|---|---|
| API-ORD-01 | Validate discount | `GET /orders/validate-discount/?code=...&total=...` | JSON co `valid=true/false`, thong diep ro |
| API-ORD-02 | Search customer | `GET /orders/search-customer/?phone=...` | JSON co `found=true/false` |
| API-ORD-03 | Update status hop le | `POST /orders/api/<id>/status/` -> `preparing/completed` | `success=true`, status thay doi |
| API-ORD-04 | Update status sai transition | completed -> pending | `400`, thong bao khong cho transition |
| API-ORD-05 | Unauthorized update status | Dang nhap role khong du quyen goi API | `403 Unauthorized` |

### 6.5 Barista dashboard

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| BAR-01 | Xem hang doi | Vao `/orders/dashboard/barista/` | O 1 hien don pending/preparing |
| BAR-02 | Chon don xem mon | Bam mot don | O 2 hien danh sach mon |
| BAR-03 | Chon mon xem cong thuc | Bam 1 mon trong O 2 | O 3 hien nguyen lieu/so luong |
| BAR-04 | Hoan thanh don | Bam `Hoan thanh` | Don bien mat khoi O 1 va vao O 4 sau reload |
| BAR-05 | Queue API | `GET /orders/dashboard/barista/queue/` | JSON tra danh sach don cho pha che |

### 6.6 San pham

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| PROD-01 | Xem list | Vao `/products/` | Hien danh sach + category filter |
| PROD-02 | Loc category | Chon category va Loc | Chi hien san pham category do |
| PROD-03 | Tao moi | `/products/create/`, nhap thong tin | Tao thanh cong va redirect detail |
| PROD-04 | Cap nhat | Vao sua 1 san pham | Du lieu duoc cap nhat |
| PROD-05 | Xoa san pham | Vao xoa + confirm | Ban ghi bi xoa khoi list |
| PROD-06 | Detail san pham | Vao trang detail | Hien recipe lien quan (neu co) |

### 6.7 Nguyen lieu + du bao

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| ING-01 | Danh sach nguyen lieu | Vao `/ingredients/` | Hien list ton kho |
| ING-02 | Loc sap het | Tick `Chi hien thi nguyen lieu sap het` | Chi con item ton <= min |
| ING-03 | Tao nguyen lieu | `/ingredients/create/` | Tao thanh cong |
| ING-04 | Validate so am | Nhap quantity/min/price am | Form bao loi |
| ING-05 | Cap nhat nguyen lieu | Sua 1 item | Luu thanh cong |
| ING-06 | Nhap kho (restock) | Bam nut restock, nhap so > 0 | Ton kho tang, co message thanh cong |
| ING-07 | Restock so <= 0 | Nhap 0 hoac am | Bi chan va bao loi |
| ING-08 | Trang goi y du bao | Vao `/ingredients/forecast/` | Hien goi y nhap thang sau + chart |

### 6.8 Khach hang

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| CUS-01 | Danh sach KH | Vao `/customers/` | Hien list theo diem |
| CUS-02 | Tim kiem | Search theo ten/SDT | Ket qua loc dung |
| CUS-03 | Loc theo tier | Chon Bac/Vang/... | Ket qua loc dung |
| CUS-04 | Tao KH moi | `/customers/create/` | Tao thanh cong, vao detail |
| CUS-05 | Trung SDT | Tao KH voi SDT da ton tai | Bao loi unique |

### 6.9 Nhan vien

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| STAFF-01 | Danh sach NV | Vao `/staff/` | Hien list day du |
| STAFF-02 | Loc role/trang thai | Dung filter role + is_active | Loc dung |
| STAFF-03 | Tao NV + account | `/staff/create/` + username/password | Tao thanh cong, login duoc bang account moi |
| STAFF-04 | Validate password confirm | Nhap password va confirm khac nhau | Bao loi |
| STAFF-05 | Validate password min length | Nhap <4 ky tu | Bao loi |
| STAFF-06 | Username duplicate | Tao NV voi username trung | Bao loi username da dung |
| STAFF-07 | Sua NV | `/staff/<id>/edit/` | Cap nhat du lieu thanh cong |
| STAFF-08 | Xoa NV | `/staff/<id>/delete/` | NV bi xoa khoi list |
| STAFF-09 | Detail NV | `/staff/<id>/` | Hien thong tin + cham cong + phan ca gan day |

### 6.10 Lich phan ca (calendar)

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| SCH-01 | Mo trang lich | Vao `/staff/schedule/` | Hien FullCalendar + panel phan ca nhanh |
| SCH-02 | Chuyen view ngay/tuan/thang | Dung toolbar calendar | Du lieu event van hien dung |
| SCH-03 | Loc theo nhan vien | Chon 1 nhan vien trong bo loc | Event hien theo bo loc |
| SCH-04 | Click ngay de prefill form | Click vao ngay tren lich | Field `Ngay lam` duoc dien |
| SCH-05 | Tao phan ca moi | Dien form va Luu | Tao thanh cong, event refresh khong reload trang |
| SCH-06 | Sua phan ca | Click event -> panel -> Sửa | Cap nhat thanh cong |
| SCH-07 | Xoa phan ca | Click event -> panel -> Xóa | Xoa thanh cong |
| SCH-08 | Chan duplicate | Tao 2 ban ghi cung staff + work_date + shift | Form/API tra loi loi duplicate |
| SCH-09 | Canh bao thieu/du nguoi | Tao it hon min hoac nhieu hon max | Event doi mau + warning dung |
| SCH-10 | JSON events API | `GET /staff/schedule/api/events/?start=...&end=...` | Tra mang JSON event co `extendedProps` |

### 6.11 Cham cong va tong hop luong

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| PAY-01 | Trang cham cong | `/staff/attendance/?month=...&year=...` | Hien work_logs theo thang |
| PAY-02 | Trang tong hop luong | `/staff/payroll/?month=...&year=...` | Hien total assigned, actual, payroll |
| PAY-03 | Monthly shift totals helper | Doi thang/nam | So ca, so gio, luong uoc tinh cap nhat dung |

### 6.12 Analytics legacy pages

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| ANA-01 | Revenue forecast | `/analytics/revenue-forecast/?days=7` | Hien du bao doanh thu |
| ANA-02 | Stock prediction | `/analytics/stock-prediction/` | Hien danh sach du bao ton kho |
| ANA-03 | Trends | `/analytics/trends/?days=30` | Hien phan tich xu huong |

### 6.13 Kiem thu integration quan trong

| ID | Muc tieu | Buoc test | Ket qua mong doi |
|---|---|---|---|
| INT-01 | Signal cong diem | Tao don completed co customer | `customer.points` tang |
| INT-02 | Signal tru ton kho | Don completed co recipe | `ingredient.quantity` giam |
| INT-03 | Signal daily stats | Don completed | `DailyStat.total_orders` +1, `total_revenue` tang |

## 7) Payload mau cho API phan ca (JSON CRUD)

Tao moi:

```json
POST /staff/schedule/api/create/
{
  "staff": 11,
  "work_date": "2026-05-10",
  "shift": "morning",
  "start_time": "07:00",
  "end_time": "12:00",
  "hourly_rate": "32000",
  "note": "Ca mo cua"
}
```

Cap nhat:

```json
POST /staff/schedule/api/123/update/
{
  "hourly_rate": "35000",
  "note": "Da dieu chinh"
}
```

Xoa:

```json
POST /staff/schedule/api/123/delete/
```

## 8) Kich ban smoke test nhanh 10 phut (goi y)

1. Login `admin/123456`.
2. Mo dashboard, check 3 tab (Tong quan, AI, Ton kho).
3. Vao POS tao 1 don co ma giam gia hop le.
4. Vao list don, mo chi tiet don vua tao.
5. Login `barista1`, vao dashboard barista, hoan thanh 1 don.
6. Vao Nguyen lieu, restock 1 item.
7. Vao Nhan vien, tao 1 nhan vien moi + account.
8. Vao Lich phan ca, tao 1 ca moi, sua va xoa lai.
9. Vao Tong hop luong, doi thang/nam de kiem tra tong hop.

## 9) Chay test tu dong

Hien tai repo co test cho `apps.orders`:

```bash
python manage.py test apps.orders
```

Ghi chu:
- Co the gap 1 fail do test assertion dang so sanh chuoi khong dau voi thong bao co dau (logic chuc nang van dung).

