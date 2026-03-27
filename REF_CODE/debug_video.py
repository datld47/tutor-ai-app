from utils import get_video_url, get_video_base_url

concept_name = "Chương_1_Tiết 1_Khái niệm và Tiếp cận"
print(f"Base URL: {get_video_base_url()}")
print(f"Concept Name: {concept_name}")
url = get_video_url(concept_name)
print(f"Generated URL: {url}")

# Test strict regex
import re
match = re.search(r'Chương_(\d+)_Tiết\s*(\d+)', concept_name, re.IGNORECASE)
print(f"Regex Match: {match}")
if match:
    print(f"Groups: {match.groups()}")
