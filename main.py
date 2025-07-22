from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
import os
from typing import Optional
import resend
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

app = FastAPI(title="Jeet Khanpara - ML/AI Engineer Portfolio")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Resend configuration
resend.api_key = os.getenv("RESEND_API_KEY")
print(f"API Key loaded: {'Yes' if resend.api_key else 'No'}")
if resend.api_key:
    print(f"Using API key: {resend.api_key[:5]}...{resend.api_key[-5:]}")  # Print first and last 5 chars of API key

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/about", response_class=HTMLResponse)
async def about(request: Request):
    return templates.TemplateResponse("about.html", {"request": request})

@app.get("/projects", response_class=HTMLResponse)
async def projects(request: Request):
    return templates.TemplateResponse("projects.html", {"request": request})

@app.get("/contact", response_class=HTMLResponse)
async def contact_get(request: Request, message: Optional[str] = None, message_type: Optional[str] = None):
    return templates.TemplateResponse(
        "contact.html", 
        {"request": request, "message": message, "message_type": message_type}
    )

@app.post("/contact", response_class=HTMLResponse)
async def contact_post(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    subject: str = Form(...),
    message: str = Form(...)
):
    try:
        if not resend.api_key:
            raise ValueError("Resend API key is not set")

        # Create and send email using Resend
        # Create a completely new email configuration
        email_data = {
            "from": f"Portfolio Contact Form <onboarding@resend.dev>",
            "to": [f"MLearner <mlearner2721@gmail.com>"],
            "reply_to": email,
            "subject": f"New Contact: {subject}",
            "html": f"""
            <div style="font-family: Arial, sans-serif;">
                <h2>New Portfolio Contact Message</h2>
                <div style="margin: 20px 0;">
                    <p><strong>From:</strong> {name}</p>
                    <p><strong>Email:</strong> {email}</p>
                    <p><strong>Subject:</strong> {subject}</p>
                    <hr style="border: 1px solid #eee; margin: 20px 0;">
                    <h3>Message:</h3>
                    <p>{message}</p>
                </div>
                <p style="color: #666; font-size: 12px;">Sent from your portfolio contact form</p>
            </div>
            """
        }
        
        print("Attempting to send email with new configuration...")
        print(f"Using API key ending in: ...{resend.api_key[-5:]}")
        print(f"Sending to: {email_data['to']}")
        
        result = resend.Emails.send(email_data)
        print("Email sent successfully:", result)

        return RedirectResponse(
            url="/contact?message=Message sent successfully!&message_type=success",
            status_code=303
        )
    except Exception as e:
        error_msg = str(e)
        print(f"Error sending email: {error_msg}")
        return RedirectResponse(
            url=f"/contact?message=Failed to send message: {error_msg}&message_type=error",
            status_code=303
        )

# Remove the uvicorn run command as Vercel will handle this
# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)