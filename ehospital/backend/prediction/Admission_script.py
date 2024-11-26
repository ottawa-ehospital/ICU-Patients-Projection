import json
import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import LabelEncoder, StandardScaler
import category_encoders as ce
from joblib import load

def preprocess_and_predict(test_data_path, model_path):
    # Load test data
    test_data = pd.read_csv(test_data_path)
    
    # Save the patient_id 
    patient_ids = test_data['patient_id']
    
    # Save the original target for comparison
    original_admission_location = test_data['ADMISSION_LOCATION'].copy()
    
    # Drop irrelevant columns
    columns_to_drop = [
        'patient_id', 'HADM_ID', 'ICUSTAY_ID', 'DBSOURCE', 'LANGUAGE',
        'RELIGION', 'FIRST_WARDID', 'LAST_WARDID', 'MARITAL_STATUS',
        'DOD_SSN', 'DEATHTIME', 'HOSPITAL_EXPIRE_FLAG', 'EDREGTIME',
        'EDOUTTIME', 'DOD'
    ]
    test_data = test_data.drop(columns=columns_to_drop, axis='columns')
    
    # Add 'DIED_IN_HOSPITAL' feature
    test_data['DIED_IN_HOSPITAL'] = test_data['DOD_HOSP'].notnull().astype(int)
    test_data = test_data.drop(columns=['DOD_HOSP'], axis='columns')
    
    # Add 'LOS_in_Hospital' feature
    test_data['ADMITTIME'] = pd.to_datetime(test_data['ADMITTIME'])
    test_data['DISCHTIME'] = pd.to_datetime(test_data['DISCHTIME'])
    test_data['LOS_in_Hospital'] = (test_data['DISCHTIME'] - test_data['ADMITTIME']).dt.days
    test_data = test_data.drop(columns=['ADMITTIME', 'DISCHTIME', 'INTIME', 'OUTTIME', 'DOB'], axis='columns')
    
    # Transform ICD9_CODE
    def transform_function(value):
        value = str(value)
        value = re.sub("V[0-9]*", "0", value)
        value = re.sub("E[0-9]*", "0", value)
        return value
    
    def transform_category(value):
        try:
            value = int(value)
        except:
            return 'Other'
        
        if (390 <= value <= 459) or value == 785:
            category = 'Circulatory'
        elif (460 <= value <= 519) or value == 786:
            category = 'Respiratory'
        elif (520 <= value <= 579) or value == 787:
            category = 'Digestive'
        elif value == 250:
            category = 'Diabetes'
        elif 800 <= value <= 999:
            category = 'Injury'
        elif 710 <= value <= 739:
            category = 'Musculoskeletal'
        elif (580 <= value <= 629) or value == 788:
            category = 'Genitourinary'
        elif 140 <= value <= 239:
            category = 'Neoplasms'
        else:
            category = 'Other'
        
        return category
    
    test_data['ICD9_CODE'] = test_data['ICD9_CODE'].apply(transform_function)
    test_data['ICD9_CATEGORY'] = test_data['ICD9_CODE'].apply(transform_category)
    test_data = test_data.drop(columns=['ICD9_CODE'], axis='columns')
    
    # Standardize features
    scaler = StandardScaler()
    test_data[['LOS', 'SEQ_NUM', 'LOS_in_Hospital']] = scaler.fit_transform(
        test_data[['LOS', 'SEQ_NUM', 'LOS_in_Hospital']]
    )
    
    # Drop ADMISSION_TYPE
    test_data = test_data.drop(columns=['ADMISSION_TYPE'], axis='columns')
    
    # One-hot encoding
    test_data = pd.get_dummies(
        test_data,
        columns=[
            'DISCHARGE_LOCATION', 'INSURANCE', 'GENDER', 'FIRST_CAREUNIT',
            'LAST_CAREUNIT', 'ICD9_CATEGORY', 'ETHNICITY', 'ADMISSION_LOCATION'
        ],
        dtype=int
    )
    
    # Base-N encoding for DIAGNOSIS
    encoder = ce.BaseNEncoder(cols=['DIAGNOSIS'], base=4)
    diagnosis_encoded = encoder.fit_transform(test_data['DIAGNOSIS'])
    test_data = pd.concat([test_data.drop(columns=['DIAGNOSIS']), diagnosis_encoded], axis=1)
    
    # Align test data columns with model's training data
    model = load(model_path)
    model_columns = model.get_booster().feature_names
    test_data = test_data.reindex(columns=model_columns, fill_value=0)
    
    # Make predictions
    predictions = model.predict(test_data)
    
    # Combine predictions with original target for comparison
    comparison_dict = {
        patient_id: {
            "Original_ADMISSION_LOCATION": original_location,
            "Predicted": "Admitted to ICU" if prediction == 1 else "Not admitted to ICU"
        }
        for patient_id, original_location, prediction in zip(
            patient_ids, original_admission_location, predictions
        )
    }
    return json.dumps(comparison_dict, indent=4)

if __name__ == "__main__":
    test_data_path = "C:\\ICUPred\\E-self-frontend\\ehospital\\backend\\patient.csv" 
    model_path = "C:\\ICUPred\\E-self-frontend\\ehospital\\backend\\mlmodel\\xgadmissionmodel3.joblib"  
    result = preprocess_and_predict(test_data_path, model_path)
    print(result)

