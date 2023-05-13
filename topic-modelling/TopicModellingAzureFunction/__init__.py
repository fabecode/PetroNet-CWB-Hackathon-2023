import logging
import azure.functions as func
import json
import urllib3
import pdfplumber
import io
import re
import openai
import time

def main(req: func.HttpRequest) -> func.HttpResponse:
    openai.api_key = "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"

    logging.info('Processing HTTP request...')
    
    try:
        req_body = req.get_json()

    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    if req_body:
        try:
            file_url = req_body.get('values')[0]["data"]["url"]
            recordId = req_body.get('values')[0]["recordId"]
        except:
            file_url = None
            result = json.dumps("")

        if file_url:
            full_text = extract_pdf_by_url(file_url)
            segments = split_text_to_segments(full_text, file_url)
            key_topics = key_topic_extraction_multiple_segments(segments)
            result = compose_response(key_topics, recordId)
        
        return func.HttpResponse(result, mimetype="application/json")
    
    else:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
def extract_pdf_by_url(url):
    """
    Extract text from pdf file in online url
    """
    http = urllib3.PoolManager()
    temp = io.BytesIO()
    temp.write(http.request("GET", url).data)
    full_text = ''
    with pdfplumber.open(temp) as pdf:
        for pdf_page in pdf.pages:
            single_page_text = pdf_page.extract_text()
            full_text = full_text + '\n' + single_page_text

    # Replace new line and tab characters with spaces
    full_text_cleaned = re.sub("\n|\t"," ",full_text)

    return full_text_cleaned

def split_text_to_segments(text, file_url=None):
    """
    Split text into segments of 2900 words each (due to OpenAI token limit)
    """
    segments = [[]]
    total_words_in_segment = 0

    sentences = text.split('. ')  # Split text into sentences based on period and space

    for sentence in sentences:
        words = sentence.split()  # Split sentence into words
        total_words_in_segment += len(words)

        if file_url:
            #if file_url contains the word 'financial', split into segments of 1900 words each 
            #this is because of much numbers, which are counted as words, taking up more tokens
            if file_url.find("financial") != -1:
                if total_words_in_segment > 1000:
                    segments.append([])
                    total_words_in_segment = len(words)
            else:
                if total_words_in_segment > 2900:
                    segments.append([])
                    total_words_in_segment = len(words)

        segments[-1].append(sentence)

    segments_string = [" ".join(segment) for segment in segments]  # Convert segments list to list of strings

    return segments_string

def wait_and_retry_if_ratelimit_error(error):
    '''
    Wait and retry if GPT rate limit is exceeded (3 req / min)
    '''
    retry_time = error.retry_after if hasattr(error, 'retry_after') else 30
    print(f"\nGPT Rate limit exceeded. Retrying in {retry_time} seconds...\n")
    time.sleep(retry_time)

def key_topic_extraction_one_segment(text):
    """
    Extract key topics from text
    """
    prompt = f"Summarise up to 5 key topics in the following given text, with each topic being 1-3 words long. Exclude entities. Output topics into a Python list. Example output: ['Innovation', 'Financial Performance',...]. \n {text} Please remember you must output topics into a Python list."
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages = [{"role":"user", "content": prompt}],
            max_tokens=100,
            temperature=0.9
        )
    except openai.error.RateLimitError as e:
        wait_and_retry_if_ratelimit_error(e)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages = [{"role":"user", "content": prompt}],
                max_tokens=100,
                temperature=0.9
            )
        except Exception as e:
            print(f"Error: {e}")
            return []
    except openai.error.InvalidRequestError as e:
        print(f"Error: {e}")
        return []

    topic_list_string = response["choices"][0]["message"]["content"]
    print(f"GPT Output: {topic_list_string}")

    start_index = topic_list_string.find("[") #safeguard in case GPT explains before outputting python list
    #if response was a python list
    if start_index != -1:
        topic_list = topic_list_string[start_index:].replace("[","").replace("]","").replace("'","").split(",")

    #if response was a numbered list
    elif topic_list_string.find("1") != -1:
        start_index = topic_list_string.find("1")
        topic_list = topic_list_string[start_index:].split("\n")

        # Remove empty lines and leading/trailing whitespaces
        topic_list = [topic.strip() for topic in topic_list if topic.strip()]

        # Remove the numbers at the beginning of each line
        topic_list = [topic.split(". ", 1)[1] for topic in topic_list]

    #if response was a - bullet list
    elif topic_list_string.find("-") != -1:
        start_index = topic_list_string.find("-")
        topic_list = topic_list_string[start_index:].split("\n")

        # Remove empty lines and leading/trailing whitespaces
        topic_list = [topic.strip() for topic in topic_list if topic.strip()]

        # Remove the - at the beginning of each line
        topic_list = [topic.split("- ", 1)[1] for topic in topic_list]

    return topic_list
    

def key_topic_extraction_multiple_segments(segments):
    """
    Extract key topics from multiple segments of text
    """
    combined_topic_list = []
    for segment in segments:
        topic_list = key_topic_extraction_one_segment(segment)
        combined_topic_list += topic_list

    print("combined_topic_list: ", combined_topic_list)

    prompt = f"Merge semantically similar phrases and output the top 8 most distinct topics that best encapsulates the meaning of all words below. Your response should only return a python list e.g. ['Innovation',  'Financial Performance',...] and nothing else. \n {combined_topic_list}"

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", 
            messages = [{"role":"user", "content": prompt}],
            max_tokens=100,
            temperature=0.9
        )
    except openai.error.RateLimitError as e:
        try:
            wait_and_retry_if_ratelimit_error(e)
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", 
                messages = [{"role":"user", "content": prompt}],
                max_tokens=100,
                temperature=0.3
            )
        except Exception as e:
            print(f"Error: {e}")
            return combined_topic_list
    except openai.error.InvalidRequestError as e:
        print(f"Error: {e}")
        return combined_topic_list

    top_8_topic_list_string = response["choices"][0]["message"]["content"]

    top_8_start_index = top_8_topic_list_string.find("[") #safeguard in case GPT explains before outputting python list
    top_8_topic_list = top_8_topic_list_string[top_8_start_index:].replace("[","").replace("]","").replace("'","").split(",")

    return top_8_topic_list

def compose_response(key_topics, recordId):
    result = {
        "values": [
            {
                "recordId": recordId,
                "data": {
                    "keyTopics": key_topics
                }
            }
        ]
    }
    return json.dumps(result)
