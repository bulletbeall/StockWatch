#python fun
from lxml import html
from collections import deque
import requests
import re
import string
import time
import os

#Daily Initial Setup
#
#At the end of this initialization, whatever analysis has been updated today by marketwatch.com is imported and we are left
#with the list stockArray, which has a list all of the stocks whose analysis has been updated today
#
todaysDate = time.strftime("%m/%d/%Y")
todaysDateNoSlash = time.strftime("%Y%m%d")

page = requests.get('http://www.marketwatch.com/tools/stockresearch/updown')
tree = html.fromstring(page.content)

stockArray2D = [[0 for x in range(3)] for x in range(200)] 

i=1
while i < 201:
    j=1
    while j < 3:
        if j==1 :
            tempXpath='//*[@id="maincontent"]/div[1]/div/div[3]/table/tbody/tr['+str(i)+']/td['+str(j)+']/text()'
        else:  
            tempXpath='//*[@id="maincontent"]/div[1]/div/div[3]/table/tbody/tr['+str(i)+']/td['+str(j)+']/a/text()'
        stockArray2D[i-1][j-1] = tree.xpath(tempXpath)
        j+=1
    i+=1
    
i=0
while i < 200:
    j=0
    while j < 2:
        tempList = stockArray2D[i][j]
        tempStr = str(tempList[0])
        stockArray2D[i][j] = tempStr
        j+=1
    i+=1    

i=len(stockArray2D)-1   
while i >= 0:
    if stockArray2D[i][0] != todaysDate:
        stockArray2D.pop()
    i=i-1

    
#
#Data Analysis to SORT stocks by the number of firms with an analysison them
#
    
i=0
j=len(stockArray2D)

while i < j:
    getAnalystString = "http://www.marketwatch.com/investing/stock/"+stockArray2D[i][1]+"/analystestimates"
    page = requests.get(getAnalystString)
    tree = html.fromstring(page.content)
    tempXpath='//*[@id="maincontent"]/div[1]/table[1]/tbody/tr[2]/td[2]/text()'
    stockArray2D[i][0] = tree.xpath(tempXpath)
    tempXpath='//*[@id="maincontent"]/div[1]/table[1]/tbody/tr[1]/td[2]/text()'
    stockArray2D[i][2] = tree.xpath(tempXpath)
    i=i+1    

i=0
j=len(stockArray2D)
while i < j:
    if not stockArray2D[i][0]:
        del stockArray2D[i]
        i=i-1        
    else :
        j=len(stockArray2D)
        tempList = stockArray2D[i][0]
        tempStr = str(tempList[0])
        tempStr = re.sub("[^0-9]", "", tempStr)
        tempStr = int(tempStr)
        stockArray2D[i][0] = tempStr
    if not stockArray2D[i][2]:
        del stockArray2D[i]
        i=i-1        
    else :
        j=len(stockArray2D)
        tempList = stockArray2D[i][2]
        tempStr = str(tempList[0])
        tempStr = re.sub("[^A-z]","", tempStr)
        stockArray2D[i][2] = tempStr                
    i=i+1    
    
    
stockArray2D.sort()
stockArray2D.reverse()
    
fileName = str(todaysDateNoSlash) + "_newStocks.txt"   
if os.path.exists(fileName):
    os.remove(fileName)
f = open(fileName,'w')
i=0
j=len(stockArray2D)
while i < j:
    f.write(str(stockArray2D[i])+"\n") # python will convert \n to os.linesep
    i=i+1  
f.close() # you can omit in most cases as the destructor will call it   
