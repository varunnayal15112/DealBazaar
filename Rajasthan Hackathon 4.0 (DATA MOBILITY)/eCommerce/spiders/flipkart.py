# -*- coding: utf-8 -*-
"""
Created on Tue Nov 21 11:13:30 2017

@author: vicky
"""

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
cursor.execute("""TRUNCATE Flipkart""")
cnx.commit()
#cnx.close()

class FlipkartProductSpider(scrapy.Spider):
    #spider name
    name = 'flipkart'

    def start_requests(self):
        #url formed as per user defined category
        yield scrapy.Request('https://www.flipkart.com/search?otracker=start&as-show=on&as=off&q=%s' % self.category,callback=self.parse)

    def parse(self,response):
        #Extracting the content using css selectors
        start_urls=[]
        urls = response.css("div._3liAhj a.Zhf2z-::attr(href)").extract()
        for link in urls:
            start_urls.append("https://www.flipkart.com"+link)
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
        url=str(response.xpath('/html/head/meta[24]/@content').extract_first())
        currency=str(response.xpath('.//*[@class="_3auQ3N _16fZeb"]/text()').extract_first())
        if currency=='':
            currency=str(response.xpath('.//*[@class="_1vC4OE _37U4_g"]/text()')[0].extract())
            price=str(response.xpath('.//*[@class="_1vC4OE _37U4_g"]/text()')[1].extract())
            price=currency+" "+price
            discount_price='none'
        else:
            price=str(response.xpath('.//*[@class="_3auQ3N _16fZeb"]/text()')[1].extract())
            price=currency+" "+price
            discount_price=str(response.xpath('.//*[@class="_1vC4OE _37U4_g"]/text()')[1].extract())
            discount_price=currency+" "+discount_price
        title=str(response.xpath('.//*[@class="_3eAQiD"]/text()').extract_first())
        product_rating=str(response.xpath('.//*[@class="niH0FQ"]/span[1]/div/text()').extract_first())
        if product_rating=='':
            product_rating='none'
        product_rating_count=str(response.xpath('.//*[@class="_38sUEc"]/span/span/text()').extract_first())
        if product_rating_count=='':
            product_rating_count='none'
        else:
            product_rating_count=product_rating_count[:-1]

        #item_specifics=str(response.css(".ui-box.product-property-main span::text").extract())
        item_specifics='none'
        seller_name=str(response.xpath('.//*[@id="sellerName"]//span/text()').extract_first())

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
            cursor.execute("""INSERT INTO Flipkart VALUES(%s,%s,%s,%s,%s,%s)""" , (title,price,discount_price,product_rating,product_rating_count,url))
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
