import pandas as pd
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')

file_path = r"d:\MY_CODE\WebPersionalLearning\DB\TMDT_Chuong1\Chương_1_Tiết 1_Khái niệm và Tiếp cận.csv"
try:
    df = pd.read_csv(file_path, encoding='utf-8', engine='python')
except Exception as e:
    print(f"UTF-8 failed: {e}")
    try:
        df = pd.read_csv(file_path, encoding='utf-16', engine='python')
    except Exception as e:
        print(f"UTF-16 failed: {e}")
        exit()

print("Original Columns:", df.columns.tolist())
df.columns = [c.strip().lower() for c in df.columns]
print("Lowered Columns:", df.columns.tolist())
print("First row:", df.iloc[0].to_dict())
