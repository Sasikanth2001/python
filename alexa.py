import speech_recognition as sr
import pyttsx3
import pywhatkit
import datetime as dt
import wikipedia
import pyjokes
import schedule
import time
import json
import os
import requests
#import geocoder

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

stop_phrases = ["stop", "quit", "exit", "bye"]


def talk(text):
    engine.say(text)
    engine.runAndWait()
    time.sleep(1)


def take_command():
    command = ""
    print('hi')
    try:
        listener = sr.Recognizer()
        with sr.Microphone() as source:
            print("Listening...")
            listener.adjust_for_ambient_noise(source)
            audio = listener.listen(source, timeout=5)
            print("ds")
        command = listener.recognize_google(audio)
        print("hello")
        print("Recognized command:", command)
        command = command.lower()

        if 'stacia' in command:
            command = command.replace('stacia', '').strip()
        print(command)
    except sr.UnknownValueError:
        print("Unable to recognize speech")
    except sr.RequestError as e:
        print(f"Error: {str(e)}")
    return command


def add_reminder(message, date, time):
    def job():
        if not active:
            print(f"Reminder: {message}")
            talk(f"Reminder: {message}")

    if not active:
        print(f"Reminder added: {message} at {date} {time}")
        talk(f"Reminder added: {message} at {date} {time}")

    schedule_date_time = f"{date} {time}"
    schedule.every().day.at(schedule_date_time).do(job)


def add_task(task):
    tasks = load_tasks()
    tasks.append(task)
    save_tasks(tasks)
    talk("Task added to the To-Do list")


def remove_task(task):
    tasks = load_tasks()
    if task in tasks:
        tasks.remove(task)
        save_tasks(tasks)
        talk("Task removed from the To-Do list")
    else:
        talk("The task is not in the To-Do list")


def show_tasks():
    tasks = load_tasks()
    if len(tasks) == 0:
        talk("There are no tasks assigned in the To-Do list.")
    else:
        talk("Here are the tasks in the To-Do list:")
        for i, task in enumerate(tasks):
            talk(f"Task {i + 1}: {task}")


def save_tasks(tasks):
    with open("tasks.json", "w") as file:
        json.dump(tasks, file)


def load_tasks():
    if not os.path.exists("tasks.json"):
        return []
    with open("tasks.json", "r") as file:
        return json.load(file)

def get_news():
    response = requests.get('https://newsapi.org/v2/top-headlines?country=us&apiKey=8dc7b6e041c746e18b31de065cd1bcf3')
    if response.status_code == 200:
        news_data = response.json()
        articles = news_data["articles"]
        if len(articles) > 0:
            talk("Here are the latest news headlines:")
            for i, article in enumerate(articles[:5]):
                title = article["title"]
                source = article["source"]["name"]
                talk(f"Headline {i + 1}: {title} from {source}")
        else:
            talk("No news articles found.")
    else:
        talk("Unable to fetch news information.")


def extract_city(command):
    words = command.split()
    if 'weather' in words:
        city_index = words.index('weather') + 2
        if city_index < len(words):
            return words[city_index]
    return ""


def weather(city):
    key = "4f0609d4cb407ad6fe62fe8a3381916e"
    weather_url = "https://api.openweathermap.org/data/2.5/weather?"
    city_name = city
    complete_url = weather_url + "appid=" + key + "&q=" + city_name
    response = requests.get(complete_url)
    x = response.json()
    if x["cod"] != "404":
        y = x["main"]
        current_temperature = y['temp']
        return str(current_temperature)


active = False


def run_alexa():
    global active
    talk("Hi, I am stacia. What can I do for you?")
    while True:
        command = take_command()
        
        if any(phrase in command for phrase in stop_phrases) and active in command:
            active = False
            talk("Goodbye!")
            break
        
        if 'stacia' in command:
            active = True
            command = command.replace('stacia', '').strip()
            print(command)
        else:
            active = False

        if active and 'play' in command:
            song = command.replace('play', '').strip()
            talk("Playing " + song)
            pywhatkit.playonyt(song)

        elif active and 'time' in command:
            current_time = dt.datetime.now().strftime('%I:%M %p')
            print(current_time)
            talk("The current time is " + current_time)

        elif active and 'tell me about' in command:
            search_query = command.replace('tell me about', '').strip()
            try:
                info = wikipedia.summary(search_query, sentences=1)
                print(info)
                talk(info)
            except wikipedia.exceptions.PageError:
                talk("Sorry, I couldn't find any information on that topic.")
            except wikipedia.exceptions.DisambiguationError:
                talk("There are multiple options for that search. Please provide more specific information.")

        elif active and 'joke' in command:
            joke = pyjokes.get_joke()
            print(joke)
            talk(joke)

        elif active and 'reminder' in command:
            talk("Sure, I can help you set a reminder. What is your message?")
            reminder_message = take_command()

            talk("On what date should I set the reminder?")
            reminder_date = take_command()

            talk("At what time should I set the reminder?")
            reminder_time = take_command()

            add_reminder(reminder_message, reminder_date, reminder_time)

        elif active and 'add task' in command:
            task = command.replace('add task', '').strip()
            add_task(task)

        elif active and 'remove task' in command:
            task = command.replace('remove task', '').strip()
            remove_task(task)

        elif active and 'show task' in command:
            show_tasks()

        elif active and 'weather' in command:
            city = extract_city(command)
            if city:
                weather_api = weather(city)
                if weather_api:
                    talk(f"The current temperature in {city} is {weather_api} degrees Fahrenheit.")
                else:
                    talk(f"Sorry, I couldn't fetch the weather information for {city}.")
            else:
                talk("Sorry, I couldn't understand the city name.")

        elif active and 'news' in command:
            get_news()

        elif active and 'hi' in command:
            talk('Hi, sir!')

        else:
            talk('Please say the command again.')

        schedule.run_pending()
        time.sleep(1)


run_alexa()