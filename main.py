import os
import pandas as pd
import openai
from flask import Flask, request, jsonify
from dotenv import load_dotenv
import io

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

# Endpoint to accept CSV and analyze it using ChatGPT
@app.route('/api/data', methods=['POST'])
def analyze_csv():
    print("Request received")
    print("Request method:", request.method)
    print("Request headers:", request.headers)
    print("Request files:", request.files)
    print("Request form:", request.form)
    print("Request data:", request.data)

    # Check if a file is uploaded
    if 'file' not in request.files:
        print("No file part in the request")
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        print("No selected file")
        return jsonify({'error': 'No selected file'}), 400

    print("File received:", file.filename)

    # Read CSV file into a pandas DataFrame
    try:
        # Use StringIO to create a file-like object from the uploaded file
        csv_data = io.StringIO(file.stream.read().decode("UTF8"), newline=None)
        df = pd.read_csv(csv_data)
        print("CSV data read successfully")
    except Exception as e:
        print(f"Error reading CSV: {str(e)}")
        return jsonify({'error': f'Error reading CSV: {str(e)}'}), 400

    # Convert DataFrame to JSON format
    data_json = df.to_json(orient='records')

    # Use OpenAI API (ChatGPT) to analyze the CSV data
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Specify the model to use (e.g., "gpt-4")
            messages=[
                {"role": "system", "content": "You are a data analyst. Analyze the given sales data and provide insights."},
                {"role": "user", "content": f"Analyze the following sales dataset and provide key insights: {data_json}"}
            ]
        )

        # Extract the analysis response
        analysis = response['choices'][0]['message']['content']
        print("Analysis completed successfully")
    except Exception as e:
        print(f"OpenAI API error: {str(e)}")
        return jsonify({'error': f'OpenAI API error: {str(e)}'}), 500

    # Return the dataset and the analysis in JSON format
    return jsonify({'data': data_json, 'analysis': analysis})

if __name__ == '__main__':
    app.run(debug=True)