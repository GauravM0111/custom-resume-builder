import json
import os
import subprocess
import tempfile
from typing import Literal
from sqlalchemy.orm import Session
from db.resumes import create_resume, update_resume
from models.resumes import CreateResume, Resume, UpdateResume
from playwright.async_api import async_playwright
import boto3

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

        pdf_bytes, img_bytes = await self.generate_pdf_and_img(resume)
        await self.save_to_s3(bucket="pdf", file_bytes=pdf_bytes, file_name=f"{resume.id}.pdf")
        await self.save_to_s3(bucket="thumbnail", file_bytes=img_bytes, file_name=f"{resume.id}.png")

        return resume


    async def update_resume(self, db: Session, update_resume_object: UpdateResume) -> Resume:
        resume = update_resume(update_resume_object, db)

        pdf_bytes, img_bytes = await self.generate_pdf_and_img(resume)
        await self.save_to_s3(bucket="pdf", file_bytes=pdf_bytes, file_name=f"{resume.id}.pdf")
        await self.save_to_s3(bucket="thumbnail", file_bytes=img_bytes, file_name=f"{resume.id}.png")

        return resume


    async def generate_pdf(self, resume: Resume) -> bytes:
        resume_html = await self.render_resume(resume)

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            page = await browser.new_page()

            # Set content to the HTML string
            await page.set_content(resume_html)

            # Generate the PDF in memory
            pdf_bytes = await page.pdf(format="A4")

            await browser.close()

        return pdf_bytes


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
    

    async def save_to_s3(self, bucket: Literal["pdf", "thumbnail"], file_bytes: str, file_name: str) -> None:
        if bucket not in ["pdf", "thumbnail"]:
            raise ValueError(f"Invalid bucket: {bucket}")
        elif bucket == "pdf" and not file_name.endswith(".pdf"):
            raise ValueError("PDF file name must end with .pdf")
        elif bucket == "thumbnail" and not file_name.endswith(".png"):
            raise ValueError("Thumbnail file name must end with .png")

        s3 = boto3.client("s3", endpoint_url=os.getenv("AWS_S3_ENDPOINT_URL"))

        response = s3.put_object(
            Bucket=bucket,
            Key=file_name,
            Body=file_bytes,
            ContentType="application/pdf" if bucket == "pdf" else "image/png"
        )

        return response
