import pandas as pd
import json

# Load the CSV data
data = pd.read_csv('patient.csv')  

# Convert DataFrame to dictionary with patient_id as the key
data_dict = data.set_index('patient_id').to_dict(orient='index')

# Save to JSON
with open('patients_data.json', 'w') as f:
    json.dump(data_dict, f, indent=4)

print(data_dict)
