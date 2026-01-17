🧾 Receipt & Invoice Digitizer

An AI-powered web application that automates the extraction, validation, and storage of financial data from receipts and invoices using OCR, Gemini AI, and SQLite.

📌 Project Overview

The Receipt and Invoice Digitizer is designed to eliminate manual data entry involved in managing receipts and invoices. The system converts unstructured financial documents into structured, searchable digital records by combining Optical Character Recognition (OCR) with AI-based data extraction.

It supports receipt uploads in multiple formats, prevents duplicate entries, validates extracted data, and stores records securely in a local database for easy retrieval.

🚀 Features

Upload receipts and invoices (PDF, JPG, JPEG, PNG)

Automatic image preprocessing for better OCR accuracy

OCR-based text extraction using Tesseract

AI-powered structured data extraction using Gemini AI

Duplicate receipt detection

Multi-level data validation

Secure and persistent storage using SQLite

User-friendly Streamlit web interface

View stored receipts and detailed line items

🛠️ Tech Stack

Frontend & UI: Streamlit

OCR Engine: Tesseract OCR

AI Parsing: Gemini API

Backend Logic: Python

Database: SQLite

Image Processing: OpenCV, PIL

PDF Handling: pdf2image

📂 Project Structure
Receipt-and-Invoice-Digitizer/
│
├── app4.py                 # Main Streamlit application
├── upload_module.py        # Upload, preprocessing, OCR flow
├── ocr_utils.py            # OCR & Gemini AI parsing logic
├── storage.py              # Database operations & duplicate handling
├── receipts.db             # SQLite database (auto-created)
├── requirements.txt        # Python dependencies
└── README.md               # Project documentation

🔄 System Workflow

User enters a valid Gemini API key

User uploads a receipt or invoice

Document is preprocessed (resize, denoise, threshold)

OCR extracts raw text from the document

Text is cleaned and normalized

Duplicate detection is performed

Gemini AI extracts structured financial data

Extracted data is validated

Valid data is stored in SQLite database

User views stored receipts and line items

🗄️ Database Design

The system uses a normalized SQLite database:

receipts Table

Stores receipt-level data (vendor, date, total, tax)

Stores cleaned OCR text for duplicate detection

items / line_items Table

Stores individual bill items

Linked to receipts via foreign key

This design ensures data integrity, duplicate prevention, and efficient retrieval.

✅ Validation & Error Handling

AI output schema enforcement via strict JSON prompts

Python-level validation for numeric and mandatory fields

Early duplicate detection using OCR text

Database-level constraints for integrity

Graceful handling of API errors, OCR failures, and invalid inputs