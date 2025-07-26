def find_max(list):
    if len(list)>0:
        max = list[0]
        for item in list:
            if item > max:
                max = item
        return max
    else:
        return float('-inf')
        
print(find_max([3, 8, 2, 10, 4]))