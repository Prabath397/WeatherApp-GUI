import os
import requests
from tkinter import Tk, Label, Entry, Button, StringVar, Frame
from tkinter import ttk
from dotenv import load_dotenv
from PIL import Image, ImageTk
from io import BytesIO
from datetime import datetime

# Load .env if present
load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
ICON_URL = "http://openweathermap.org/img/wn/{}@2x.png"

def get_weather(city, api_key=API_KEY, units="metric"):
    if not api_key:
        return None, "API key not found. Set OPENWEATHER_API_KEY in env or .env file."
    params = {"q": city, "appid": api_key, "units": units}
    try:
        resp = requests.get(BASE_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, str(e)

def get_forecast(city, api_key=API_KEY, units="metric"):
    if not api_key:
        return None, "API key not found."
    params = {"q": city, "appid": api_key, "units": units}
    try:
        resp = requests.get(FORECAST_URL, params=params, timeout=10)
        resp.raise_for_status()
        return resp.json(), None
    except Exception as e:
        return None, str(e)

def show_weather():
    city = city_var.get().strip()
    if not city:
        current_result_var.set("Enter a city name!")
        icon_label.config(image="")
        return

    data, error = get_weather(city)
    if error:
        current_result_var.set(error)
        icon_label.config(image="")
    elif data:
        try:
            name = data.get("name")
            country = data.get("sys", {}).get("country", "")
            temp = data.get("main", {}).get("temp")
            feels_like = data.get("main", {}).get("feels_like")
            desc = data.get("weather", [{}])[0].get("description", "N/A").title()
            humidity = data.get("main", {}).get("humidity")
            wind = data.get("wind", {}).get("speed")

            result = (f"🌍 {name}, {country}\n"
                      f"🌡️ Temp: {temp} °C (Feels like {feels_like} °C)\n"
                      f"☁️ Condition: {desc}\n"
                      f"💧 Humidity: {humidity}%\n"
                      f"💨 Wind: {wind} m/s")
            current_result_var.set(result)

            # Weather icon
            icon_code = data.get("weather", [{}])[0].get("icon")
            if icon_code:
                icon_url = ICON_URL.format(icon_code)
                icon_resp = requests.get(icon_url, timeout=10)
                img = Image.open(BytesIO(icon_resp.content))
                img = img.resize((100, 100))
                tk_img = ImageTk.PhotoImage(img)
                icon_label.config(image=tk_img)
                icon_label.image = tk_img
        except Exception:
            current_result_var.set("Error parsing weather data.")
            icon_label.config(image="")

def show_forecast():
    city = city_var.get().strip()
    if not city:
        forecast_result_var.set("Enter a city name!")
        return

    data, error = get_forecast(city)
    if error:
        forecast_result_var.set(error)
    elif data:
        try:
            forecast_text = f"5-Day Forecast for {city.title()}:\n"
            seen_dates = set()

            for entry in data["list"]:
                dt = datetime.fromtimestamp(entry["dt"])
                date_str = dt.strftime("%Y-%m-%d")
                time_str = dt.strftime("%H:%M")
                # Pick around 12:00 (midday) for each day
                if time_str == "12:00" and date_str not in seen_dates:
                    temp = entry["main"]["temp"]
                    desc = entry["weather"][0]["description"].title()
                    forecast_text += f"{date_str}: {temp} °C, {desc}\n"
                    seen_dates.add(date_str)

            forecast_result_var.set(forecast_text)
        except Exception:
            forecast_result_var.set("Error parsing forecast data.")
    else:
        forecast_result_var.set("Unknown error.")

# GUI setup
root = Tk()
root.title("Weather App")
root.geometry("450x500")

Label(root, text="Enter City:").pack(pady=5)
city_var = StringVar()
Entry(root, textvariable=city_var, width=30).pack(pady=5)

Button(root, text="Get Weather", command=show_weather).pack(pady=5)
Button(root, text="Get Forecast", command=show_forecast).pack(pady=5)

# Notebook for tabs
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", pady=10)

# Current Weather Tab
current_frame = Frame(notebook)
notebook.add(current_frame, text="Current Weather")

current_result_var = StringVar()
Label(current_frame, textvariable=current_result_var, justify="left", font=("Arial", 12), wraplength=400).pack(pady=10)

icon_label = Label(current_frame)
icon_label.pack(pady=5)

# Forecast Tab
forecast_frame = Frame(notebook)
notebook.add(forecast_frame, text="5-Day Forecast")

forecast_result_var = StringVar()
Label(forecast_frame, textvariable=forecast_result_var, justify="left", font=("Arial", 11), wraplength=400).pack(pady=10)

root.mainloop()
