import os
from PyPDF2 import PdfReader, PdfWriter
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

load_dotenv()

STORAGE_ACCT_NAME = os.getenv("STORAGE_ACCT_NAME")
STORAGE_ACCT_KEY = os.getenv("STORAGE_ACCT_KEY")
STORAGE_CONTAINER_NAME = os.getenv("STORAGE_CONTAINER_NAME")

storageConnectionString = f"DefaultEndpointsProtocol=https;AccountName={STORAGE_ACCT_NAME};AccountKey={STORAGE_ACCT_KEY};EndpointSuffix=core.windows.net"
blob_service_client = BlobServiceClient.from_connection_string(storageConnectionString)
storage_container_name = STORAGE_CONTAINER_NAME



def extract_specified_pages_from_pdf_in_folder_and_upload(folder, numPages):
    """
    Extracts specified pages from a pdf file and saves it as a new pdf file
    """
    try:
        for file in os.listdir(f'data\original-data\{folder}'):
            print(f"Processing {file}")
            if file.endswith('.pdf'):
                #if the file is a pdf file
                pdf_file_path = f'data\original-data\{folder}\{file}'
                file_base_name = pdf_file_path.split(f'original-data\{folder}\\')[1].replace('.pdf', '')

                pdf = PdfReader(pdf_file_path)
                if numPages > len(pdf.pages):
                    numPages = len(pdf.pages)

                pages = range(0,numPages)
                pdfWriter = PdfWriter()

                for page_num in pages:
                    pdfWriter.add_page(pdf.pages[page_num])

                new_pdf_file_path = f"data\demo-data\{folder}\{file_base_name}.pdf"

                with open(new_pdf_file_path.format(file_base_name), 'wb') as f:
                    pdfWriter.write(f)
                    f.close()
    except Exception as e:
        print('Exception:', e)

def upload_blob_file(blob_service_client: BlobServiceClient, container_name, reportType, file_path):
    if folder == 'integrated_and_annual_reports':
        reportType = 'Integrated and Annual Report'
    elif folder == 'sustainability':
        reportType = 'Sustainability Report'
    elif folder == 'financial_reports':
        reportType = 'Financial Report'

    try:
        container_client = blob_service_client.get_container_client(container=container_name)
        metadata = {"reportType": reportType}
        file_name = file_path.split('\\')[-1]
        with open(file=os.path.join(file_path), mode="rb") as data:
            container_client.upload_blob(name=f"{file_name}", data=data, metadata=metadata, overwrite=True)
        print(f"{file_name} uploaded to blob successfully")
    except Exception as e:
        print('Exception:', e)

def upload_blob_files_in_folder(blob_service_client: BlobServiceClient, container_name, reportType, folder_path):
    for file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file)
        upload_blob_file(blob_service_client, container_name, reportType, file_path)
    
for folder in os.listdir('data\original-data'):
    extract_specified_pages_from_pdf_in_folder_and_upload(folder, 10)
    upload_blob_files_in_folder(blob_service_client, storage_container_name, folder, f'data\demo-data\{folder}')

    