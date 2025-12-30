import re
import os

# Danh sách các file cần xử lý
files_to_process = [
    'scraper.py',
    'analyzer.py', 
    'main.py',
    'database.py'
]

# Regex để loại bỏ emoji
emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
        u"\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
        "]+", flags=re.UNICODE)

# Thay thế các emoji cụ thể
emoji_replacements = {
    '✅': '',
    '❌': '',
    '⚠️': '',
    '📚': '',
    '🕷️': '',
    '📊': '',
    '📈': '',
    '🔍': '',
    '📖': '',
    '🏆': '',
    '⭐': '',
    '📄': '',
    '🚪': '',
    '📁': '',
    '✍️': '',
    '💰': '',
    '🛒': '',
    '🏷️': '',
    '🚀': '',
    '⏱️': '',
    '💾': '',
    '🧪': '',
    '👤': '',
    '📝': '',
    '📅': '',
    '👉': '',
    '⏎': '',
    '🎨': '',
    '🏗️': '',
    '🎉': '',
    '⚙️': '',
    '🔗': '',
    '💪': '',
    '👋': '',
}

for filename in files_to_process:
    filepath = os.path.join(os.path.dirname(__file__), filename)
    
    if not os.path.exists(filepath):
        continue
        
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Thay thế các emoji cụ thể
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        # Loại bỏ các emoji còn lại
        content = emoji_pattern.sub('', content)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"Đã xử lý: {filename}")
    except Exception as e:
        print(f"Lỗi khi xử lý {filename}: {e}")

print("\nHoàn tất!")
