import React, { useState } from 'react';
import Header from './Header'; 

function DiagnosisPage() {
  const [patientId, setPatientId] = useState('');
  const [patientData, setPatientData] = useState(null);
  const [error, setError] = useState(null);

  // Fetch patient data when a patientId is entered
  const fetchPatientData = async () => {
    if (!patientId) {
      alert("Please enter a Patient ID.");
      return;
    }

    try {
      const response = await fetch(`https://your-api-url.com/patient/${patientId}`);
      const data = await response.json();
      
      if (response.ok) {
        setPatientData(data); // Store patient data
        setError(null);  // Reset error state
      } else {
        setPatientData(null);  // Clear previous data
        setError(data.error || "Error fetching patient data.");
      }
    } catch (err) {
      setPatientData(null);  // Clear previous data
      setError("Failed to fetch patient data. Please try again.");
    }
  };

  return (
    <div>
      <Header /> {/* Add the Header component */}
      <div style={{ padding: '20px' }}>
        <h2>Diagnosis Page</h2>
        <input
          type="text"
          placeholder="Enter Patient ID"
          value={patientId}
          onChange={(e) => setPatientId(e.target.value)}
        />
        <button onClick={fetchPatientData}>Search</button>

        {error && <div style={{ color: 'red' }}>{error}</div>}

        {patientData && (
          <div>
            <h3>Patient Details</h3>
            <p><strong>Age:</strong> {patientData.age}</p>
            <p><strong>Ethnicity:</strong> {patientData.ethnicity}</p>
            <p><strong>Gender:</strong> {patientData.gender}</p>
            <p><strong>Diagnosis:</strong> {patientData.diagnosis}</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default DiagnosisPage;
