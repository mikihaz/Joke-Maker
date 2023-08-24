import random
import requests
import streamlit as st
import concurrent.futures
import os
import pandas as pd

# Profile Class


class Profile:
    def __init__(self, ageGroup, gender, weather, cityName):
        self.ageGroup = ageGroup
        self.gender = gender
        self.weather = weather
        self.cityName = cityName

    def __str__(self):
        return f"Profile: Age Group - {self.ageGroup}, Gender - {self.gender}, Weather - {self.weather}, City Name - {self.cityName}"

# Random Profile Generator


def rand_profile():
    ageGroupsData = {
        "Silent Generation": "Born between 1928 and 1945",
        "Baby Boomers": "Born between 1946 and 1964",
        "Generation X": "Born between 1965 and 1980",
        "Millennials (Generation Y)": "Born between 1981 and 1996",
        "Generation Z": "Born between 1997 and 2012",
        "Generation Alpha": "Born from 2013 onwards"}

    ageGroups = list(ageGroupsData.keys())
    genders = ['Female', 'Male', 'Others']
    cityNames = ['Delhi', 'Bangalore', 'Kolkata']
    weathers = [
        "Rainy",
        "Sunny",
        "Hot",
        "Cold",
        "Foggy",
        "Hazy",
        "Humid",
        "Dry",
        "Cloudy",
        "Thunderstorms",
        "Dust storms",
        "Cyclonic"
    ]
    # Generate Random Profile
    # Generate random values
    random_age_group = random.choice(ageGroups)
    random_gender = random.choice(genders)
    random_city_name = random.choice(cityNames)
    random_weather = random.choice(weathers)

    # Create a dictionary representing the random profile
    random_profile = {
        "ageGroup": random_age_group,
        "gender": random_gender,
        "cityName": random_city_name,
        "weather": random_weather
    }

    return random_profile


# Fetching OpenAPI Key from OS ENV
api_key = "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"
# api_key = os.getenv('openai_api_key')

# Function to call the OpenAI API


def call_api():
    profile = rand_profile()
    jokeInitializer = [
        "Generate a one-liner joke suitable for a ${profile.ageGroup} ${profile.gender} on a ${profile.weather} day in ${profile.cityName}",
        "Craft a joke that would make a ${profile.ageGroup} ${profile.gender} laugh on a ${profile.weather} day in ${profile.cityName}",
        "Imagine a scenario where a ${profile.ageGroup} ${profile.gender} in ${profile.cityName} experiences ${profile.weather} weather. Create a joke for it",
        "Write a joke that fits the theme of a ${profile.weather} day in ${profile.cityName} and would be appreciated by a ${profile.ageGroup} ${profile.gender}",
        "Develop a humorous one-liner for a ${profile.ageGroup} ${profile.gender} experiencing ${profile.weather} weather in the city of ${profile.cityName}",
        "You're an AI comedian creating a joke about ${profile.cityName}'s ${profile.weather} weather for a ${profile.ageGroup} ${profile.gender}",
        "On a day with ${profile.weather} weather in ${profile.cityName}, give me a joke that a ${profile.ageGroup} ${profile.gender} would find funny",
        "Craft a joke that relates to the ${profile.weather} conditions in ${profile.cityName} and would resonate with a ${profile.ageGroup} ${profile.gender}",
        "Imagine entertaining a ${profile.ageGroup} ${profile.gender} in ${profile.cityName} on a ${profile.weather} day. Share a joke suitable for the moment",
        "Write a one-liner for a ${profile.ageGroup} ${profile.gender} enjoying ${profile.weather} weather in the urban setting of ${profile.cityName}",
        "You're hosting a comedy show for ${profile.ageGroup} ${profile.gender} residents of ${profile.cityName} on a ${profile.weather} day. Prepare a joke",
        "Create a joke that's relatable to a ${profile.ageGroup} ${profile.gender} experiencing ${profile.weather} weather in the city of ${profile.cityName}",
        "As an AI comedian, your task is to come up with a joke that captures the essence of ${profile.cityName}'s ${profile.weather} day for ${profile.ageGroup} ${profile.gender}",
        "Write a humorous line that would make a ${profile.ageGroup} ${profile.gender} smile during ${profile.weather} weather in the urban environment of ${profile.cityName}"
    ]
    # Propmt for the AI
    prompt = f"User: ${random.choice(jokeInitializer)}. The Joke must me relateable to the person, place and weather.\nAI:"

    # Getting AI Response
    # Define the headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ${api_key}'
    }

    # Define the API endpoint URL
    url = 'https://api.openai.com/v1/engines/text-davinci-003/completions'

    # Define the request payload
    payload = {
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 100,
        "n": 1,
        "stop": None
    }

    # Send the POST request
    response = requests.post(url, headers=headers, json=payload)

    # Check the response status code
    if response.status_code == 200:
        response_json = response.json()
        # Handle the response as needed (e.g., extract the generated joke)
        generated_joke = response_json['choices'][0]['text']
        print("Generated Joke - ${prompt}:", generated_joke)
        return {
            "status_code": 200,
            "prompt": prompt,
            "response": response_json
        }
    else:
        print(f'Error: {response.status_code}')
        return {
            "status_code": response.status_code,
            "prompt": prompt,
            "response": ''
        }


# Create a load testing function with concurrent user and data that returns all types of reports
# Define the number of concurrent users and requests per user
concurrent_users = 5  # Number of concurrent users
requests_per_user = 10  # Number of requests per user

# Function to simulate concurrent users


def simulate_users(concurrent_users):
    all_responses = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        for user_id in range(concurrent_users):
            user_responses = executor.submit(call_api).result()
            print(user_responses)
            all_responses.extend(user_responses)
    return all_responses


# Streamlit app
st.title("Load Testing and Reporting App")

# Load testing configuration
concurrent_users = st.number_input(
    "Concurrent Users", min_value=1, max_value=100, value=5)
requests_per_user = st.number_input(
    "Requests Per User", min_value=1, max_value=100, value=10)

# Start load testing
if st.button("Start Load Testing"):
    st.text("Load testing in progress...")
    responses = simulate_users(concurrent_users)

    # Generate a DataFrame for the responses
    df = pd.DataFrame(responses)

    # Calculate statistics
    num_successful_requests = df[df['status_code'] == 200].shape[0]
    num_failed_requests = df[df['status_code'] != 200].shape[0]
    success_rate = (num_successful_requests /
                    (num_successful_requests + num_failed_requests)) * 100

    st.text(f"Load testing completed.")
    st.text(f"Successful requests: {num_successful_requests}")
    st.text(f"Failed requests: {num_failed_requests}")
    st.text(f"Success rate: {success_rate:.2f}%")

    # Generate and display charts
    st.subheader("Response Status Distribution")
    status_counts = df['status_code'].value_counts()
    st.bar_chart(status_counts)

    # Option to download the report
    if st.button("Download Report"):
        df.to_csv("load_testing_report.csv", index=False)
        st.success("Report downloaded successfully.")

# Optionally, display the report if it exists
if os.path.exists("load_testing_report.csv"):
    st.subheader("Load Testing Report")
    df = pd.read_csv("load_testing_report.csv")
    st.write(df)

# Optionally, display additional charts or data as needed
