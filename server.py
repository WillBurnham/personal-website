from flask import Flask, render_template, redirect, request
import mysql.connector
import pyowm
from apscheduler.schedulers.background import BackgroundScheduler
import time
from city import City
import smtplib
from bs4 import BeautifulSoup
import xlsxwriter
import pandas as pd
import requests
import os


#using these variables to control the 
first_loop = True
i = 0


#importing the Open Weather Map API key
owm = pyowm.OWM('ecb7040454382ee36fdd354262f71db1')


#SMTP server credentials and target addresses
send_email = "wb.weather.app@gmail.com"
rec_email = ["burnham.will2020@gmail.com", "nmgiacomello@gmail.com"]
password = "2FC018z69420!"


#creating cities to be monitored 
dal = City('Dallas')
hou = City('Houston')
aus = City('Austin')
city_list = [dal, hou, aus]


#initializing current weather status
current_austin_weather = ""
current_dallas_weather = ""
current_houston_weather = ""


#getting weather status to determine the image we use 
if aus.find_bad_weather() == True:
    current_austin_weather = "rain"
else:
    current_austin_weather = "cloud"
    
if dal.find_bad_weather() == True:
    current_dallas_weather = "rain"
else:
    current_dallas_weather = "cloud"
    
if hou.find_bad_weather() == True:
    current_houston_weather = "rain"
else:
    current_houston_weather = "cloud"


#routes to the image
aus_img = "/static/images/" + current_austin_weather + ".png"
dal_img = "/static/images/" + current_dallas_weather + ".png"
hou_img = "/static/images/" + current_houston_weather + ".png"


#send email when find_bad_weather = true
def send():
    
    global current_austin_weather
    global current_dallas_weather
    global current_houston_weather
    global aus_img
    global dal_img
    global hou_img
    
    #starting smtp server
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(send_email, password)
    
    #constructing email body
    message = "It's going to rain tomorrow in "
    cities = []
    
    #resetting values in each weather column
    current_austin_weather = ""
    current_dallas_weather = ""
    current_houston_weather = ""
    for city in city_list:
        if city.find_bad_weather() == True:
            
            #detailing weather at each city so I can apply the appropriate weather icon
            if (city.name == 'Austin'):
                current_austin_weather = "rain"
                print('Found bad weather in ' + city.name)
            if (city.name == 'Dallas'):
                current_dallas_weather = "rain"
                print('Found bad weather in ' + city.name)
            if (city.name == 'Houston'):
                current_houston_weather = "rain"
                print('Found bad weather in ' + city.name)
            cities.append(city.name)
        else:
            if (city.name == 'Austin'):
                current_austin_weather = "cloud"
                print('Found good weather in ' + city.name)
            if (city.name == 'Dallas'):
                current_dallas_weather = "cloud"
                print('Found good weather in ' + city.name)
            if (city.name == 'Houston'):
                current_houston_weather = "cloud"
                print('Found good weather in ' + city.name)

    #finishing email body
    message += str(cities)
    message += ". Give Jackson his medicine if you will be either of these places tomorrow."
    
    
    #reloading image names so they will update dynamically
    aus_img = "/static/images/" + current_austin_weather + ".png"
    dal_img = "/static/images/" + current_dallas_weather + ".png"
    hou_img = "/static/images/" + current_houston_weather + ".png"
    
    #sending the email
    server.sendmail(send_email, rec_email, message)


#setting up database connection
def connectToDB():
    con = mysql.connector.connect(
    user = "ardit700_student",
    password = "ardit700_student",
    host = "108.167.140.122",
    database = "ardit700_pm1database"
    )
    return con


#scraping page data from website
def get_content(state, city):
    url = "https://www.trulia.com/" + state + "/" + city
    req = requests.get(url, headers={'User-agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0'})
    content = req.content
    soup = BeautifulSoup(content, 'html.parser')
    all_property_data = soup.find_all("div", {"class":"Box-sc-8ox7qa-0 jIGxjA"})
    return all_property_data
    

#creating excel workbook
def start_workbook():
    return xlsxwriter.Workbook('C:/Users/burnh/Desktop/Python/Personal Website/Excel/real_estate.xlsx')


#creating a worksheet from the workbook
def create_worksheet(workbook):
    
    worksheet = workbook.add_worksheet()
    
    worksheet.write('A1', 'Price')
    worksheet.write('B1', 'Beds')
    worksheet.write('C1', 'Bath')
    worksheet.write('D1', 'Address')
    worksheet.write('E1', 'Region')
    
    return worksheet


#grabbing each individual element from the webpage for each property
def fill_data(all_property_data, worksheet):
    for i in range (0, len(all_property_data)):
        property_price = all_property_data[i].find_all("div", {"data-testid":"property-price"})
        property_beds = all_property_data[i].find_all("div", {"data-testid": "property-beds"})
        property_baths = all_property_data[i].find_all("div", {"data-testid": "property-baths"})
        property_address = all_property_data[i].find_all("div", {"data-testid":"property-street"})
        property_region = all_property_data[i].find_all("div", {"data-testid": "property-region"})
        if property_price:
            property_price = property_price[0].text
        else:
            property_price = "$0"
        if property_beds:
            property_beds = property_beds[0].text
        else:
            property_beds = "0bd"
        if property_baths:
            property_baths = property_baths[0].text
        else:
            property_baths = "0ba"
            
        if property_address:
            property_address = property_address[0].text
        else:
            property_address = ""
        if property_region:
            property_region = property_region[0].text
        else:
            property_region = ""
        
        #using this work around so that we can begin writing data to all rows underneath row 1 in the workbook
        row_a = ["A", str(i+2)]
        row_b = ["B", str(i+2)]
        row_c = ["C", str(i+2)]
        row_d = ["D", str(i+2)]
        row_e = ["E", str(i+2)]
        
        #writing the info to the worksheet
        worksheet.write(''.join(row_a), property_price)
        worksheet.write(''.join(row_b), property_beds)
        worksheet.write(''.join(row_c), property_baths)
        worksheet.write(''.join(row_d), property_address)
        worksheet.write(''.join(row_e), property_region)
    

#starting background task scheduler to pull weather data behind the scenes
sched = BackgroundScheduler(daemon=True)
sched.add_job(send,'cron',minute = '30', hour = '20')
sched.start()


#creating application object
app = Flask(__name__)


#setting up home route
@app.route('/')
def home():
    return render_template("index.html")


#route to projects page
@app.route('/projects/')
def projects():
    return render_template("projects.html", austin_image = aus_img, dallas_image = dal_img, houston_image = hou_img)


#route to resume
@app.route('/resume/') 
def resume():
    return redirect("/static/Will Burnham Official Resume PDF.pdf") 


#route to spreadsheet
@app.route('/spreadsheet/', methods=['POST'])
def spreadsheet():
    global first_loop
    global i
    
    
    #kept having weird error where the html page data would update but it would always render the prev. version
    #got around this by creating a new html page every time the form submits. 
    
    #if its not the first iteration of the loop, remove the last iterations html page
    if not first_loop:
        os.remove("C:/Users/burnh/Desktop/Python/Personal Website/templates/spreadsheet" + str(i-1) +".html")
        
    #else search through the directory and ensure there are no spreadsheets to avoid buildup
    else:
        dir = "C:/Users/burnh/Desktop/Python/Personal Website/templates/"
        for files in os.walk(os.path.abspath(dir)):
            for file in files[2]:
                if 'spreadsheet' in file:
                    os.remove("C:/Users/burnh/Desktop/Python/Personal Website/templates/" + file)
                print(file)
        first_loop = False
    
    city = request.form['city']
    state = request.form['category']
    
    workbook = start_workbook()
    worksheet = create_worksheet(workbook)
    content = get_content(state, city)
    fill_data(content, worksheet)
    workbook.close()
    
    #reading the excel doc with panda's and turning it into an html page for in browser readability
    df = pd.read_excel("C:/Users/burnh/Desktop/Python/Personal Website/Excel/real_estate.xlsx")
    df.to_html("C:/Users/burnh/Desktop/Python/Personal Website/templates/spreadsheet" + str(i) + ".html")
    
    #rendering the template before we increment
    template = render_template("spreadsheet" + str(i) + ".html")
    
    i+=1
    
    return template


#route for data submitted through form
@app.route('/projects/', methods=['POST'])
def handle_data():    
    
    #getting word from form
    word = request.form['message']
    word = word.lower()
    
    #output when no definitions are found
    no_search_results = "Please enter a valid word."
    
    #connection to db
    con = connectToDB()
    cursor = con.cursor()
    
    #input validation
    for char in word:
        if (char.isalpha() == False):
            return render_template("projects.html", value = no_search_results)
            
    #constructing query and fetching results
    query = cursor.execute("SELECT Definition FROM Dictionary WHERE Expression = '%s'" % word)
    results = cursor.fetchall()
    
    #if there are results pass up to 3 definitions then close connection
    if results:
        arr = []
        for result in results:
            arr.append(result[0])
        if len(arr) >= 3:
            con.close()
            return render_template("projects.html", value = arr[0], value2 = arr[1], value3=arr[2], austin_image = aus_img, dallas_image = dal_img, houston_image = hou_img)
        if len(arr) == 2:
            con.close()
            return render_template("projects.html", value = arr[0], value2 = arr[1], austin_image = aus_img, dallas_image = dal_img, houston_image = hou_img)
        if len(arr) == 1:
            con.close()
            return render_template("projects.html", value = arr[0], austin_image = aus_img, dallas_image = dal_img, houston_image = hou_img)
           
    else:
        con.close()
        return render_template("projects.html", value = no_search_results, austin_image = aus_img, dallas_image = dal_img, houston_image = hou_img)

          
if __name__ == "__main__":
    app.run(debug=False)