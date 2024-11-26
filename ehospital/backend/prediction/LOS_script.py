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
    
    # Save the patient_id to use as keys in the output dictionary
    patient_ids = test_data['patient_id'].copy()
    
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
    
    DF_1 = test_data.copy()

    # Defining the bin edges
    bins = [0, 1, 5, 10, 20, 50, np.inf]
    labels = ['0-1', '1-5', '5-10', '10-20', '20-50', '50+']
    DF_1['LOS_Binned'] = pd.cut(DF_1['LOS'], bins=bins, labels=labels)

    # Save the original target for comparison
    original_LOS = DF_1['LOS_Binned'].copy()
    
    columns_to_drop = ['LOS']
    DF_1 = DF_1.drop(columns=columns_to_drop)

    # Standardize features
    scaler = StandardScaler()
    DF_1[['SEQ_NUM', 'LOS_in_Hospital']] = scaler.fit_transform(
        DF_1[['SEQ_NUM', 'LOS_in_Hospital']]
    )
    
    # Drop ADMISSION_TYPE
    DF_1 = DF_1.drop(columns=['ADMISSION_TYPE'], axis='columns')
    
    DF_1.loc[DF_1['ETHNICITY'] != 'WHITE', 'ETHNICITY'] = 'NON-WHITE'
    DF_1.loc[DF_1['ADMISSION_LOCATION'] != 'EMERGENCY ROOM ADMIT', 'ADMISSION_LOCATION'] = 'NO EMERGENCY ROOM ADMIT'

    # One-hot encoding
    DF_1 = pd.get_dummies(
        DF_1,
        columns=[
            'DISCHARGE_LOCATION', 'INSURANCE', 'GENDER', 'FIRST_CAREUNIT',
            'LAST_CAREUNIT', 'ICD9_CATEGORY', 'ETHNICITY', 'ADMISSION_LOCATION'
        ],
        dtype=int
    )
    
    # Base-N encoding for DIAGNOSIS
    encoder = ce.BaseNEncoder(cols=['DIAGNOSIS'], base=4)
    diagnosis_encoded = encoder.fit_transform(DF_1['DIAGNOSIS'])
    DF_1 = pd.concat([DF_1.drop(columns=['DIAGNOSIS']), diagnosis_encoded], axis=1)
    
    label_encoder = LabelEncoder()
    DF_1['LOS_Binned'] = label_encoder.fit_transform(DF_1['LOS_Binned'])

    # Align test data columns with model's training data
    model = load(model_path)
    model_columns = model.feature_names_in_
    DF_1 = DF_1.reindex(columns=model_columns, fill_value=0)

    # Make predictions
    predictions = model.predict(DF_1)
    
    # Use predefined labels for inverse transformation
    labels = ['0-1', '1-5', '5-10', '10-20', '20-50', '50+']
    predictions = np.clip(predictions, 0, len(labels) - 1)  
    
    # Convert predictions back to the original bins
    predicted_labels = [labels[i] for i in predictions]    
    
    # Prepare the dictionary output
    output_dict = {}
    for idx, patient_id in enumerate(patient_ids):
        output_dict[patient_id] = {
            'Original_LOS': original_LOS.iloc[idx],
            'Predicted': predicted_labels[idx]
        }
    return json.dumps(output_dict, indent=4)

if __name__ == "__main__":
    test_data_path = "C:\\ICUPred\\E-self-frontend\\ehospital\\backend\\patient.csv" 
    model_path = "C:\\ICUPred\\E-self-frontend\\ehospital\\backend\\mlmodel\\KNN_classifier_LOS.pkl"  
    result = preprocess_and_predict(test_data_path, model_path)
    print(result)