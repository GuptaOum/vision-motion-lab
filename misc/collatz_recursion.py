def recursion(lst,ind=0):
    if ind>=len(lst):
        return
    if lst[ind]%2==0:
        lst[ind]//=2
    else:
        lst[ind]=lst[ind]*3+1
    recursion(lst,ind+1)
    if ind< len(lst)-1:
        lst[ind]+=lst[ind+1]
number=[5,8,3,7,10]
recursion(number)
for i in range(len(number)-1,-1,-1):
    number[i]=number[i]-(number[i-1] if i>0 else 0)
print(number)
