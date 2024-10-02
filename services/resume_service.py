from requests import Session
from db.resumes import create_resume
from models.jobs import Job
from models.resumes import Resume
from models.users import User
from openai import OpenAI
from settings.settings import OPENAI_API_KEY, OPENAI_ASSISTANT_ID
import json


class ResumeService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_and_save_resume(self, user: User, job: Job, db: Session) -> Resume:
        resume = Resume(user_id=user.id, job_id=job.id, resume={"wooo": "testing resume hehehehe"})
        return create_resume(resume, db)

#         profile = self.client.files.create(
#             file=open("LinkedIn_profile.json", "rb"),   # TODO: input profile instead of hardcoding
#             purpose="assistants"
#         )

#         # OpenAI automatically creates a vector store for the file that expires in 7 days
#         thread = self.client.beta.threads.create(
#             tool_resources={
#                 'file_search': {
#                     'vector_stores': [
#                         {
#                             'file_ids': [profile.id]
#                         }
#                     ]
#                 }
#             },
#             messages=[
#                 {
#                     'role': 'user',
#                     'content': job_details.description
#                 }
#             ]
#         )

#         self.run_assistant(thread.id)
#         resume = self.extract_resume(thread.id)
#         return resume
    
    
#     def run_assistant(self, thread_id):
#         return self.client.beta.threads.runs.create_and_poll(
#             thread_id=thread_id,
#             assistant_id=OPENAI_ASSISTANT_ID
#         )


#     def extract_resume(self, thread_id):
#         thread_messages = self.client.beta.threads.messages.list(thread_id)
#         asssitant_response = thread_messages.data[0].content[0].text.value

#         # Extract the JSON resume from the message content
#         start = asssitant_response.index("```json") + len("```json")
#         end = asssitant_response.index("```", start)

#         resume = json.loads(asssitant_response[start:end])

#         # Remove endDate if empty (indicates current position)
#         for experience in resume["work"]:
#             if experience.get("endDate") == "":
#                 experience.pop("endDate")
        
#         return resume


# # %%
# from jsonschema import validate
# import json

# # read in schema
# with open("schema.json", "r") as f:
#     schema = json.loads(f.read())
# print(schema)

# # Validate Schema
# def validate_and_correct_resume(resume):
#     try:
#         validate(instance=resume, schema=schema)
#     except Exception as e:
#         print(f'Error validating JSON Schema: {e}')
        
#         # Feed error back into assistant
#         client.beta.threads.messages.create(
#             thread_id=thread.id,
#             role="user",
#             content=f'There was an error validating the generated JSON resume against the JSON Schema.\
#                 Fix the issues outlined by the following error and regenerate the JSON resume: {e}'
#         )

#         run_assistant(thread.id)
#         resume = validate_and_correct_resume(extract_resume(thread.id))
    
#     return resume

# resume = validate_and_correct_resume(resume)

# # %%
# # write custom resume to file
# with open('custom_resume.json', 'w') as output_file:
#     json.dump(resume, output_file)


