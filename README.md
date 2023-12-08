# Weather In The UK - Go Travel! Weather Tool

This project is a web application that provides weather information and a chatbot for discussing weather-related queries. The application is built using Flask, SQLAlchemy, OpenWeatherMap API, and ChatterBot.

## Features
- **Weather Information**: View current weather details for selected locations in the UK.
- **Interactive Map**: A map with markers representing selected locations.
- **Chatbot Integration**: Chat with the WeatherBot to get weather-related information and engage in small talk.

## Prerequisites
- Python 3.7.9
- Flask
- SQLAlchemy
- OpenWeatherMap API Key
- ChatterBot

## Installation
1. Clone the repository: `git clone https://github.com/nickmarriott11/WeatherApp_ChatBot.git`
2. Install dependencies: `pip install -r requirements.txt`
3. Obtain an API key from [OpenWeatherMap](https://openweathermap.org/) and save it in a file named `api_key.txt`.
4. Run the application: `python app.py`

## Usage
1. Access the application in your web browser at [http://localhost:5000](http://localhost:5000).
2. Select a location from the dropdown menu to view current weather details and the location on the map.
3. Open the chat window to interact with the WeatherBot. You can ask 3 different types of quieries: What is the weather in 'city name'?, What is the weather in 'city name' for then next 5 days?, What is the best day to visit 'city name'?
   

## Files and Directories
- **app.py**: Main application file containing Flask routes, database models, and API interactions.
- **index.html**: HTML template for the main page.
- **styles.css**: CSS styles for the application.
- **map_interactions.js**: JavaScript file for map interactions.
- **weather_database.db**: SQLite database file for storing weather and forecast data.

## Database Schema
- **City**: Stores information about cities.
- **WeatherData**: Stores current weather data.
- **ForecastData**: Stores 5-day forecast data.

## WeatherBot Training
The chatbot is trained with both user-generated questions and statements as well as a database populated with weather data fetched from the API and ChatterBot corpus data related to general topics for smalltalk purposes.

## Acknowledgments
- OpenWeatherMap for providing weather data.
- ChatterBot for the chatbot functionality.
- Leaflet for the interactive map.

## Contributors
- Nick Marriott(https://github.com/nickmarriott11)

