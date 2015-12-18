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

#store todays date for file naming and to make sure we dont double up checks on data pulled from the website
todaysDate = time.strftime("%m/%d/%Y")
todaysDateNoSlash = time.strftime("%Y%m%d")

#pull html from the website and parse it into xPATH in the tree variable
page = requests.get('http://www.marketwatch.com/tools/stockresearch/updown')
tree = html.fromstring(page.content)

#initialize the array used for holding our daily data
#data1 = [date, Stock Name, null]
#data2 = [number of analysts, stock name, Average Recommendation, investopedia open price today, average target price]
stockArray2D = [[0 for x in range(6)] for x in range(200)] 

#The stockmarket page has the most recent 200 entries on the page, so we pull in the 200 entries and grab 
#the appropriate data we want
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
    
#Iterates through our array and converts the list objects in each cell to strings because xPATH is stupid and inserts /text as a list object
i=0
while i < 200:
    j=0
    while j < 2:
        tempList = stockArray2D[i][j]
        tempStr = str(tempList[0])
        stockArray2D[i][j] = tempStr
        j+=1
    i+=1    

#Removes all entries that didnt occur TODAY    
i=len(stockArray2D)-1   
while i >= 0:
    if stockArray2D[i][0] != todaysDate:
        stockArray2D.pop()
    i=i-1

    
#
#Data Analysis to SORT stocks by the number of firms with an analysis on them
#

#Acquire the number of analysts and the average rating
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
    tempXpath='//*[@id="maincontent"]/div[1]/table[1]/tbody/tr[1]/td[4]/text()'
    stockArray2D[i][4] = tree.xpath(tempXpath)
    i=i+1 

#Acquire the opening price from investopedia today
i=0
j=len(stockArray2D)
while i < j:
    getAnalystString = "http://www.investopedia.com/markets/stocks/"+ str(stockArray2D[i][1].lower()) +"/"
    page = requests.get(getAnalystString)
    tree = html.fromstring(page.content)
    tempXpath='//*[@id="block-system-main"]/div/div[3]/div/div[2]/div[1]/table/tbody/tr[5]/td[2]/text()'
    tempString= tree.xpath(tempXpath)
    tempString= str(tempString[0])
    stockArray2D[i][3] = float(tempString)
    i=i+1     

#go through the array and check to make sure the data is valid. If there is a null 
#in the number of analyst column, delete the entry row, if there is anything but a number
#remove it, and convert the string of numbers into an int. Also if the number of analysts
#is less than 10(this number will be changed to dynamic and editable later) make the 
#average rating column null to be deleted in the next loop
i=0
j=len(stockArray2D)
while i < j:
    if not stockArray2D[i][0]:
        del stockArray2D[i]
        i=i-1        
    else :
        tempList = stockArray2D[i][0]
        tempStr = str(tempList[0])
        tempStr = re.sub("[^0-9]", "", tempStr)
        tempStr = int(tempStr)
        if tempStr < 10:
            stockArray2D[i][2] = ""
        stockArray2D[i][0] = tempStr  
    i=i+1
    j=len(stockArray2D)
    
#go through the array and check to make sure the data is valid. If there is a 
#null in the average rating column, delete the entry row, if there is anything 
#but letters remove it   
i=0
j=len(stockArray2D)
while i < j:
    if not stockArray2D[i][2]:
        del stockArray2D[i]
        i=i-1        
    else :
        tempList = stockArray2D[i][2]
        tempStr = str(tempList[0])
        tempStr = re.sub("[^A-z]","", tempStr)
        stockArray2D[i][2] = tempStr        
    i=i+1
    j=len(stockArray2D)   
    
#make column 4 a float and not object
i=0
j=len(stockArray2D)
while i < j:
    tempList = stockArray2D[i][4]
    tempStr = str(tempList[0])
    stockArray2D[i][4] = float(tempStr)
    stockArray2D[i][5] = float('%.3f'%(stockArray2D[i][4]/stockArray2D[i][3]))
    i=i+1
   
#delete any duplicate entries due to multiple analysts changing their recommendation
i=0
j=len(stockArray2D)-1
while i < j:
    if stockArray2D[i][1] == stockArray2D[i+1][1]:
        del stockArray2D[i]
        i=i-1              
    i=i+1
    j=len(stockArray2D)-1

#delete any entries that are changes to HOLD, underweight, or sell
i=0
j=len(stockArray2D)
while i < j:
    if stockArray2D[i][2] == "Hold":
        del stockArray2D[i]
        i=i-1              
    if stockArray2D[i][2] == "Underweight":
        del stockArray2D[i]
        i=i-1              
    if stockArray2D[i][2] == "Sell":
        del stockArray2D[i]
        i=i-1              
    i=i+1
    j=len(stockArray2D)-1

numBuy=0
i=0
j=len(stockArray2D)
while i < j:
    if stockArray2D[i][2] == "Buy":
        numBuy=numBuy+1
    i=i+1
    
stockArray2D.sort()
stockArray2D.reverse()
    
i=0
j=len(stockArray2D)
while i < j:
    print stockArray2D[i]
    i=i+1

#Convert number of analysts to a ranking    
i=0
j=len(stockArray2D)
while i < j:
    stockArray2D[i][0] = int(i+1)
    i=i+1
    j=len(stockArray2D)

stockArray2D.sort()
   
   
i=0
j=len(stockArray2D)
while i < j:
    tempStrA = stockArray2D[i][0]
    tempStrB = stockArray2D[i][1]
    stockArray2D[i][0] = stockArray2D[i][2]
    stockArray2D[i][1] = tempStrA
    stockArray2D[i][2] = tempStrB
    i=i+1
    j=len(stockArray2D)
    

#sort the stocks by number of analysts in descending order    
stockArray2D.sort()
    
#Dwindle to 20
i=20
j=len(stockArray2D)
while i < j:
    stockArray2D.pop()
    j=len(stockArray2D)
    
    
i=0
j=len(stockArray2D)
while i < j:
    if i < numBuy:
        stockArray2D[i][0] = float(100)
    else:    
        tempStrA = stockArray2D[i][0]
        stockArray2D[i][0] = float(stockArray2D[i][5])
        stockArray2D[i][5] = tempStrA
    i=i+1

stockArray2D.sort()
stockArray2D.reverse()
    
i=0
j=len(stockArray2D)
while i < j:
    if i < numBuy:
        stockArray2D[i][0] = "Buy"
    else:    
        tempStrA = stockArray2D[i][0]
        stockArray2D[i][0] = stockArray2D[i][5]
        stockArray2D[i][5] = float(tempStrA)
    i=i+1
    
#Dwindle to 10
i=10
j=len(stockArray2D)
while i < j:
    stockArray2D.pop()
    j=len(stockArray2D)
    
    

#create a filename based on the date, delete it if it already exists,
#open the file, write all of the entries in line by line, and close file
fileName = str(todaysDateNoSlash) + "_newStocks.txt"   
if os.path.exists(fileName):
    os.remove(fileName)
f = open(fileName,'w')
i=0
j=len(stockArray2D)
while i < j:
    f.write(str(stockArray2D[i])+"\n") # python will convert \n to os.linesep
    i=i+1  
f.close()   
