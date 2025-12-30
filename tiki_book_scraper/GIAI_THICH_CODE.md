# GIẢI THÍCH CHI TIẾT CÁC FILE TRONG PROJECT

## Đồ án: Web Scraping dữ liệu sách từ Tiki.vn

---

## 1. FILE `config.py` - Cấu hình chung

File này chứa tất cả các **hằng số** và **cài đặt** cho toàn bộ project.

### Các biến quan trọng:

```python
# URL gốc của Tiki
BASE_URL = "https://tiki.vn"

# API của Tiki (web dùng API để load sản phẩm)
API_URL = "https://tiki.vn/api/personalish/v1/blocks/listings"

# Kết nối MongoDB Atlas (database online)
MONGODB_URI = "mongodb+srv://..."
MONGODB_DATABASE = "tiki_books_db"

# Cài đặt scraping
DELAY_BETWEEN_REQUESTS = 2  # Đợi 2 giây giữa mỗi request (tránh bị block)
MAX_PAGES = 10              # Cào tối đa 10 trang
PRODUCTS_PER_PAGE = 40      # Mỗi trang có 40 sản phẩm

# Headers giả lập trình duyệt (để website nghĩ mình là người thật)
HEADERS = {
    "User-Agent": "Mozilla/5.0...",  # Giả làm Chrome
    ...
}

# Các thể loại sách cần cào (tên: mã category)
BOOK_CATEGORIES = {
    "sach-truyen-tieng-viet": 316,
    "sach-kinh-te": 8322,
    ...
}
```

### Tại sao cần file config?
- **Dễ thay đổi**: Muốn đổi database hay URL chỉ cần sửa 1 chỗ
- **Tái sử dụng**: Các file khác import vào dùng chung
- **Chuyên nghiệp**: Code sạch, không hard-code

---

## 2. FILE `scraper.py` - Thu thập dữ liệu

File này chứa class `TikiBookScraper` - bộ máy cào dữ liệu chính.

### Class TikiBookScraper:

#### Hàm `__init__()` - Khởi tạo
```python
def __init__(self):
    self.session = requests.Session()  # Tạo session HTTP
    self.session.headers.update(HEADERS)  # Thêm headers giả trình duyệt
    self.db = DatabaseManager(...)  # Kết nối database
    self.all_books = []  # Danh sách sách cào được
```

#### Hàm `get_category_products()` - Gọi API lấy sản phẩm
```python
def get_category_products(self, category_id, page=1, limit=40):
    # Tạo params cho API
    params = {
        "category": category_id,
        "page": page,
        "limit": limit,
        ...
    }
    # Gọi API và trả về JSON
    response = self.session.get(API_URL, params=params)
    return response.json()
```
**Giải thích**: Tiki dùng API trả về JSON thay vì HTML thông thường. Ta gọi API này để lấy danh sách sản phẩm.

#### Hàm `parse_product()` - Trích xuất thông tin sách
```python
def parse_product(self, product_data, category_name):
    return {
        "tiki_id": product_data.get("id"),
        "name": product_data.get("name"),
        "price": product_data.get("price"),
        "rating_average": product_data.get("rating_average"),
        "quantity_sold": ...,
        "author": ...,  # Lấy từ mảng authors
        "publisher": ...,  # Lấy từ specifications
        ...
    }
```
**Giải thích**: Từ dữ liệu JSON thô, ta lọc ra các trường cần thiết.

#### Hàm `scrape_category()` - Cào 1 thể loại
```python
def scrape_category(self, category_name, category_id, max_pages=10):
    for page in range(1, max_pages + 1):
        data = self.get_category_products(category_id, page)
        for product in data.get("data", []):
            book = self.parse_product(product, category_name)
            category_books.append(book)
        time.sleep(DELAY_BETWEEN_REQUESTS)  # Đợi để không bị block
    return category_books
```

#### Hàm `scrape_all_categories()` - Cào tất cả thể loại
```python
def scrape_all_categories(self, max_pages_per_category=5):
    for category_name, category_id in BOOK_CATEGORIES.items():
        books = self.scrape_category(category_name, category_id, ...)
        self.db.insert_many_books(books)  # Lưu vào database
    self.save_to_json()  # Backup ra file JSON
    return self.all_books
```

---

## 3. FILE `database.py` - Quản lý Database

File này chứa class `DatabaseManager` - quản lý toàn bộ thao tác với MongoDB.

### Class DatabaseManager:

#### Hàm `__init__()` và `connect()` - Kết nối database
```python
def __init__(self, connection_string, db_name):
    self.connection_string = connection_string
    self.db_name = db_name

def connect(self):
    self.client = MongoClient(self.connection_string)
    self.db = self.client[self.db_name]
    self.books_collection = self.db['books']  # Collection chứa sách
```

#### Hàm `create_indexes()` - Tạo index tối ưu truy vấn
```python
def create_indexes(self):
    # Index cho tiki_id (không trùng)
    self.books_collection.create_index([("tiki_id", ASCENDING)], unique=True)
    # Index cho tìm kiếm nhanh
    self.books_collection.create_index([("category", ASCENDING)])
    ...
```
**Giải thích**: Index giúp truy vấn nhanh hơn nhiều lần.

#### Hàm `insert_book()` - Thêm/Cập nhật sách
```python
def insert_book(self, book_data):
    book_data['scraped_at'] = datetime.now()  # Thêm thời gian cào
    result = self.books_collection.update_one(
        {'tiki_id': book_data.get('tiki_id')},  # Tìm theo tiki_id
        {'$set': book_data},  # Cập nhật dữ liệu
        upsert=True  # Nếu chưa có thì thêm mới
    )
```
**Giải thích**: `upsert=True` nghĩa là "update or insert" - cập nhật nếu có, thêm mới nếu chưa có.

#### Các hàm truy vấn thống kê (dùng Aggregation Pipeline):

```python
def get_category_statistics(self):
    pipeline = [
        {'$group': {  # Nhóm theo category
            '_id': '$category',
            'book_count': {'$sum': 1},  # Đếm số sách
            'avg_price': {'$avg': '$price'},  # Giá trung bình
        }},
        {'$sort': {'book_count': -1}}  # Sắp xếp giảm dần
    ]
    result = self.books_collection.aggregate(pipeline)
```
**Giải thích**: Aggregation Pipeline là cách MongoDB xử lý dữ liệu theo các bước (như SQL GROUP BY).

#### Hàm `search_books()` - Tìm kiếm sách
```python
def search_books(self, keyword):
    books = self.books_collection.find({
        '$or': [  # Tìm trong name HOẶC author
            {'name': {'$regex': keyword, '$options': 'i'}},
            {'author': {'$regex': keyword, '$options': 'i'}}
        ]
    })
```
**Giải thích**: `$regex` cho phép tìm kiếm theo mẫu, `$options: 'i'` = không phân biệt hoa thường.

---

## 4. FILE `analyzer.py` - Phân tích và Vẽ biểu đồ

File này chứa class `DataAnalyzer` - phân tích dữ liệu và tạo biểu đồ.

### Class DataAnalyzer:

#### Hàm `load_data()` - Lấy dữ liệu từ database
```python
def load_data(self):
    self.db.connect()
    self.df = self.db.get_all_books()  # Lấy tất cả sách thành DataFrame
    return self.df
```

#### Hàm `basic_statistics()` - Thống kê cơ bản
```python
def basic_statistics(self):
    print(f"Tổng số sách: {len(self.df)}")
    print(f"Giá trung bình: {self.df['price'].mean():,.0f} VNĐ")
    print(f"Điểm TB: {self.df['rating_average'].mean():.2f}/5")
    ...
```

#### Các hàm vẽ biểu đồ:

**1. `plot_category_distribution()` - Biểu đồ phân bố thể loại**
```python
def plot_category_distribution(self):
    category_counts = self.df['category'].value_counts()
    
    # Vẽ pie chart (biểu đồ tròn)
    axes[0].pie(category_counts.values, labels=..., autopct='%1.1f%%')
    
    # Vẽ bar chart ngang
    axes[1].barh(category_counts.index, category_counts.values)
    
    plt.savefig('charts/category_distribution.png')
```

**2. `plot_price_distribution()` - Biểu đồ phân bố giá**
- Histogram giá sách
- Box plot giá theo thể loại
- Phân bố theo khoảng giá
- Scatter plot giá vs giảm giá

**3. `plot_rating_analysis()` - Phân tích đánh giá**
- Histogram điểm đánh giá
- Điểm TB theo thể loại
- Số reviews theo thể loại

**4. `plot_sales_analysis()` - Phân tích doanh số**
- Top 10 sách bán chạy
- Doanh số theo thể loại
- Mối quan hệ giá - số lượng bán

**5. `plot_correlation_heatmap()` - Ma trận tương quan**
```python
def plot_correlation_heatmap(self):
    correlation = self.df[numeric_cols].corr()  # Tính tương quan
    sns.heatmap(correlation, annot=True)  # Vẽ heatmap
```
**Giải thích**: Heatmap cho thấy các biến nào liên quan với nhau (VD: giá và đánh giá có liên quan không?)

#### Hàm `export_report()` - Xuất báo cáo HTML
```python
def export_report(self):
    html_content = f"""
    <html>
        <h1>Báo cáo phân tích</h1>
        <p>Tổng số sách: {len(self.df)}</p>
        <img src="category_distribution.png">
        ...
    </html>
    """
    with open('charts/report.html', 'w') as f:
        f.write(html_content)
```

---

## 5. FILE `main.py` - Chương trình chính

File này là điểm khởi đầu của chương trình, chứa menu và điều hướng.

### Các hàm chính:

#### `print_menu()` - Hiển thị menu
```python
def print_menu():
    print("1. Cào dữ liệu sách")
    print("2. Xem thống kê")
    ...
```

#### `scrape_data()` - Chức năng cào dữ liệu
```python
def scrape_data():
    pages = int(input("Số trang mỗi thể loại: "))
    scraper = TikiBookScraper()  # Tạo scraper
    books = scraper.scrape_all_categories(max_pages_per_category=pages)
```

#### `main()` - Vòng lặp chính
```python
def main():
    print_banner()
    while True:
        print_menu()
        choice = input("Chọn: ")
        
        if choice == '1':
            scrape_data()
        elif choice == '2':
            view_statistics()
        ...
        elif choice == '9':
            break  # Thoát
```

---

## 6. FILE `requirements.txt` - Thư viện cần cài

```
requests        # Gọi HTTP requests
pymongo         # Kết nối MongoDB
pandas          # Xử lý dữ liệu dạng bảng
matplotlib      # Vẽ biểu đồ
seaborn         # Vẽ biểu đồ đẹp hơn
tqdm            # Thanh tiến trình
```

**Cách cài**: `pip install -r requirements.txt`

---

## LUỒNG HOẠT ĐỘNG CỦA CHƯƠNG TRÌNH

```
1. Chạy main.py
   ↓
2. Hiển thị menu
   ↓
3. Người dùng chọn chức năng
   ↓
4. VD: Chọn "Cào dữ liệu"
   ↓
5. scraper.py gọi API Tiki
   ↓
6. Lấy JSON → parse_product() → dictionary
   ↓
7. database.py lưu vào MongoDB
   ↓
8. Lưu backup ra file JSON
   ↓
9. VD: Chọn "Tạo biểu đồ"
   ↓
10. analyzer.py load từ database
    ↓
11. Dùng pandas xử lý
    ↓
12. Dùng matplotlib/seaborn vẽ biểu đồ
    ↓
13. Lưu ra file .png
```

---

## CÁC KHÁI NIỆM QUAN TRỌNG

### 1. Web Scraping
- Thu thập dữ liệu từ website
- Có 2 cách: Parse HTML hoặc Gọi API
- Project này dùng **API** của Tiki

### 2. MongoDB
- Database NoSQL (không dùng bảng như SQL)
- Lưu dữ liệu dạng JSON (document)
- Collection = Bảng, Document = Dòng

### 3. Pandas DataFrame
- Thư viện xử lý dữ liệu của Python
- DataFrame = Bảng dữ liệu (như Excel)
- Dễ dàng tính toán, lọc, thống kê

### 4. Matplotlib/Seaborn
- Thư viện vẽ biểu đồ
- Matplotlib: cơ bản, linh hoạt
- Seaborn: đẹp hơn, dễ dùng hơn

---

## LƯU Ý KHI CHẠY

1. **Cài thư viện**: `pip install -r requirements.txt`
2. **Chạy chương trình**: `python main.py`
3. **Thứ tự**: Cào dữ liệu trước (1) → rồi mới xem thống kê/biểu đồ
4. **MongoDB Atlas**: Cần có internet để kết nối database online

---

*Tài liệu này giải thích chi tiết code cho sinh viên hiểu rõ từng phần của đồ án.*
