from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from lxml import etree
from datetime import datetime
import time
import pandas as pd
import os


#呼叫瀏覽器
chrome_options = ChromeOptions()
chrome_options.add_experimental_option("detach",True)
browser = webdriver.Chrome(options=chrome_options)

# 抓取網頁資料
browser.get('https://www.momoshop.com.tw/edm/cmmedm.jsp?lpn=O1K5FBOqsvN&n=1')
html = browser.page_source

browser.close()

#解析資料
html = etree.HTML(html)

#爬蟲所需資料

event_time = html.xpath('//div[@class="MENTAL"][1]/div[@class="dateTime"]/div[@class="time"]/span/text()')
product_image = html.xpath('//div[@class="MENTAL"][1]/ul/li/div[@class="productImage"]/img/@src')
product_brand1 = html.xpath('//div[@class="MENTAL"][1]/ul/li/div[@class="brand"]/text()')
product_brand2 = html.xpath('//div[@class="MENTAL"][1]/ul/li/div[@class="brand2"]/text()')
discount = html.xpath('//div[@class="MENTAL"][1]/ul/li/div[@class="discountArea"]/div[1]/span/text()')
old_price = html.xpath('//div[@class="MENTAL"][1]/ul/li/div[@class="discountArea"]/div[2]/span/text()') # print純數字需.split('$')[1]
quantity = html.xpath('//div[@class="MENTAL"][1]/ul/li/div[@class="last"]/span/text()')
dis_price = html.xpath('//div[@class="MENTAL"][1]/ul/li/div[@class="price"]/span/text()')# print純數字需.replace(',','')
p_link = html.xpath('//div[@class="MENTAL"][1]/ul/li/div[@class="topnavArea"]/a/@href') # 連結整理 'https:'+link
nowtime = datetime.now().strftime("%Y/%m/%d %H:%M:%S") #日期時間分開 .split(' ')[0] .split(' ')[1]

'''
print(product_brand1)

t = 0 #測試用
for i in product_image:
    print(i)
    t += 1 #測試用
    if t>1: break #測試用
'''

# 確保所有列表的長度相同，以最長的列表為基準
max_length = max(len(event_time), len(product_image), len(product_brand1), len(product_brand2),
                  len(discount), len(old_price), len(quantity), len(dis_price), len(p_link))

# 將列表長度擴展至相同
event_time.extend([event_time[0]] * (max_length - len(event_time)))
product_image.extend(['none'] * (max_length - len(product_image)))
product_brand1.extend(['none'] * (max_length - len(product_brand1)))
product_brand2.extend(['none'] * (max_length - len(product_brand2)))
discount.extend(['none'] * (max_length - len(discount)))
old_price.extend(['none'] * (max_length - len(old_price)))
quantity.extend(['none'] * (max_length - len(quantity)))
dis_price.extend(['none'] * (max_length - len(dis_price)))
p_link.extend(['none'] * (max_length - len(p_link)))

# 格式處理
old_price = [i.split('$')[1] for i in old_price]
dis_price = [i.replace(',','') for i in dis_price]

#------------抓取產品類別---------------------------
#呼叫瀏覽器2
browser2 = webdriver.Chrome(options=chrome_options)

# 抓取網頁資料
#t = 0 #測試用
all_categ1=[]
all_categ2=[]
all_categ3=[]
all_categ4=[]
for link in p_link:
    link = 'https:'+link
    
    print(link)
    browser2.get(link)
    time.sleep(4)
    html2 = browser2.page_source
    
    #解析資料
    html2 = etree.HTML(html2)
    #t += 1 #測試用
    #if t>3: break #測試用
        
    # 爬蟲產品類別資料
    categ1 = html2.xpath('//div[@id="bt_2_layout_NAV"]/ul/li[2]/a/text()')
    if categ1: all_categ1.append(categ1[0])
    categ2 = html2.xpath('//div[@id="bt_2_layout_NAV"]/ul/li[3]/h1/a/text()')
    if categ2: all_categ2.append(categ2[0])
    categ3 = html2.xpath('//div[@id="bt_2_layout_NAV"]/ul/li[4]/a/text()')
    if categ3: all_categ3.append(categ3[0])
    categ4 = html2.xpath('//div[@id="bt_2_layout_NAV"]/ul/li[5]/h2/a/text()')
    if categ4: all_categ4.append(categ4[0])
    #print(categ1,categ2,categ3,categ4)
browser2.close()

all_categ1.extend(['none'] * (max_length - len(all_categ1)))
all_categ2.extend(['none'] * (max_length - len(all_categ2)))
all_categ3.extend(['none'] * (max_length - len(all_categ3)))
all_categ4.extend(['none'] * (max_length - len(all_categ4)))

#儲存進df
df=pd.DataFrame()
# 將資料組成字典
data = {
    "爬蟲日期": nowtime.split(' ')[0],
    "爬蟲時間": nowtime.split(' ')[1],
    "活動檔期": event_time,
    "品牌": product_brand1,
    "產品名稱": product_brand2,
    "產品類別1":all_categ1,
    "產品類別2":all_categ2,
    "產品類別3":all_categ3,
    "產品類別4":all_categ4,
    "折扣數": discount,
    "原價": old_price ,
    "數量": quantity,
    "折扣價": dis_price,
    "產品連結": ['https:' + link for link in p_link],
    "產品圖片": product_image,
}

try:
    # 建立 DataFrame
    df = pd.DataFrame(data)

    # 印出 DataFrame 的前几行
    print(df.head())

    # 設定 CSV 文件名稱
    filename = f'{datetime.now().strftime("%Y-%m-%d")}_momo.csv'

    # 檢查檔案是否存在
    if os.path.exists(filename):
        # 如果檔案已存在，則讀取現有 CSV 文件
        existing_df = pd.read_csv(filename)
        # 將新數據追加到現有 DataFrame
        updated_df = pd.concat([existing_df, df], ignore_index=True)

        # 寫入更新後的 DataFrame 到 CSV 文件
        updated_df.to_csv(filename, index=False)
    else:
        # 如果檔案不存在，則直接將 DataFrame 寫入到新建的 CSV 文件
        df.to_csv(filename, index=False)

    print(nowtime,'成功執行')
    
except Exception as e:
# 發生錯誤時，開啟文字檔並將相關資料寫入
    error_filename = f'error_{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.txt'
    with open(error_filename, 'w',encoding='UTF-8') as error_file:
        error_file.write(f"Error occurred at {nowtime}\n")
        error_file.write(f"Error details: {str(e)}\n")
        error_file.write("Data values:\n")
        for key, value in data.items():
            error_file.write(f"{key}: {value}\n")
    print(len(event_time),len(product_brand1),len(product_brand2),len(all_categ1),len(all_categ2),len(all_categ3),len(all_categ4),len(discount),len(old_price),len(quantity),len(dis_price),len(p_link),len(product_image))
    print(nowtime,'發生錯誤，已存成文字檔')

