# PetroNet-CWB-Hackathon-2023
Microsoft Code Without Barriers Hackathon 2023
## PETRONAS Problem Statement
There are 8 different types of publicly-available PETRONAS reports (i.e. Integrated & Annual Reports, Financial Reports & Sustainability) These reports contain a wealth of information, but their complex format and large volume make it challenging for users to quickly identify key topics and generate insights. How can we use Microsoft AI-related services to develop a solution that can automatically extract and organize relevant information from these PETRONAS reports to help users quickly find and understand the topics that they are interested in?
- Leverage on Microsoft AI-related services to extract and categorize text and images from PETRONAS reports, and identify key topics within each report. 
- Develop a landing page with search bar that utilizes Natural Language Understanding (NLU) to allow users to search for topics of interest within the reports. 
- Upon a search query, the tool should surface relevant documents related to the query and highlight specific keywords from the content across multiple reports. 
- The tool should also generate a visual representation of relevant entities in a knowledge-graph with their relationships to help users better understand the context of the topics they are interested in.

## Solution Overview
1. Create the required Azure resources via the Azure Portal - Azure Cognitive Search, Azure Blob Storage, Azure Function resources
2. Run [preprocessing/extract_n_upload_pdf.py](preprocessing/extract_n_upload_pdf.py) to extract pages from PDFs (to fit Cognitive Search Basic Tier limit) and upload to Azure Blob Storage
    - Update the 'STORAGE_ACCT_NAME', 'STORAGE_ACCT_KEY', 'STORAGE_CONTAINER_NAME' variables in a .env file
3. Run [topic-modelling/TopicModellingAzureFunction/init.py](topic-modelling/TopicModellingAzureFunction/__init__.py) and publish the topic modelling Azure Function as an Azure Function App
4. Run [search-index-pipeline/create-search.cmd](search-index-pipeline/create-search.cmd) to create the Azure Cognitive Search index
    - Update the 'url', 'admin_key' variables in a .env file
    - Update connectionString in [search-datasource.json](search-index-pipeline/search-datasource.json), and azure function url in [search-skillset.json](search-index-pipeline/search-datasource.json)
5. Run [web-app-frontend\CognitiveSearch.Template.sln](web-app-frontend\CognitiveSearch.Template.sln) in Visual Studio to load front-end
    - Update appsettings.json with your configurations

## Online Resources
Azure Cognitive Search
* [Microsoft Learn - AI-900 Lab: create-cognitive-search-solution](https://microsoftlearning.github.io/AI-900-AIFundamentals/instructions/05-create-cognitive-search-solution.html)
* [Github - Azure-Samples/azure-search-knowledge-mining](https://github.com/Azure-Samples/azure-search-knowledge-mining)
* [Github - Azure-Samples/azure-search-power-skills](https://github.com/Azure-Samples/azure-search-power-skills/tree/main/Text/TextSummarization)
* [Docs - Tips for AI Enrichment in Azure Cognitive Search](https://learn.microsoft.com/en-us/azure/search/cognitive-search-concept-troubleshooting)
* [Docs - Add a scoring profile](https://learn.microsoft.com/en-us/azure/search/index-add-scoring-profiles)

Azure Blob Storage
* [Docs - Use blob index tags](https://learn.microsoft.com/en-us/azure/storage/blobs/storage-blob-index-how-to?tabs=azure-portal)

Azure Functions
* [Github - Azure Functions](https://github.com/Azure/Azure-Functions/tree/main)
* [Docs - Creating Azure functions with Python using VSC](https://learn.microsoft.com/en-us/azure/azure-functions/create-first-function-vs-code-python?pivots=python-mode-configuration)
* [Docs - Publishing to Azure via Remote Build](https://learn.microsoft.com/en-us/azure/azure-functions/functions-reference-python?tabs=asgi%2Capplication-level&pivots=python-mode-configuration#remote-build)
* [Docs - Troubleshoot Python errors in Azure Functions](https://learn.microsoft.com/en-us/azure/azure-functions/recover-python-functions?pivots=python-mode-configuration&tabs=vscode%2Cbash)