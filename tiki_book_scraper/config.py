"""
Cấu hình cho dự án Web Scraping Sách Tiki
"""

# URL cơ sở
BASE_URL = "https://tiki.vn"
BOOKS_URL = "https://tiki.vn/sach-truyen-tieng-viet/c316"

# API endpoint (Tiki sử dụng API để load sản phẩm)
API_URL = "https://tiki.vn/api/personalish/v1/blocks/listings"

# Cấu hình MongoDB
MONGODB_URI = "mongodb://localhost:27017/books_db_v1"
# "mongodb+srv://Diep:Ex5I2RNkj5PWz4yb@cluster0.z6n12pj.mongodb.net/?appName=Cluster0"
MONGODB_DATABASE = "tiki_books_db"
MONGODB_COLLECTION = "books"

# Cấu hình Scraping
DELAY_BETWEEN_REQUESTS = 2  # Giây
MAX_PAGES = 10  # Số trang tối đa để cào
PRODUCTS_PER_PAGE = 40

# Headers giả lập trình duyệt
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive",
    "Referer": "https://tiki.vn/",
}

# Các thể loại sách cần cào
BOOK_CATEGORIES = {
    "sach-truyen-tieng-viet": 316,
    "sach-kinh-te": 8322,
    "sach-van-hoc": 7358,
    "sach-ky-nang-song": 8594,
    "sach-thieu-nhi": 1084,
    "sach-giao-khoa": 9404,
}

# Thư mục lưu trữ
DATA_DIR = "data"
CHARTS_DIR = "charts"
