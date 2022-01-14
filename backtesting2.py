import csv
file=open('BANKNIFTY.csv','r')
fout=open("myfile.txt",'a')
csvreader = csv.reader(file)
rows=[]
for row in csvreader:
    rows.append(row)
# print(rows[0])
curr=rows[0]
prevdate=curr[1]
time=curr[2]
ope=float(curr[3])
high=float(curr[4])
low=float(curr[5])
close=float(curr[6])
hrs=time[0:2]
mins=int(time[3:])
maxi=high
mini=low
flag=0
sl=0
flag2=0 # 0-no transac, 1- transac done
totalprofit=0
for i in range(1,len(rows)):
    curr=rows[i]
    date=curr[1]
    if date==prevdate and flag2==0:
        time = curr[2]
        ope = float(curr[3])
        high = float(curr[4])
        low = float(curr[5])
        close = float(curr[6])
        hrs = time[0:2]
        mins = int(time[3:])
        if hrs=='09' and mins<=30:
            if high>=maxi:
                maxi=high
            if low<=mini:
                mini=low
        elif flag==0: # buying or selling
            if ope>maxi:
                buy=ope
                flag=1
            elif high>maxi:
                buy=high
                flag = 1
            elif low>maxi:
                buy=low
                flag = 1
            elif close>maxi:
                buy=close
                flag = 1
            if ope<mini:
                sell=ope
                flag = 2
            elif high<mini:
                sell=high
                flag = 2
            elif low<mini:
                sell=low
                flag = 2
            elif close<mini:
                sell=close
                flag = 2
            if flag==1:
                sl = (0.5 / 100) * buy
                sl = buy - sl
            elif flag==2:
                sl = (0.5 / 100) * sell
                sl = buy + sl
        elif flag==1: #stop loss first buy then sell
            if ope<sl:
                sold=ope
                flag2=1
            elif high<sl:
                sold=high
                flag2 = 1
            elif low<sl:
                sold=low
                flag2 = 1
            elif close<sl:
                sold=close
                flag2 = 1
            if flag2==1:
                diff=sold-buy
                totalprofit+=diff
                # print(date,": Bought at ",buy," and sold at ",sold ," at time: ",time ," for a profit/loss of =",diff)
                strx=date+": Bought at "+str(buy)+" and sold at "+str(sold)+" at time: "+time +" for a profit/loss of ="
                str2=str(diff)+"\n"
                l = [strx.ljust(95,"="), str2]
                fout.writelines(l)
        elif flag==2:#stop loss first sell then buy
            if ope>sl:
                bought=ope
                flag2=1
            elif low>sl:
                bought=low
                flag2 = 1
            elif high>sl:
                bought=high
                flag2 = 1
            elif close>sl:
                bought=close
                flag2 = 1
            if flag2==1:
                diff=sell-bought
                totalprofit+=diff
                # print(date,": Short Sold at ",sell," and bought at ",bought ," at time: ",time ," for a profit/loss of =",diff)
                strx=date+": Short Sold at "+str(sell)+" and bought at "+str(bought)+" at time: "+time+" for a profit/loss of ="
                str2 = str(diff) + "\n"
                l = [strx.ljust(95,"="), str2]
                fout.writelines(l)

    elif date!=prevdate:
        if flag2==0:
            if flag==1:
                sold=close
                diff=sold-buy
                totalprofit += diff
                # print(prevdate,": Bought at ",buy," and sold at ",sold ," at time: ",time ," for a profit/loss of=",diff)
                strx=prevdate+": Bought at "+str(buy)+" and sold at "+str(sold)+" at time: "+time +" for a profit/loss of ="
                str2 = str(diff) + "\n"
                l = [strx.ljust(95,"="), str2]
                fout.writelines(l)
            elif flag==2:
                bought=close
                diff=sell-bought
                totalprofit+=diff
                # print(prevdate,": Short Sold at ",sell," and bought at ",bought ," at time: ",time ," for a profit/loss of=",diff)
                strx = prevdate + ": Short Sold at " + str(sell) + " and bought at " + str(bought) + " at time: " + time + " for a profit/loss of ="
                str2 = str(diff) + "\n"
                l = [strx.ljust(95,"="), str2]
                fout.writelines(l)
        time = curr[2]
        ope = float(curr[3])
        high = float(curr[4])
        low = float(curr[5])
        close = float(curr[6])
        hrs = time[0:2]
        mins = int(time[3:])
        maxi = high
        mini = low
        flag2=0
        flag=0
        prevdate=date
print("total profit ",totalprofit)
strx="\nTotal Annual Profit/Loss ="
str2=str(totalprofit)+"\n"
l = [strx.ljust(95,"="), str2]
fout.writelines(l)






