from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse
import shutil
import os
import requests

app = FastAPI()

# Directory for saving uploaded files
UPLOAD_DIRECTORY = "temp_dir"
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

# Dictionary to store file paths by filename
file_paths = {}

# FlowiseAI API URL
API_URL = "http://localhost:3000/api/v1/prediction/39007626-3b04-49bb-83a2-de354bd7f133"

def query_flowiseai(file_path, question):
    """Query FlowiseAI API with the given file and question."""
    try:
        with open(file_path, 'rb') as file:
            files = {'files': file}
            # Send the question in form data
            data = {'question': question}
            response = requests.post(API_URL, files=files, data=data)
            
            # Check if the response status code is OK
            if response.status_code != 200:
                return {"error": f"API returned status code {response.status_code}"}
            
            # Try to parse the response as JSON
            try:
                return response.json()
            except requests.exceptions.JSONDecodeError:
                return {"error": "Invalid JSON response from the API", "content": response.text}
    
    except requests.RequestException as e:
        return {"error": str(e)}


@app.post("/uploadfile/")
async def upload_file(file: UploadFile = File(...)):
    file_location = os.path.join(UPLOAD_DIRECTORY, file.filename)
    
    # Save the uploaded file
    with open(file_location, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Store the file path in memory (for simplicity)
    file_paths[file.filename] = file_location
    
    return JSONResponse(content={"filename": file.filename, "message": "File uploaded successfully"})

@app.post("/askquestion/")
async def ask_question(file_name: str = Form(...), question: str = Form(...)):
    # Validate that file_name and question are provided
    if not file_name or not question:
        raise HTTPException(status_code=422, detail="file_name and question are required")
    
    # Check if the file exists in file_paths
    if file_name not in file_paths:
        raise HTTPException(status_code=404, detail="File not found")
    
    # Retrieve file path
    file_path = file_paths[file_name]
    
    # Query the FlowiseAI API with the file and question
    response = query_flowiseai(file_path, question)
    
    # Process the response and return
    if "error" in response:
        raise HTTPException(status_code=500, detail=response["error"])
    
    return JSONResponse(content={"file_name": file_name, "question": question, "response": response})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
