from flask import Flask, render_template, redirect, request
import mysql.connector
import pyowm
from apscheduler.schedulers.background import BackgroundScheduler
import time
from city import City
import smtplib
import requests

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

#importing the Open Weather Map API key
owm = pyowm.OWM('ecb7040454382ee36fdd354262f71db1')

send_email = "wb.weather.app@gmail.com"
rec_email = ["burnham.will2020@gmail.com", "nmgiacomello@gmail.com"]
pw = "2FC018z69420!"

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
    server.login(send_email, pw)
    
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
    return redirect("/static/Will Burnham Resume.pdf") 

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
            arr = []
            arr.append(no_search_results)
            return render_template("projects.html", my_list = arr, austin_image = aus_img, dallas_image = dal_img, houston_image = hou_img)
            
    #constructing query and fetching results
    query = cursor.execute("SELECT Definition FROM Dictionary WHERE Expression = '%s'" % word)
    results = cursor.fetchall()
    
    #if there are results pass up to 3 definitions then close connection
    if results:
        arr = []
        for result in results:
            arr.append(result[0])
        
        con.close()
        return render_template("projects.html", my_list = arr, austin_image = aus_img, dallas_image = dal_img, houston_image = hou_img)
       
           
    else:
        arr = []
        arr.append(no_search_results)
        con.close()
        return render_template("projects.html", my_list = arr, austin_image = aus_img, dallas_image = dal_img, houston_image = hou_img)

          
if __name__ == "__main__":
    app.run(debug=False)
