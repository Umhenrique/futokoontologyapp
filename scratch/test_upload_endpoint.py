import os
import requests

url = "http://127.0.0.1:5000/api/upload_pdf"
pdf_path = r"testes/Student_Understanding_Model_Sheet_Fillable.pdf"

print(f"Testing upload endpoint with: {pdf_path}")
if not os.path.exists(pdf_path):
    print(f"Error: {pdf_path} does not exist.")
    exit(1)

try:
    with open(pdf_path, 'rb') as f:
        files = {'file': f}
        r = requests.post(url, files=files)
        print(f"Status Code: {r.status_code}")
        print("Response JSON:")
        print(r.json())
except Exception as e:
    print(f"Requests failed: {e}")
    # Try using manual urllib if requests fails
    print("Trying with urllib...")
    import urllib.request
    import uuid

    boundary = uuid.uuid4().hex
    headers = {'Content-Type': f'multipart/form-data; boundary={boundary}'}
    
    with open(pdf_path, 'rb') as f:
        file_content = f.read()
        
    body = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="file"; filename="test.pdf"\r\n'
        f"Content-Type: application/pdf\r\n\r\n"
    ).encode('utf-8') + file_content + f"\r\n--{boundary}--\r\n".encode('utf-8')
    
    req = urllib.request.Request(url, data=body, headers=headers, method='POST')
    try:
        with urllib.request.urlopen(req) as response:
            html = response.read().decode('utf-8')
            print(f"Urllib Status Code: {response.status}")
            print("Response:")
            print(html)
    except Exception as ex:
        print(f"Urllib also failed: {ex}")
