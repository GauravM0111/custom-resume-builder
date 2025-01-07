import json
import os
import subprocess
import tempfile
from sqlalchemy.orm import Session
from db.resumes import create_resume, update_resume
from models.resumes import CreateResume, Resume, UpdateResume
from playwright.async_api import async_playwright
import boto3
from settings.settings import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_S3_THUMBNAILS_BUCKET

AVAILABLE_THEMES = ["jsonresume-theme-even"]


class ResumeService:
    def __init__(self):
        pass


    async def render_resume(self, resume: Resume, theme: str = "jsonresume-theme-even") -> str:
        if theme not in AVAILABLE_THEMES:
            raise ValueError(f"Theme {theme} is not available")

        input_file = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        output_file = tempfile.NamedTemporaryFile(mode='r', suffix='.html', delete=False)

        json.dump(resume.resume, input_file)
        input_file.flush()

        try:
            subprocess.run(
                ["npx", "resumed", "--theme", theme, "--output", output_file.name, input_file.name],
                capture_output=True,
                check=True
            )

            # Read the output file
            output_file.seek(0)
            result = output_file.read()
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error rendering resume: {e.stderr}")
        finally:
            # Clean up temporary files
            os.unlink(input_file.name)
            os.unlink(output_file.name)

        return result
    

    async def save_resume(self, db: Session, create_resume_object: CreateResume) -> Resume:
        if not create_resume_object.job_title:
            create_resume_object.job_title = "Untitled Resume"

        resume = create_resume(create_resume_object, db)

        _, img_bytes = await self.generate_pdf_and_img(resume)
        await self.save_thumbnail_to_s3(img_bytes, f"{resume.id}.png")

        return resume


    async def update_resume(self, db: Session, update_resume_object: UpdateResume) -> Resume:
        resume = update_resume(update_resume_object, db)

        _, img_bytes = await self.generate_pdf_and_img(resume)
        await self.save_thumbnail_to_s3(img_bytes, f"{resume.id}.png")

        return resume


    async def generate_pdf_and_img(self, resume: Resume) -> tuple[bytes, bytes]:
        resume_html = await self.render_resume(resume)

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            await page.set_content(resume_html)
            await page.emulate_media(media="screen")  # Emulate media to screen mode instead of print mode

            pdf_bytes = await page.pdf()
            img_bytes = await page.screenshot(full_page=True, scale="css", type="png")

            await browser.close()

        return pdf_bytes, img_bytes


    async def save_thumbnail_to_s3(self, img_bytes: bytes, file_name: str) -> None:
        if not file_name.endswith(".png"):
            raise ValueError("Thumbnail file name must end with .png")
        
        await self.s3_client().put_object(
            Bucket=AWS_S3_THUMBNAILS_BUCKET,
            Key=file_name,
            Body=img_bytes,
            ContentType="image/png"
        )


    async def s3_client(self):
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )
