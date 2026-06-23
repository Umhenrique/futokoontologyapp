import requests
import pypdf
import os

url = "http://127.0.0.1:5000/api/download_fillable"
output_path = "scratch/downloaded_fillable_test.pdf"

print(f"Testing download endpoint: {url}")
try:
    r = requests.get(url)
    print(f"Status Code: {r.status_code}")
    if r.status_code == 200:
        with open(output_path, "wb") as f:
            f.write(r.content)
        print(f"Saved downloaded file to: {output_path}")
        size = os.path.getsize(output_path)
        print(f"File size: {size} bytes")
        
        # Verify it is a valid PDF and has fields
        reader = pypdf.PdfReader(output_path)
        fields = reader.get_fields()
        print(f"Found {len(fields) if fields else 0} interactive form fields in the downloaded PDF.")
        
        # Clean up
        if os.path.exists(output_path):
            os.remove(output_path)
        print("SUCCESS: Download API verified successfully!")
    else:
        print(f"Error: Response content: {r.text}")
except Exception as e:
    print(f"Test failed: {e}")
