# We'll make a web app using streamlit that will tell jokes.
# We'll use open AI to generate the jokes.
# The required parameters will be place(city), age group, weather
# We have to be cautious about the jokes, those shouldn't be offensive.

import streamlit as st
import openai
import os
from textblob import TextBlob


openai.api_key = os.getenv('openai_api_key')

def get_joke(place, age_group, weather,gender):
    prompt = f"User: You are a One Liner Joke Generator AI. Tell a joke for {gender} of {age_group} on a {weather} day in {place}. The Joke must me relateable to the person, place and weather.\nAI:"
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        max_tokens=100,
        n=1,
        stop=None,
        temperature=0.7
    )
    joke = response['choices'][0]['text']
    
    # Sentiment analysis validation
    sentiment = TextBlob(joke).sentiment.polarity
    if sentiment < 0:
        return get_joke(place, age_group, weather,gender) # Retry if negative sentiment detected
    
    return joke


def main():
    st.title("Joke Generator")
    st.write("This is a web app to generate jokes using OpenAI.")
    place = st.text_input("Enter a place name: ")
    age_group = st.selectbox("Select an age group: ", ("Kids","Adults","Old"))
    weather = st.selectbox("Select a weather: ", ("Sunny", "Rainy", "Cold", "Windy"))
    gender = st.selectbox("Select a Gender: ", ("Male","Female"))
    if st.button("Tell me a joke"):
        joke = get_joke(place, age_group, weather,gender)
        st.write(joke)

if __name__ == "__main__":
    main()

# Run the app using the following command:
# streamlit run jokes.py
# The app will be running on http://localhost:8501/
# You can also share the app using the following command:
# streamlit run jokes.py --share
