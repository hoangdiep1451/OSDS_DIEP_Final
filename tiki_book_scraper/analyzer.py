"""
Module Phân tích và Trực quan hóa dữ liệu
Khảo sát thông tin và vẽ biểu đồ
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime

from config import CHARTS_DIR, MONGODB_URI, MONGODB_DATABASE
from database import DatabaseManager

# Cấu hình matplotlib cho tiếng Việt
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['figure.dpi'] = 100

# Màu sắc đẹp cho biểu đồ
COLORS = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FFEAA7', 
          '#DDA0DD', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E9']


class DataAnalyzer:
    """Lớp phân tích và trực quan hóa dữ liệu"""
    
    def __init__(self, connection_string=MONGODB_URI, db_name=MONGODB_DATABASE):
        """Khởi tạo analyzer"""
        self.db = DatabaseManager(connection_string, db_name)
        self.df = None
        os.makedirs(CHARTS_DIR, exist_ok=True)
        
    def load_data(self):
        """Load dữ liệu từ database"""
        self.db.connect()
        self.df = self.db.get_all_books()
        print(f"Đã load {len(self.df)} bản ghi từ database")
        return self.df
        
    def basic_statistics(self):
        """Thống kê cơ bản về dữ liệu"""
        print("\n" + "=" * 60)
        print("THỐNG KÊ CƠ BẢN")
        print("=" * 60)
        
        if self.df is None or len(self.df) == 0:
            print("Chưa có dữ liệu. Hãy chạy load_data() trước.")
            return
            
        print(f"\nTổng số sách: {len(self.df)}")
        print(f"Số thể loại: {self.df['category'].nunique()}")
        print(f"Số tác giả: {self.df['author'].nunique()}")
        print(f"Số nhà xuất bản: {self.df['publisher'].nunique()}")
        
        print("\nTHỐNG KÊ GIÁ:")
        print(f"   - Giá trung bình: {self.df['price'].mean():,.0f} VNĐ")
        print(f"   - Giá thấp nhất: {self.df['price'].min():,.0f} VNĐ")
        print(f"   - Giá cao nhất: {self.df['price'].max():,.0f} VNĐ")
        print(f"   - Giá trung vị: {self.df['price'].median():,.0f} VNĐ")
        
        print("\nTHỐNG KÊ ĐÁNH GIÁ:")
        rated = self.df[self.df['rating_average'] > 0]
        print(f"   - Số sách có đánh giá: {len(rated)}")
        print(f"   - Điểm TB: {rated['rating_average'].mean():.2f}/5")
        print(f"   - Tổng reviews: {self.df['review_count'].sum():,}")
        
        print("\nTHỐNG KÊ BÁN HÀNG:")
        print(f"   - Tổng đã bán: {self.df['quantity_sold'].sum():,}")
        print(f"   - TB mỗi sách: {self.df['quantity_sold'].mean():,.0f}")
        
        print("\nTHỐNG KÊ GIẢM GIÁ:")
        discounted = self.df[self.df['discount_rate'] > 0]
        print(f"   - Số sách giảm giá: {len(discounted)}")
        print(f"   - Giảm giá TB: {discounted['discount_rate'].mean():.1f}%")
        
    def plot_category_distribution(self):
        """Biểu đồ phân bố theo thể loại"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Đếm số sách theo thể loại
        category_counts = self.df['category'].value_counts()
        
        # Pie chart
        axes[0].pie(category_counts.values, labels=category_counts.index, 
                    autopct='%1.1f%%', colors=COLORS[:len(category_counts)],
                    explode=[0.05] * len(category_counts))
        axes[0].set_title('Phân bố sách theo thể loại', fontsize=14, fontweight='bold')
        
        # Bar chart
        bars = axes[1].barh(category_counts.index, category_counts.values, color=COLORS[:len(category_counts)])
        axes[1].set_xlabel('Số lượng sách')
        axes[1].set_title('Số lượng sách theo thể loại', fontsize=14, fontweight='bold')
        
        # Thêm số liệu trên bar
        for bar, count in zip(bars, category_counts.values):
            axes[1].text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2, 
                        f'{count}', va='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{CHARTS_DIR}/category_distribution.png', dpi=150, bbox_inches='tight')
        plt.show()
        print(f"Đã lưu biểu đồ: {CHARTS_DIR}/category_distribution.png")
        
    def plot_price_distribution(self):
        """Biểu đồ phân bố giá"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # Histogram giá
        axes[0, 0].hist(self.df['price'], bins=50, color='#4ECDC4', edgecolor='white', alpha=0.7)
        axes[0, 0].axvline(self.df['price'].mean(), color='red', linestyle='--', label=f'TB: {self.df["price"].mean():,.0f}đ')
        axes[0, 0].axvline(self.df['price'].median(), color='orange', linestyle='--', label=f'Median: {self.df["price"].median():,.0f}đ')
        axes[0, 0].set_xlabel('Giá (VNĐ)')
        axes[0, 0].set_ylabel('Số lượng')
        axes[0, 0].set_title('Phân bố giá sách', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        
        # Box plot giá theo thể loại
        category_order = self.df.groupby('category')['price'].median().sort_values().index
        sns.boxplot(data=self.df, x='category', y='price', ax=axes[0, 1], 
                   order=category_order, palette=COLORS)
        axes[0, 1].set_xticklabels(axes[0, 1].get_xticklabels(), rotation=45, ha='right')
        axes[0, 1].set_ylabel('Giá (VNĐ)')
        axes[0, 1].set_xlabel('')
        axes[0, 1].set_title('Phân bố giá theo thể loại', fontsize=12, fontweight='bold')
        
        # Phân bố khoảng giá
        price_ranges = pd.cut(self.df['price'], 
                             bins=[0, 50000, 100000, 200000, 500000, float('inf')],
                             labels=['<50K', '50K-100K', '100K-200K', '200K-500K', '>500K'])
        price_range_counts = price_ranges.value_counts().sort_index()
        
        axes[1, 0].bar(price_range_counts.index, price_range_counts.values, color=COLORS[:5])
        axes[1, 0].set_xlabel('Khoảng giá')
        axes[1, 0].set_ylabel('Số lượng')
        axes[1, 0].set_title('Số sách theo khoảng giá', fontsize=12, fontweight='bold')
        for i, (idx, v) in enumerate(price_range_counts.items()):
            axes[1, 0].text(i, v + 5, str(v), ha='center', fontsize=10)
        
        # Giá vs Giảm giá
        discounted = self.df[self.df['discount_rate'] > 0]
        axes[1, 1].scatter(discounted['original_price'], discounted['discount_rate'], 
                          alpha=0.5, c='#FF6B6B', s=30)
        axes[1, 1].set_xlabel('Giá gốc (VNĐ)')
        axes[1, 1].set_ylabel('Tỷ lệ giảm giá (%)')
        axes[1, 1].set_title('Mối quan hệ giá gốc và % giảm giá', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{CHARTS_DIR}/price_distribution.png', dpi=150, bbox_inches='tight')
        plt.show()
        print(f"Đã lưu biểu đồ: {CHARTS_DIR}/price_distribution.png")
        
    def plot_rating_analysis(self):
        """Phân tích đánh giá"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # Lọc sách có đánh giá
        rated = self.df[self.df['rating_average'] > 0].copy()
        
        # Histogram điểm đánh giá
        axes[0, 0].hist(rated['rating_average'], bins=20, color='#45B7D1', edgecolor='white')
        axes[0, 0].axvline(rated['rating_average'].mean(), color='red', linestyle='--', 
                          label=f'TB: {rated["rating_average"].mean():.2f}')
        axes[0, 0].set_xlabel('Điểm đánh giá')
        axes[0, 0].set_ylabel('Số lượng')
        axes[0, 0].set_title('Phân bố điểm đánh giá', fontsize=12, fontweight='bold')
        axes[0, 0].legend()
        
        # Điểm TB theo thể loại
        category_rating = self.df.groupby('category')['rating_average'].mean().sort_values()
        bars = axes[0, 1].barh(category_rating.index, category_rating.values, color=COLORS[:len(category_rating)])
        axes[0, 1].set_xlabel('Điểm đánh giá trung bình')
        axes[0, 1].set_title('Điểm đánh giá TB theo thể loại', fontsize=12, fontweight='bold')
        axes[0, 1].set_xlim(0, 5)
        for bar, val in zip(bars, category_rating.values):
            axes[0, 1].text(val + 0.05, bar.get_y() + bar.get_height()/2, 
                           f'{val:.2f}', va='center', fontsize=10)
        
        # Số reviews theo thể loại
        category_reviews = self.df.groupby('category')['review_count'].sum().sort_values()
        axes[1, 0].barh(category_reviews.index, category_reviews.values, color=COLORS[:len(category_reviews)])
        axes[1, 0].set_xlabel('Tổng số reviews')
        axes[1, 0].set_title('Tổng số reviews theo thể loại', fontsize=12, fontweight='bold')
        
        # Rating vs Số reviews
        axes[1, 1].scatter(rated['review_count'], rated['rating_average'], 
                          alpha=0.5, c='#96CEB4', s=30)
        axes[1, 1].set_xlabel('Số lượng reviews')
        axes[1, 1].set_ylabel('Điểm đánh giá')
        axes[1, 1].set_title('Mối quan hệ số reviews và điểm đánh giá', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{CHARTS_DIR}/rating_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        print(f"Đã lưu biểu đồ: {CHARTS_DIR}/rating_analysis.png")
        
    def plot_sales_analysis(self):
        """Phân tích doanh số bán hàng"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # Lọc sách có dữ liệu bán
        sold = self.df[self.df['quantity_sold'] > 0].copy()
        
        # Top 10 sách bán chạy
        top_sold = sold.nlargest(10, 'quantity_sold')
        axes[0, 0].barh(range(10), top_sold['quantity_sold'].values, color=COLORS[0])
        axes[0, 0].set_yticks(range(10))
        axes[0, 0].set_yticklabels([name[:30] + '...' if len(name) > 30 else name 
                                    for name in top_sold['name'].values])
        axes[0, 0].set_xlabel('Số lượng đã bán')
        axes[0, 0].set_title('Top 10 sách bán chạy nhất', fontsize=12, fontweight='bold')
        axes[0, 0].invert_yaxis()
        
        # Số lượng bán theo thể loại
        category_sold = self.df.groupby('category')['quantity_sold'].sum().sort_values()
        axes[0, 1].barh(category_sold.index, category_sold.values, color=COLORS[:len(category_sold)])
        axes[0, 1].set_xlabel('Tổng số lượng đã bán')
        axes[0, 1].set_title('Doanh số theo thể loại', fontsize=12, fontweight='bold')
        
        # Giá vs Số lượng bán
        axes[1, 0].scatter(sold['price'], sold['quantity_sold'], 
                          alpha=0.5, c='#DDA0DD', s=30)
        axes[1, 0].set_xlabel('Giá (VNĐ)')
        axes[1, 0].set_ylabel('Số lượng đã bán')
        axes[1, 0].set_title('Mối quan hệ giá và số lượng bán', fontsize=12, fontweight='bold')
        
        # Điểm đánh giá vs Số lượng bán
        rated_sold = sold[sold['rating_average'] > 0]
        axes[1, 1].scatter(rated_sold['rating_average'], rated_sold['quantity_sold'], 
                          alpha=0.5, c='#F7DC6F', s=30)
        axes[1, 1].set_xlabel('Điểm đánh giá')
        axes[1, 1].set_ylabel('Số lượng đã bán')
        axes[1, 1].set_title('Mối quan hệ đánh giá và doanh số', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{CHARTS_DIR}/sales_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        print(f"Đã lưu biểu đồ: {CHARTS_DIR}/sales_analysis.png")
        
    def plot_discount_analysis(self):
        """Phân tích giảm giá"""
        fig, axes = plt.subplots(1, 2, figsize=(14, 6))
        
        # Phân bố mức giảm giá
        discount_ranges = pd.cut(self.df['discount_rate'], 
                                bins=[-1, 0, 20, 40, 60, 100],
                                labels=['Không giảm', '1-20%', '21-40%', '41-60%', '>60%'])
        discount_counts = discount_ranges.value_counts()
        
        axes[0].pie(discount_counts.values, labels=discount_counts.index, 
                   autopct='%1.1f%%', colors=COLORS[:5],
                   explode=[0.05] * len(discount_counts))
        axes[0].set_title('Phân bố mức giảm giá', fontsize=12, fontweight='bold')
        
        # Giảm giá trung bình theo thể loại
        category_discount = self.df.groupby('category')['discount_rate'].mean().sort_values()
        bars = axes[1].barh(category_discount.index, category_discount.values, 
                           color=COLORS[:len(category_discount)])
        axes[1].set_xlabel('Tỷ lệ giảm giá trung bình (%)')
        axes[1].set_title('Giảm giá TB theo thể loại', fontsize=12, fontweight='bold')
        for bar, val in zip(bars, category_discount.values):
            axes[1].text(val + 0.5, bar.get_y() + bar.get_height()/2, 
                        f'{val:.1f}%', va='center', fontsize=10)
        
        plt.tight_layout()
        plt.savefig(f'{CHARTS_DIR}/discount_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        print(f"Đã lưu biểu đồ: {CHARTS_DIR}/discount_analysis.png")
        
    def plot_publisher_analysis(self):
        """Phân tích theo nhà xuất bản"""
        fig, axes = plt.subplots(1, 2, figsize=(16, 6))
        
        # Top 10 NXB có nhiều sách nhất
        publisher_counts = self.df['publisher'].value_counts().head(10)
        
        axes[0].barh(publisher_counts.index, publisher_counts.values, color=COLORS[0])
        axes[0].set_xlabel('Số lượng sách')
        axes[0].set_title('Top 10 NXB có nhiều sách nhất', fontsize=12, fontweight='bold')
        axes[0].invert_yaxis()
        
        # Điểm đánh giá TB của top 10 NXB
        top_publishers = publisher_counts.index.tolist()
        pub_ratings = self.df[self.df['publisher'].isin(top_publishers)].groupby('publisher')['rating_average'].mean()
        pub_ratings = pub_ratings.reindex(top_publishers)
        
        axes[1].barh(pub_ratings.index, pub_ratings.values, color=COLORS[1])
        axes[1].set_xlabel('Điểm đánh giá trung bình')
        axes[1].set_title('Điểm đánh giá TB của Top 10 NXB', fontsize=12, fontweight='bold')
        axes[1].invert_yaxis()
        axes[1].set_xlim(0, 5)
        
        plt.tight_layout()
        plt.savefig(f'{CHARTS_DIR}/publisher_analysis.png', dpi=150, bbox_inches='tight')
        plt.show()
        print(f"Đã lưu biểu đồ: {CHARTS_DIR}/publisher_analysis.png")
        
    def plot_correlation_heatmap(self):
        """Biểu đồ tương quan"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        # Chọn các cột số
        numeric_cols = ['price', 'original_price', 'discount_rate', 
                       'rating_average', 'review_count', 'quantity_sold']
        
        correlation = self.df[numeric_cols].corr()
        
        sns.heatmap(correlation, annot=True, cmap='RdYlGn', center=0,
                   fmt='.2f', square=True, ax=ax,
                   xticklabels=['Giá', 'Giá gốc', 'Giảm giá', 'Đánh giá', 'Reviews', 'Đã bán'],
                   yticklabels=['Giá', 'Giá gốc', 'Giảm giá', 'Đánh giá', 'Reviews', 'Đã bán'])
        
        ax.set_title('Ma trận tương quan giữa các biến', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig(f'{CHARTS_DIR}/correlation_heatmap.png', dpi=150, bbox_inches='tight')
        plt.show()
        print(f"Đã lưu biểu đồ: {CHARTS_DIR}/correlation_heatmap.png")
        
    def generate_all_charts(self):
        """Tạo tất cả biểu đồ"""
        print("\n" + "=" * 60)
        print("TẠO TẤT CẢ BIỂU ĐỒ PHÂN TÍCH")
        print("=" * 60)
        
        self.basic_statistics()
        
        print("\nĐang tạo biểu đồ...")
        
        self.plot_category_distribution()
        self.plot_price_distribution()
        self.plot_rating_analysis()
        self.plot_sales_analysis()
        self.plot_discount_analysis()
        self.plot_publisher_analysis()
        self.plot_correlation_heatmap()
        
        print("\n" + "=" * 60)
        print(f"ĐÃ TẠO TẤT CẢ BIỂU ĐỒ TẠI: {CHARTS_DIR}/")
        print("=" * 60)
        
    def export_report(self, filename="report.html"):
        """Xuất báo cáo HTML"""
        html_content = f"""
        <!DOCTYPE html>
        <html lang="vi">
        <head>
            <meta charset="UTF-8">
            <title>Báo cáo phân tích dữ liệu sách Tiki</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 40px; }}
                h1 {{ color: #2c3e50; }}
                h2 {{ color: #3498db; }}
                .stat {{ background: #f8f9fa; padding: 20px; margin: 10px 0; border-radius: 5px; }}
                img {{ max-width: 100%; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Báo cáo phân tích dữ liệu sách Tiki.vn</h1>
            <p>Ngày tạo: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            
            <h2>Thống kê tổng quan</h2>
            <div class="stat">
                <p><strong>Tổng số sách:</strong> {len(self.df)}</p>
                <p><strong>Số thể loại:</strong> {self.df['category'].nunique()}</p>
                <p><strong>Giá trung bình:</strong> {self.df['price'].mean():,.0f} VNĐ</p>
                <p><strong>Điểm đánh giá TB:</strong> {self.df[self.df['rating_average'] > 0]['rating_average'].mean():.2f}/5</p>
            </div>
            
            <h2>Biểu đồ phân tích</h2>
            <img src="category_distribution.png" alt="Phân bố theo thể loại">
            <img src="price_distribution.png" alt="Phân bố giá">
            <img src="rating_analysis.png" alt="Phân tích đánh giá">
            <img src="sales_analysis.png" alt="Phân tích doanh số">
            <img src="discount_analysis.png" alt="Phân tích giảm giá">
            <img src="publisher_analysis.png" alt="Phân tích NXB">
            <img src="correlation_heatmap.png" alt="Ma trận tương quan">
        </body>
        </html>
        """
        
        with open(f'{CHARTS_DIR}/{filename}', 'w', encoding='utf-8') as f:
            f.write(html_content)
            
        print(f"Đã xuất báo cáo: {CHARTS_DIR}/{filename}")


# Test module
if __name__ == "__main__":
    analyzer = DataAnalyzer()
    analyzer.load_data()
    analyzer.basic_statistics()
