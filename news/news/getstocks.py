# myapp/utils.py
import pandas as pd
import json
import os

def generate_symbols_json():
    # Get the directory of the CSV file
    csv_filename = 'MW-NIFTY-50-16-May-2024.csv'
    csv_file_path = os.path.join(os.path.dirname(__file__), csv_filename)

    # Read CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file_path)

    # Extract symbols (first column) from DataFrame
    symbols = df.iloc[:, 0].tolist()

    # Create a dictionary to store symbols
    symbols_dict = {'symbols': symbols}

    # Return the dictionary (JSON data)
    return symbols_dict

# myapp/views.py
from django.http import JsonResponse

def symbols_json(request):
    # Generate JSON data using a utility function (e.g., from CSV file)
    symbols_data = generate_symbols_json()  # Implement this function to generate your JSON data

    # Return JSON response
    return JsonResponse(symbols_data)

