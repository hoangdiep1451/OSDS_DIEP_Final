from config import *
from database import DatabaseManager
import requests
import json
import time
import random
import os
from tqdm import tqdm
from datetime import datetime


class TikiBookScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        self.db = DatabaseManager(MONGODB_URI, MONGODB_DATABASE)
        self.all_books = []
        os.makedirs(DATA_DIR, exist_ok=True)
        os.makedirs(CHARTS_DIR, exist_ok=True)

    def get_category_products(self, category_id, page=1, limit=40):
        params = {
            "limit": limit,
            "include": "advertisement",
            "aggregations": 2,
            "version": "home-persionalized",
            "trackity_id": "",
            "category": category_id,
            "page": page,
            "urlKey": "sach-truyen-tieng-viet"
        }
        try:
            response = self.session.get(API_URL, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except:
            return None

    def parse_product(self, product_data, category_name):
        try:
            author = ""
            if "authors" in product_data and product_data["authors"]:
                authors_list = product_data["authors"]
                if isinstance(authors_list, list):
                    author = ", ".join([a.get("name", "") for a in authors_list if a.get("name")])
            
            publisher = ""
            if "specifications" in product_data:
                for spec in product_data.get("specifications", []):
                    if "attributes" in spec:
                        for attr in spec["attributes"]:
                            if attr.get("code") == "publisher_vn":
                                publisher = attr.get("value", "")
            
            quantity_sold = product_data.get("quantity_sold", {})
            if isinstance(quantity_sold, dict):
                quantity_sold = quantity_sold.get("value", 0)
            
            return {
                "tiki_id": product_data.get("id"),
                "name": product_data.get("name", ""),
                "short_description": product_data.get("short_description", ""),
                "price": product_data.get("price", 0),
                "original_price": product_data.get("original_price", 0),
                "discount_rate": product_data.get("discount_rate", 0),
                "rating_average": product_data.get("rating_average", 0),
                "review_count": product_data.get("review_count", 0),
                "quantity_sold": quantity_sold if isinstance(quantity_sold, int) else 0,
                "author": author,
                "publisher": publisher,
                "category": category_name,
                "thumbnail_url": product_data.get("thumbnail_url", ""),
                "url": f"https://tiki.vn/{product_data.get('url_path', '')}"
            }
        except:
            return None

    def scrape_category(self, category_name, category_id, max_pages=10):
        print(f"\nĐang cào dữ liệu: {category_name}")
        print("=" * 50)
        category_books = []
        
        for page in tqdm(range(1, max_pages + 1), desc=f"Cào {category_name}"):
            data = self.get_category_products(category_id, page)
            if not data:
                continue
            
            products = data.get("data", [])
            if not products:
                break
            
            for product in products:
                book = self.parse_product(product, category_name)
                if book and book.get("tiki_id"):
                    category_books.append(book)
            
            time.sleep(random.uniform(1, DELAY_BETWEEN_REQUESTS))
        
        print(f"Đã cào {len(category_books)} sách từ {category_name}")
        return category_books

    def scrape_all_categories(self, max_pages_per_category=5):
        print("\n" + "=" * 60)
        print("BẮT ĐẦU CÀO DỮ LIỆU SÁCH TỪ TIKI.VN")
        print("=" * 60)
        
        start_time = datetime.now()
        self.db.connect()
        self.db.create_indexes()
        
        for category_name, category_id in BOOK_CATEGORIES.items():
            try:
                books = self.scrape_category(category_name, category_id, max_pages_per_category)
                self.all_books.extend(books)
                self.db.insert_many_books(books)
                self.db.log_scrape_history(category_name, len(books), "SUCCESS")
            except Exception as e:
                print(f"Lỗi: {e}")
                self.db.log_scrape_history(category_name, 0, f"FAILED: {str(e)}")
        
        duration = (datetime.now() - start_time).total_seconds()
        print("\n" + "=" * 60)
        print("KẾT QUẢ")
        print("=" * 60)
        print(f"Tổng số sách: {len(self.all_books)}")
        print(f"Thời gian: {duration:.2f} giây")
        print(f"Database: {MONGODB_DATABASE}")
        self.db.disconnect()
        self.save_to_json()
        
        return self.all_books

    def save_to_json(self, filename=None):
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{DATA_DIR}/books_{timestamp}.json"
        
        # Chuyển datetime thành string để có thể serialize JSON
        books_to_save = []
        for book in self.all_books:
            book_copy = book.copy()
            if 'scraped_at' in book_copy and isinstance(book_copy['scraped_at'], datetime):
                book_copy['scraped_at'] = book_copy['scraped_at'].isoformat()
            books_to_save.append(book_copy)
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(books_to_save, f, ensure_ascii=False, indent=2)
        
        print(f"Đã lưu: {filename}")
