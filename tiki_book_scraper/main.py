"""
MAIN - Chương trình chính
Đồ án cuối kỳ: Web Scraping dữ liệu sách từ Tiki.vn

Tác giả: [Tên sinh viên]
MSSV: [Mã số sinh viên]
"""

import sys
import os
from datetime import datetime


from config import *
from scraper import TikiBookScraper
from database import DatabaseManager
from analyzer import DataAnalyzer


def print_banner():
    """In banner chào mừng"""
    print("\n" + "="*60)
    print("  ĐỒ ÁN CUỐI KỲ - WEB SCRAPING")
    print("  Thu thập dữ liệu sách từ Tiki.vn")
    print("="*60)


def print_menu():
    """In menu chức năng"""
    print("\n--- MENU ---")
    print("1. Cào dữ liệu sách")
    print("2. Xem thống kê")
    print("3. Tạo biểu đồ")
    print("4. Truy vấn MongoDB")
    print("5. Tìm kiếm sách")
    print("6. Top sách bán chạy")
    print("7. Top sách đánh giá cao")
    print("8. Xuất báo cáo HTML")
    print("9. Thoát")
    print("-"*60)


def scrape_data():
    """Cào dữ liệu từ Tiki"""
    print("\n>> Bắt đầu cào dữ liệu...")
    
    try:
        pages = int(input("Số trang mỗi thể loại (1-20): ") or "5")
        pages = min(max(1, pages), 20)
    except ValueError:
        pages = 5
        
    scraper = TikiBookScraper()
    books = scraper.scrape_all_categories(max_pages_per_category=pages)
    
    print(f"✓ Hoàn thành! Đã cào được {len(books)} cuốn sách.")
    return books


def view_statistics():
    """Xem thống kê cơ bản"""
    analyzer = DataAnalyzer()
    df = analyzer.load_data()
    
    if len(df) == 0:
        print("Chưa có dữ liệu. Hãy cào dữ liệu trước (chọn 1).")
        return
        
    analyzer.basic_statistics()


def generate_charts():
    """Tạo biểu đồ phân tích"""
    analyzer = DataAnalyzer()
    df = analyzer.load_data()
    
    if len(df) == 0:
        print("Chưa có dữ liệu. Hãy cào dữ liệu trước (chọn 1).")
        return
        
    analyzer.generate_all_charts()


def query_data():
    """Truy vấn dữ liệu tùy chỉnh với MongoDB"""
    print("\n>> Truy vấn MongoDB")
    print("1. Số sách theo thể loại")
    print("2. Giá trung bình theo thể loại")
    print("3. Top 10 sách bán chạy")
    print("4. Top 10 sách đánh giá cao")
    
    db = DatabaseManager(MONGODB_URI, MONGODB_DATABASE)
    db.connect()
    
    while True:
        choice = input("\nChọn (1-4, exit để thoát): ").strip()
        
        if choice.lower() == 'exit':
            break
            
        try:
            if choice == '1':
                result = db.get_category_statistics()
                print(result.to_string())
            elif choice == '2':
                result = db.get_price_statistics()
                print(result.to_string())
            elif choice == '3':
                result = db.get_best_selling_books(10)
                print(result.to_string())
            elif choice == '4':
                result = db.get_top_rated_books(10)
                print(result.to_string())
            else:
                print("Lựa chọn không hợp lệ")
        except Exception as e:
            print(f"Lỗi: {e}")
            
    db.disconnect()


def search_books():
    """Tìm kiếm sách"""
    print("\n>> Tìm kiếm sách")
    keyword = input("Nhập từ khóa: ").strip()
    
    if not keyword:
        print("Vui lòng nhập từ khóa.")
        return
        
    db = DatabaseManager(MONGODB_URI, MONGODB_DATABASE)
    db.connect()
    
    results = db.search_books(keyword)
    
    if len(results) == 0:
        print(f"Không tìm thấy '{keyword}'")
    else:
        print(f"\nKết quả: {len(results)} sách")
        for idx, row in results.iterrows():
            print(f"{idx+1}. {row['name'][:50]}")
            print(f"   {row['author'] or 'N/A'} | {row['price']:,}đ | {row['rating_average']:.1f}★")
        
    db.disconnect()


def show_top_selling():
    """Hiển thị top sách bán chạy"""
    print("\n>> Top sách bán chạy")
    
    db = DatabaseManager(MONGODB_URI, MONGODB_DATABASE)
    db.connect()
    
    results = db.get_best_selling_books(limit=15)
    
    if len(results) == 0:
        print("Chưa có dữ liệu.")
    else:
        for idx, row in results.iterrows():
            print(f"{idx+1}. {row['name'][:50]}")
            print(f"   Đã bán: {row['quantity_sold']:,} | {row['price']:,}đ")
        
    db.disconnect()


def show_top_rated():
    """Hiển thị top sách đánh giá cao"""
    print("\n>> Top sách đánh giá cao")
    
    db = DatabaseManager(MONGODB_URI, MONGODB_DATABASE)
    db.connect()
    
    results = db.get_top_rated_books(limit=15)
    
    if len(results) == 0:
        print("Chưa có dữ liệu.")
    else:
        for idx, row in results.iterrows():
            print(f"{idx+1}. {row['name'][:50]}")
            print(f"   {row['rating_average']:.1f}★ ({row['review_count']:,} reviews) | {row['price']:,}đ")
        
    db.disconnect()


def export_report():
    """Xuất báo cáo HTML"""
    analyzer = DataAnalyzer()
    df = analyzer.load_data()
    
    if len(df) == 0:
        print("Chưa có dữ liệu. Hãy cào dữ liệu trước (chọn 1).")
        return
        
    analyzer.export_report()
    print(f"\n✓ Đã xuất báo cáo: {CHARTS_DIR}/report.html")


def main():
    """Hàm chính"""
    print_banner()
    
    while True:
        print_menu()
        
        choice = input("\nChọn: ").strip()
        
        if choice == '1':
            scrape_data()
        elif choice == '2':
            view_statistics()
        elif choice == '3':
            generate_charts()
        elif choice == '4':
            query_data()
        elif choice == '5':
            search_books()
        elif choice == '6':
            show_top_selling()
        elif choice == '7':
            show_top_rated()
        elif choice == '8':
            export_report()
        elif choice == '9':
            print("\nTạm biệt!")
            break
        else:
            print("Chọn từ 1-9!")
            
        input("\nNhấn Enter để tiếp tục...")


if __name__ == "__main__":
    main()
