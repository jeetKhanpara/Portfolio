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
        params = {
            "from": "onboarding@resend.dev",
            "to": "mlearner2721@gmail.com",
            "subject": f"Portfolio Contact: {subject}",
            "html": f"""
            <h2>New message from your portfolio website</h2>
            <p><strong>Name:</strong> {name}</p>
            <p><strong>Email:</strong> {email}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <h3>Message:</h3>
            <p>{message}</p>
            """
        }
        
        print("Sending email with params:", params)
        result = resend.Emails.send(params)
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
