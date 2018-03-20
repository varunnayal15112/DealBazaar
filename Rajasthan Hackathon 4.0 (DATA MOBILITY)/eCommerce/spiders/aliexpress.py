# -*- coding: utf-8 -*-
import scrapy

import mysql.connector
#database connection
config = {
   'user': 'root',
   'password': 'aitpune411015',
   'host': '127.0.0.1',
   'database': 'DealBazaar',
   'raise_on_warnings': True,
 }

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()
cursor.execute("""TRUNCATE AliExpress""")
cnx.commit()
#cnx.close()

class AliexpressSpider(scrapy.Spider):
    #spider name
    name = 'aliexpress'

    def start_requests(self):
        #url formed as per user defined category
        # g-y for grid view
        yield scrapy.Request('https://www.aliexpress.com/wholesale?catId=0&initiative_id=SB_20171114192306&g=y&SearchText=%s' % self.category,callback=self.parse)

    def parse(self,response):
        #Extracting the content using css selectors
        start_urls=[]
        urls =response.css("div.info a.history-item.product::attr(href)").extract()
        for link in urls:
            start_urls.append("https:"+link)
        for url in start_urls:
            print(url)
            #calling parse function as per url to scrap info related to the product link
            yield scrapy.Request(url=url, callback=self.parse_product_info)
        info={
            'status':'successfully scrapped',
          }
        yield info

    def parse_product_info(self, response):

        #Extracting the content using css or xpath selectors
        url=str(response.xpath('/html/head/meta[7]/@content').extract_first())
        currency=str(response.xpath('.//*[@class="p-symbol"]/text()').extract_first())
        price=str(response.xpath('//*[@class="p-price"]/text()').extract_first())
        if price==' - ':
            price=str(response.xpath('.//*[@class="p-price"]/span/text()').extract_first())+"-"+str(response.xpath('.//*[@class="p-price"]/span[2]/text()').extract_first())
        price=currency+price
        discount_price=str(response.xpath('//*[@id="j-sku-discount-price"]/text()').extract_first())
        title=str(response.css("title::text").extract_first())
        product_rating=str(response.xpath('//*[@id="j-customer-reviews-trigger"]/span[2]/text()').extract_first())
        product_rating_count=str(response.xpath('//*[@id="j-customer-reviews-trigger"]/span[3]/text()').extract_first())
        item_specifics=str(response.css(".ui-box.product-property-main span::text").extract())
        seller_name=str(response.xpath('//*[@id="j-store-info-wrap"]/dl/dd[1]/a/text()').extract_first())

        # print ('URL :',url)
        # print('CURRENCY :',currency)
        # print ('Price :',price)
        # print ('D_Price :',discount_price)
        # print ('Title :',title)
        # print ('P_Rating :',product_rating)
        # print ('P_R_Count :',product_rating_count)
        # print ('Item_Specifics :',item_specifics)
        # print ('Seller_Name :',seller_name)

        if url!='' and price!='' and discount_price!='' and title!='' and product_rating!='' and product_rating_count!='':
            cursor.execute("""INSERT INTO AliExpress VALUES(%s,%s,%s,%s,%s,%s)""" , (title,price,discount_price,product_rating,product_rating_count,url))
            print ("%d rows were inserted" % cursor.rowcount)
            cnx.commit()

        #create a dictionary to store the scraped info
        scraped_info = {

            'url' : url,
            'price' : price,
            'discount_price' : discount_price,
            'title' : title,
            'product_rating' : product_rating,
            'product_rating_count' : product_rating_count,
            'item_specifics' : item_specifics,
            'seller_name' : seller_name,
        }

        #yield or give the scraped info to scrapy
        yield scraped_info
