from typing import List, Optional, Dict, Any, Union, TypeVar, cast
from pydantic import BaseModel, Field

# Define a Float type alias for clarity (instead of using the non-existent Float from typing)
Float = float  # Use the built-in float type

class Education(BaseModel):
    institution: str
    degree: str
    field_of_study: str
    graduation_year: Optional[int] = None


class WorkExperience(BaseModel):
    company: str
    role: str
    current: bool = False
    description: str
    skills_used: List[str]
    achievements: Optional[List[str]] = None


class Project(BaseModel):
    name: str
    description: str
    technologies: List[str]
    skills_gained: Optional[List[str]] = None


class Certification(BaseModel):
    name: str
    skills_validated: List[str]


class Assessment(BaseModel):
    """Hire3x platform specific assessment results"""
    assessment_id: str
    name: str
    score: float  # Score from 0-100
    percentile: float  # Percentile compared to other test takers
    skills_evaluated: List[str]
    completion_time: int  # In minutes
    allowed_time: int  # In minutes
    completion_rate: float  # completion_time / allowed_time
    accuracy: float  # Correctness of answers
    confidence_score: float  # Confidence in answering
    taken_date: str  # Format: YYYY-MM-DD
    proficiency_level: str  # "Beginner", "Intermediate", "Advanced", "Expert"
    test_duration_minutes: int
    certificates_earned: Optional[List[str]] = None


class Course(BaseModel):
    name: str
    category: str
    completion_status: str
    completion_date: Optional[str] = None
    assignments_total: int
    assignment_avg_score: float
    instructor_evaluation: float
    capstone_project_score: Optional[float] = None


class SkillValidation(BaseModel):
    skill: str
    validation_source: str
    validated_level: float
    confidence: str
    practical_application_score: float
    theoretical_knowledge_score: float


class LearningPatterns(BaseModel):
    preferred_learning_time: str
    average_session_duration: int  # in minutes
    consistency_score: float
    completion_tendency: float
    learning_style: str


class Hire3xData(BaseModel):
    joined_date: str
    profile_completion: int
    activity_score: int
    login_frequency: str
    assessments: List[Assessment]
    courses: List[Course]
    skill_validations: List[SkillValidation]
    learning_patterns: LearningPatterns


class CandidateProfile(BaseModel):
    id: str
    name: str
    email: str
    phone: Optional[str] = None
    profile_picture: Optional[str] = None
    linkedin_url: Optional[str] = None
    github_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    location: str
    headline: str
    summary: str
    current_role: str
    years_of_experience: float
    education: List[Education]
    experience: List[WorkExperience]
    skills: Dict[str, float]  # Skill name to proficiency level (0-1)
    projects: Optional[List[Project]] = None
    certifications: Optional[List[Certification]] = None
    languages: Optional[Dict[str, str]] = None
    hire3x_data: Hire3xData
    availability: Optional[str] = None
    desired_role: Optional[str] = None
    preferred_work_type: Optional[str] = None
    
    def to_text(self) -> str:
        """Convert the candidate profile to a text representation for embedding."""
        text_parts = [
            f"Name: {self.name}",
            f"Headline: {self.headline}",
            f"Summary: {self.summary}",
            f"Current Role: {self.current_role}",
            f"Skills: {', '.join(self.skills.keys())}",
            f"Years of Experience: {self.years_of_experience}",
            f"Location: {self.location}",
            f"Desired Role: {self.desired_role}" if self.desired_role else "",
            f"Preferred Work Type: {self.preferred_work_type}" if self.preferred_work_type else ""
        ]
        
        # Add education
        text_parts.append("Education:")
        for edu in self.education:
            grad_year = f", {edu.graduation_year}" if edu.graduation_year else ""
            text_parts.append(f"  {edu.degree} in {edu.field_of_study} from {edu.institution}{grad_year}")
        
        # Add work experience
        text_parts.append("Work Experience:")
        for exp in self.experience:
            current = "(Current)" if exp.current else ""
            text_parts.append(f"  {exp.role} at {exp.company} {current}")
            text_parts.append(f"  Description: {exp.description}")
            text_parts.append(f"  Skills Used: {', '.join(exp.skills_used)}")
            if exp.achievements:
                text_parts.append(f"  Achievements: {', '.join(exp.achievements)}")
        
        # Add projects
        if self.projects:
            text_parts.append("Projects:")
            for project in self.projects:
                text_parts.append(f"  {project.name}: {project.description}")
                text_parts.append(f"  Technologies: {', '.join(project.technologies)}")
        
        # Add certifications
        if self.certifications:
            text_parts.append("Certifications:")
            for cert in self.certifications:
                text_parts.append(f"  {cert.name}")
                text_parts.append(f"  Skills Validated: {', '.join(cert.skills_validated)}")
        
        # Add Hire3x assessments
        text_parts.append("Hire3x Assessments:")
        for assessment in self.hire3x_data.assessments:
            text_parts.append(f"  {assessment.name}: Score {assessment.score}/100, {assessment.percentile}th percentile")
            text_parts.append(f"  Skills Evaluated: {', '.join(assessment.skills_evaluated)}")
            text_parts.append(f"  Completion Time: {assessment.completion_time} minutes (of {assessment.allowed_time} allowed)")
        
        # Add courses
        text_parts.append("Courses Completed:")
        for course in self.hire3x_data.courses:
            text_parts.append(f"  {course.name} ({course.category}): Score {course.assignment_avg_score}/100")
        
        return "\n".join(text_parts)
    
    def get_metadata(self) -> Dict[str, Any]:
        """Extract metadata for storage in ChromaDB."""
        # Basic metadata
        metadata = {
            "id": self.id,
            "name": self.name,
            "years_of_experience": self.years_of_experience,
            "location": self.location,
            "headline": self.headline,
            "current_role": self.current_role,
            "skills": ",".join(self.skills.keys()),
            "top_skills": ",".join([skill for skill, level in sorted(self.skills.items(), key=lambda x: x[1], reverse=True)[:5]]),
            "preferred_work_type": self.preferred_work_type if self.preferred_work_type else "Not Specified",
            "github_url": self.github_url if self.github_url else "",
            "linkedin_url": self.linkedin_url if self.linkedin_url else "",
            "portfolio_url": self.portfolio_url if self.portfolio_url else "",
        }
        
        # Add Hire3x metrics
        metadata["hire3x_profile_completion"] = self.hire3x_data.profile_completion
        metadata["hire3x_activity_score"] = self.hire3x_data.activity_score
        
        # Add assessment data
        if self.hire3x_data.assessments:
            avg_score = sum(a.score for a in self.hire3x_data.assessments) / len(self.hire3x_data.assessments)
            avg_percentile = sum(a.percentile for a in self.hire3x_data.assessments) / len(self.hire3x_data.assessments)
            avg_completion_rate = sum(a.completion_rate for a in self.hire3x_data.assessments) / len(self.hire3x_data.assessments)
            avg_accuracy = sum(a.accuracy for a in self.hire3x_data.assessments) / len(self.hire3x_data.assessments)
            
            metadata["avg_assessment_score"] = avg_score
            metadata["avg_assessment_percentile"] = avg_percentile
            metadata["avg_completion_rate"] = avg_completion_rate
            metadata["avg_accuracy"] = avg_accuracy
            
            # Add specific assessment scores
            assessment_names = [a.name for a in self.hire3x_data.assessments]
            assessment_scores = [a.score for a in self.hire3x_data.assessments]
            metadata["assessment_names"] = ",".join(assessment_names)
            metadata["assessment_scores"] = ",".join([str(score) for score in assessment_scores])
            
            # Add skills evaluated in assessments
            all_skills_evaluated = []
            for assessment in self.hire3x_data.assessments:
                all_skills_evaluated.extend(assessment.skills_evaluated)
            metadata["skills_evaluated"] = ",".join(set(all_skills_evaluated))
        
        # Add education level
        highest_degree = "None"
        for edu in self.education:
            if "Ph.D." in edu.degree or "Doctorate" in edu.degree:
                highest_degree = "Ph.D."
                break
            elif "Master" in edu.degree and highest_degree not in ["Ph.D."]:
                highest_degree = "Master's"
            elif "Bachelor" in edu.degree and highest_degree not in ["Ph.D.", "Master's"]:
                highest_degree = "Bachelor's"
            elif "Associate" in edu.degree and highest_degree not in ["Ph.D.", "Master's", "Bachelor's"]:
                highest_degree = "Associate's"
        
        metadata["highest_degree"] = highest_degree
        
        return metadata


class JobDescription(BaseModel):
    id: str
    title: str
    company: str
    location: Optional[str] = None
    remote_option: Optional[str] = None  # "Remote Only", "Hybrid", "On-Site", "No Preference"
    description: str
    requirements: List[str]
    responsibilities: List[str]
    preferred_qualifications: Optional[List[str]] = None
    required_assessments: Optional[List[str]] = None  # Hire3x assessments required for the role
    min_assessment_score: Optional[float] = None  # Minimum assessment score required
    required_skills: List[str]  # Core skills for the role
    experience_level: str  # e.g., "Entry Level", "Mid-Level", "Senior", "Expert"
    employment_type: str  # e.g., "Full-time", "Part-time", "Contract", "Freelance"
    salary_range: Optional[Dict[str, float]] = None  # e.g., {"min": 80000, "max": 120000}
    
    def to_text(self) -> str:
        """Convert the job description to a text representation for embedding."""
        text_parts = [
            f"Title: {self.title}",
            f"Company: {self.company}",
            f"Experience Level: {self.experience_level}",
            f"Employment Type: {self.employment_type}",
            f"Description: {self.description}",
        ]
        
        if self.location:
            text_parts.append(f"Location: {self.location}")
            
        if self.remote_option:
            text_parts.append(f"Remote Option: {self.remote_option}")
        
        text_parts.append(f"Required Skills: {', '.join(self.required_skills)}")
            
        text_parts.append("Requirements:")
        for req in self.requirements:
            text_parts.append(f"  - {req}")
        
        text_parts.append("Responsibilities:")
        for resp in self.responsibilities:
            text_parts.append(f"  - {resp}")
        
        if self.preferred_qualifications:
            text_parts.append("Preferred Qualifications:")
            for qual in self.preferred_qualifications:
                text_parts.append(f"  - {qual}")
        
        if self.required_assessments:
            text_parts.append("Required Hire3x Assessments:")
            for assessment in self.required_assessments:
                text_parts.append(f"  - {assessment}")
            
            if self.min_assessment_score:
                text_parts.append(f"Minimum Assessment Score: {self.min_assessment_score}/100")
        
        if self.salary_range:
            text_parts.append(f"Salary Range: ${self.salary_range['min']:,} - ${self.salary_range['max']:,}")
        
        return "\n".join(text_parts)


class CandidateMatch(BaseModel):
    candidate_id: str
    candidate_name: str
    headline: str
    current_role: str
    similarity_score: float  # Basic embedding similarity
    profile_picture: Optional[str] = None
    years_of_experience: float
    location: str
    skills: Dict[str, float]  # Skill name to proficiency
    matching_skills: List[str]  # Skills that match the job requirements
    assessment_bonus: float = 0.0  # Bonus score from assessments
    overall_score: float  # Final combined score
    ranking_factors: Dict[str, float]  # Individual factors that contributed to the score
    github_url: Optional[str] = None
    linkedin_url: Optional[str] = None
    portfolio_url: Optional[str] = None
    
    class Config:
        schema_extra = {
            "example": {
                "candidate_id": "fs001",
                "candidate_name": "Michael Rodriguez",
                "headline": "Full Stack Developer specializing in React, Node.js, and AWS",
                "current_role": "Senior Full Stack Developer at TechInnovate",
                "similarity_score": 0.85,
                "profile_picture": "https://randomuser.me/api/portraits/men/1.jpg",
                "years_of_experience": 6.5,
                "location": "Austin, TX",
                "skills": {"JavaScript": 0.95, "React": 0.9, "Node.js": 0.85},
                "matching_skills": ["JavaScript", "React", "Node.js"],
                "assessment_bonus": 0.12,
                "overall_score": 0.89,
                "ranking_factors": {
                    "skill_match": 0.75,
                    "experience_match": 0.80,
                    "assessment_performance": 0.92,
                    "course_completion": 0.85
                },
                "github_url": "https://github.com/mrodriguez",
                "linkedin_url": "https://linkedin.com/in/michael-rodriguez",
                "portfolio_url": "https://michaelrodriguez.dev"
            }
        }


class EmailTemplate(BaseModel):
    to_email: str
    subject: str
    body: str
    
    class Config:
        schema_extra = {
            "example": {
                "to_email": "candidate@example.com",
                "subject": "Interview Invitation for [Position] at [Company]",
                "body": "Dear [Candidate_Name],\n\nWe were impressed by your profile and would like to invite you for an interview for the [Position] position at [Company].\n\nPlease let us know your availability for next week.\n\nBest regards,\n[Recruiter_Name]\n[Company]"
            }
        }