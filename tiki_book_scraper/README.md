# 📚 Tiki Book Scraper - Đồ án cuối kỳ Web Scraping

## 📋 Giới thiệu

Dự án này thu thập và phân tích dữ liệu sách từ **Tiki.vn** - một trong những trang thương mại điện tử lớn nhất Việt Nam.

### Mục tiêu:
- ✅ Cào dữ liệu sách từ nhiều thể loại trên Tiki.vn
- ✅ Lưu trữ dữ liệu vào database SQLite
- ✅ Khảo sát và phân tích thông tin bằng SQL Query
- ✅ Trực quan hóa dữ liệu bằng các biểu đồ

## 🏗️ Cấu trúc dự án

```
tiki_book_scraper/
│
├── main.py              # Chương trình chính với menu tương tác
├── config.py            # Cấu hình (URL, database, ...)
├── scraper.py           # Module cào dữ liệu từ Tiki API
├── database.py          # Module quản lý SQLite database
├── analyzer.py          # Module phân tích và vẽ biểu đồ
├── requirements.txt     # Các thư viện cần thiết
│
├── data/                # Thư mục lưu file JSON backup
├── charts/              # Thư mục lưu biểu đồ
└── tiki_books.db        # SQLite database
```


### Chạy chương trình
```bash
python main.py
```

### Menu chức năng:
1. **Cào dữ liệu sách** - Thu thập dữ liệu từ Tiki
2. **Xem thống kê cơ bản** - Hiển thị thông tin tổng quan
3. **Tạo biểu đồ phân tích** - Vẽ các biểu đồ phân tích
4. **Truy vấn dữ liệu SQL** - Thực hiện câu lệnh SQL tùy chỉnh
5. **Tìm kiếm sách** - Tìm sách theo từ khóa
6. **Top sách bán chạy** - Xem sách bán chạy nhất
7. **Top sách đánh giá cao** - Xem sách được đánh giá cao nhất
8. **Xuất báo cáo HTML** - Tạo báo cáo tổng hợp

## 📊 Các thể loại sách được thu thập

| Thể loại | ID |
|----------|-----|
| Sách truyện tiếng Việt | 316 |
| Sách kinh tế | 8322 |
| Sách văn học | 7358 |
| Sách kỹ năng sống | 8594 |
| Sách thiếu nhi | 1084 |
| Sách giáo khoa | 9404 |

## 🗄️ Cấu trúc Database

### Bảng `books`
| Cột | Kiểu | Mô tả |
|-----|------|-------|
| id | INTEGER | Primary key |
| tiki_id | INTEGER | ID sách trên Tiki |
| name | TEXT | Tên sách |
| price | INTEGER | Giá bán |
| original_price | INTEGER | Giá gốc |
| discount_rate | INTEGER | % giảm giá |
| rating_average | REAL | Điểm đánh giá TB |
| review_count | INTEGER | Số lượt đánh giá |
| quantity_sold | INTEGER | Số lượng đã bán |
| author | TEXT | Tác giả |
| publisher | TEXT | Nhà xuất bản |
| category | TEXT | Thể loại |

## 📈 Các biểu đồ phân tích

1. **Phân bố theo thể loại** - Pie chart & Bar chart
2. **Phân bố giá** - Histogram, Box plot
3. **Phân tích đánh giá** - Rating distribution
4. **Phân tích doanh số** - Top sellers
5. **Phân tích giảm giá** - Discount analysis
6. **Phân tích NXB** - Publisher analysis
7. **Ma trận tương quan** - Correlation heatmap

## 🔍 Ví dụ truy vấn SQL

```sql
-- Đếm sách theo thể loại
SELECT category, COUNT(*) as total 
FROM books 
GROUP BY category 
ORDER BY total DESC;

-- Top 10 sách rẻ nhất
SELECT name, price, author 
FROM books 
ORDER BY price ASC 
LIMIT 10;

-- Sách có giảm giá trên 50%
SELECT name, original_price, price, discount_rate 
FROM books 
WHERE discount_rate > 50;

-- Thống kê theo nhà xuất bản
SELECT publisher, 
       COUNT(*) as book_count,
       AVG(price) as avg_price,
       AVG(rating_average) as avg_rating
FROM books 
WHERE publisher IS NOT NULL
GROUP BY publisher 
ORDER BY book_count DESC 
LIMIT 10;
```

## 🛠️ Công nghệ sử dụng

- **Python 3.x** - Ngôn ngữ lập trình
- **Requests** - HTTP requests
- **BeautifulSoup4** - Parse HTML (backup)
- **SQLite** - Database
- **Pandas** - Xử lý dữ liệu
- **Matplotlib & Seaborn** - Vẽ biểu đồ
- **tqdm** - Progress bar



---
