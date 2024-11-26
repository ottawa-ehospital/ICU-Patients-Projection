from flask import Flask, jsonify, request
import subprocess
import json
import os
from flask_cors import CORS

app = Flask(__name__) 
CORS(app)

with open('patients_data.json', 'r') as f:
    data_dict = json.load(f)

def run_script(script_name):
    pt = "C:\\ICUPred\\E-self-frontend\\ehospital\\backend\\prediction\\" + script_name
   
    # script_path = os.path.join(SCRIPTS_DIR, script_name)
    result = subprocess.run(['python', pt], capture_output=True, text=True)
    return json.loads(result.stdout)  

@app.route('/get_patient_data', methods=['GET'])
def get_patient_data():
    # Get the patient_id from the query parameter
    patient_id = request.args.get('patient_id')
    if not patient_id:
        return jsonify({'error': 'Patient ID is required'}), 400
    
    admission_data = run_script('Admission_script.py')
    discharge_data = run_script('Discharge_script.py')
    los_data = run_script('LOS_script.py')  

    print("Admission Data -------", admission_data, type(admission_data))
    print("Discharge Data -------", discharge_data, type(discharge_data))
    print("Loss Data -------", los_data, type(los_data))
   
    # Find the data for the given patient_id
    admission = admission_data.get(patient_id)
    discharge = discharge_data.get(patient_id)
    los = los_data.get(patient_id)

    if admission is None or discharge is None or los is None:
        return jsonify({'error': 'Patient ID not found in the records'}), 404
    patient_info = data_dict.get(patient_id)
    # Return the data in the response
    return jsonify({
        'patient_id': patient_id,
        'original_admission_location': admission.get('Original_ADMISSION_LOCATION'),
        'predicted_admission_location': admission.get('Predicted'),
        'original_discharge_location': discharge.get('Original_DISCHARGE_LOCATION'),
        'predicted_discharge_location': discharge.get('Predicted'),
        'original_los': los.get('Original_LOS'),
        'predicted_los': los.get('Predicted'),
        'age': patient_info.get("Age"),
        'ethnicity': patient_info.get("ETHNICITY"),
        'gender': patient_info.get("GENDER"),
        'diagnosis': patient_info.get("DIAGNOSIS")
    })
 
if __name__ == '__main__':
    app.run(debug=True)