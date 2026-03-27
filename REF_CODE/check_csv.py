import csv
import sys

# Force UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

csv_path = r"d:\MY_CODE\WebPersionalLearning\DB\TMDT_Chuong1\Chương_1_Tiết 1_Khái niệm và Tiếp cận.csv"

try:
    with open(csv_path, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        print(f"Headers: {headers}")
        row1 = next(reader)
        print(f"Row 1: {row1}")
except Exception as e:
    print(f"Error: {e}")
