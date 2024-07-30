import telebot
import schedule
import time
import datetime
import threading
import requests
from telebot import types
from confing import API_TOKEN  , api_key , base_url , phone_number
user_locations = {}  # Dictionary to store user locations
schedule_var = 1
language = 1
repeation = 1

bot = telebot.TeleBot(API_TOKEN)
def about_us(key_language):                            #about us text
    if(key_language):
        return "این ربات در جهت گزارش لحظه ای اب و هوای منطقه شما ساخته شده است"
    else:
        return "This robot is designed to report the current weather of your area "
def daily_repeation_text():                            #schedule text
    text = ""
    if language and repeation :
        text = "ارسال روزانه فعال شد"
    elif language and  repeation == 0:
        text = "ارسال روزانه غیر فعال شد"
    elif language == 0 and  repeation == 0:
        text = "schedule turned off"
    elif language == 0 and  repeation == 1:
        text = "schedule turned on"
    return text
def settings_keyboard_language(key_language):          #settings option keyboard
    if(key_language):
        settings_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        language_change =types.KeyboardButton("زبان/language")
        daily_schedule =types.KeyboardButton("ارسال روزانه") 
        settings_keyboard.add(language_change , daily_schedule)
        return settings_keyboard
    else:
        settings_keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        language_change =types.KeyboardButton("زبان/language")
        daily_schedule =types.KeyboardButton("daily schedule") 
        settings_keyboard.add(language_change , daily_schedule)
        return settings_keyboard  
def keyboard_language(key_language):                   #main keyboard
    #  farsi == 1  ,  english == 0
    if(key_language):
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button_weather = types.KeyboardButton("اب و هوا")
        contact_us = types.KeyboardButton("تماس با ما")
        about_us = types.KeyboardButton("درباره ما")
        settings = types.KeyboardButton("تنظیمات")
        button_location = types.KeyboardButton('ارسال موقعیت مکانی', request_location=True)
        keyboard.add(button_weather , button_location , about_us , contact_us , settings)
        return keyboard
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button_weather = types.KeyboardButton("weather")
        contact_us = types.KeyboardButton("contact us")
        about_us = types.KeyboardButton("about us")
        settings = types.KeyboardButton("settings")
        button_location = types.KeyboardButton('send location', request_location=True)
        keyboard.add(button_weather , button_location , about_us , contact_us , settings)
        return keyboard
def check_schedule():                                  #checking schedule_var
    if schedule_var:
        daily_weather_update()
def daily_weather_update():                            #send daily wather report
    for user_id, location in user_locations.items():
        if location:
            latitude, longitude = location
            params = {"lat": latitude, "lon": longitude, "appid": api_key, "units": "metric"}
            response = requests.get(base_url, params=params)
            data = response.json()

            if "main" in data:
                weather_info = format_weather_data(data)
                bot.send_message(user_id, weather_info)
            else:
                bot.send_message(user_id, "City Not Found")
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

def format_weather_data(weather_data):
    if language:
        formatted_data = f"""
    سلام! این به‌روزرسانی وضعیت آب و هوا برای {weather_data['name']}, {weather_data['sys']['country']} است:

    مختصات: 
        عرض جغرافیایی: {weather_data['coord']['lat']}
        طول جغرافیایی: {weather_data['coord']['lon']}
    
    دما: 
        فعلی: {weather_data['main']['temp']} کلوین
        احساس می‌شود: {weather_data['main']['feels_like']} کلوین
        حداقل: {weather_data['main']['temp_min']} کلوین
        حداکثر: {weather_data['main']['temp_max']} کلوین

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
        طلوع خورشید: {datetime.datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')}
        غروب خورشید: {datetime.datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')}

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
        Current: {weather_data['main']['temp']} K
        Feels Like: {weather_data['main']['feels_like']} K
        Minimum: {weather_data['main']['temp_min']} K
        Maximum: {weather_data['main']['temp_max']} K

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
        Sunrise at: {datetime.datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%Y-%m-%d %H:%M:%S')}
        Sunset at: {datetime.datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%Y-%m-%d %H:%M:%S')}

    Timezone: 
        Value: GMT{weather_data['timezone']//3600}:{(weather_data['timezone']%3600)//60}

    Data Time: 
        Value: {datetime.datetime.fromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S')}

Stay safe and have a great day!
    """
    return formatted_data

location_channel_msg = "Here, you can get today's weather.\nTo provide you with the most accurate information,"
send_location = "please send your location."

# Handler for the /start command
@bot.message_handler(commands=["start"])
def start(message):
    user_id = message.from_user.id
    user_locations[user_id] = None  # Initialize user location to None
    if(language):
        bot.send_message(user_id, f"به برنامه ما خوش امدی {message.from_user.first_name}!\nما به صورت روزانه وضعیت اب و هوایی منطقه شما را ارسال میکنیم" , reply_markup=keyboard_language(language))
    else: 
        bot.send_message(user_id, f"Welcome to our Weather App, {message.from_user.first_name}!\n{location_channel_msg}{send_location}" , reply_markup = keyboard_language(language))
# Handler for location messages
@bot.message_handler(content_types=["location"])
def handle_location(message):
    user_id = message.from_user.id
    latitude = message.location.latitude
    longitude = message.location.longitude
    user_locations[user_id] = (latitude, longitude)  # Store the user's location
    if(language):
        bot.reply_to(message, "جهت دیدن وضعیت اب و هوایی روی گزینه 'اب و هوا' کلیک کنید")
    else:
        bot.reply_to(message, "Please type 'weather' for today's details.")
# Handler for weather forecast requests
@bot.message_handler(func=lambda message: message.text.lower() in ["weather", "اب و هوا"])
def handle_weather_forecast(message):
    user_id = message.from_user.id
    if user_id not in user_locations or user_locations[user_id] is None:
        bot.reply_to(message, send_location)  # Ask for location if not provided
        return
    latitude, longitude = user_locations[user_id]
    params = {"lat": latitude, "lon": longitude, "appid": api_key}

    response = requests.get(base_url, params=params)
    data = response.json()

    if "main" in data:
        weather_info = format_weather_data(data)
        bot.reply_to(message, weather_info)  # Send formatted weather data
    else:
        bot.reply_to(message, "City Not Found")  # Handle case where city is not found
# Handler for about_us requests
@bot.message_handler(func=lambda message: message.text.lower() in ["about us" , "درباره ما"])
def handel_about_us(message):
    info = about_us(keyboard_language(language))
    bot.reply_to(message , info)

@bot.message_handler(func=lambda message: message.text.lower() in ["contact us" , "تماس با ما"])
def handel_contact_us(message):
    tap = f'<a href="tel:{phone_number}">{phone_number}</a>'
    if(language):
        bot.reply_to(message, f'راه های ارتباط با ما:\nشماره تماس:  {tap}\nایمیل:   info@partotaprayan.ir', parse_mode='HTML')
    else:
        bot.reply_to(message, f'Get in Touch with Us {message.from_user.first_name}, We’d love to hear from you!\nTel: {tap}\nEmail: info@partotaprayan.ir', parse_mode='HTML')

@bot.message_handler(func=lambda message: message.text.lower() in ["settings" , "تنظیمات"])
def shandel_settings(message):
    user_id = message.from_user.id  # Get the user ID
    if language:
        bot.send_message(user_id , "تنظیمات\nزبان:           تغییر زبان برنامه\nارسال روزانه:    (on/off)" , reply_markup = settings_keyboard_language(language) )
    else:
        bot.send_message(user_id , "Settings\n'Language': Change the program language\n'Daily Send (on/off)'", reply_markup= settings_keyboard_language(language))

@bot.message_handler(func=lambda message: message.text.lower() in ["زبان/language"])
def handel_language(message):
    user_id = message.from_user.id  # Get the user ID
    global language
    if language:
        language = 0
        bot.send_message(user_id , "please click on start to reset the app" , reply_markup = keyboard_language(language))
    else:
        language = 1
        bot.send_message(user_id , "لطفا جهت راه اندازی مجدد بر روی گزینه statrt کلیک کنید" , reply_markup = keyboard_language(language))

@bot.message_handler(func=lambda message: message.text.lower() in ["ارسال روزانه" , "daily schedule"])
def handel_schedule(message):
    global repeation
    user_id = message.from_user.id
    if repeation == 1:
        repeation = 0
        bot.send_message(user_id , f"{daily_repeation_text()}" , reply_markup = keyboard_language(language))
    else:
        repeation = 1
        bot.send_message(user_id , f"{daily_repeation_text()}" , reply_markup = keyboard_language(language))

schedule.every().day.at("20:13").do(check_schedule) 
threading.Thread(target=reo).start()

bot.infinity_polling()