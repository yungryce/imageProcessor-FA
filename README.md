# Azure Function App: Image Upload and Compression

This Azure Function App allows users to upload images, which are then compressed and stored in Azure Blob Storage. Users can also retrieve the compressed images via a provided endpoint.

## Features

- Upload images via HTTP POST requests.
- Compress uploaded images to ensure they do not exceed a specified size.
- Store compressed images in Azure Blob Storage.
- Fetch images from Azure Blob Storage via HTTP GET requests.

## Prerequisites

- An Azure subscription.
- Azure SDK for Python.
- Azure Function App setup.

## Configuration

### Environment Variables

Make sure to set the following environment variables in your Azure Function App configuration:

- **AzureWebJobsStorage**: Your Azure Blob Storage connection string.

### Python Packages

Ensure that the following Python packages are included in your Function App:

- `azure-functions`
- `azure-storage-blob`
- `Pillow` (PIL)

## Functionality

### Upload Image

The `upload_image` function processes image uploads. It performs the following actions:

1. Receives an image file through an HTTP POST request.
2. Compresses the image using the `compress_image` function.
3. Uploads the compressed image to Azure Blob Storage.

- **Endpoint**: `/upload-image`
- **HTTP Method**: `POST`
- **Request Format**: Form-data containing a file field named `file`.

### Get Image

The `get_image` function retrieves a specified image from Azure Blob Storage. It performs the following actions:

1. Fetches the image from the Blob Storage using the provided image name.
2. Returns the image as an HTTP response.

- **Endpoint**: `/get-image/{image}`
- **HTTP Method**: `GET`
- **Path Parameter**: `image` - The name of the image file to fetch.

## Compression Logic

The `compress_image` function compresses uploaded images to ensure they are below a specified size (20 KB by default). The compression quality is adjusted iteratively until the desired size is achieved or the quality falls below 10.

## Logging

Logging is set up to provide feedback on image processing operations. You can view logs in the Azure portal under the Function App's "Log stream".

## Troubleshooting

- Ensure that the environment variable for the connection string is correctly set.
- Verify that the image being uploaded is valid and supported.
- Check Azure logs for detailed error messages if image upload or retrieval fails.

## License

This project is licensed under the MIT License.


## Helpful CLI commands
### To fetch app settings
func azure functionapp fetch-app-settings <APP_NAME>

### To deploy function app
func azure functionapp publish <APP_NAME>

### To reference key from key vault
@Microsoft.KeyVault(SecretUri=https://.vault.azure.net/secrets//)