import json
import pandas as pd
import numpy as np
import re
from sklearn.preprocessing import LabelEncoder, StandardScaler
import category_encoders as ce
from joblib import load
from sklearn.impute import SimpleImputer


def preprocess_and_predict(test_data_path, model_path):
    # Load test data
    test_data = pd.read_csv(test_data_path)
    
    # Save 'patient_id' before dropping columns
    patient_ids = test_data['patient_id']
    
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
    
    # Drop ADMISSION_TYPE and Firstcareunit
    test_data = test_data.drop(columns=['ADMISSION_TYPE','FIRST_CAREUNIT'], axis='columns')
    
    DF_2 = test_data.copy()

    # Function to categorize the discharge location
    def categorize_discharge(location):
        if location in ['HOME', 'HOME HEALTH CARE']:
            return 'HOME'
        elif location == 'REHAB/DISTINCT PART HOSP':
            return 'REHAB'
        elif location == 'LONG TERM CARE HOSPITAL':
            return 'LONG TERM CARE FACILITY'
        else:
            return 'OTHERS'

    # Applying the mapping to the DISCHARGE_LOCATION
    DF_2['DISCHARGE_LOCATION'] = DF_2['DISCHARGE_LOCATION'].apply(categorize_discharge)
   
    # Save the original target for comparison
    original_discharge_location = DF_2['DISCHARGE_LOCATION'].copy()
    
    # Reducing distinct values for ETHNICITY as few values are dominant
    DF_2.loc[DF_2['ETHNICITY']!='WHITE','ETHNICITY']='NON-WHITE'

    # One-hot encoding
    DF_2 = pd.get_dummies(
        test_data,
        columns=[
            'INSURANCE', 'GENDER','LAST_CAREUNIT', 'ICD9_CATEGORY', 'ETHNICITY', 'ADMISSION_LOCATION'
        ],
        dtype=int
    )
    
    # Base-N encoding for DIAGNOSIS
    encoder = ce.BaseNEncoder(cols=['DIAGNOSIS'], base=4)
    diagnosis_encoded = encoder.fit_transform(DF_2['DIAGNOSIS'])
    DF_2 = pd.concat([DF_2.drop(columns=['DIAGNOSIS']), diagnosis_encoded], axis=1)
    
    label_encoder = LabelEncoder()
    DF_2['DISCHARGE_LOCATION'] = label_encoder.fit_transform(DF_2['DISCHARGE_LOCATION'])

    # Impute missing values in DF_2
    imputer = SimpleImputer(strategy='mean')
    DF_2 = pd.DataFrame(imputer.fit_transform(DF_2), columns=DF_2.columns)


    # Align test data columns with model's training data
    model = load(model_path)
    model_columns = model.feature_names_in_
    DF_2 = DF_2.reindex(columns=model_columns, fill_value=0)

    # Make predictions
    predictions = model.predict(DF_2)
    predicted_categories = label_encoder.inverse_transform(predictions)
    
    # Combine predictions with original target for comparison
    comparison = pd.DataFrame({
        'patient_id': patient_ids,
        'Original_DISCHARGE_LOCATION': original_discharge_location,
        'Predicted': predicted_categories
    })
    
    # Convert comparison to dictionary with patient_id as the key
    result_dict = comparison.set_index('patient_id').to_dict(orient='index')
    
    return json.dumps(result_dict, indent=4)

if __name__ == "__main__":
    test_data_path = "C:\\ICUPred\\E-self-frontend\\ehospital\\backend\\patient.csv" 
    model_path = "C:\\ICUPred\\E-self-frontend\\ehospital\\backend\\mlmodel\\KNN_classifier_discharge.pkl"  
    result = preprocess_and_predict(test_data_path, model_path)
    print(result)
