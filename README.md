# ICU-Patients-Projection

We have implemented the Machine learning model which predicts the Patients ICU admission prediction, Length of stay and Discharge prediction from ICU and visualised the predictions in the React web application.
This standalone ICU prediction system is designed with flexibility, making it easy to integrate as a component within the e-hospital website. By using the React framework for the frontend and a Flask API with Python for the backend, it ensures seamless data flow and interaction between the system and infrastructure. The system’s modular design makes the future integration process simpler, enabling the e-hospital website to access and display critical patient predictions with minimal setup. This makes it an ideal solution for enhancing the e-hospital website’s functionality without disrupting existing services.

**Backend api in ehospital/backend**
Within the ehospital folder, the backend folder has two subfolders mlmodel which stores the trained models and prediction folder has the three scripts which take the raw data of patients based on patient ID and apply preprocessing and the saved model to give the final predictions.
"app.py" - This Flask API fetches patient details and predictions by running external Python scripts for admission, discharge, and length of stay (LOS), combining their outputs with data from a JSON file. It retrieves the relevant patient data based on a patient_id provided as a query parameter in the /get_patient_data endpoint. The API integrates script outputs and static info, returning a structured JSON response with original and predicted values.


**Frontend codebase in ehospital/src-**
The HomePage.js React component allows ehospital users to search for a patient's data by entering their Patient ID. It fetches data from the app.py backend API, handles errors, and displays detailed patient information (e.g., age, gender, diagnosis) and ICU predictions (e.g., admission location, length of stay). ![image](https://github.com/user-attachments/assets/09ee4867-8942-4e77-be11-ccd36a6cd71e)


NOTE - The trained ML models are very large files so they have been uploaded as a zip folder.
