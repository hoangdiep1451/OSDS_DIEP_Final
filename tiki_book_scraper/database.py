"""
Module quản lý MongoDB Database
Tạo collection, thêm dữ liệu, truy vấn
"""

from pymongo import MongoClient, ASCENDING, DESCENDING
import pandas as pd
from datetime import datetime
import os

class DatabaseManager:
    """Quản lý kết nối và thao tác với MongoDB Database"""
    
    def __init__(self, connection_string="mongodb://localhost:27017/", db_name="tiki_books_db"):
        """Khởi tạo kết nối database"""
        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None
        self.books_collection = None
        self.history_collection = None
        
    def connect(self):
        """Tạo kết nối đến database"""
        try:
            self.client = MongoClient(self.connection_string)
            self.db = self.client[self.db_name]
            self.books_collection = self.db['books']
            self.history_collection = self.db['scrape_history']
            
            # Test connection
            self.client.admin.command('ping')
            print(f"Đã kết nối đến MongoDB database: {self.db_name}")
        except Exception as e:
            print(f"Lỗi kết nối MongoDB: {e}")
            print("Vui lòng đảm bảo MongoDB đang chạy trên localhost:27017")
            raise
        
    def disconnect(self):
        """Đóng kết nối database"""
        if self.client:
            self.client.close()
            print("Đã đóng kết nối database")
            
    def create_indexes(self):
        """Tạo các index để tối ưu truy vấn"""
        # Index cho tiki_id (unique)
        self.books_collection.create_index([("tiki_id", ASCENDING)], unique=True)
        # Index cho category
        self.books_collection.create_index([("category", ASCENDING)])
        # Index cho rating
        self.books_collection.create_index([("rating_average", DESCENDING)])
        # Index cho quantity_sold
        self.books_collection.create_index([("quantity_sold", DESCENDING)])
        # Text index cho tìm kiếm
        self.books_collection.create_index([("name", "text"), ("author", "text")])
        
        print("Đã tạo các index trong database")
        
    def insert_book(self, book_data):
        """Thêm một cuốn sách vào database"""
        try:
            book_data['scraped_at'] = datetime.now()
            result = self.books_collection.update_one(
                {'tiki_id': book_data.get('tiki_id')},
                {'$set': book_data},
                upsert=True
            )
            return True
        except Exception as e:
            print(f"Lỗi khi thêm sách: {e}")
            return False
            
    def insert_many_books(self, books_list):
        """Thêm nhiều sách vào database"""
        success_count = 0
        for book in books_list:
            if self.insert_book(book):
                success_count += 1
        print(f"Đã thêm {success_count}/{len(books_list)} sách vào database")
        return success_count
        
    def log_scrape_history(self, category, total_products, status):
        """Ghi lịch sử cào dữ liệu"""
        history = {
            'category': category,
            'total_products': total_products,
            'status': status,
            'scraped_at': datetime.now()
        }
        self.history_collection.insert_one(history)
        
    # ============ CÁC TRUY VẤN KHẢO SÁT DỮ LIỆU ============
    
    def get_all_books(self):
        """Lấy tất cả sách"""
        books = list(self.books_collection.find())
        return pd.DataFrame(books)
    
    def get_books_count(self):
        """Đếm tổng số sách"""
        return self.books_collection.count_documents({})
    
    def get_books_by_category(self, category):
        """Lấy sách theo thể loại"""
        books = list(self.books_collection.find({'category': category}))
        return pd.DataFrame(books)
    
    def get_top_rated_books(self, limit=10):
        """Lấy top sách đánh giá cao nhất"""
        books = list(self.books_collection.find(
            {'rating_average': {'$ne': None}},
            {'name': 1, 'author': 1, 'rating_average': 1, 'review_count': 1, 'price': 1, '_id': 0}
        ).sort([('rating_average', DESCENDING), ('review_count', DESCENDING)]).limit(limit))
        return pd.DataFrame(books)
    
    def get_best_selling_books(self, limit=10):
        """Lấy top sách bán chạy nhất"""
        books = list(self.books_collection.find(
            {'quantity_sold': {'$ne': None}},
            {'name': 1, 'author': 1, 'quantity_sold': 1, 'price': 1, '_id': 0}
        ).sort('quantity_sold', DESCENDING).limit(limit))
        return pd.DataFrame(books)
    
    def get_price_statistics(self):
        """Thống kê giá sách"""
        pipeline = [
            {
                '$match': {'price': {'$ne': None}}
            },
            {
                '$group': {
                    '_id': None,
                    'total_books': {'$sum': 1},
                    'avg_price': {'$avg': '$price'},
                    'min_price': {'$min': '$price'},
                    'max_price': {'$max': '$price'},
                    'avg_discount': {'$avg': '$discount_rate'}
                }
            }
        ]
        result = list(self.books_collection.aggregate(pipeline))
        return pd.DataFrame(result) if result else pd.DataFrame()
    
    def get_category_statistics(self):
        """Thống kê theo thể loại"""
        pipeline = [
            {
                '$group': {
                    '_id': '$category',
                    'book_count': {'$sum': 1},
                    'avg_price': {'$avg': '$price'},
                    'avg_rating': {'$avg': '$rating_average'},
                    'total_sold': {'$sum': '$quantity_sold'}
                }
            },
            {
                '$project': {
                    'category': '$_id',
                    'book_count': 1,
                    'avg_price': 1,
                    'avg_rating': 1,
                    'total_sold': 1,
                    '_id': 0
                }
            },
            {
                '$sort': {'book_count': -1}
            }
        ]
        result = list(self.books_collection.aggregate(pipeline))
        return pd.DataFrame(result)
    
    def get_publisher_statistics(self):
        """Thống kê theo nhà xuất bản"""
        pipeline = [
            {
                '$match': {
                    'publisher': {'$ne': None, '$ne': ''}
                }
            },
            {
                '$group': {
                    '_id': '$publisher',
                    'book_count': {'$sum': 1},
                    'avg_price': {'$avg': '$price'},
                    'avg_rating': {'$avg': '$rating_average'}
                }
            },
            {
                '$project': {
                    'publisher': '$_id',
                    'book_count': 1,
                    'avg_price': 1,
                    'avg_rating': 1,
                    '_id': 0
                }
            },
            {
                '$sort': {'book_count': -1}
            },
            {
                '$limit': 20
            }
        ]
        result = list(self.books_collection.aggregate(pipeline))
        return pd.DataFrame(result)
    
    def get_discount_distribution(self):
        """Phân bố giảm giá"""
        pipeline = [
            {
                '$project': {
                    'discount_range': {
                        '$switch': {
                            'branches': [
                                {'case': {'$or': [{'$eq': ['$discount_rate', None]}, {'$eq': ['$discount_rate', 0]}]}, 'then': 'Không giảm'},
                                {'case': {'$and': [{'$gte': ['$discount_rate', 1]}, {'$lte': ['$discount_rate', 20]}]}, 'then': '1-20%'},
                                {'case': {'$and': [{'$gte': ['$discount_rate', 21]}, {'$lte': ['$discount_rate', 40]}]}, 'then': '21-40%'},
                                {'case': {'$and': [{'$gte': ['$discount_rate', 41]}, {'$lte': ['$discount_rate', 60]}]}, 'then': '41-60%'}
                            ],
                            'default': 'Trên 60%'
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': '$discount_range',
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    'discount_range': '$_id',
                    'count': 1,
                    '_id': 0
                }
            }
        ]
        result = list(self.books_collection.aggregate(pipeline))
        return pd.DataFrame(result)
    
    def get_price_range_distribution(self):
        """Phân bố giá"""
        pipeline = [
            {
                '$match': {'price': {'$ne': None}}
            },
            {
                '$project': {
                    'price_range': {
                        '$switch': {
                            'branches': [
                                {'case': {'$lt': ['$price', 50000]}, 'then': 'Dưới 50K'},
                                {'case': {'$and': [{'$gte': ['$price', 50000]}, {'$lte': ['$price', 100000]}]}, 'then': '50K - 100K'},
                                {'case': {'$and': [{'$gte': ['$price', 100001]}, {'$lte': ['$price', 200000]}]}, 'then': '100K - 200K'},
                                {'case': {'$and': [{'$gte': ['$price', 200001]}, {'$lte': ['$price', 500000]}]}, 'then': '200K - 500K'}
                            ],
                            'default': 'Trên 500K'
                        }
                    }
                }
            },
            {
                '$group': {
                    '_id': '$price_range',
                    'count': {'$sum': 1}
                }
            },
            {
                '$project': {
                    'price_range': '$_id',
                    'count': 1,
                    '_id': 0
                }
            }
        ]
        result = list(self.books_collection.aggregate(pipeline))
        return pd.DataFrame(result)
    
    def search_books(self, keyword):
        """Tìm kiếm sách theo từ khóa"""
        books = list(self.books_collection.find(
            {
                '$or': [
                    {'name': {'$regex': keyword, '$options': 'i'}},
                    {'author': {'$regex': keyword, '$options': 'i'}}
                ]
            },
            {'name': 1, 'author': 1, 'price': 1, 'rating_average': 1, '_id': 0}
        ).limit(20))
        return pd.DataFrame(books)


# Test module
if __name__ == "__main__":
    db = DatabaseManager()
    db.connect()
    db.create_indexes()
    
    # Test thêm sách
    test_book = {
        'tiki_id': 123456,
        'name': 'Sách Test',
        'short_description': 'Mô tả ngắn',
        'price': 100000,
        'original_price': 150000,
        'discount_rate': 33,
        'rating_average': 4.5,
        'review_count': 100,
        'quantity_sold': 500,
        'author': 'Tác giả Test',
        'publisher': 'NXB Test',
        'category': 'Test',
        'thumbnail_url': 'https://example.com/image.jpg',
        'url': 'https://tiki.vn/test'
    }
    
    db.insert_book(test_book)
    print(f"Tổng số sách: {db.get_books_count()}")
    
    db.disconnect()
