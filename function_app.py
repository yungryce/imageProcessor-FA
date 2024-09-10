import azure.functions as func
from azure.storage.blob import BlobServiceClient
from azure.identity import DefaultAzureCredential
import logging
from PIL import Image
from io import BytesIO


# Retrieve the connection string from environment variables
# CONNECTION_STRING = os.getenv('AzureWebJobsStorage')
# Use Managed Identity for authentication
credential = DefaultAzureCredential()

CONTAINER_NAME = 'image-files'

# Compress Image Function
def compress_image(image_bytes):
    """Compress the uploaded image."""
    try:
        image = Image.open(BytesIO(image_bytes))
    except Exception as e:
        logging.error(f"Error opening image: {e}")
        raise ValueError("Cannot open image file")
    
    output_io = BytesIO()
    image.save(output_io, format='JPEG', quality=85)  # Compress image to 85% quality
    output_io.seek(0)
    return output_io

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


# Azure Function v2.0 with HTTP trigger and Blob output binding
@app.route(route="upload-image")  # HTTP Trigger
# @app.blob_output(arg_name="output_blob", path=f"{CONTAINER_NAME}/compressed_{blob_name}", connection="AzureWebJobsStorage")
def upload_image(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get uploaded image
        image_data = req.files['file'].read()
        
        # Compress the image
        compressed_image = compress_image(image_data)

        # Generate dynamic blob name
        blob_name = f"{req.files['file'].filename}"
        
        # Upload compressed image to Blob Storage
        # output_blob.set(compressed_image)

        # Upload compressed image to Blob Storage using connection string
        # blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

        # Initialize BlobServiceClient with Managed Identity
        blob_service_client = BlobServiceClient(account_url=f"https://imageappbcd4.blob.core.windows.net", credential=credential)

        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=blob_name)
        blob_client.upload_blob(compressed_image, overwrite=True)

        logging.info('Compressed image uploaded to blob storage successfully')
        return func.HttpResponse(f"Image '{req.files['file'].filename}' compressed and uploaded successfully.", status_code=200)
    except Exception as e:
        logging.error(f"Error processing image: {e}")
        return func.HttpResponse("Failed to process image.", status_code=500)


# Function to fetch image from blob storage and return it to the user
@app.route(route="get-image/{image}", methods=[func.HttpMethod.GET])  # HTTP Trigger
def get_image(req: func.HttpRequest) -> func.HttpResponse:
    try:
        image_name = req.route_params.get('image')
        # Initialize BlobServiceClient using connection string
        # blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

        # Initialize BlobServiceClient with Managed Identity
        blob_service_client = BlobServiceClient(account_url=f"https://imageappbcd4.blob.core.windows.net", credential=credential)

        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=image_name)
        
        # Download blob content
        download_stream = blob_client.download_blob()
        image_bytes = download_stream.readall()

        # Return the image as an HTTP response
        return func.HttpResponse(body=image_bytes, mimetype="image/jpeg", status_code=200)
    
    except Exception as e:
        logging.error(f"Error fetching image '{image_name}': {e}")
        return func.HttpResponse(f"Failed to fetch image '{image_name}'.", status_code=404)