from bs4 import BeautifulSoup #to parse HTML data
import os
import shutil
import requests #to get HTML data
import xlsxwriter #to save scrapped data to the excel spreadsheet
from datetime import date #to get today's date which will be used in naming of the file
import re #to get rid of text in price column
from time import sleep

today = date.today()
current_path = str(os.getcwd()) + "\\" + str(today) + ".xlsx"


print("Today's date:", today)

products = {"rtx+3060","rtx+3070","rtx+3080+10","rtx+3090","rtx+4080","rtx+4090","rx+6700","rx+6800","rx+6900",
            "samsung+qn90b+43","samsung+qn90b+50","samsung+qn90b+55","samsung+qn90b+65","samsung+qn90b+75",
            'lg+oled+c2+42','lg+oled+c2+48','lg+oled+c2+55','lg+oled+c2+65','lg+oled+c2+77',
            'samsung+s95b+55','samsung+s95b+65'
            }
row = 1
column = 0
row1 = 1
column1 = 1
column2 = 2
column3 = 3
nameOfWorkbook = str(today)+".xlsx"
print(nameOfWorkbook)
workbook = xlsxwriter.Workbook(nameOfWorkbook)
delay = 1
#workbook = xlsxwriter.Workbook(r'W:\Coding\PythonProjects\data.xlsx')
worksheet = workbook.add_worksheet()
worksheet.write_row(0, 0, ['Name', 'Price','Query Name','Date of Extraction'])
for product in products:
    url = f"https://www.salidzini.lv/cena?q={product}"
    response = requests.get(url)
    page = response.text
    sleep(delay)
    # print(webpage.text)
    soup = BeautifulSoup(page,'html.parser')
    names = soup.findAll("h2", class_="item_name")
    #results = soup.find("div", class_="item_box_main")
    #print(results)


    for name in names:
        #print(name.text.strip(), end="\n"*2)
        #a = str(name.text.strip())
        nameAsText = str(name.text.strip())
        worksheet.write(row, column, nameAsText)
        worksheet.write(row,column2,product)
        worksheet.write(row,column3,today)
        sleep(delay)
        row += 1


    prices = soup.findAll("div", class_="item_price")
    for price in prices:
        #print(price.text.strip(),end="\n"*2)
        PriceAsText = str(price.text.strip())
        PriceAsText = PriceAsText.split(".")
        PriceAsText = re.sub("[^0-9]", "", PriceAsText[0])
        sleep(delay)
        worksheet.write(row1, column1, PriceAsText)
        row1 += 1

workbook.close()
shutil.move(current_path,f"W:\\Coding\\PythonProjects\\ScrappedData\\OneDrive\\Salidzini_scrapping")
print("Data is extracted succesfully!")
