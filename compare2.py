file_list = ['data/test0.csv', 'data/test1.csv']

with open(file_list[0], 'r', encoding='utf-8') as f:
    f1 = f.readlines()

with open(file_list[1], 'r', encoding='utf-8') as f:
    f2 = f.readlines()

for row1 in f1:
    if row1 not in f2:
        print("Tag removed:", row1.strip()) 

for row2 in f2:
    if row2 not in f1:
        print("Tag added:", row2.strip())  
