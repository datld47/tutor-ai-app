def findMax(list):
    if len(list)>0:
        max = list[0]
        for item in list:
            if item > max:
                max = item
        return max
    else:
        return None
        
print(findMax([-1,0,2,3,5]))