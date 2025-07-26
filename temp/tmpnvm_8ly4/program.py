def find_max(danh_sach):
	max_num = danh_sach[0]
   for num in danh_sach:
        if num > max_num: # Lỗi logic ở đây, đúng ra phải là >
            max_num = num
    return max_num