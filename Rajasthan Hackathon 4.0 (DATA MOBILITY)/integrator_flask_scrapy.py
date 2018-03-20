from flask import Flask, redirect, url_for, render_template, request
import subprocess
import time

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

# Initialize the Flask application
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/home',methods = ['POST','GET'])
def return_to_home():
    if request.method == 'POST':
        return redirect(url_for('home'))

@app.route('/result',methods = ['POST', 'GET'])
def result():
    product_name = str(request.form['product_name'])
    print (product_name)
    #return product_name
    """
    Run spider in another process and store items in file. Simply issue command:

    > scrapy crawl <spider_name> -a category=<argument/parameter>

    wait for  this command to finish, and read output.json to client.
    """
    ePlatform = str(request.form['ePlatform'])
    if ePlatform == 'AliExpress':
        spider_name = "aliexpress"
    elif ePlatform == 'Flipkart':
        spider_name = "flipkart"
    elif ePlatform == 'Amazon':
        spider_name = "amazon"
    elif ePlatform == 'Ebay':
        spider_name = "ebay"
    print (spider_name)
    subprocess.check_output(['scrapy', 'crawl', spider_name, "-a", "category="+product_name])
    #return redirect(url_for('home'))
    if ePlatform == 'AliExpress':
        table_name = "AliExpress"
    elif ePlatform == 'Flipkart':
        table_name = "Flipkart"
    elif ePlatform == 'Amazon':
        table_name = "Amazon"
    elif ePlatform == 'Ebay':
        table_name = "Ebay"
    cursor.execute("""SELECT * FROM %s""" %table_name)
    data = cursor.fetchall()
    cnx.commit()
    print (data)
    return render_template('print_items_table.html',items=data)
    #with open("output.json") as items_file:
    #    return items_file.read()

if __name__ == '__main__':
    app.run(debug=True)
