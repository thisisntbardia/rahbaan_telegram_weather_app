import telebot
import schedule
import time
import datetime
import threading
import requests
from telebot import types
from confing import API_TOKEN  , api_key , base_url , phone_number , channel_id

# Initialize global variables
user_locations = {}  # Dictionary to store user locations and prefared language
user_language = {}   # Dictionary to store user prefared language
schedule_var = 1  # Variable to control the scheduling of weather updates
language = 1  # Variable to control the language of the bot's responses (1 for Farsi, 0 for English)
Repetition = 1  # Variable to control whether daily weather updates are sent

# Initialize the bot
bot = telebot.TeleBot(API_TOKEN)

# Function to return about us text based on the language
def about_us(user_preferred):    #about us text
    if(user_preferred):
        return "این ربات در جهت گزارش لحظه ای اب و هوای منطقه شما ساخته شده است.\nکلیه حقوق این سامانه متعلق به شرکت X می باشد."
    else:
        return "This robot is designed to report the current weather of your area.\nAll rights of this system are reserved by X Company. "

# Function checks if user is a member of the channel
def check_user_membership(user_id: int, channel_id: str):
    try:
        chat_member = bot.get_chat_member(channel_id, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True     # User is a member of the channel
        else:
            return False    # User is not a member of the channel
    except Exception as e:
        return f'Error: {e}'    # If an error occurs

# Function to return schedule text based on the language and repeation
def daily_Repetition_text():                            #schedule text
    text = ""
    if language and Repetition :
        text = "ارسال روزانه فعال شد"   # Farsi message for enabled updates
    elif language and  Repetition == 0:
        text = "ارسال روزانه غیر فعال شد"  # Farsi message for disabled updates
    elif language == 0 and  Repetition == 0:
        text = "schedule turned off"  # English message for disabled updates
    elif language == 0 and  Repetition == 1:
        text = "schedule turned on"  # English message for enabled updates
    return text

# Function to return settings option keyboard based on the language
def settings_keyboard_language(key_language):          #settings option keyboard
    if(key_language):
        settings_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        language_change =types.KeyboardButton("زبان/language")  # Button to change language
        daily_schedule =types.KeyboardButton("ارسال روزانه")    # Button to enable/disable daily updates
        settings_keyboard.add(language_change , daily_schedule)
        return settings_keyboard
    else:
        settings_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        language_change =types.KeyboardButton("زبان/language")  # Button to change language
        daily_schedule =types.KeyboardButton("daily schedule")  # Button to enable/disable daily updates
        settings_keyboard.add(language_change , daily_schedule)
        return settings_keyboard

# Function to return main keyboard based on the language
def keyboard_language(key_language):                   #main keyboard
    #  farsi == 1  ,  english == 0
    if(key_language):
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button_weather = types.KeyboardButton("اب و هوا") # Button to request weather
        contact_us = types.KeyboardButton("تماس با ما")  # Button to contact us
        about_us = types.KeyboardButton("درباره ما")  # Button to learn about us
        settings = types.KeyboardButton("تنظیمات")  # Button to access settings
        button_location = types.KeyboardButton('ارسال موقعیت مکانی', request_location=True)  # Button to send location
        keyboard.add(button_weather , button_location , about_us , contact_us , settings)
        return keyboard
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button_weather = types.KeyboardButton("weather")  # Button to request weather
        contact_us = types.KeyboardButton("contact us")  # Button to contact us
        about_us = types.KeyboardButton("about us")  # Button to learn about us
        settings = types.KeyboardButton("settings")  # Button to access settings
        button_location = types.KeyboardButton('send location', request_location=True)  # Button to send location
        keyboard.add(button_weather , button_location , about_us , contact_us , settings)
        return keyboard

# Function to check schedule_var and call daily_weather_update if it's true
def check_schedule():  # Function to check if daily updates are enabled and call the update function if they are
    if schedule_var:
        daily_weather_update()

# Function to send daily weather report to all users
def daily_weather_update():                            #send daily wather report
    for user_id, location in user_locations.items():
        if user_id not in user_locations:
            user_locations[user_id] = None  # Initialize user location to None
            return
        if user_id not in user_language:
           user_language[user_id] = 1
        result = check_user_membership(user_id, channel_id)
        if result == True:
            if location:
                latitude, longitude = location
                params = {"lat": latitude, "lon": longitude, "appid": api_key, "units": "metric"}
                response = requests.get(base_url, params=params)
                data = response.json()

                if "main" in data:
                    weather_info = format_weather_data(data , user_language[user_id])
                    bot.send_message(user_id, weather_info)
                else:
                    bot.send_message(user_id, "City Not Found")
        elif result == False:
           bot.send_message(user_id , "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @rahbaan_ir")
        else :
            bot.send_message(user_id , result)
# Function to run schedule
def reo():                                             #running schedule
    while True:
        schedule.run_pending()
        time.sleep(1)

#start keyboard
start_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
# Create the KeyboardButton
start_button = types.KeyboardButton("/start")
# Add the button to the keyboard
start_keyboard.add(start_button)

# Function to format weather data into a readable string
def format_weather_data(weather_data , user_preferred):
    if user_preferred:
        formatted_data = f"""
    سلام! این به‌روزرسانی وضعیت آب و هوا برای {weather_data['name']}, {weather_data['sys']['country']} است:

    مختصات:
        عرض جغرافیایی: {weather_data['coord']['lat']}
        طول جغرافیایی: {weather_data['coord']['lon']}

    دما:
        فعلی: {weather_data['main']['temp']} سانتی گراد
        احساس می‌شود: {weather_data['main']['feels_like']} سانتی گراد
        حداقل: {weather_data['main']['temp_min']} سانتی گراد
        حداکثر: {weather_data['main']['temp_max']} سانتی گراد

    فشار:
        سطح دریا: {weather_data['main']['sea_level']} هکتوپاسکال
        سطح زمین: {weather_data['main']['grnd_level']} هکتوپاسکال

    رطوبت:
        مقدار: {weather_data['main']['humidity']}%

    دید:
        مقدار: {weather_data['visibility']} متر

    باد:
        سرعت: {weather_data['wind']['speed']} متر بر ثانیه
        جهت: {weather_data['wind']['deg']}°

    ابرها:
        مقدار: {weather_data['clouds']['all']}%

    زمان طلوع و غروب خورشید:
        طلوع خورشید: {datetime.datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M:%S')}
        غروب خورشید: {datetime.datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M:%S')}

    منطقه زمانی:
        مقدار: GMT{weather_data['timezone']//3600}:{(weather_data['timezone']%3600)//60}

    زمان داده:
        مقدار: {datetime.datetime.fromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S')}

موفق و سلامت باشید!
    """
    else:
        formatted_data = f"""
    Hello! Here is your weather update for {weather_data['name']}, {weather_data['sys']['country']}:

    Coordinates:
        Latitude: {weather_data['coord']['lat']}
        Longitude: {weather_data['coord']['lon']}

The sky looks clear today with {weather_data['weather'][0]['description']}.

    Temperature:
        Current: {weather_data['main']['temp']} C
        Feels Like: {weather_data['main']['feels_like']} C
        Minimum: {weather_data['main']['temp_min']} C
        Maximum: {weather_data['main']['temp_max']} C

    Pressure:
        Sea Level: {weather_data['main']['sea_level']} hPa
        Ground Level: {weather_data['main']['grnd_level']} hPa

    Humidity:
        Value: {weather_data['main']['humidity']}%

    Visibility:
        Value: {weather_data['visibility']} meters

    Wind:
        Speed: {weather_data['wind']['speed']} m/s
        Direction: {weather_data['wind']['deg']}°

    Clouds:
        Value: {weather_data['clouds']['all']}%

    Sunrise and Sunset times:
        Sunrise at: {datetime.datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M:%S')}
        Sunset at: {datetime.datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M:%S')}

    Timezone:
        Value: GMT{weather_data['timezone']//3600}:{(weather_data['timezone']%3600)//60}

    Data Time:
        Value: {datetime.datetime.fromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S')}

Stay safe and have a great day!
    """
    return formatted_data

# Messages to be sent to the user
location_channel_msg = "Here, you can get today's weather.\nTo provide you with the most accurate information,"
send_location = "please send your location.\n لطفا موقعیت مکانی خود را ارسال کنید"

# Handler for the /start command
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id  # Get the user ID
    result = check_user_membership(user_id, channel_id)
    if result == True:
        user_locations[user_id] = None  # Initialize user location to None
        user_language[user_id] = 1
        # Check the current language and send the appropriate welcome message
        if(language):
            bot.send_message(user_id, f"به برنامه ما خوش امدی {message.from_user.first_name}!\nما به صورت روزانه وضعیت اب و هوایی منطقه شما را ارسال میکنیم" , reply_markup=keyboard_language(user_language[user_id]))
        else:
            bot.send_message(user_id, f"Welcome to our Weather App, {message.from_user.first_name}!\n{location_channel_msg}{send_location}" , reply_markup = keyboard_language(user_language[user_id]))
    elif result == False:
        bot.send_message(user_id , "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @rahbaan_ir")
    else :
        bot.send_message(user_id , result)

# Handler for location messages
@bot.message_handler(content_types=["location"])
def handle_location(message):
    user_id = message.from_user.id  # Get the user ID
    if user_id not in user_locations:
        user_locations[user_id] = None  # Initialize user location to None

    if user_id not in user_language:
        user_language[user_id] = 1
    result = check_user_membership(user_id, channel_id)
    if result == True:
        latitude = message.location.latitude    # Get the latitude from the location
        longitude = message.location.longitude  # Get the longitude from the location
        user_locations[user_id] = (latitude, longitude)  # Store the user's location
        # Check the current language and send the appropriate message
        if(user_language[user_id]):
            bot.reply_to(message, "جهت دیدن وضعیت اب و هوایی روی گزینه 'اب و هوا' کلیک کنید")
        else:
            bot.reply_to(message, "Please type 'weather' for today's details.")
    elif result == False:
        bot.send_message(user_id , "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @rahbaan_ir")
    else :
        bot.send_message(user_id , result)

# Handler for weather forecast requests
@bot.message_handler(func=lambda message: message.text.lower() in ["weather", "اب و هوا"])
def handle_weather_forecast(message):
    user_id = message.from_user.id  # Get the user ID
    result = check_user_membership(user_id, channel_id)
    if result == True:
        # If the user's location is not provided, ask for it
        if user_id not in user_locations or user_locations[user_id] is None:
            bot.reply_to(message, send_location)  # Ask for location if not provided
            return
        latitude, longitude = user_locations[user_id]    # Get the user's location
        params = {"lat": latitude, "lon": longitude, "appid": api_key, "units": "metric"}  # Parameters for the weather API

        response = requests.get(base_url, params=params)    # Send a request to the weather API
        data = response.json()  # Get the response data

        # If the response data contains weather information, format it and send it to the user
        if "main" in data:
            weather_info = format_weather_data(data , user_language[user_id])
            bot.reply_to(message, weather_info)  # Send formatted weather data
        else:
            bot.reply_to(message, "City Not Found")  # Handle case where city is not found
    elif result == False:
        bot.send_message(user_id , "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @rahbaan_ir")
    else :
        bot.send_message(user_id , result)

# Handler for about_us requests
@bot.message_handler(func=lambda message: message.text.lower() in ["about us" , "درباره ما"])
def handel_about_us(message):
    user_id = message.from_user.id  # Get the user ID
    result = check_user_membership(user_id, channel_id)
    if result == True:
        # Get the about us information based on the current language
        info = about_us(user_language[user_id])
        # Reply to the user with the about us information
        bot.reply_to(message , info)
    elif result == False:
        bot.send_message(user_id , "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @rahbaan_ir")
    else :
        bot.send_message(user_id , result)

# Handler for 'contact us' requests
@bot.message_handler(func=lambda message: message.text.lower() in ["contact us" , "تماس با ما"])
def handel_contact_us(message):
    user_id = message.from_user.id  # Get the user ID
    if user_id not in user_locations:
        user_locations[user_id] = None  # Initialize user location to None

    if user_id not in user_language:
        user_language[user_id] = 1
    # Create a clickable phone number link
    tap = f'<a href="tel:{phone_number}">{phone_number}</a>'
    # Check the current language and send the appropriate message
    if(user_language[user_id]):
        bot.reply_to(message, f'راه های ارتباط با ما:\nشماره تماس:  {tap}\nایمیل:   info@partotaprayan.ir', parse_mode='HTML')
    else:
        bot.reply_to(message, f'Get in Touch with Us {message.from_user.first_name}, We’d love to hear from you!\nTel: {tap}\nEmail: info@partotaprayan.ir', parse_mode='HTML')

# Handler for 'settings' requests
@bot.message_handler(func=lambda message: message.text.lower() in ["settings" , "تنظیمات"])
def shandel_settings(message):
    user_id = message.from_user.id  # Get the user ID
    result = check_user_membership(user_id, channel_id)
    if result == True:
        # Check the current language and send the appropriate settings message
        if user_language[user_id]:
            bot.send_message(user_id , "تنظیمات\nزبان:           تغییر زبان برنامه\nارسال روزانه:    (on/off)" , reply_markup = settings_keyboard_language(user_language[user_id]) )
        else:
            bot.send_message(user_id , "Settings\nLanguage: Switch the program language\nDaily Send: Turn On/Off", reply_markup= settings_keyboard_language(user_language[user_id]))
    elif result == False:
        bot.send_message(user_id , "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @rahbaan_ir")
    else :
        bot.send_message(user_id , result)

# Handler for language change requests
@bot.message_handler(func=lambda message: message.text.lower() in ["زبان/language"])
def handel_language(message):
    user_id = message.from_user.id  # Get the user ID
    result = check_user_membership(user_id, channel_id)
    if result == True:
        global language
        # Check the current language and switch it
        if user_language[user_id]:
            user_language[user_id] = 0
            bot.send_message(user_id , "language changed successfully" , reply_markup = keyboard_language(user_language[user_id]))
        else:
            user_language[user_id] = 1
            bot.send_message(user_id , "زبان با موفقیت تغییر کرد", reply_markup = keyboard_language(user_language[user_id]))
    elif result == False:
        bot.send_message(user_id , "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @rahbaan_ir")
    else :
        bot.send_message(user_id , result)

# Handler for daily schedule on/off
@bot.message_handler(func=lambda message: message.text.lower() in ["ارسال روزانه" , "daily schedule"])
def handel_schedule(message):
    user_id = message.from_user.id  # Get the user ID
    if user_id not in user_locations:
        user_locations[user_id] = None
        bot.reply_to(message, send_location)  # Ask for location if not provided
        return
    if user_id not in user_language:
        user_language[user_id] = 1
    global Repetition       # Access the global variable repeation
    result = check_user_membership(user_id, channel_id)
    if result == True:
        # Check the current state of repeation
        if Repetition == 1:
            Repetition = 0      # If repeation is 1, set it to 0
            # Send a message to the user with the daily_repeation_text and the keyboard language
            bot.send_message(user_id , f"{daily_Repetition_text()}" , reply_markup = keyboard_language(user_language[user_id]))
        else:
            Repetition = 1      # If repeation is not 1, set it to 1
            # Send a message to the user with the daily_repeation_text and the keyboard language
            bot.send_message(user_id , f"{daily_Repetition_text()}" , reply_markup = keyboard_language(user_language[user_id]))
    elif result == False:
        bot.send_message(user_id , "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @rahbaan_ir")
    else :
        bot.send_message(user_id , result)

# Schedule the check_schedule function to run every day at 08:00 AM
schedule.every().day.at("08:00").do(check_schedule)

# Start a new thread that runs the reo function
threading.Thread(target=reo).start()

# Start polling for updates from the bot
bot.infinity_polling()