# MedCare Chatbot – Medication Assistant Module

This folder contains the chatbot module for the MedCare system. It is built using Flask and JSON-based NLP. The chatbot handles patient queries, medication schedules, and basic first-aid responses.

## Features
- Add medicines with timing  
- Retrieve next dose  
- Show patient profile  
- Show age, gender, and contact  
- List all patient profiles  
- Count total patients  
- Provide basic first-aid responses (cough, cold, fever, headache, burns, cuts, stomach pain)

Integration Notes

Replace database.json operations with real database queries when integrating with the main project backend.

The /chat endpoint should remain the same for frontend compatibility.

The module connects to data tables represented in the ER diagram: users, patient_profile, prescriptions, and prescription_medicines.
