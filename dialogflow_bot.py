import os
import dialogflow

from dotenv import load_dotenv
load_dotenv()

project_id="mychatbot-307913"

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]=os.getenv('DIAGFLOW_PATH')

def send_message(message=None):
    if message:
        response = detect_intent_texts(project_id, "unique", message, 'en')
        return response

def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        response = session_client.detect_intent(
            session=session, query_input=query_input)
        return response.query_result.fulfillment_text