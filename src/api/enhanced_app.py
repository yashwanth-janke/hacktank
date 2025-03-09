from typing import List, Optional, Dict, Any
from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Depends, Query, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import json
import uuid
import os
from pathlib import Path
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pdfkit

from src.data_processing.hire3x_models import JobDescription, CandidateMatch, CandidateProfile, EmailTemplate
from src.embeddings.generator import EmbeddingGenerator
from src.database.vector_db import VectorDatabase
from src.matching.hire3x_matcher import Hire3xCandidateMatcher


# Ensure necessary directories exist
os.makedirs("data", exist_ok=True)
os.makedirs("pdfs", exist_ok=True)

# Initialize FastAPI app
app = FastAPI(
    title="Hire3x - AI-Powered Candidate Matching System",
    description="Match candidates to job descriptions using embeddings, vector search, and Hire3x assessment metrics"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

# Initialize components
embedding_generator = EmbeddingGenerator()
vector_db = VectorDatabase(embedding_generator=embedding_generator)
candidate_matcher = Hire3xCandidateMatcher(vector_db=vector_db)


@app.get("/")
def read_root():
    return FileResponse('frontend/index.html')


@app.get("/api/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


@app.post("/api/candidates/", response_model=Dict[str, Any])
async def add_candidate(candidate: Dict[str, Any]):
    """
    Add a candidate to the system.
    """
    try:
        # Ensure ID exists
        if "id" not in candidate:
            candidate["id"] = str(uuid.uuid4())
            
        # Convert to CandidateProfile for validation
        candidate_obj = CandidateProfile(**candidate)
        
        vector_db.add_candidate(candidate_obj)
        return {"message": f"Candidate {candidate_obj.name} added successfully", "id": candidate_obj.id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add candidate: {str(e)}")


@app.post("/api/candidates/batch/", response_model=Dict[str, Any])
async def add_candidates_batch(candidates: List[Dict[str, Any]]):
    """
    Add multiple candidates to the system.
    """
    try:
        validated_candidates = []
        
        for candidate in candidates:
            # Ensure ID exists
            if "id" not in candidate:
                candidate["id"] = str(uuid.uuid4())
                
            # Convert to CandidateProfile for validation
            candidate_obj = CandidateProfile(**candidate)
            validated_candidates.append(candidate_obj)
        
        vector_db.add_candidates_batch(validated_candidates)
        return {"message": f"{len(validated_candidates)} candidates added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to add candidates: {str(e)}")


@app.post("/api/candidates/upload/", response_model=Dict[str, Any])
async def upload_candidates(
    file: UploadFile = File(...),
):
    """
    Upload candidates from a JSON file.
    """
    try:
        content = await file.read()
        candidates_data = json.loads(content)
        
        # Handle both single candidate and array of candidates
        if isinstance(candidates_data, dict):
            candidates_data = [candidates_data]
        
        # Convert to CandidateProfile objects
        candidates = []
        for data in candidates_data:
            # Ensure each candidate has an ID
            if "id" not in data:
                data["id"] = str(uuid.uuid4())
            
            # Convert to CandidateProfile for validation
            try:
                candidate_obj = CandidateProfile(**data)
                candidates.append(candidate_obj)
            except Exception as e:
                print(f"Error validating candidate: {e}")
                continue
        
        vector_db.add_candidates_batch(candidates)
        
        return {"message": f"{len(candidates)} candidates uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to upload candidates: {str(e)}")


@app.post("/api/jobs/match/", response_model=List[CandidateMatch])
async def match_candidates(
    job: JobDescription,
    top_k: Optional[int] = Query(10, description="Number of top candidates to return"),
    min_experience: Optional[float] = Query(None, description="Minimum years of experience"),
    location_filter: Optional[str] = Query(None, description="Filter by location"),
    min_assessment_score: Optional[float] = Query(None, description="Minimum assessment score (0-100)")
):
    """
    Match candidates to a job description.
    """
    try:
        matches = candidate_matcher.match_candidates(
            job=job,
            top_k=top_k,
            min_experience=min_experience,
            location_filter=location_filter,
            min_assessment_score=min_assessment_score
        )
        return matches
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to match candidates: {str(e)}")


@app.get("/api/candidates/{candidate_id}", response_model=Dict[str, Any])
async def get_candidate_profile(candidate_id: str):
    """
    Get the full profile of a candidate by their ID.
    """
    try:
        profile = candidate_matcher.get_candidate_profile(candidate_id)
        if profile:
            return profile
        else:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get candidate profile: {str(e)}")


@app.post("/api/email/generate", response_model=EmailTemplate)
async def generate_email(
    candidate_id: str = Body(...),
    job: JobDescription = Body(...)
):
    """
    Generate an email template for contacting a candidate.
    """
    try:
        # Get matching result for the candidate
        matches = candidate_matcher.match_candidates(job, top_k=100)
        
        candidate_match = None
        for match in matches:
            if match.candidate_id == candidate_id:
                candidate_match = match
                break
                
        if not candidate_match:
            # Fallback to just fetching profile
            profile = candidate_matcher.get_candidate_profile(candidate_id)
            if not profile:
                raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
                
            # Create a minimal match object
            candidate_match = CandidateMatch(
                candidate_id=profile["id"],
                candidate_name=profile["name"],
                headline=profile.get("headline", ""),
                current_role=profile.get("current_role", ""),
                similarity_score=0.0,
                years_of_experience=profile.get("years_of_experience", 0),
                location=profile.get("location", ""),
                skills=profile.get("skills", {}),
                matching_skills=list(profile.get("skills", {}).keys())[:3],
                overall_score=0.0,
                ranking_factors={}
            )
            
        email_template = candidate_matcher.generate_email_template(candidate_match, job)
        
        # Construct response
        response = EmailTemplate(
            to_email=email_template.get("to_email", "candidate@example.com"),
            subject=email_template.get("subject", ""),
            body=email_template.get("body", "")
        )
        
        return response
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate email: {str(e)}")


@app.post("/api/email/send", response_model=Dict[str, str])
async def send_email(
    email_data: EmailTemplate,
    sender_email: str = Body(...),
    sender_password: str = Body(...)
):
    """
    Send an email to a candidate (requires email credentials).
    """
    try:
        # Create a MIME email
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email_data.to_email
        message["Subject"] = email_data.subject
        
        # Attach the body
        message.attach(MIMEText(email_data.body, "plain"))
        
        # Connect to SMTP server (using Gmail as an example)
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        
        # Login and send
        try:
            server.login(sender_email, sender_password)
            server.send_message(message)
            server.quit()
            return {"message": f"Email sent successfully to {email_data.to_email}"}
        except Exception as e:
            raise HTTPException(status_code=401, detail=f"Failed to authenticate or send email: {str(e)}")
            
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send email: {str(e)}")


@app.post("/api/candidates/export-pdf/{candidate_id}", response_model=Dict[str, str])
async def export_candidate_pdf(
    candidate_id: str,
    job_id: Optional[str] = None
):
    """
    Export a candidate profile as PDF.
    """
    try:
        profile = candidate_matcher.get_candidate_profile(candidate_id)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Candidate {candidate_id} not found")
            
        # Generate HTML content for the PDF
        html_content = f"""
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333366; }}
                h2 {{ color: #336699; border-bottom: 1px solid #ccc; padding-bottom: 5px; margin-top: 20px; }}
                .summary {{ background-color: #f5f5f5; padding: 10px; border-radius: 5px; margin: 10px 0; }}
                .skills {{ display: flex; flex-wrap: wrap; margin: 10px 0; }}
                .skill {{ background-color: #e1e1e1; padding: 5px 10px; margin: 5px; border-radius: 15px; }}
                .assessment {{ background-color: #e1f5fe; padding: 10px; margin: 10px 0; border-radius: 5px; }}
                .experience {{ margin-bottom: 15px; }}
                .contact {{ background-color: #f9f9f9; padding: 10px; border-radius: 5px; }}
            </style>
        </head>
        <body>
            <h1>{profile.get('name', 'Candidate Profile')}</h1>
            <div class="contact">
                <p><strong>Email:</strong> {profile.get('email', 'N/A')}</p>
                <p><strong>Phone:</strong> {profile.get('phone', 'N/A')}</p>
                <p><strong>Location:</strong> {profile.get('location', 'N/A')}</p>
                <p><strong>Current Role:</strong> {profile.get('current_role', 'N/A')}</p>
                <p><strong>Years of Experience:</strong> {profile.get('years_of_experience', 'N/A')}</p>
            </div>
            
            <h2>Summary</h2>
            <div class="summary">
                <p>{profile.get('summary', 'No summary available.')}</p>
            </div>
            
            <h2>Skills</h2>
            <div class="skills">
        """
        
        # Add skills
        for skill, proficiency in profile.get('skills', {}).items():
            html_content += f'<div class="skill">{skill} ({int(proficiency * 100)}%)</div>'
            
        html_content += """
            </div>
            
            <h2>Experience</h2>
        """
        
        # Add experience
        for exp in profile.get('experience', []):
            html_content += f"""
            <div class="experience">
                <h3>{exp.get('role', 'Role')} at {exp.get('company', 'Company')}</h3>
                <p>{exp.get('description', 'No description available.')}</p>
                <p><strong>Skills Used:</strong> {', '.join(exp.get('skills_used', []))}</p>
                <p><strong>Achievements:</strong></p>
                <ul>
            """
            
            for achievement in exp.get('achievements', []):
                html_content += f'<li>{achievement}</li>'
                
            html_content += """
                </ul>
            </div>
            """
            
        # Add education
        html_content += "<h2>Education</h2>"
        for edu in profile.get('education', []):
            html_content += f"""
            <div class="education">
                <p><strong>{edu.get('degree', 'Degree')}</strong> in {edu.get('field_of_study', 'Field')}</p>
                <p>{edu.get('institution', 'Institution')}, {edu.get('graduation_year', 'Year')}</p>
            </div>
            """
            
        # Add Hire3x assessments
        html_content += "<h2>Hire3x Assessments</h2>"
        for assessment in profile.get('hire3x_data', {}).get('assessments', []):
            html_content += f"""
            <div class="assessment">
                <h3>{assessment.get('name', 'Assessment')}</h3>
                <p><strong>Score:</strong> {assessment.get('score', 'N/A')}/100 ({assessment.get('percentile', 'N/A')}th percentile)</p>
                <p><strong>Skills Evaluated:</strong> {', '.join(assessment.get('skills_evaluated', []))}</p>
                <p><strong>Completion Time:</strong> {assessment.get('completion_time', 'N/A')} minutes (of {assessment.get('allowed_time', 'N/A')} allowed)</p>
                <p><strong>Accuracy:</strong> {int(assessment.get('accuracy', 0) * 100)}%</p>
            </div>
            """
            
        # Close HTML
        html_content += """
        </body>
        </html>
        """
        
        # Generate PDF
        pdf_filename = f"pdfs/candidate_{candidate_id}.pdf"
        pdfkit.from_string(html_content, pdf_filename)
        
        # Return success response with the file path
        return {"message": "PDF generated successfully", "filename": pdf_filename}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to generate PDF: {str(e)}")


@app.get("/api/candidates/pdf/{candidate_id}")
async def get_candidate_pdf(candidate_id: str):
    """
    Get the generated PDF for a candidate.
    """
    pdf_filename = f"pdfs/candidate_{candidate_id}.pdf"
    if os.path.exists(pdf_filename):
        return FileResponse(pdf_filename, media_type="application/pdf", filename=f"candidate_{candidate_id}.pdf")
    else:
        raise HTTPException(status_code=404, detail="PDF not found. Please generate it first.")


@app.get("/api/candidates/count/", response_model=Dict[str, int])
async def get_candidate_count():
    """
    Get the number of candidates in the database.
    """
    try:
        count = vector_db.get_candidate_count()
        return {"count": count}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to get candidate count: {str(e)}")


@app.delete("/api/candidates/{candidate_id}", response_model=Dict[str, str])
async def delete_candidate(candidate_id: str):
    """
    Delete a candidate from the system.
    """
    try:
        vector_db.delete_candidate(candidate_id)
        return {"message": f"Candidate {candidate_id} deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to delete candidate: {str(e)}")