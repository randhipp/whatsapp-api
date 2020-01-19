import pymysql.cursors
import peewee
import schedule
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import datetime
import os
import json
from peewee import *
from flask import Flask, request
from flask_restful import reqparse, Resource, Api
from sqlalchemy import create_engine
from json import dumps
from flask_jsonpify import jsonify

browser = None
Contact = None
message = None
Link = "https://web.whatsapp.com/"
wait = None
choice = None
docChoice = None
doc_filename = None
unsaved_Contacts = None

parser = reqparse.RequestParser()

db_connect = MySQLDatabase('omapit',user='root',password='')

#db_connect = create_engine('sqlite:///chinook.db')
app = Flask(__name__)
api = Api(app)



def whatsapp_login():
    global wait, browser, Link
    chrome_options = Options()
    chrome_options.add_argument('--user-data-dir=./User_Data')
    browser = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(browser, 600)
    browser.get(Link)
    browser.maximize_window()
    print("QR scanned")

def sender():
    global Contact
    for i in Contact:
        send_message(i)
        print("Message sent to ", i)
    time.sleep(5)
    # browser.refresh()

def numberSender(custNumber):
    link = "https://web.whatsapp.com/send?phone=" + custNumber
    #driver  = webdriver.Chrome()
    browser.get(link)
    time.sleep(15)
    # browser.find_element_by_xpath('//*[@id="action-button"]').click()
    # time.sleep(5)
    # browser.find_element_by_xpath('//*[@id="content"]/div/div/div/a').click()
    # time.sleep(5)
    print("Sending message to", custNumber)
    send_unsaved_contact_message()

def send_unsaved_contact_message():
    global message
    x = 1
    
    try:
        time.sleep(7)
        input_box = browser.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        
        text = json.loads(message)
        
        invDetail = []

        # for detail in text['barang']:
        #     print(detail)

        for detail in text['barang']:
            invDetail.append(str(x) + ". "
                                + str(detail['kode']) + " : " 
                                + str(detail['qty']) + " set"
                                + "\n   @ " + str(detail['harga'])
                                + " = " + str(detail['total'])
                            )
            x += 1
        
        invDetail = "\n".join(invDetail)

        invoice =  ("No Invoice : "+str(text['no_invoice']) + "\n" +
                    invDetail + "\n"
                    "Total  : " + str(text['total_nominal']).rjust(10, ' ') + "\n" +
                    "Ongkir : " + str(text['ongkir']).rjust(10, ' ') + "\n" +
                    "*Grand Total* : \nRp " + str(text['gt']) + ",-\n"
                    + text['keterangan'])

        # print(invoice)
        for ch in invoice:
            if ch == "\n":
                # "\n"
                ActionChains(browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.BACKSPACE).perform()
            else:
                # print(ch)
                input_box.send_keys(ch)
        

        # input_box.send_keys(text)
        # input_box.send_keys(Keys.SPACE)
        input_box.send_keys(Keys.ENTER)
        print("Message sent successfuly")
    except NoSuchElementException:
        print("Failed to send message")
        return

def send_message(target):
    global message, wait, browser
    try:
        x_arg = '//span[contains(@title,' + target + ')]'
        ct = 0
        while ct != 10:
            try:
                group_title = wait.until(EC.presence_of_element_located((By.XPATH, x_arg)))
                group_title.click()
                break
            except:
                ct += 1
                time.sleep(3)
        input_box = browser.find_element_by_xpath('//*[@id="main"]/footer/div[1]/div[2]/div/div[2]')
        for ch in message:
            if ch == "\n":
                ActionChains(browser).key_down(Keys.SHIFT).key_down(Keys.ENTER).key_up(Keys.ENTER).key_up(Keys.SHIFT).key_up(Keys.BACKSPACE).perform()
            else:
                input_box.send_keys(ch)
        input_box.send_keys(Keys.ENTER)
        print("Message sent successfuly")
        time.sleep(1)
    except NoSuchElementException:
        return

class Customers(Model):
    id = CharField()
    no_hp = CharField()
    
    class Meta:
        database = db_connect

class Transactions(Model):
    id = CharField()
    no_invoice = CharField()
    total_nominal = CharField()
    customer_id = ForeignKeyField(Customers, backref='customer')
    
    class Meta:
        database = db_connect



class SendMessage(Resource):
    def post(self):
        # todo_id = int(max(TODOS.keys()).lstrip('todo')) + 1
        # todo_id = 'todo%i' % todo_id
        # TODOS[todo_id] = {'task': args['task']}
        # # return TODOS[todo_id], 201

        global Contact, message

        parser.add_argument('number')
        args = parser.parse_args()        
        number = args['number']
        
        parser.add_argument('textMessage')
        args = parser.parse_args()        
        textMessage = args['textMessage']
        
        message = textMessage
        # Contact = [number]


        # query = (Transactions
        #             .select(Transactions, Customers)
        #             .join(Customers)
        #             .where(Transactions.id == queryId))

        # result = []

        # message.append("Kode :"+str(query[0].no_invoice))
        # message.append("Total : Rp "+str(query[0].total_nominal))
        
        

        # print(number)
        # print(textMessage)
        
        numberSender(number)

        # for trx in query:
            # result.append({'kode': trx.no_invoice, 'total': trx.total_nominal})
        
        # return jsonify(result)
        # transaction = Transaction.select()
        # conn = db_connect.connect() # connect to database
        # query = conn.execute("select * from employees") # This line performs query and returns json result
        # return {'transactions': [i[1] for i in Transactions.select()]} # Fetches first column that is Employee ID

# class Tracks(Resource):
#     def get(self):
#         conn = db_connect.connect()
#         query = conn.execute("select trackid, name, composer, unitprice from tracks;")
#         result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
#         return jsonify(result)

# class Employees_Name(Resource):
#     def get(self, employee_id):
#         conn = db_connect.connect()
        # query = conn.execute("select * from employees where EmployeeId =%d "  %int(employee_id))
#         result = {'data': [dict(zip(tuple (query.keys()) ,i)) for i in query.cursor]}
#         return jsonify(result)
        

api.add_resource(SendMessage, '/send') # Route_1
# api.add_resource(Tracks, '/tracks') # Route_2
# api.add_resource(Employees_Name, '/employees/<employee_id>') # Route_3


if __name__ == '__main__':
     whatsapp_login()
     app.run(port='5002')
        