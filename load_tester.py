from datetime import datetime
from datetime import timedelta
import random
import tempfile
import requests
import streamlit as st
import concurrent.futures
import os
import time
import pdfkit
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
    random_profile = Profile(
        random_age_group, random_gender, random_city_name, random_weather)

    return random_profile


# Fetching OpenAPI Key from OS ENV
api_key = os.getenv('openai_api_key')

# Function to call the OpenAI API


def call_api(user_no, request_no):
    profile = rand_profile()
    jokeInitializer = [
        "Generate a one-liner joke suitable for a {} {} on a {} day in {}".format(
            profile.ageGroup, profile.gender, profile.weather, profile.cityName),
        "Craft a joke that would make a {} {} laugh on a {} day in {}".format(
            profile.ageGroup, profile.gender, profile.weather, profile.cityName),
        "Imagine a scenario where a {} {} in {} experiences {} weather. Create a joke for it".format(
            profile.ageGroup, profile.gender, profile.cityName, profile.weather),
        "Write a joke that fits the theme of a {} day in {} and would be appreciated by a {} {}".format(
            profile.weather, profile.cityName, profile.ageGroup, profile.gender),
        "Develop a humorous one-liner for a {} {} experiencing {} weather in the city of {}".format(
            profile.ageGroup, profile.gender, profile.weather, profile.cityName),
        "You're an AI comedian creating a joke about {}'s {} weather for a {} {}".format(
            profile.cityName, profile.weather, profile.ageGroup, profile.gender),
        "On a day with {} weather in {}, give me a joke that a {} {} would find funny".format(
            profile.weather, profile.cityName, profile.ageGroup, profile.gender),
        "Craft a joke that relates to the {} conditions in {} and would resonate with a {} {}".format(
            profile.weather, profile.cityName, profile.ageGroup, profile.gender),
        "Imagine entertaining a {} {} in {} on a {} day. Share a joke suitable for the moment".format(
            profile.ageGroup, profile.gender, profile.cityName, profile.weather),
        "Write a one-liner for a {} {} enjoying {} weather in the urban setting of {}".format(
            profile.ageGroup, profile.gender, profile.weather, profile.cityName),
        "You're hosting a comedy show for {} {} residents of {} on a {} day. Prepare a joke".format(
            profile.ageGroup, profile.gender, profile.cityName, profile.weather),
        "Create a joke that's relatable to a {} {} experiencing {} weather in the city of {}".format(
            profile.ageGroup, profile.gender, profile.weather, profile.cityName),
        "As an AI comedian, your task is to come up with a joke that captures the essence of {}'s {} day for {} {}".format(
            profile.cityName, profile.weather, profile.ageGroup, profile.gender),
        "Write a humorous line that would make a {} {} smile during {} weather in the urban environment of {}".format(
            profile.ageGroup, profile.gender, profile.weather, profile.cityName)
    ]
    random_joke = random.choice(jokeInitializer)
    # Propmt for the AI
    prompt = "User: {}. The Joke must me relateable to the person, place and weather.\nAI:".format(
        random_joke)
    authorization = '{} {}'.format('Bearer ', api_key)

    # Getting AI Response
    # Define the headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': authorization
    }

    # Define the API endpoint URL
    url = 'https://api.openai.com/v1/completions'

    # Define the request payload
    payload = {
        "model": "text-davinci-003",
        "prompt": prompt,
        "temperature": 0.7,
        "max_tokens": 100,
        "n": 1,
        "stop": None
    }

    # Start Time
    start_time = time.time()
    # Send the POST request
    response = requests.post(url, headers=headers, json=payload)
    # End Time
    end_time = time.time()
    response_time = end_time - start_time

    # Check the response status code
    if response.status_code == 200:
        response_json = response.json()
        # Handle the response as needed (e.g., extract the generated joke)
        generated_joke = response_json['choices'][0]['text']
        # print("\nGenerated Joke - {}:".format(prompt), generated_joke)
        return {
            "user num": user_no,
            "req num": request_no,
            "status_code": 200,
            "prompt": random_joke,
            "joke": generated_joke,
            "response_time": response_time,
            "api_call_time": datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            # "response": response_json
        }
    else:
        print(f'Error: {response.status_code}')
        response_json = response.json()
        return {
            "user num": user_no,
            "req num": request_no,
            "status_code": response.status_code,
            "prompt": random_joke,
            "joke": None,
            "response_time": response_time,
            "api_call_time": datetime.utcfromtimestamp(start_time).strftime('%Y-%m-%d %H:%M:%S')
            # "response": response_json
        }


# Create a load testing function with concurrent user and data that returns all types of reports
# Define the number of concurrent users and requests per user
concurrent_users = 5  # Number of concurrent users
requests_per_user = 1  # Number of requests per user

# Function to simulate concurrent users


def simulate_users(concurrent_users, requests_per_user):
    
    all_responses = []

    with concurrent.futures.ThreadPoolExecutor(max_workers=concurrent_users) as executor:
        futures = []
        for user_no in range(concurrent_users):
            for request_no in range(requests_per_user):
                future = executor.submit(call_api, user_no, request_no)
                futures.append(future)

        # Wait for all futures to complete
        concurrent.futures.wait(futures)

        # Collect results
        for future in futures:
            response = future.result()
            all_responses.append(response)

    return all_responses


# Streamlit app
st.title("JOKE API Load Testing and Reporting App")

# Load testing configuration
concurrent_users = st.number_input(
    "Concurrent Users", min_value=1, max_value=100, value=5)
requests_per_user = st.number_input(
    "Requests Per User", min_value=1, max_value=100, value=1)

# Start load testing
if st.button("Start Load Testing"):
    st.text("Load testing in progress...")
    responses = simulate_users(concurrent_users, requests_per_user)

    # Generate a DataFrame for the responses
    df = pd.DataFrame.from_dict(responses, orient='columns')  # type: ignore

    # Calculate statistics
    num_successful_requests = df[df['status_code'] == 200].shape[0]
    num_failed_requests = df[df['status_code'] != 200].shape[0]
    success_rate = (num_successful_requests /
                    (num_successful_requests + num_failed_requests)) * 100

    st.text(f"Load testing completed.")
    st.write(f"Successful requests: {num_successful_requests}")
    st.write(f"Failed requests: {num_failed_requests}")
    st.write(f"Success rate: {success_rate:.2f}%")

    # Calculate response time statistics
    response_times = [response['response_time']
                      for response in responses if response['status_code'] == 200]
    average_response_time = sum(response_times) / len(response_times)
    min_response_time = min(response_times)
    max_response_time = max(response_times)

    st.write(f"Average Response Time: {average_response_time:.2f} seconds")
    st.write(f"Minimum Response Time: {min_response_time:.2f} seconds")
    st.write(f"Maximum Response Time: {max_response_time:.2f} seconds")

    # Create a DataFrame for response times
    df_response_times = pd.DataFrame({
        'Timestamp': [datetime.now() - timedelta(seconds=(len(response_times) - i)) for i in range(len(response_times))],
        'Response Time (s)': response_times
    })
    st.subheader("Response Time Graph")
    st.line_chart(df_response_times.set_index('Timestamp'))

    # Generate and display charts
    st.subheader("Response Status Distribution")
    status_counts = df['status_code'].value_counts()
    st.bar_chart(status_counts)
    st.subheader("Prompts and Responses Details")
    st.table(df)
    # Option to download the report
    # Define a button to generate and download the PDF
    if st.button("Generate PDF Report"):
        # Create a temporary directory
        temp_dir = tempfile.mkdtemp()

        # Define the HTML file path
        html_file_path = os.path.join(temp_dir, "streamlit_report.html")

        # Write the Streamlit app's HTML content to the HTML file
        with open(html_file_path, "w", encoding="utf-8") as html_file:
            html_file.write(st._repr_html())  # type: ignore # Capture Streamlit app's HTML content

        # Define the PDF file path
        pdf_file_path = os.path.join(temp_dir, "report.pdf")

        # Define the PDF options
        pdf_options = {
            "quiet": "",
            "page-size": "A4",
            "disable-smart-shrinking": "",
        }

        # Generate the PDF from the HTML content
        pdfkit.from_file(html_file_path, pdf_file_path, options=pdf_options)

        # Provide a download link for the generated PDF
        with open(pdf_file_path, "rb") as pdf_file:
            st.download_button("Download PDF Report", pdf_file, key="pdf")

        # Cleanup temporary files and directory
        os.remove(html_file_path)
        os.remove(pdf_file_path)
        os.rmdir(temp_dir)

# Optionally, display additional charts or data as needed
