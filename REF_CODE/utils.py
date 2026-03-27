import re
import os

def get_video_base_url():
    """Reads the base URL from DB/videosLinksCourse.txt"""
    try:
        file_path = os.path.join(os.getcwd(), 'DB', 'videosLinksCourse.txt')
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for line in lines:
                if line.startswith('http'):
                    return line.strip()
    except Exception as e:
        print(f"Error reading video base URL: {e}")
    
    # Fallback
    return "https://tranthanhthangbmt.github.io/WebTracNghiem/"

def get_video_url(concept_name):
    """
    Constructs the video URL from the concept name.
    Expected format: "Chương_1_Tiết 1_Khái niệm..."
    Target format: {base_url}/Video/Chuong_1_Tiet_1/index.html
    """
    base_url = get_video_base_url()
    
    # Extract Chapter and Lesson
    # Retry regex for "Chương_X" and "Tiết Y"
    # Case 1: "Chương_1_Tiết 1_..."
    # Regex robust for "Chương...Tiết..."
    # Handles: "Chương_1_Tiết 1", "Chương 1 Tiết 1", "Chuong_2_Tiet_2", etc.
    match = re.search(r'(?:Chương|Chuong)\D*(\d+)\D*(?:Tiết|Tiet)\D*(\d+)', concept_name, re.IGNORECASE)
    
    if match:
        chapter = match.group(1)
        lesson = match.group(2)
        
        # Ensure base_url ends with slash
        if not base_url.endswith('/'):
            base_url += '/'
            
        url = f"{base_url}Video/Chuong_{chapter}_Tiet_{lesson}/index.html"
        print(f"[DEBUG] Video URL generated for '{concept_name}': {url}")
        return url
    
    print(f"[DEBUG] No video match found for: '{concept_name}'")
    return None
