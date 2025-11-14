# DataOrigin Package

This package provides core utilities for the DataOrigin project, focusing on leveraging AI-driven data insights for sales prospecting and lead generation in the B2B event space.

## Installation

To install the `dataorigin` package, you can use pip:

```bash
pip install dataorigin
```

## Usage

Example usage for `google_sheets.py` (assuming you have configured credentials):

```python
from dataorigin.google_sheets import GoogleSheetsConnector

# Initialize the connector (requires GOOGLE_SHEETS_CREDENTIALS_PATH environment variable)
connector = GoogleSheetsConnector()

# Example: Read data from a spreadsheet
spreadsheet_id = "YOUR_SPREADSHEET_ID"
data = connector.read_sheet_data(spreadsheet_id)
print(data)

# Example: Write data to a spreadsheet
# Los datos se deben presentar en formato DataFrame de pandas
df = pd.DataFrame([{"a": 1, "b": 2}, {"a": 3, "b": 4}])

res = upsert_google_sheet(
    df=df,
    spreadsheet_id="YOUR_SPREADSHEET_ID",           # o usa spreadsheet_nombre="..."
    sheet_name="data", # Crea o modifica la hoja
    folder_id=os.getenv("GDRIVE_FOLDER_ID"), # OPCIONAL
    clear=True,
    value_input_option="USER_ENTERED"              # RAW o USER_ENTERED
)
```

## License

This project is licensed under the GNU General Public License v3.0 - see the `LICENSE` file for details.
