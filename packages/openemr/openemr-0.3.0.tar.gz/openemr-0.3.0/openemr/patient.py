import requests
import mimetypes
import os

class Patient:
    def __init__(self, client, patient_data):
        self.client = client
        self.data = patient_data
        self.id = patient_data.get('pid')
        self.uuid = patient_data.get('uuid')

    def get_documents(self) -> list:
        """Get all documents for this patient, 404 if no documents are found"""
        api_uri = f"{self.client.api_url}/patient/{self.id}/document?path=/MedicalRecord"
        return self.client._get(api_uri)

    def get_document(self, doc_id, local_path):
        """Download a specific document by ID"""
        api_uri = f"{self.client.api_url}/patient/{self.id}/document/{doc_id}"

        try:
            response = self.client.session.get(api_uri, stream=True)
            response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

            # log headers
            print(f"Headers: {response.headers}")

            # Ensure the directory exists
            os.makedirs(os.path.dirname(local_path), exist_ok=True)

            with open(local_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    # filter out keep-alive new chunks
                    if chunk:
                        f.write(chunk)
            print(f"Document {doc_id} downloaded successfully to {local_path}")
            return local_path

        except requests.exceptions.RequestException as e:
            print(f"Error downloading document {doc_id}: {e}")
            # Re-raise or handle the error as appropriate for your application
            raise
        except IOError as e:
            print(f"Error writing document {doc_id} to {local_path}: {e}")
            # Re-raise or handle the error as appropriate
            raise

    def post_document(self, source_document, document_type=None):
        """Post a document for this patient
        
        Args:
            source_document (str): Path to the document file
            document_type (str, optional): MIME type of the document. If None, it will be inferred from the file extension.
        """
        url = f"{self.client.api_url}/patient/{self.id}/document"

        params = {
            "path": "/MedicalRecord"
        }

        headers = {
            # Authorization header is already set on the session; do NOT
            # pre-set Content-Type so that `requests` can add the correct
            # multipart boundary (this was the root of the 500 error).
            "Accept": "application/json",
            "Authorization": f"Bearer {self.client.access_token}",
        }

        if document_type is None:
            document_type = mimetypes.guess_type(source_document)[0] or "application/octet-stream"

        filename = os.path.basename(source_document)

        with open(source_document, 'rb') as f:
            # Prepare the 'files' dictionary for multipart upload
            # Structure: {form_field_name: (filename, file_object, content_type)}
            files = {
                "document": (filename, f, document_type)
            }
            r = requests.post(url, headers=headers, params=params, files=files)

        if r.status_code != 200:
            raise Exception(f"Failed to post document: {r.status_code} {r.text}")
        return r

    def get_encounters(self) -> list:
        """Get all encounters for this patient"""
        return self.client._get(f"{self.client.api_url}/patient/{self.id}/encounter")

    def get_appointments(self) -> list:
        """Get all appointments for this patient"""
        return self.client._get(f"{self.client.api_url}/patient/{self.id}/appointment")

    # Add getter methods to access patient attributes
    def __getattr__(self, name):
        """Allow access to patient data via attributes"""
        if name in self.data:
            return self.data[name]
        raise AttributeError(f"Patient has no attribute '{name}'")