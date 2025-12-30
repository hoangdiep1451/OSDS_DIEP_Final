"""
📓 Jupyter Notebook Demo - Phân tích dữ liệu sách Tiki
Chạy từng cell để xem kết quả
"""

# %% [markdown]
# # 📚 Phân tích dữ liệu sách từ Tiki.vn
# 
# Notebook này trình bày quá trình:
# 1. Cào dữ liệu từ Tiki API
# 2. Lưu trữ vào SQLite
# 3. Khảo sát và phân tích dữ liệu
# 4. Vẽ biểu đồ trực quan

# %% 
# Import thư viện cần thiết
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import sqlite3
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

# Cấu hình hiển thị
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 12

print("✅ Đã import thư viện thành công!")

# %%
# Import các module của dự án
from config import *
from database import DatabaseManager
from scraper import TikiBookScraper
from analyzer import DataAnalyzer

print("✅ Đã import các module dự án!")

# %% [markdown]
# ## 1. 🕷️ Cào dữ liệu từ Tiki

# %%
# Khởi tạo scraper
scraper = TikiBookScraper()

# Cào dữ liệu từ 1 thể loại (demo)
# Thay đổi max_pages để cào nhiều hơn
books = scraper.scrape_category("sach-van-hoc", 7358, max_pages=2)

print(f"\n📚 Đã cào được {len(books)} sách")

# %%
# Xem mẫu dữ liệu
df_sample = pd.DataFrame(books[:5])
print("📖 Mẫu dữ liệu đã cào:")
df_sample[['name', 'price', 'rating_average', 'author']]

# %% [markdown]
# ## 2. 💾 Lưu vào Database SQLite

# %%
# Kết nối và lưu vào database
db = DatabaseManager("tiki_books.db")
db.connect()
db.create_tables()

# Lưu dữ liệu
db.insert_many_books(books)

print(f"✅ Đã lưu {db.get_books_count()} sách vào database")

# %% [markdown]
# ## 3. 🔍 Truy vấn dữ liệu với SQL

# %%
# Load toàn bộ dữ liệu
df = db.get_all_books()
print(f"📊 Tổng số sách trong database: {len(df)}")
df.head()

# %%
# Thống kê giá
price_stats = db.get_price_statistics()
print("💰 Thống kê giá sách:")
price_stats

# %%
# Top 10 sách bán chạy
top_selling = db.get_best_selling_books(10)
print("🏆 Top 10 sách bán chạy:")
top_selling

# %%
# Top 10 sách đánh giá cao
top_rated = db.get_top_rated_books(10)
print("⭐ Top 10 sách đánh giá cao:")
top_rated

# %%
# Thống kê theo thể loại
category_stats = db.get_category_statistics()
print("📁 Thống kê theo thể loại:")
category_stats

# %% [markdown]
# ## 4. 📊 Trực quan hóa dữ liệu

# %%
# Phân bố giá sách
fig, ax = plt.subplots(figsize=(12, 6))
ax.hist(df['price'], bins=50, color='#4ECDC4', edgecolor='white', alpha=0.7)
ax.axvline(df['price'].mean(), color='red', linestyle='--', linewidth=2, label=f'Trung bình: {df["price"].mean():,.0f}đ')
ax.axvline(df['price'].median(), color='orange', linestyle='--', linewidth=2, label=f'Trung vị: {df["price"].median():,.0f}đ')
ax.set_xlabel('Giá (VNĐ)', fontsize=12)
ax.set_ylabel('Số lượng sách', fontsize=12)
ax.set_title('📊 Phân bố giá sách trên Tiki', fontsize=14, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.show()

# %%
# Phân bố đánh giá
rated = df[df['rating_average'] > 0]
fig, ax = plt.subplots(figsize=(10, 6))
ax.hist(rated['rating_average'], bins=20, color='#45B7D1', edgecolor='white')
ax.axvline(rated['rating_average'].mean(), color='red', linestyle='--', linewidth=2, 
           label=f'Trung bình: {rated["rating_average"].mean():.2f}')
ax.set_xlabel('Điểm đánh giá', fontsize=12)
ax.set_ylabel('Số lượng', fontsize=12)
ax.set_title('⭐ Phân bố điểm đánh giá', fontsize=14, fontweight='bold')
ax.legend()
plt.tight_layout()
plt.show()

# %%
# Số sách theo thể loại (nếu có nhiều thể loại)
if df['category'].nunique() > 1:
    fig, ax = plt.subplots(figsize=(10, 6))
    category_counts = df['category'].value_counts()
    colors = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', '#DDA0DD']
    ax.barh(category_counts.index, category_counts.values, color=colors[:len(category_counts)])
    ax.set_xlabel('Số lượng sách', fontsize=12)
    ax.set_title('📚 Số sách theo thể loại', fontsize=14, fontweight='bold')
    for i, v in enumerate(category_counts.values):
        ax.text(v + 5, i, str(v), va='center')
    plt.tight_layout()
    plt.show()

# %%
# Box plot giá theo thể loại
if df['category'].nunique() > 1:
    fig, ax = plt.subplots(figsize=(12, 6))
    df.boxplot(column='price', by='category', ax=ax)
    ax.set_ylabel('Giá (VNĐ)', fontsize=12)
    ax.set_title('Phân bố giá theo thể loại', fontsize=14, fontweight='bold')
    plt.suptitle('')
    plt.tight_layout()
    plt.show()

# %%
# Mối quan hệ giữa giá và đánh giá
fig, ax = plt.subplots(figsize=(10, 6))
scatter = ax.scatter(rated['price'], rated['rating_average'], 
                     c=rated['review_count'], cmap='viridis', 
                     alpha=0.6, s=50)
ax.set_xlabel('Giá (VNĐ)', fontsize=12)
ax.set_ylabel('Điểm đánh giá', fontsize=12)
ax.set_title('💰 Mối quan hệ Giá - Đánh giá', fontsize=14, fontweight='bold')
plt.colorbar(scatter, label='Số reviews')
plt.tight_layout()
plt.show()

# %%
# Ma trận tương quan
fig, ax = plt.subplots(figsize=(10, 8))
numeric_cols = ['price', 'original_price', 'discount_rate', 'rating_average', 'review_count', 'quantity_sold']
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, cmap='RdYlGn', center=0, fmt='.2f', 
            square=True, ax=ax)
ax.set_title('🔗 Ma trận tương quan', fontsize=14, fontweight='bold')
plt.tight_layout()
plt.show()

# %% [markdown]
# ## 5. 📈 Tổng kết

# %%
# Tổng kết thông tin
print("=" * 60)
print("📊 TỔNG KẾT PHÂN TÍCH DỮ LIỆU")
print("=" * 60)
print(f"\n📚 Tổng số sách: {len(df)}")
print(f"📁 Số thể loại: {df['category'].nunique()}")
print(f"✍️ Số tác giả: {df['author'].nunique()}")

print(f"\n💰 Giá trung bình: {df['price'].mean():,.0f} VNĐ")
print(f"💰 Giá thấp nhất: {df['price'].min():,.0f} VNĐ")
print(f"💰 Giá cao nhất: {df['price'].max():,.0f} VNĐ")

print(f"\n⭐ Điểm đánh giá TB: {rated['rating_average'].mean():.2f}/5")
print(f"📝 Tổng số reviews: {df['review_count'].sum():,}")
print(f"🛒 Tổng đã bán: {df['quantity_sold'].sum():,}")

print("\n" + "=" * 60)
print("✅ HOÀN THÀNH PHÂN TÍCH!")
print("=" * 60)

# %%
# Đóng kết nối database
db.disconnect()
print("✅ Đã đóng kết nối database")
