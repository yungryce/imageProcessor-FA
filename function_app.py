import azure.functions as func
from azure.storage.blob import BlobServiceClient, BlobProperties
import logging
import os
from PIL import Image
from io import BytesIO


# Retrieve the connection string from environment variables
CONNECTION_STRING = os.getenv('AzureWebJobsStorage')

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)

CONTAINER_NAME = 'image-files'
MAX_SIZE_KB = 20

# Compress Image Function
def compress_image(image_bytes, quality=95):
    """Compress the uploaded image and reduce quality if necessary."""
    try:
        image = Image.open(BytesIO(image_bytes))
    except Exception as e:
        logging.error(f"Error opening image: {e}")
        raise ValueError("Cannot open image file")
    
    output_io = BytesIO()

    # Loop to adjust quality until the image is under the specified size
    while True:
        output_io.seek(0)  # Reset buffer
        output_io.truncate()  # Clear the buffer
        image.save(output_io, format='JPEG', quality=quality)
        
        # Calculate current image size
        image_data = output_io.getvalue()
        image_size_kb = len(image_data) / 1024  # Size in KB

        logging.info(f"Current compressed image size: {image_size_kb:.2f} KB with quality {quality}")

        # Break the loop if the image size is below the threshold
        if image_size_kb <= MAX_SIZE_KB or quality <= 10:  # Prevent quality from going below 10
            break
        
        # Decrease quality for the next iteration
        quality -= 5  # Reduce quality by 5 each iteration

    output_io.seek(0)
    return output_io



# Azure Function v2.0 with HTTP trigger and Blob output binding
@app.route(route="upload-image", methods=[func.HttpMethod.POST])  # HTTP Trigger
# @app.blob_output(arg_name="output_blob", path=f"{CONTAINER_NAME}/compressed_{blob_name}", connection="AzureWebJobsStorage")
def upload_image(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Get uploaded image
        image_data = req.files['file'].read()
        
        # Compress the image
        compressed_image = compress_image(image_data)

        # Generate dynamic blob name
        blob_name = f"{req.files['file'].filename}"

        # Upload compressed image to Blob Storage using connection string
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

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
        blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

        blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=image_name)
        
        # Download blob content
        download_stream = blob_client.download_blob()
        image_bytes = download_stream.readall()

        # Return the image as an HTTP response
        return func.HttpResponse(body=image_bytes, mimetype="image/jpeg", status_code=200)
    
    except Exception as e:
        logging.error(f"Error fetching image '{image_name}': {e}")
        return func.HttpResponse(f"Failed to fetch image '{image_name}'.", status_code=404)
