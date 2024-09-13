import streamlit as st
import requests

# FastAPI server URL
FASTAPI_URL = "http://localhost:8000"

def upload_file(file):
    """Upload a file to the FastAPI backend."""
    try:
        response = requests.post(f"{FASTAPI_URL}/uploadfile/", files={"file": file})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

def ask_question(file_name, question):
    """Ask a question to the FastAPI backend."""
    try:
        response = requests.post(f"{FASTAPI_URL}/askquestion/", data={"file_name": file_name, "question": question})
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        return {"error": str(e)}

st.title("File Upload and Question")

# Upload section
st.header("Upload File")
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file:
    st.write("Uploading file...")
    upload_response = upload_file(uploaded_file)
    
    if "error" in upload_response:
        st.error(f"Error uploading file: {upload_response['error']}")
    else:
        st.write(upload_response)
        file_name = upload_response.get("filename")

        if file_name:
            st.session_state.file_name = file_name
        else:
            st.error("File upload failed. Please try again.")

# Chat section
st.header("Ask a Question")
if "file_name" in st.session_state:
    question = st.text_input("Your question:")

    if st.button("Submit"):
        if not question:
            st.error("Please enter a question.")
        else:
            response = ask_question(st.session_state.file_name, question)
            
            if "error" in response:
                st.error(f"Error: {response['error']}")
            else:
                st.write(response)
else:
    st.write("Please upload a file first.")
