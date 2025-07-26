def tim_so_lon_nhat(danh_sach):
    max_num = danh_sach[0]
    for num in danh_sach:
        if num < max_num:
            max_num = num
    return max_num

print(tim_so_lon_nhat([1,2,3,4])