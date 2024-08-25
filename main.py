import telebot
import sqlite3
import schedule
import logging  
import time
import datetime
import threading
import requests
from telebot import types
from confing import API_TOKEN  , api_key , base_url , phone_number , channel_id
log_admin = 12345   #admin id

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')  # Added logging configuration
# Initialize the bot
bot = telebot.TeleBot(API_TOKEN)

def change_language(user_id , message , var , lang):
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        # Fetch the current preferred language
        cursor.execute('''
            SELECT preferred_language
            FROM user_information
            WHERE user_id = ?
        ''', (user_id,))
        preferred_language = cursor.fetchone()

        # Check if the user exists
        if preferred_language is None:
            set_user_info(user_id , message , var , lang)

        # Toggle the preferred language
        new_language = 1 if preferred_language[0] == 0 else 0
        cursor.execute('''
            UPDATE user_information
            SET preferred_language = ?
            WHERE user_id = ?
        ''', (new_language, user_id))
        conn.commit()

        # success message
        message = "Language changed successfully" if new_language == 0 else "زبان با موفقیت تغییر کرد"
        return message

    except sqlite3.Error as e:
        logging.error(f"An error occurred while toggling user language: {e}")  # Logging the error
        return "An error occurred while changing the language."

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def set_phone(user_id, message, var, lang):
    conn = None
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        cursor.execute('''
            SELECT 1
            FROM user_information
            WHERE user_id = ?        
        ''', (user_id,))
        result = cursor.fetchone()
        
        if result is None:
            set_user_info(user_id, message, var, lang)

        cursor.execute('''
            UPDATE user_information
            SET phone_number = ?
            WHERE user_id = ?
        ''', (message.contact.phone_number, user_id))

        # Commit the transaction
        conn.commit()

    except sqlite3.Error as e:
        logging.error(f"An error occurred while setting phone number: {e}")  # Logging the error
        bot.send_message(log_admin , f"An error occurred in set user info:\n {e}")

    finally:
        # Ensure the cursor and connection are closed
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def user_log(user_id , message , weather_data = None):
    conn = None
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        if weather_data is None:
            # Insert data into user_log
            cursor.execute('''
                INSERT INTO user_log
                (user_id, user_name ,chat_id, chat_type, message_id, message_content, date_time, first_name, last_name)
                VALUES
                (? , ? , ? , ? , ? , ?, ? , ? , ?)
            ''', (user_id, message.from_user.username ,message.chat.id, message.chat.type, message.message_id, message.text,  datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S') , message.from_user.first_name, message.from_user.last_name))
            conn.commit()
        else:
            # Insert data into user_log
            cursor.execute('''
                INSERT INTO user_log
                (user_id, user_name ,chat_id, chat_type, message_id, message_content, date_time, first_name, last_name , country , city)
                VALUES
                (? , ? , ? , ? , ? , ?, ? , ? , ? , ? , ?)
            ''', (user_id, message.from_user.username ,message.chat.id, message.chat.type, message.message_id, message.text,  datetime.datetime.fromtimestamp(message.date).strftime('%Y-%m-%d %H:%M:%S') , message.from_user.first_name, message.from_user.last_name , weather_data['sys']['country'], weather_data['name']))
            conn.commit()

    except sqlite3.Error as e:
        logging.error(f"An error occurred while setting data to log table: {e}")  # Logging the error
        bot.send_message(log_admin , f"An error occurred in set_phone:\n {e}")

    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()

def change_schedule_var(user_id , message , var , lang):
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        # Fetch the current schedule_var
        cursor.execute('''
            SELECT schedule_var
            FROM user_information
            WHERE user_id = ?
        ''', (user_id,))
        schedule_var = cursor.fetchone()
        schedule_var = schedule_var[0]

        # Check if the user exists
        if schedule_var is None:
            set_user_info(user_id , message , var , lang)
        
        # Toggle the schedule_var
        new_schedule_var = 1 if schedule_var == 0 else 0
        cursor.execute('''
            UPDATE user_information
            SET schedule_var = ?
            WHERE user_id = ?
        ''', (new_schedule_var, user_id))
        conn.commit()

        # Success message
        message = "Daily schedule enabled" if new_schedule_var == 1 else "Daily schedule disabled"
        return message

    except sqlite3.Error as e:
        logging.error(f"An error occurred while toggling schedule variable: {e}")  # Logging the error
        return "An error occurred while changing the schedule."
    
    finally:
        # Ensure the connection is closed
        if conn:
            conn.close()
#initializing user_information table for new user
def set_user_info(user_id, message , var , lang):
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        # Check if user exists in user_information
        cursor.execute('''
            SELECT 1
            FROM user_information
            WHERE user_id = ?        
        ''', (user_id,))
        result = cursor.fetchone()
        print(result)
        if result:
            # User exists, update location if message contains location data
            if hasattr(message, 'location') and message.location is not None:
                longitude = message.location.longitude
                latitude = message.location.latitude
                cursor.execute('''
                    UPDATE user_information
                    SET longitude = ?, latitude = ?
                    WHERE user_id = ?
                ''', (longitude, latitude, user_id))
                conn.commit()
        elif result is None:
            # User does not exist, insert data into user_information
            if hasattr(message, 'location') and message.location is not None:
                longitude = message.location.longitude
                latitude = message.location.latitude
            else:
                longitude = None
                latitude = None

            cursor.execute('''
                INSERT INTO user_information 
                (user_id, longitude, latitude, schedule_var, preferred_language)
                VALUES 
                (?, ?, ?, ?, ?)
            ''', (user_id, longitude, latitude, var , lang))
            conn.commit()
    except sqlite3.Error as e:
        logging.error(f"An error occurred in the set_user)info handler: {e}")  # Logging the error
        print(f"An error occurred: {e}")
        bot.send_message(log_admin , f"An error occurred in set user info:\n {e}")

    finally:
        if conn:
            conn.close()

#get weather
def get_weather(user_id):
    conn = None
    try:
        # Connect to the database
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        # Check if the location exists in the database
        cursor.execute('SELECT latitude, longitude FROM user_information WHERE user_id = ?', (user_id,))
        result_location_exist = cursor.fetchone()

        if result_location_exist is None:
            return False  # Location does not exist
        elif result_location_exist[0] is None or result_location_exist[1] is None:
            return False  #Location does not exist

        # Extract latitude and longitude
        latitude, longitude = result_location_exist

        # Parameters for the weather API
        params = {"lat": latitude, "lon": longitude, "appid": api_key, "units": "metric"}

        # Send a request to the weather API
        response = requests.get(base_url, params=params)
        data = response.json()  # Get the response data
        return data  # Return the result from the API

    except sqlite3.Error as e:
        logging.error(f"An error occurred in the def get_weather function: {e}")  # Logging the error
        bot.send_message(log_admin , f"An error occurred in get weather:\n {e}")
        print(f"An error occurred: {e}")
        return None

    finally:
        if conn:
            conn.close()    

# Check user language
def check_language(user_id, message):
    conn = None 
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        # Check if user exists in user_information
        cursor.execute('''
            SELECT 1
            FROM user_information
            WHERE user_id = ?        
        ''', (user_id,))
        result = cursor.fetchone()
        
        if result is None:
            set_user_info(user_id, message , 1 ,1)

        cursor.execute('''
            SELECT preferred_language
            FROM user_information
            WHERE user_id = ?
        ''', (user_id,))

        user_language = cursor.fetchone()[0]
        if user_language == None:
            cursor.execute('''
                update user_information
                set preferred_language = ?
                WHERE user_id = ?
            ''', (1 , user_id))
            conn.commit()
            user_language = 1
        return user_language  # Return the actual language

    except sqlite3.Error as e:
        logging.error(f"An error occurred in the check_language function: {e}")  # Logging the error
        print(f"An error occurred: {e}")
        bot.send_message(log_admin , f"An error occurred in check language:\n {e}")

        return None

    finally:
        if conn:
            conn.close()

#check user var
def check_var(user_id, message):
    conn = None
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()

        # Check if user exists in user_information
        cursor.execute('''
            SELECT 1
            FROM user_information
            WHERE user_id = ?        
        ''', (user_id,))
        result = cursor.fetchone()

        if result is None:
            set_user_info(user_id, message , 1 ,1)

        cursor.execute('''
            SELECT schedule_var
            FROM user_information
            WHERE user_id = ?
        ''', (user_id,))

        schedule_var = cursor.fetchone()
        return schedule_var[0]

    except sqlite3.Error as e:
        logging.error(f"An error occurred in the schedule_var checking function: {e}")  # Logging the error
        print(f"An error occurred: {e}")
        bot.send_message(log_admin , f"An error occurred in schedule_var:\n {e}")

        return None

    finally:
        if conn:
            conn.close()

# Function to return about us text based on the language
def about_us(user_preferred):    # About us text
    if user_preferred:
        return "🤖 این ربات برای گزارش لحظه‌ای آب و هوای منطقه شما ساخته شده است. 🌦️\nکلیه حقوق این سامانه متعلق به شرکت x می‌باشد. 🏢"
    else:
        return "🤖 This robot is designed to report the current weather of your area. 🌦️\nAll rights of this system are reserved by x Company. 🏢"

# Function checks if user is a member of the channel
def check_user_membership(user_id: int, channel_id: str):
    try:
        chat_member = bot.get_chat_member(channel_id, user_id)
        if chat_member.status in ['member', 'administrator', 'creator']:
            return True     # User is a member of the channel
        else:
            return False    # User is not a member of the channel
    except Exception as e:
        bot.send_message(log_admin , f"An error occurred in check membership:\n {e}")
        return f'Error: {e}'    # If an error occurs

# Function to return schedule text based on the language and repeation
def daily_Repetition_text(language , repetition_status):                            #schedule text
    text = ""
    if language and repetition_status :
        text = "ارسال روزانه فعال شد"   # Farsi message for enabled updates
    elif language and  repetition_status == 0:
        text = "ارسال روزانه غیر فعال شد"  # Farsi message for disabled updates
    elif language == 0 and  repetition_status == 0:
        text = "schedule turned off"  # English message for disabled updates
    elif language == 0 and  repetition_status == 1:
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
    #  farsi is 1  ,  english is 0
    if(key_language):
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button_weather = types.KeyboardButton("آب و هوا") # Button to request weather
        contact_us = types.KeyboardButton("تماس با ما" , request_contact=True)  # Button to contact us
        about_us = types.KeyboardButton("درباره ما")  # Button to learn about us
        settings = types.KeyboardButton("تنظیمات")  # Button to access settings
        button_location = types.KeyboardButton('ارسال موقعیت مکانی', request_location=True)  # Button to send location
        keyboard.add(button_weather , button_location , about_us , contact_us , settings)
        return keyboard
    else:
        keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        button_weather = types.KeyboardButton("weather")  # Button to request weather
        contact_us = types.KeyboardButton("contact us",request_contact=True)  # Button to contact us
        about_us = types.KeyboardButton("about us")  # Button to learn about us
        settings = types.KeyboardButton("settings")  # Button to access settings
        button_location = types.KeyboardButton('send location', request_location=True)  # Button to send location
        keyboard.add(button_weather , button_location , about_us , contact_us , settings)
        return keyboard

# Function to check schedule_var and call daily_weather_update if it's true
def check_schedule():
    conn = None
    try:
        conn = sqlite3.connect('user_data.db')
        cursor = conn.cursor()
        cursor.execute('''
            SELECT user_id, longitude, latitude, schedule_var, preferred_language
            FROM user_information
        ''')
        rows = cursor.fetchall()
        for row in rows:
            user_id, longitude, latitude, schedule_var, preferred_language = row
            if schedule_var == 1:
                location = (latitude , longitude)
                daily_weather_update(user_id, location, preferred_language)
    except sqlite3.Error as e:
        logging.error(f"An error occurred while checking schedule: {e}")  # Logging the error
        bot.send_message(log_admin , f"An error occurred while checking schedule: {e}")
    finally:
        if conn:
            conn.close()

def daily_weather_update(user_id, location, preferred_language):
    try:
        result = check_user_membership(user_id, channel_id)
        if result is True:
            if location[0] is not None and location[1] is not None:
                latitude, longitude = location
                params = {"lat": latitude, "lon": longitude, "appid": api_key, "units": "metric"}
                response = requests.get(base_url, params=params)
                data = response.json()
                if "main" in data:
                    weather_info = format_weather_data(data, preferred_language)
                    bot.send_message(user_id, weather_info)
                else:
                    bot.send_message(user_id, "City Not Found")
            else:
                bot.send_message(user_id, "Location data is missing or invalid please send your location or you can turn off daily schedule.")
        elif result is False:
            bot.send_message(user_id, "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @x")
        else:
            bot.send_message(user_id, result)
    except Exception as e:
            logging.error(f"An error occurred in the daily weather update: {e}")  # Logging the error
            bot.send_message(log_admin , f"An error occurred in the daily weather update: {e}")
            
# Function to run schedule
def reo():                                             #running schedule
    try:    
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
        logging.error(f"An error occurred in the reo: {e}")  # Logging the error
        bot.send_message(log_admin , f"An error occurred in the reo: {e}")

#start keyboard
start_keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
# Create the KeyboardButton
start_button = types.KeyboardButton("/start")
# Add the button to the keyboard
start_keyboard.add(start_button)

# Function to format weather data into a readable string
def format_weather_data(weather_data, user_preferred):
    if user_preferred:
        formatted_data = f"""
    🌤️ سلام! این به‌روزرسانی وضعیت آب و هوا برای {weather_data['name']}, {weather_data['sys']['country']} است:

    ────────────────
    📍 مختصات:
         عرض جغرافیایی: {weather_data['coord']['lat']}
         طول جغرافیایی: {weather_data['coord']['lon']}
    ────────────────
    🌡️ دما:
         فعلی: {weather_data['main']['temp']} سانتی گراد
         احساس می‌شود: {weather_data['main']['feels_like']} سانتی گراد
         حداقل: {weather_data['main']['temp_min']} سانتی گراد
         حداکثر: {weather_data['main']['temp_max']} سانتی گراد
    ────────────────
    🌬️ فشار:
        🌊 سطح دریا: {weather_data['main']['sea_level']} هکتوپاسکال
        🌍 سطح زمین: {weather_data['main']['grnd_level']} هکتوپاسکال
    ────────────────
    💧 رطوبت:
         مقدار: {weather_data['main']['humidity']}%
    ────────────────
    👁️ دید:
         مقدار: {weather_data['visibility']} متر
    ────────────────
    🌬️ باد:
        🌬️ سرعت: {weather_data['wind']['speed']} متر بر ثانیه
        🧭 جهت: {weather_data['wind']['deg']}°
    ────────────────
    ☁️ ابرها:
         مقدار: {weather_data['clouds']['all']}%
    ────────────────
    🌅 زمان طلوع و غروب خورشید:
        🌄 طلوع خورشید: {datetime.datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M:%S')}
        🌆 غروب خورشید: {datetime.datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M:%S')}
    ────────────────
    ⏰ منطقه زمانی:
         مقدار: GMT{weather_data['timezone']//3600}:{(weather_data['timezone']%3600)//60}
    ────────────────
    🕒 زمان داده:
         مقدار: {datetime.datetime.fromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S')}
    ────────────────

موفق و سلامت باشید! 🌟
    """
    else:
        formatted_data = f"""
    🌤️ Hello! Here is your weather update for {weather_data['name']}, {weather_data['sys']['country']}:

    ────────────────
    📍 Coordinates:
         Latitude: {weather_data['coord']['lat']}
         Longitude: {weather_data['coord']['lon']}
    ────────────────
    🌤️ The sky looks clear today with {weather_data['weather'][0]['description']}.
    ────────────────
    🌡️ Temperature:
         Current: {weather_data['main']['temp']} C
         Feels Like: {weather_data['main']['feels_like']} C
         Minimum: {weather_data['main']['temp_min']} C
         Maximum: {weather_data['main']['temp_max']} C
    ────────────────
    🌬️ Pressure:
        🌊 Sea Level: {weather_data['main']['sea_level']} hPa
        🌍 Ground Level: {weather_data['main']['grnd_level']} hPa
    ────────────────
    💧 Humidity:
         Value: {weather_data['main']['humidity']}%
    ────────────────
    👁️ Visibility:
         Value: {weather_data['visibility']} meters
    ────────────────
    🌬️ Wind:
        🌬️ Speed: {weather_data['wind']['speed']} m/s
        🧭 Direction: {weather_data['wind']['deg']}°
    ────────────────
    ☁️ Clouds:
         Value: {weather_data['clouds']['all']}%
    ────────────────
    🌅 Sunrise and Sunset times:
        🌄 Sunrise at: {datetime.datetime.fromtimestamp(weather_data['sys']['sunrise']).strftime('%H:%M:%S')}
        🌆 Sunset at: {datetime.datetime.fromtimestamp(weather_data['sys']['sunset']).strftime('%H:%M:%S')}
    ────────────────
    ⏰ Timezone:
         Value: GMT{weather_data['timezone']//3600}:{(weather_data['timezone']%3600)//60}
    ────────────────
    🕒 Data Time:
         Value: {datetime.datetime.fromtimestamp(weather_data['dt']).strftime('%Y-%m-%d %H:%M:%S')}
    ────────────────

Stay safe and have a great day! 🌟
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
    if result is True:
        try:
            set_user_info(user_id, message, 1 , 1)
            user_log(user_id , message)
            preferred_language = check_language(user_id, message)
            if preferred_language:
                welcome_message = (
                    f"🎉 به برنامه ما خوش آمدی {message.from_user.first_name}!\n"
                    "🌤️ ما به صورت روزانه وضعیت آب و هوایی منطقه شما را ارسال می‌کنیم.\n"
                    "😊 امیدواریم روز خوبی داشته باشی و از برنامه ما لذت ببری!"
                )
                bot.send_message(user_id, welcome_message, reply_markup=keyboard_language(preferred_language))
            else:
                welcome_message = (
                    f"🎉 Welcome to our Weather App, {message.from_user.first_name}!\n"
                    "🌤️ We're excited to keep you updated with the latest weather forecasts for your area.\n"
                    "😊 We hope you have a fantastic day and enjoy using our app!\n")
                bot.send_message(user_id, welcome_message, reply_markup=keyboard_language(preferred_language))
        except Exception as e:
            logging.error(f"An error occurred in the /start handler: {e}")  # Logging the error
            bot.send_message(user_id, "An error occurred while processing your request.")
            bot.send_message(log_admin , f"An error occurred in start:\n {e}")
    elif result is False:
        bot.send_message(user_id, "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @x")
    else:
        bot.send_message(user_id, result)

# Handler for location messages
@bot.message_handler(content_types=["location"])
def handle_location(message):
    user_id = message.from_user.id  # Get the user ID
    result = check_user_membership(user_id, channel_id)
    if result is True:
        try:
            preferred_language = check_language(user_id, message)
            schedule_var = check_var(user_id , message)
            set_user_info(user_id, message , schedule_var ,preferred_language)
            user_log(user_id , message )
            if preferred_language:
                bot.reply_to(message, "جهت دیدن وضعیت اب و هوایی روی گزینه 'اب و هوا' کلیک کنید")
            else:
                bot.reply_to(message, "Please type 'weather' for today's details.")
        except Exception as e:
            logging.error(f"An error occurred in the location handler: {e}")  # Logging the error
            bot.send_message(log_admin , f"An error occurred in location:\n {e}")

            bot.send_message(user_id, "An error occurred while processing your location.")
    elif result is False:
        bot.send_message(user_id, "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @x")
    else:
        bot.send_message(user_id, result)

# Handler for weather forecast requests
@bot.message_handler(func=lambda message: message.text.lower() in ["weather", "آب و هوا"])
def handle_weather_forecast(message):
    user_id = message.from_user.id  # Get the user ID
    result = check_user_membership(user_id, channel_id)
    if result is True:
        try:
            weather_data = get_weather(user_id)
            if weather_data is False:
                preferred_language = check_language(user_id, message)
                if preferred_language:
                    bot.reply_to(message, "لطفا موقعیت مکانی خودتان را ارسال کنید")
                else:
                    bot.reply_to(message, "Please provide your location.")
            elif weather_data is None:
                bot.reply_to(message, "An error occurred while fetching the weather data.")
            else:
                if "main" in weather_data:
                    preferred_language = check_language(user_id, message)  # Ensure preferred_language is set
                    weather_info = format_weather_data(weather_data, preferred_language)
                    user_log(user_id , message , weather_data)
                    bot.reply_to(message, weather_info)  # Send formatted weather data
                else:
                    bot.reply_to(message, "City Not Found")  # Handle case where city is not found
        except Exception as e:
            logging.error(f"An error occurred in the weather forecast handler: {e}")  # Logging the error
            bot.send_message(log_admin , f"An error occurred in the weather forecast handler: {e}")
            bot.reply_to(message, "An error occurred while processing your request.")
    elif result is False:
        bot.send_message(user_id, "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @x")
    else:
        bot.send_message(user_id, result)

# Handler for about_us requests
@bot.message_handler(func=lambda message: message.text.lower() in ["about us", "درباره ما"])
def handel_about_us(message):
    user_id = message.from_user.id  # Get the user ID
    result = check_user_membership(user_id, channel_id)
    if result is True:
        try:
            preferred_language = check_language(user_id, message)
            info = about_us(preferred_language)
            user_log(user_id , message)
            bot.reply_to(message, info)
        except Exception as e:
            logging.error(f"An error occurred in the about_us handler: {e}")  # Logging the error
            bot.send_message(log_admin , f"An error occurred in about us:\n {e}")
            bot.reply_to(message, "An error occurred while processing your request.")
    elif result is False:
        bot.send_message(user_id, "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @x")
    else:
        bot.send_message(user_id, result)

# Handler for 'settings' requests
@bot.message_handler(content_types=['contact'])
def handel_contact_us(message):
    user_id = message.from_user.id  # Get the user ID
    try:
        preferred_language = check_language(user_id, message)
        schedule_var = check_var(user_id , message)
        user_log(user_id , message)
        tap = f'<a href="tel:{phone_number}">{phone_number}</a>'
        set_phone(user_id , message , schedule_var , preferred_language)
        if preferred_language:
            contact_message = (
                "📞 راه های ارتباط با ما:\n"
                f"📱 شماره تماس: {tap}\n"
                "📧 ایمیل: info@x.ir"
            )
            bot.reply_to(message, contact_message, parse_mode='HTML')
        else:
            contact_message = (
                f"📞 Get in Touch with Us {message.from_user.first_name}, We’d love to hear from you!\n"
                f"📱 Tel: {tap}\n"
                "📧 Email: info@x.ir"
            )

            bot.reply_to(message, contact_message, parse_mode='HTML')
    except Exception as e:
        logging.error(f"An error occurred in the contact_us handler: {e}")  # Logging the error
        bot.send_message(log_admin , f"An error occurred in contact us:\n {e}")
        bot.reply_to(message, "An error occurred while processing your request.")

# Handler for 'settings' requests
@bot.message_handler(func=lambda message: message.text.lower() in ["settings", "تنظیمات"])
def handel_settings(message):
    user_id = message.from_user.id  # Get the user ID
    result = check_user_membership(user_id, channel_id)
    if result is True:
        try:
            preferred_language = check_language(user_id, message)
            user_log(user_id , message)
            if preferred_language:
                settings_message = (
                    "⚙️ تنظیمات\n"
                    "🌐 زبان: تغییر زبان برنامه\n"
                    "📅 ارسال روزانه: (on/off)"
                )
                bot.send_message(user_id, settings_message, reply_markup=settings_keyboard_language(preferred_language))
            else:
                settings_message = (
                    "⚙️ Settings\n"
                    "🌐 Language: Switch the program language\n"
                    "📅 Daily Send: Turn On/Off"
                )
                bot.send_message(user_id, settings_message, reply_markup=settings_keyboard_language(preferred_language))
        except Exception as e:
            logging.error(f"An error occurred in the settings handler: {e}")  # Logging the error
            bot.send_message(log_admin , f"An error occurred in setting handler:\n {e}")
            bot.send_message(user_id, "An error occurred while processing your request.")
    elif result is False:
        bot.send_message(user_id, "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @x")
    else:
        bot.send_message(user_id, result)

# Handler for language change requests
@bot.message_handler(func=lambda message: message.text.lower() in ["زبان/language"])
def handel_language(message):
    try:
        user_id = message.from_user.id  # Get the user ID
        result = check_user_membership(user_id, channel_id)
        if result is True:
            preferred_language = check_language(user_id, message)
            schedule_var = check_var(user_id , message)
            message_text = change_language(user_id , message , schedule_var , preferred_language )
            user_log(user_id , message)
            preferred_language = check_language(user_id , message)
            bot.send_message(user_id, message_text, reply_markup=keyboard_language(preferred_language))
        elif result is False:
            bot.send_message(user_id, "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @x")
        else:
            bot.send_message(user_id, result)
    except Exception as e:
        bot.send_message(log_admin , f"An error occurred in language:\n {e}")

# Handler for language change requests
@bot.message_handler(func=lambda message: message.text.lower() in ["ارسال روزانه", "daily schedule"])
def handel_schedule(message):
    try:
        user_id = message.from_user.id  # Get the user ID
        result = check_user_membership(user_id, channel_id)
        if result is True:
            schedule_var = check_var(user_id , message)
            preferred_language = check_language(user_id, message )
            message_text = change_schedule_var(user_id , message , schedule_var , preferred_language)
            user_log(user_id , message)
            status = 1 if "enabled" in message_text else 0
            bot.send_message(user_id, f"{daily_Repetition_text(preferred_language, status)}", reply_markup=keyboard_language(preferred_language))
        elif result is False:
            bot.send_message(user_id, "لطفا جهت استفاده از ربات عضو کانال تلگرام ما شوید\nادرس کانال تلگرام:  @x")
        else:
            bot.send_message(user_id, result)
    except Exception as e:
        bot.send_message(log_admin , f"An error occurred in daily schedul:\n {e}")

schedule.every().day.at("08:00").do(check_schedule)

# Start a new thread that runs the reo function
threading.Thread(target=reo).start()

# Start polling for updates from the bot
bot.infinity_polling()