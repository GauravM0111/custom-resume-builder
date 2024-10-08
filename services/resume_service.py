from requests import Session
from db.resumes import create_resume
from models.jobs import Job
from models.resumes import Resume
from models.users import User
from openai import OpenAI
from settings.settings import OPENAI_API_KEY
import json


SYSTEM_PROMPT = """
Convert a given user profile in JSON format and a job description into a comprehensive JSON resume.

The model should analyze the user's profile and the job description to extract key details and qualifications, then compile these into a structured JSON resume format. Ensure that the resume highlights relevant skills, experiences, and achievements that match the job description.

# Steps

1. **Analyze User Profile**: Extract important details such as name, contact information, education, work experiences, skills, and achievements from the user's profile JSON.
2. **Review Job Description**: Identify key skills, qualifications, and responsibilities mentioned in the job description.
3. **Match Qualifications**: Compare the user's profile with the job description to find relevant experiences and skills.
4. **Compile Resume**: Structure a resume in JSON format that includes sections for contact information, summary or objective, work experience, education, skills, and additional sections if relevant (e.g., certifications, projects).
5. **Emphasize Relevance**: Ensure that the highlighted information in the resume closely aligns with the job description requirements.

# Output Format

The output should be a JSON object structured as follows:

```json
{
  "basics": {
    "name": "Full Name",
    "label": "e.g. Web Developer",
    "image": "URL (as per RFC 3986) to a image in JPEG or PNG format",
    "email": "email@example.com",
    "phone": "(123) 456-7890",
    "url": "URL (as per RFC 3986) to your website or personal homepage. e.g. https://example.com",
    "summary": "Write a short 2-3 sentence biography",
    "location": {
      "address": "To add multiple address lines, use \n. For example, 1234 Glücklichkeit Straße\nHinterhaus 5. Etage li.",
      "postalCode": "e.g. CA 94115",
      "city": "e.g. San Francisco",
      "countryCode": "code as per ISO-3166-1 ALPHA-2, e.g. US, AU, IN, etc.",
      "region": "The general region where you live. Can be a US state, or a province, for instance.e.g. California"
    },
    "profiles": [
      {
        "network": "Social Network e.g. Twitter",
        "username": "e.g. john",
        "url": "URL to your social media profile. e.g. https://twitter.com/john"
      },
      "...more profiles..."
    ]
  },
  "work": [
    {
        "name": "Company Name e.g. Facebook",
        "location": "Company Location e.g. San Francisco, CA",
        "description": "Short description of the company e.g. Social Media Company",
        "position": "Position in the company e.g. President",
        "url": "URL to your company homepage. e.g. https://example.com",
        "startDate": "Start Date in iso8601 format e.g. 2014-06-29",
        "endDate": "End Date in iso8601 format e.g. 2014-01-01",
        "summary": "Give an overview of your responsibilities at the company",
        "highlights": [
        "e.g. Increased profits by 20% from 2011-2012 through viral advertising",
        "...more highlights..."
        ]
    },
    "...more work experiences..."
  ],
  "volunteer": [{
    "organization": "Organization",
    "position": "Volunteer",
    "url": "https://organization.com/",
    "startDate": "2012-01-01",
    "endDate": "2013-01-01",
    "summary": "Description…",
    "highlights": [
      "Awarded 'Volunteer of the Month'"
    ]
  }],
  "education": [{
    "institution": "University",
    "url": "https://institution.com/",
    "area": "Software Development",
    "studyType": "Bachelor",
    "startDate": "2011-01-01",
    "endDate": "2013-01-01",
    "score": "4.0",
    "courses": [
      "DB1101 - Basic SQL"
    ]
  }],
  "awards": [{
    "title": "Award",
    "date": "2014-11-01",
    "awarder": "Company",
    "summary": "There is no spoon."
  }],
  "certificates": [{
    "name": "Certificate",
    "date": "2021-11-07",
    "issuer": "Company",
    "url": "https://certificate.com"
  }],
  "publications": [{
    "name": "Publication",
    "publisher": "Company",
    "releaseDate": "2014-10-01",
    "url": "https://publication.com",
    "summary": "Description…"
  }],
  "skills": [{
    "name": "Web Development",
    "level": "Master",
    "keywords": [
      "HTML",
      "CSS",
      "JavaScript"
    ]
  }],
  "languages": [{
    "language": "English",
    "fluency": "Native speaker"
  }],
  "interests": [{
    "name": "Wildlife",
    "keywords": [
      "Ferrets",
      "Unicorns"
    ]
  }],
  "references": [{
    "name": "Jane Doe",
    "reference": "Reference…"
  }],
  "projects": [{
    "name": "Project",
    "startDate": "2019-01-01",
    "endDate": "2021-01-01",
    "description": "Description...",
    "highlights": [
      "Won award at AIHacks 2016"
    ],
    "url": "https://project.com/"
  }]
}
```

# Examples

## Example 1

**Input:**

- User Profile JSON:
  ```json
  {
    "name": "Jane Doe",
    "email": "jane.doe@example.com",
    "phone": "555-1234",
    "linkedin": "https://linkedin.com/in/janedoe",
    "education": [
      {
        "degree": "BSc Computer Science",
        "institution": "University of Example",
        "dates": "2015 - 2019"
      }
    ],
    "experience": [
      {
        "position": "Software Developer",
        "company": "Tech Corp",
        "dates": "2019 - Present",
        "responsibilities": [
          "Developed software solutions for clients",
          "Led a team of developers"
        ]
      }
    ],
    "skills": ["Python", "JavaScript", "Leadership"]
  }
  ```

- Job Description: "Looking for a Software Developer skilled in Python and leadership to lead projects at Tech Solutions."

**Output:**
```json
{
  "name": "Jane Doe",
  "contact_info": {
    "email": "jane.doe@example.com",
    "phone": "555-1234",
    "linkedin": "https://linkedin.com/in/janedoe"
  },
  "summary": "Experienced Software Developer skilled at leading projects with proficiency in Python and leadership.",
  "work_experience": [
    {
      "position": "Software Developer",
      "company": "Tech Corp",
      "dates": "2019 - Present",
      "responsibilities": [
        "Developed software solutions for clients",
        "Led a team of developers"
      ]
    }
  ],
  "education": [
    {
      "degree": "BSc Computer Science",
      "institution": "University of Example",
      "dates": "2015 - 2019"
    }
  ],
  "skills": ["Python", "Leadership"]
}
```

# Notes

- Ensure the JSON is well-formed and all the necessary information fields are filled out based on the user's data and job description requirements.
- Tailor the resume's objective, experiences, and skills directly towards the job description's requirements and preferred qualifications.
"""


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


