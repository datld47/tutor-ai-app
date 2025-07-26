def findMax(list):
    if len(list)>0:
        max = list[0]
        for i in range(1,len(list)):
            if max < list[i]:
                max = list[i]
        return max;
    return float('-inf')