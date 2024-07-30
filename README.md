# rahbaan_telegram_weather_app
WeatherBot This Python script is a Telegram bot that provides weather updates to users. It uses the telebot library for interacting with the Telegram API and the requests library for fetching weather data from an API. The bot supports both English and Persian languages.

#Key Features
Daily Weather Updates: The bot can send daily weather updates to users at a specific time.
Real-time Weather Updates: Users can request the current weather at any time.
Location-based Weather: The bot fetches weather data based on the user’s location.
Multilingual Support: The bot supports both English and Persian languages.

#Code Structure
The script is structured into several sections:

Imports and Initial Setup: The script imports necessary libraries and sets up the bot using the API token. It also initializes some variables and dictionaries to store user-specific data like locations and language preferences.

Helper Functions: These functions are used to generate different types of messages and keyboards based on the user’s language preference.

Weather Update Functions: These functions are responsible for sending daily weather updates to all users.

Message Handlers: These functions define how the bot should respond to different types of messages or commands from users.

Weather Forecast Handler: This function fetches the weather data for the user’s location and sends a formatted weather report to the user.

Schedule Setup: The script uses the schedule library to run the check_schedule function every day at a specific time. This is done in a separate thread so that it doesn’t block the main thread where the bot is polling for new updates.

Bot Polling: The last line of the script starts the bot. The bot will keep polling the Telegram server for new updates.

#Usage
Users can interact with the bot using various commands and buttons. They can send their location to the bot, request the current weather, and enable or disable daily weather updates. The bot also provides options to change the language.

#Dependencies
The bot requires the following Python libraries:

telebot
schedule
requests
It also requires a Telegram API token and a weather API key, which are imported from the confing module. The weather API key is used to fetch weather data from a weather API. The base URL of the weather API and the phone number for contact are also imported from the confing module.

#Note
Please replace the API_TOKEN, api_key, base_url, and phone_number in the confing module with your own credentials before running the bot.

Disclaimer
This bot is for educational purposes only. Please use it responsibly. The author is not responsible for any misuse or damage.
