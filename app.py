from flask import Flask, render_template, request, jsonify
import requests
from sqlalchemy import create_engine, Column, Integer, String, Date, Float, ForeignKey
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from chatterbot import ChatBot
from chatterbot.trainers import ListTrainer, ChatterBotCorpusTrainer

app = Flask(__name__)

# Define the database schema
Base = declarative_base()

# Read API key from api_key.txt file and save it to api_key variable
with open('api_key.txt', 'r') as file:
    api_key = file.read().strip()

# Define the itinerary as a list of dictionaries
itinerary = [
    {"name": "Corfe Castle", "coordinates": "50.6395,-2.0566"},
    {"name": "Cheltenham", "coordinates": "51.8330,-1.8433"},
    {"name": "Cambridge", "coordinates": "52.2053,0.1218"},
    {"name": "Bristol", "coordinates": "51.4545,-2.5879"},
    {"name": "Oxford", "coordinates": "51.7520,-1.2577"},
    {"name": "Norwich", "coordinates": "52.6309,1.2974"},
    {"name": "Amesbury", "coordinates": "51.1789,-1.8262"},
    {"name": "Newquay", "coordinates": "50.4429,-5.0553"},
    {"name": "Birmingham", "coordinates": "52.4862,-1.8904"}
]


# Function to retrieve weather data from the OpenWeatherMap API
def get_weather_data(coordinates):
    base_url = "https://api.openweathermap.org/data/2.5/weather"
    lat, lon = coordinates.split(',')
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": "metric"  # Retrieve temperature in Celsius
    }
    response = requests.get(base_url, params=params)

    # Print statements for debugging purposes
    print("API Request URL:", response.url)
    print("API Response Status Code:", response.status_code)

    if response.status_code == 200:
        data = response.json()
        print("API Response JSON:", data)
        return data
    else:
        print("API Request Failed. Status Code:", response.status_code)
        return

        # Define the city table schema


# Define the city table schema
class City(Base):
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True)
    weather_data = relationship('WeatherData', backref='city', cascade='all, delete-orphan')
    forecast_data = relationship('ForecastData', backref='city', cascade='all, delete-orphan')


# Define the weather data table schema
class WeatherData(Base):
    __tablename__ = 'weather_data'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    conditions = Column(String(50))
    temperature = Column(Float)
    city_id = Column(Integer, ForeignKey('cities.id'))


# Define the forecast data table schema
class ForecastData(Base):
    __tablename__ = 'forecast_data'

    id = Column(Integer, primary_key=True)
    date = Column(Date)
    conditions = Column(String(50))
    temperature = Column(Float)
    city_id = Column(Integer, ForeignKey('cities.id'))


# Initialize the engine and session
engine = create_engine('sqlite:///weather_database.db', connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

# Create the tables if they don't exist
Base.metadata.create_all(engine)

# Define API key and list of cities
cities = ['Corfe Castle', 'Cheltenham', 'Cambridge', 'Bristol', 'Oxford', 'Norwich', 'Amesbury', 'Newquay',
          'Birmingham']

# Initialize the chatbot and trainer
chatbot = ChatBot('WeatherBot', logic_adapters=['chatterbot.logic.BestMatch'])
list_trainer = ListTrainer(chatbot)
corpus_trainer = ChatterBotCorpusTrainer(chatbot)


# Function to clear existing data in the database
def clear_existing_data():
    session.query(WeatherData).delete()
    session.query(ForecastData).delete()
    session.query(City).delete()
    session.commit()


# Function to fetch and store current weather data for a city
def fetch_and_store_weather_data(city_name):
    api_url = f'http://api.openweathermap.org/data/2.5/weather?q={city_name},GB&appid={api_key}'

    try:
        response = requests.get(api_url)
        data = response.json()

        # Get the city object from the database or create a new one if it doesn't exist
        city = session.query(City).filter_by(name=city_name).first()
        if not city:
            city = City(name=city_name)
            session.add(city)

        # Extract current weather data from the API response
        timestamp = data['dt']
        date_info = datetime.utcfromtimestamp(timestamp).strftime('%d-%m-%Y')
        conditions = data['weather'][0]['description']
        temperature_kelvin = data['main']['temp']
        temperature_celsius = round((temperature_kelvin - 273.15), 2)

        # Convert the date string to a Python date object
        date_info = datetime.strptime(date_info, '%d-%m-%Y').date()

        # Create a new WeatherData object and add it to the session
        weather_data = WeatherData(date=date_info, conditions=conditions, temperature=temperature_celsius)
        session.add(weather_data)

        # Add the weather data to the city's relationship
        city.weather_data.append(weather_data)

        # Commit the changes to the database
        session.commit()
        print(f'Successfully updated weather data for {city_name}')
    except Exception as e:
        print(f'Error fetching or storing data for {city_name}: {e}')


# Function to fetch and store 5-day forecast data for a city
def fetch_and_store_5_day_forecast(city_name):
    api_url = f'http://api.openweathermap.org/data/2.5/forecast?q={city_name},GB&appid={api_key}'

    try:
        response = requests.get(api_url)
        data = response.json()

        # Get the city object from the database or create a new one if it doesn't exist
        city = session.query(City).filter_by(name=city_name).first()
        if not city:
            city = City(name=city_name)
            session.add(city)

        for entry in data['list']:
            timestamp = entry['dt']
            date_info = datetime.utcfromtimestamp(timestamp).strftime('%d-%m-%Y')
            time_info = datetime.utcfromtimestamp(timestamp).strftime('%H:%M:%S')

            if time_info == '12:00:00':
                conditions = entry['weather'][0]['description']
                temperature_kelvin = entry['main']['temp']
                temperature_celsius = round((temperature_kelvin - 273.15), 2)

                # Convert the date string to a Python date object
                date_info = datetime.strptime(date_info, '%d-%m-%Y').date()

                # Create a new ForecastData object and add it to the session
                forecast_data = ForecastData(date=date_info, conditions=conditions, temperature=temperature_celsius)
                session.add(forecast_data)

                # Add the forecast data to the city's relationship
                city.forecast_data.append(forecast_data)

        # Commit the changes to the database
        session.commit()
        print(f'Successfully updated 5-day forecast data for {city_name}')

    except Exception as e:
        print(f'Error fetching or storing 5-day forecast data for {city_name}: {e}')


# Function to fetch 5-day forecast data from the database
def fetch_5_day_forecast_from_database(city_name):
    city = session.query(City).filter_by(name=city_name).first()

    if city:
        return city.forecast_data
    else:
        return None


# Function to process user input
def process_user_input(user_input):
    if 'weather' in user_input.lower() or 'temperature' in user_input.lower():
        for city in cities:
            if city.lower() in user_input.lower():
                return city

    if 'best day to visit' in user_input.lower():
        for city in cities:
            if city.lower() in user_input.lower():
                return city

    return None


# Function to determine the best day to visit a city
def determine_best_day(city_name):
    forecast_data = fetch_5_day_forecast_from_database(city_name)

    if forecast_data:
        best_day = None
        best_conditions = None
        best_temperature = float('-inf')

        for entry in forecast_data:
            date, conditions, temperature = entry.date, entry.conditions, entry.temperature

            if conditions_in_priority(conditions) or (
                    conditions == best_conditions and temperature > best_temperature):
                best_day = date
                best_conditions = conditions
                best_temperature = temperature

        return best_day, best_conditions, best_temperature
    else:
        return None


# Function to check if conditions are in priority
def conditions_in_priority(conditions):
    priority_conditions = ['clear sky', 'few clouds', 'scattered clouds', 'broken clouds', 'overcast clouds']
    return conditions in priority_conditions


# Clear existing data in the database before fetching and storing new data
clear_existing_data()

# Update weather data for all cities
for city in cities:
    fetch_and_store_weather_data(city)

# Fetch and store 5-day forecast data for all cities
for city in cities:
    fetch_and_store_5_day_forecast(city)

# Train the chatbot with weather data
weather_data = session.query(WeatherData).all()

# Loop through the weather data and extract the city name, date, conditions, and temperature
for data_point in weather_data:
    city_name = data_point.city.name
    date_info = data_point.date
    conditions_info = data_point.conditions
    temperature_info = data_point.temperature

# Questions
    questions = [
        f'What is the weather in {city_name} today?',
        f'What is the temperature in {city_name} today?',
        f'What is the weather forecast for {city_name}?',
        f'What is the temperature in {city_name} for the next 5 days?',
        f'What is the best day to visit {city_name}?',
    ]

# Statements
    statements = [
        f'The weather in {city_name} on {date_info} is {conditions_info} with a temperature of {temperature_info}°C.',
        f'The temperature in {city_name} on {date_info} is {temperature_info}°C.',
    ]

# Train the chatbot with the questions and statements
    list_trainer.train(questions)
    list_trainer.train(statements)

# Train the chatbot with the ChatterBot corpus data
corpus_trainer.train('chatterbot.corpus.english.greetings',
                     'chatterbot.corpus.english.conversations',
                     'chatterbot.corpus.english.botprofile',
                     'chatterbot.corpus.english.computers',
                     )

# Fetch 5-day forecast data for all cities
forecast_data_all_cities = {city: fetch_5_day_forecast_from_database(city) for city in cities}

# Close the session
session.close()


def get_chatbot_response(user_input):
    # Process user input and interact with the chatbot
    city_name = process_user_input(user_input)

    if city_name:
        try:
            city = session.query(City).filter_by(name=city_name).first()

            if city:
                weather_data = session.query(WeatherData).filter_by(city=city).order_by(WeatherData.date.desc()).first()

                if weather_data:
                    city_name = weather_data.city.name
                    date_info = weather_data.date
                    conditions_info = weather_data.conditions
                    temperature_info = weather_data.temperature

                    if 'best day to visit' in user_input.lower():
                        best_day_info = determine_best_day(city_name)

                        if best_day_info:
                            best_day, best_conditions, best_temperature = best_day_info
                            formatted_best_day = best_day.strftime("%d-%m-%Y")
                            response_text = f'The best day to visit {city_name} is {formatted_best_day}. The weather is {best_temperature}°C and {best_conditions}.'
                        else:
                            response_text = f'Error: Unable to determine the best day to visit {city_name}'
                    elif 'next 5 days' in user_input.lower():
                        forecast_data = forecast_data_all_cities.get(city_name)

                        if forecast_data:
                            response_text = f'5-day weather forecast for {city_name}:\n'
                            for entry in forecast_data:
                                date = entry.date
                                formatted_date = date.strftime("%d-%m-%Y")
                                conditions = entry.conditions
                                temperature = entry.temperature
                                response_text += f'{formatted_date}: {temperature}°C and {conditions}\n'
                        else:
                            response_text = f'Error: Unable to retrieve 5-day forecast for {city_name}'
                    else:
                        formatted_date_info = date_info.strftime("%d-%m-%Y")
                        response_text = f'The weather in {city_name} on {formatted_date_info} is {conditions_info} with a temperature of {temperature_info}°C.'
                else:
                    response_text = f'Error: Unable to retrieve weather data for {city_name}'
            else:
                response_text = f'Error: City {city_name} not found in the database'
        except Exception as e:
            response_text = f'Error fetching or processing data: {e}'
    else:
        # If the user input is not related to weather, use the chatbot for small talk
        bot_response = chatbot.get_response(user_input)
        response_text = str(bot_response)

    return response_text


# Route to display dropdown menu and weather data
@app.route('/')
def index():
    selected_location = request.args.get('location')
    location_name = None  # Initialize location_name

    if selected_location:
        # Retrieve the location name from the itinerary based on the selected coordinates
        for location in itinerary:
            if location['coordinates'].replace(" ", "") == selected_location:
                location_name = location['name']
                break

        weather_data = get_weather_data(selected_location)

        if 'weather' in weather_data and 'main' in weather_data:
            # Retrieve weather description, temperature, and timestamp
            weather_description = weather_data['weather'][0]['description']
            weather_icon = weather_data['weather'][0]['icon']
            temperature_celsius = weather_data['main']['temp']
            feels_like_celsius = weather_data['main']['feels_like']

            # Convert timestamp to date and time
            timestamp = weather_data['dt']
            date_time = datetime.utcfromtimestamp(timestamp)
            date = date_time.strftime('%d/%m/%Y')
            time = date_time.strftime('%I:%M %p')  # 12-hour time with AM/PM

            return render_template('index.html', itinerary=itinerary, selected_location=selected_location,
                                   location_name=location_name, weather_description=weather_description.capitalize(),
                                   weather_icon=weather_icon, temperature_celsius=int(temperature_celsius),
                                   feels_like_celsius=int(feels_like_celsius), date=date, time=time)

    return render_template('index.html', itinerary=itinerary, selected_location=selected_location,
                           location_name=location_name)


@app.route('/get_response', methods=['POST'])
def get_response():
    user_input = request.json['user_input']
    bot_response = get_chatbot_response(user_input)

    return jsonify({'bot_response': bot_response})


# Entry point of application
if __name__ == "__main__":
    app.run(debug=True)
