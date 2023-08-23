import subprocess
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

# Function to run Locust in a subprocess
def run_locust(num_users, hatch_rate, host):
    cmd = f"locust -f locustfile.py --no-web -c {num_users} -r {hatch_rate} --host={host}"
    process = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode(), stderr.decode()

# Function to parse Locust CSV report and return as DataFrame
def parse_locust_csv(report_path):
    try:
        df = pd.read_csv(report_path)
        return df
    except Exception as e:
        st.error(f"Error parsing CSV: {e}")
        return None

# Streamlit UI
st.title("API Load Tester")

# User input for load test parameters
num_users = st.number_input("Number of Users:", min_value=1, step=1)
hatch_rate = st.number_input("Hatch Rate:", min_value=1, step=1)
host = st.text_input("Host (e.g., https://example.com):")

if st.button("Start Load Test"):
    st.text("Running Load Test... (Check the terminal for progress)")

    # Run Locust in a subprocess
    stdout, stderr = run_locust(num_users, hatch_rate, host)

    st.text("Load Test Completed.")
    st.subheader("Results:")

    # Save the results to a temporary file
    with open("load_test_results.txt", "w") as f:
        f.write(stdout)

    st.success("Results saved temporarily. You can download the detailed report below.")

    # Parse Locust CSV report
    df = parse_locust_csv("locust_stats.csv")

    if df is not None:
        # Display summary statistics
        st.subheader("Summary Statistics:")
        st.write(df.describe())

        # Create a line chart for response times
        st.subheader("Response Times (in ms):")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.plot(df['Timestamp'], df['Response Time'], marker='o', linestyle='-')
        ax.set_xlabel("Timestamp")
        ax.set_ylabel("Response Time (ms)")
        st.pyplot(fig)

        # Create a bar chart for the number of requests
        st.subheader("Number of Requests:")
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.bar(df['Name'], df['Request Count'])
        ax.set_xlabel("Endpoint")
        ax.set_ylabel("Request Count")
        ax.tick_params(axis='x', rotation=45)
        st.pyplot(fig)

        # Save detailed report as a CSV
        df.to_csv("load_test_detailed_report.csv", index=False)

        # Provide a download link for the detailed report
        csv_report_data = df.to_csv(index=False)
        csv_report_bytes = csv_report_data.encode()
        st.download_button(
            label="Download Detailed Report",
            data=csv_report_bytes,
            file_name="load_test_detailed_report.csv",
            key="download_detailed_report"
        )
    else:
        st.error("Failed to parse the Locust CSV report.")

# Clean up temporary files
if st.button("Clean Up"):
    subprocess.run("rm load_test_results.txt locust_stats.csv load_test_detailed_report.csv", shell=True)
    st.success("Temporary files removed.")
