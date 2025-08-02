import pandas as pd
# Add your other imports here

def generate_dataframe():
"""
Extract your dataframe creation logic from Turnus.py into this function
This will be used by both Streamlit and the email script
"""
# Copy your dataframe creation code from Turnus.py here
# For example:

# df = pd.read_csv('your_data.csv')
# df = df.groupby('column').sum()
# df = df.sort_values('some_column', ascending=False)

# Return your processed dataframe
return df

def format_dataframe_for_email(df):
"""
Format dataframe for email (HTML table or text)
"""
# Option 1: HTML table (nicer formatting)
html_table = df.to_html(index=False, table_id="weekly-report")

# Option 2: Plain text (simpler)
text_table = df.to_string(index=False)

return html_table, text_table
