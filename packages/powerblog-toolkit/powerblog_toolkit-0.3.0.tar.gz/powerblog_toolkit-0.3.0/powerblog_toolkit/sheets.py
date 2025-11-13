import gspread
from gspread_dataframe import set_with_dataframe, get_as_dataframe

def save_to_sheet(gc, file_name, sheet_name, df):
    """
    Saves a DataFrame to a Google Sheet tab.
    If the sheet exists → clears and overwrites it.
    If it doesn't exist → creates it automatically.
    """
    sh = gc.open(file_name)

    try:
        ws = sh.worksheet(sheet_name)
        ws.clear()
        print(f"🧾 Overwriting existing sheet: {sheet_name}")
    except Exception:
        print(f"✨ Sheet '{sheet_name}' not found. Creating new one...")
        ws = sh.add_worksheet(title=sheet_name, rows=str(len(df) + 10), cols=str(len(df.columns) + 5))

    set_with_dataframe(ws, df)
    print(f"✅ Data written to sheet: {sheet_name} ({df.shape[0]} rows)")
