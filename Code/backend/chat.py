import openai
import requests
import re
import json
from datetime import datetime, timedelta
from googletrans import Translator
from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

# API Configuration
OPENROUTER_API_KEY = "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"  # Replace with your key
WEATHER_API_KEY = "4755ac7786463300024c523fd7582e1a"
PIXABAY_API_KEY = "49507918-8121ad7375feb3f28c1f38692"
IPINFO_TOKEN = "e3b07d6f5956b1"  # From ipinfo.io

# API Endpoints
WEATHER_FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"
PIXABAY_URL = "https://pixabay.com/api/"
IPINFO_URL = "https://ipinfo.io/json"

# File Paths
LOCATION_FILE = "curr_location.txt"
WEATHER_FILE = "weather_report.txt"
WEATHER_DETAILS_FILE = "weather_details.txt"
KEYWORDS_FILE = "image_keywords.txt"

translator = Translator(service_urls=['translate.google.com'])
openai.api_base = "https://openrouter.ai/api/v1"
openai.api_key = OPENROUTER_API_KEY

def get_user_location():
    """Get location from IP and store in file"""
    try:
        response = requests.get(f"{IPINFO_URL}?token={IPINFO_TOKEN}", timeout=5)
        data = response.json()
        location = f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
        with open(LOCATION_FILE, 'w') as f:
            f.write(location)
        return location
    except Exception as e:
        print(f"Location Error: {str(e)}")
        return "Unknown Location"

def get_weather_forecast(location):
    """Get 3-day forecast and store in file"""
    try:
        params = {
            'q': location.split(',')[0],
            'appid': WEATHER_API_KEY,
            'units': 'metric',
            'cnt': 24*3  # 3 days data
        }
        response = requests.get(WEATHER_FORECAST_URL, params=params)
        data = response.json()
        
        forecast = {}
        for entry in data['list']:
            date = datetime.fromtimestamp(entry['dt']).strftime('%Y-%m-%d')
            if date not in forecast:
                forecast[date] = []
            forecast[date].append({
                'temp': entry['main']['temp'],
                'humidity': entry['main']['humidity'],
                'description': entry['weather'][0]['description'],
                'wind_speed': entry['wind']['speed'],
                'time': datetime.fromtimestamp(entry['dt']).strftime('%H:%M')
            })
        
        with open(WEATHER_FILE, 'w') as f:
            json.dump(forecast, f)
        return forecast
    except Exception as e:
        print(f"Weather Error: {str(e)}")
        return None

def extract_query_location(query):
    """Enhanced location extraction from query"""
    pattern = r'\b(?:in|for|at|near)\s+([A-Za-z\s,]+?)(?:\b|$|\.|\?|,)'
    matches = re.findall(pattern, query, re.IGNORECASE)
    return matches[0].strip() if matches else None

def store_query_weather(query, location):
    """Store weather details for query locations"""
    try:
        weather = get_weather_forecast(location)
        if weather:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'original_query': query,
                'location': location,
                'weather': weather
            }
            with open(WEATHER_DETAILS_FILE, 'a') as f:
                json.dump(entry, f)
                f.write('\n')
    except Exception as e:
        print(f"Weather Storage Error: {str(e)}")

def extract_keywords(query):
    """Use Deepseek R1 for keyword extraction"""
    try:
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat:r1",  # New R1 model
            messages=[{
                "role": "user",
                "content": f"Extract 5-6 comma-separated image keywords from: {query}"
            }],
            temperature=0.3,
            max_tokens=50
        )
        keywords = response.choices[0].message.content.strip()
        keywords = re.sub(r'[^a-zA-Z, ]', '', keywords)
        with open(KEYWORDS_FILE, 'w') as f:
            f.write(keywords)
        return keywords
    except Exception as e:
        print(f"Keyword Error: {str(e)}")
        return "agriculture"

def get_pixabay_images(keywords):
    """Fetch images from Pixabay"""
    try:
        params = {
            'key': PIXABAY_API_KEY,
            'q': keywords,
            'image_type': 'photo',
            'per_page': 3,
            'safesearch': 'true'
        }
        response = requests.get(PIXABAY_URL, params=params)
        return [hit['webformatURL'] for hit in response.json().get('hits', [])[:3]]
    except Exception as e:
        print(f"Pixabay Error: {str(e)}")
        return []

def generate_advice(query, location, weather):
    """Generate response using Deepseek R1 with context"""
    try:
        weather_context = "\n".join([
            f"{date}: {entries[0]['description']}, {entries[0]['temp']}°C"
            for date, entries in weather.items()
        ]) if weather else "Weather data unavailable"
        
        prompt = f"""As an agricultural expert in {location}, consider:
        - 3-day weather forecast: {weather_context}
        - User query: {query}
        Provide detailed advice with bullet points in simple language.
        if asked for prices of a crop in particular area just give the price you may think of in that area(Warning: never say that you dont know the price)
        if asked for schemes just tell about the schemes you know for the crop(Warning: never say that you dont know the schemes)
        if asked for temperature the current temperature just give the recent temperature as answer
        also dont give the prices of the crop until explicitly asked
        Prioritize and give answer for what is asked first other things are secondary
        Dont derive information from old prompts 
        Also the answer should be only 2 to 3 lines in word copyable format
        Extreme Warning: give answer for User query "only" using the information provided"""
        
        response = openai.ChatCompletion.create(
            model="deepseek/deepseek-chat:r1",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=600
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return "Advice generation failed. Please try again."

@socketio.on('message')
def handle_message(data):
    try:
        query = data['message'][:500]
        lang = data.get('language', 'en')
        
        # Get base context
        base_location = get_user_location()
        base_weather = get_weather_forecast(base_location)
        
        # Process query locations
        query_location = extract_query_location(query)
        if query_location:
            store_query_weather(query, query_location)
        
        # Generate response
        keywords = extract_keywords(query)
        images = get_pixabay_images(keywords)
        advice = generate_advice(query, base_location, base_weather)
        
        # Translation
        if lang != 'en':
            try:
                advice = translator.translate(advice, dest=lang).text
            except Exception as e:
                print(f"Translation Error: {str(e)}")
        
        # Send response
        emit('recv_message', {
            'text': advice.replace('->', '•').replace('**', ''),
            'images': images
        })
        
    except Exception as e:
        emit('recv_message', {
            'text': f"System Error: {str(e)}",
            'images': []
        })

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)