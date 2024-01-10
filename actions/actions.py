# actions.py
from datetime import datetime
import holidays
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from sympy import sympify, SympifyError
import requests
from rasa_sdk.events import SlotSet
import re
from pymongo import MongoClient

class ActionTellTime(Action):
    def name(self) -> Text:
        return "action_tell_time"

    def run(self, dispatcher, tracker, domain):
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        dispatcher.utter_message(text=f"The current time is {current_time}")
        return []

class ActionTellDate(Action):
    def name(self) -> Text:
        return "action_tell_date"

    def run(self, dispatcher, tracker, domain):
        today_date = datetime.now().strftime("%d %B %Y")
        dispatcher.utter_message(text=f"Today's date is {today_date}")
        return []

class ActionSpecialDay(Action):
    def name(self) -> Text:
        return "action_special_day"

    def run(self, dispatcher, tracker, domain):
        country = tracker.get_slot('country')
        if not country:
            dispatcher.utter_message(text="Please tell me which country's holidays you are interested in.")
            return []

        today_date = datetime.now()
        country_holidays = holidays.CountryHoliday(country)
        if today_date in country_holidays:
            message = f"Today is {country_holidays.get(today_date)}."
        else:
            message = "There are no special holidays today."
        dispatcher.utter_message(text=message)
        return []

class ActionPerformCalculation(Action):
    def name(self) -> Text:
        return "action_perform_calculation"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker, domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        user_message = tracker.latest_message.get('text')

        math_expr = re.findall(r"([-+]?[0-9]*\.?[0-9]+[*/+-][-+]?[0-9]*\.?[0-9]*)", user_message)

        if math_expr:
            try:
                result = sympify(math_expr[0])
                dispatcher.utter_message(text=f"The result is {result}")
            except SympifyError:
                dispatcher.utter_message(text="I'm sorry, I cannot compute that.")
        else:
            dispatcher.utter_message(text="I couldn't find a mathematical expression to evaluate.")
        return []

class ActionTeachLanguage(Action):
    def name(self) -> Text:
        return "action_teach_language"

    def run(self, dispatcher, tracker, domain):
        # Setup MongoDB client
        client = MongoClient('mongodb://localhost:27017/')
        db = client['chatbot_db']
        translations = db['translations']

        language = tracker.get_slot('language').lower()
        english_word = tracker.get_slot('english_word')

        if not language or not english_word:
            dispatcher.utter_message(text="Please specify both a word and a language for translation.")
            return []

        try:
            language_data = translations.find_one({"english": english_word})
            if language_data and language in language_data:
                translated_word = language_data.get(language)
                message = f"'{english_word}' in {language} is '{translated_word}'."
            else:
                message = f"I don't have the translation for '{english_word}' in {language}."
        except Exception as e:
            print(f"Error when accessing the database: {e}")
            message = "I'm having trouble accessing the translation right now."

        dispatcher.utter_message(text=message)
        return []

