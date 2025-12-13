a=[
    [3,6,12,3],
    [4,5,6,9],
    [7,2,14,8],
    
]
def cancel(row_1,row2):
    return [i1-i2 for i1,i2 in zip(row_1,row2)]
def multiple(row,factor):
    return [i*factor for i in row]

for i in range(len(a)-1):
    for ii in range(i,len(a)-1):
        print(a[ii+1][i]/a[i][i])
        a[ii+1]=cancel(a[ii+1],multiple(a[i],a[ii+1][i]/a[i][i]))
    print(a)
print(a)