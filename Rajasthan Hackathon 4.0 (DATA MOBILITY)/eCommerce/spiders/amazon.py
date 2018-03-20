# -*- coding: utf-8 -*-

import scrapy
import requests
import re
from bs4 import BeautifulSoup

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
cursor.execute("""TRUNCATE Amazon""")
cnx.commit()
#cnx.close()

class AmazonProductSpider(scrapy.Spider):
    #spider name
    name = "amazon"
    #allowed_domains = ["amazon.in"]
    def start_requests(self):

        #url formed as per user defined category
        url = 'https://www.amazon.in/s?keywords=%s' % self.category
        print (url)
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        page = requests.get(url,headers=headers)

        soup = BeautifulSoup(page.content, 'html.parser')
        link_all=[]
        count_link=0
        for link in soup.find_all('a',attrs={'class' : 'a-link-normal a-text-normal' , 'href' : re.compile("^https://www.amazon.in/")}):
            count_link+=1
            link_all.append(link.get('href'))
        start_urls=[]
        for i in range(0,count_link,2):
            start_urls.append(link_all[i])
        for url in start_urls:
            #calling parse function as per url to scrap info related to the product link
            print (url)
            yield scrapy.Request(url=url,headers=headers,callback=self.parse_product_info)

    def parse_product_info(self, response):

        headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.90 Safari/537.36'}
        page = requests.get(response.url,headers=headers)
        soup = BeautifulSoup(page.content, 'html.parser')

        #Extracting the content using css or xpath selectors or BeautifulSoup
        url = response.url
        title = response.xpath('//h1[@id="title"]/span/text()').extract()
        sale_price = response.xpath('//span[contains(@id,"ourprice") or contains(@id,"saleprice")]/text()').extract()
        category = response.xpath('//a[@class="a-link-normal a-color-tertiary"]/text()').extract()
        availability = response.xpath('//div[@id="availability"]//text()').extract()
        if(soup.find('i',attrs={'class' : 'a-icon a-icon-star a-star-3'})):
            product_rating = soup.find('i',attrs={'class' : 'a-icon a-icon-star a-star-3'}).get_text()
        else:
            product_rating='none'

        if(soup.find('span',attrs={'id' : 'acrCustomerReviewText'})):
            product_rating_count = soup.find('span',attrs={'id' : 'acrCustomerReviewText'}).get_text()
        else:
            product_rating_count='none'


        url=str(url)
        title = str(''.join(title).strip())
        price = str(''.join(sale_price).strip())
        category = str(','.join(map(lambda x: x.strip(), category)).strip())
        availability = str(''.join(availability).strip())
        product_rating = str(product_rating)
        product_rating_count = str(product_rating_count)

        discount_price = 'none'
        item_specifics = 'none'
        seller_name = 'none'


        # print ('URL :',url)
        # print('CURRENCY :',currency)
        # print ('Price :',price)
        # print ('D_Price :',discount_price)
        # print ('Title :',title)
        # print ('P_Rating :',product_rating)
        # print ('P_R_Count :',product_rating_count)
        # print ('Item_Specifics :',item_specifics)
        # print ('Seller_Name :',seller_name)
        # print ('Seller_rating :',seller_rating)

        if url!='' and price!='' and discount_price!='' and title!='' and product_rating!='' and product_rating_count!='':
            cursor.execute("""INSERT INTO Amazon VALUES(%s,%s,%s,%s,%s,%s)""" , (title,price,discount_price,product_rating,product_rating_count,url))
            print ("%d rows were inserted" % cursor.rowcount)
            cnx.commit()

        # create a dictionary to store the scraped info
        scraped_info = {

            'url' : url,
            'price' : price,
            'discount_price' : discount_price,
            'title' : title,
            'product_rating' : product_rating,
            'product_rating_count' : product_rating_count,
            'item_specifics' : item_specifics,
            'seller_name' : seller_name,
            #'seller_rating' : seller_rating,
        }

        # yield or give the scraped info to scrapy
        yield scraped_info
