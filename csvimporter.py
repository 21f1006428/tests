from flask import Flask, request, jsonify, render_template
import traceback
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from gspread_dataframe import set_with_dataframe

app = Flask(__name__)

# Define the Google Sheets API client with explicit credentials
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
json_keyfile_path = 'sheets-400705-3eea117bda5e.json'  # Replace with the path to your JSON key file

creds = ServiceAccountCredentials.from_json_keyfile_name(json_keyfile_path, scope)
client = gspread.authorize(creds)

# Function to create a new Google Sheets spreadsheet
def create_spreadsheet(title):
    gc = gspread.service_account(filename=json_keyfile_path)
    spreadsheet = gc.create(title)
    return spreadsheet

# Function to share the worksheet with anyone with the link and provide edit access
def share_worksheet(spreadsheet):
    spreadsheet.share('', perm_type='anyone', role='writer', with_link=True)

@app.route('/', methods=['GET'])
def index():
    return render_template('import.html')

@app.route('/import', methods=['POST'])
def import_to_google_sheets():
    try:
        # Get selected columns from the frontend
        selected_columns = request.form.getlist('columns')
        ll = selected_columns[0].split(',')
        selected_columns = ll

        # Get the uploaded CSV file from the request
        uploaded_file = request.files['file']
        if not uploaded_file:
            return jsonify({'error': 'No file uploaded'})

        # Read CSV data into a DataFrame
        df = pd.read_csv(uploaded_file)

        # Create a new Google Sheets worksheet
        spreadsheet_name = 'My_Spreadsheet'  # Replace with your desired spreadsheet title
        spreadsheet = create_spreadsheet(spreadsheet_name)
        worksheet = spreadsheet.get_worksheet(0)

        # Filter DataFrame to include only selected columns
        df = df[selected_columns]

        # Write DataFrame to Google Sheets
        set_with_dataframe(worksheet, df)

        # Get the URL of the worksheet
        worksheet_url = spreadsheet.url
        print(spreadsheet.url)
        # Share the worksheet with anyone with the link and provide edit access
        share_worksheet(spreadsheet)

        return jsonify({'success': 'Data imported to ', 'worksheet_url': worksheet_url})

    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)
