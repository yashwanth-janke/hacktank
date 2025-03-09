from typing import List, Dict, Any, Optional, Set, Tuple
from collections import Counter
import re
import json
import ast
import numpy as np

from src.data_processing.hire3x_models import JobDescription, CandidateMatch, CandidateProfile
from src.database.vector_db import VectorDatabase


class Hire3xCandidateMatcher:
    def __init__(self, vector_db: VectorDatabase):
        """
        Initialize the candidate matcher with a vector database.
        
        Args:
            vector_db: The vector database to use for searching
        """
        self.vector_db = vector_db
    
    def match_candidates(
        self, 
        job: JobDescription, 
        top_k: int = 10, 
        min_experience: Optional[float] = None,
        location_filter: Optional[str] = None,
        min_assessment_score: Optional[float] = None
    ) -> List[CandidateMatch]:
        """
        Match candidates to a job description using enhanced Hire3x metrics.
        
        Args:
            job: The job description to match against
            top_k: Number of top candidates to return
            min_experience: Minimum years of experience required (optional)
            location_filter: Filter by location (optional)
            min_assessment_score: Minimum assessment score (optional)
            
        Returns:
            List of candidate matches, ranked by relevance
        """
        # Prepare filters
        filters = {}
        if min_experience is not None:
            filters["years_of_experience"] = {"$gte": min_experience}
        if location_filter:
            filters["location"] = {"$eq": location_filter}
        if min_assessment_score is not None:
            filters["avg_assessment_score"] = {"$gte": min_assessment_score}
        
        # Get raw matches from vector database - fetch 3x the requested amount to allow for filtering
        raw_matches = self.vector_db.search_candidates(
            job=job,
            top_k=top_k * 3,
            filters=filters if filters else None
        )
        
        # Extract job key information
        job_role_keywords = self._extract_role_keywords(job.title)
        required_skills = set(job.required_skills)
        
        # Process and rank matches
        candidate_matches = []
        
        for match in raw_matches:
            try:
                # Parse metadata
                metadata = match["metadata"]
                
                # Extract skills from candidate
                skills_str = metadata.get("skills", "")
                skills = skills_str.split(",") if skills_str else []
                
                # Find matching skills
                matching_skills = [skill for skill in skills if skill.lower() in [s.lower() for s in required_skills]]
                
                # Calculate skill match score (weighted by required skills presence)
                if not required_skills:
                    skill_match_score = 0.5  # Default if no required skills specified
                else:
                    skill_match_score = len(matching_skills) / len(required_skills)
                
                # Calculate role match score
                candidate_role = metadata.get("current_role", "")
                role_match_score = self._calculate_role_match(candidate_role, job.title, job_role_keywords)
                
                # Calculate experience match score
                experience_years = metadata.get("years_of_experience", 0)
                required_years = self._extract_experience_requirement(job)
                experience_match_score = min(experience_years / max(required_years, 1), 1.5)  # Cap at 1.5
                
                # Parse skill proficiency if available
                skill_proficiency_score = 0.0
                try:
                    # Calculate average proficiency for matching skills
                    if "top_skills" in metadata:
                        top_skills = metadata["top_skills"].split(",")
                        skill_overlap = set(top_skills).intersection(set(required_skills))
                        if skill_overlap:
                            skill_proficiency_score = len(skill_overlap) / len(top_skills)
                except:
                    skill_proficiency_score = 0.0
                    
                # Calculate assessment performance scores
                assessment_scores = {}
                
                # Hire3x assessment score
                avg_assessment_score = metadata.get("avg_assessment_score", 0)
                if avg_assessment_score:
                    assessment_scores["assessment_score"] = min(float(avg_assessment_score) / 100, 1.0)
                else:
                    assessment_scores["assessment_score"] = 0.0
                
                # Assess completion rate (faster completion = better)
                avg_completion_rate = metadata.get("avg_completion_rate", 0)
                if avg_completion_rate:
                    # Lower is better, so invert: 1 - (rate capped at 1.0)
                    completion_efficiency = 1.0 - min(float(avg_completion_rate), 1.0)
                    assessment_scores["completion_efficiency"] = completion_efficiency
                else:
                    assessment_scores["completion_efficiency"] = 0.0
                
                # Assess accuracy
                avg_accuracy = metadata.get("avg_accuracy", 0)
                if avg_accuracy:
                    assessment_scores["accuracy"] = float(avg_accuracy)
                else:
                    assessment_scores["accuracy"] = 0.0
                
                # Hire3x specific assessment match
                assessment_relevance = 0.0
                if job.required_assessments and "assessment_names" in metadata:
                    assessment_names = metadata["assessment_names"].split(",")
                    for req_assessment in job.required_assessments:
                        if any(req_assessment.lower() in name.lower() for name in assessment_names):
                            assessment_relevance = 1.0
                            break
                assessment_scores["relevance"] = assessment_relevance
                
                # Get profile completion and activity scores
                profile_completion = float(metadata.get("hire3x_profile_completion", 0)) / 100
                activity_score = float(metadata.get("hire3x_activity_score", 0)) / 100
                
                # Convert ChromaDB distance to similarity score (1 - distance)
                similarity_score = 1.0 - (match["score"] if match["score"] is not None else 0.0)
                
                # Compute assessment bonus
                assessment_bonus = 0.0
                if assessment_scores:
                    assessment_bonus = (
                        assessment_scores.get("assessment_score", 0) * 0.4 +
                        assessment_scores.get("completion_efficiency", 0) * 0.2 +
                        assessment_scores.get("accuracy", 0) * 0.3 +
                        assessment_scores.get("relevance", 0) * 0.1
                    )
                
                # Calculate overall score with weighted components
                # Different weights for different job types
                weights = self._get_role_specific_weights(job.title)
                
                overall_score = (
                    similarity_score * weights["similarity"] +
                    skill_match_score * weights["skill_match"] +
                    role_match_score * weights["role_match"] +
                    experience_match_score * weights["experience"] +
                    skill_proficiency_score * weights["skill_proficiency"] +
                    assessment_bonus * weights["assessment"] +
                    profile_completion * weights["profile_completion"] +
                    activity_score * weights["activity"]
                )
                
                # Normalize to 0-1 range
                overall_score = min(max(overall_score, 0.0), 1.0)
                
                # Get candidate skills as a dictionary (with fallback to empty dict)
                try:
                    candidate_skills_str = metadata.get("skills", "")
                    candidate_skills = {skill: 0.8 for skill in candidate_skills_str.split(",")} if candidate_skills_str else {}
                except:
                    candidate_skills = {}
                
                # Create candidate match object
                candidate_match = CandidateMatch(
                    candidate_id=match["id"],
                    candidate_name=metadata.get("name", "Unknown"),
                    headline=metadata.get("headline", ""),
                    current_role=metadata.get("current_role", ""),
                    similarity_score=similarity_score,
                    profile_picture=None,  # Not stored in metadata
                    years_of_experience=float(metadata.get("years_of_experience", 0)),
                    location=metadata.get("location", ""),
                    skills=candidate_skills,
                    matching_skills=matching_skills,
                    assessment_bonus=assessment_bonus,
                    overall_score=overall_score,
                    ranking_factors={
                        "similarity": similarity_score,
                        "skill_match": skill_match_score,
                        "role_match": role_match_score,
                        "experience_match": experience_match_score,
                        "skill_proficiency": skill_proficiency_score,
                        "assessment_performance": assessment_bonus,
                        "profile_completion": profile_completion,
                        "activity_score": activity_score
                    },
                    github_url=metadata.get("github_url", None),
                    linkedin_url=metadata.get("linkedin_url", None),
                    portfolio_url=metadata.get("portfolio_url", None)
                )
                
                candidate_matches.append(candidate_match)
            except Exception as e:
                print(f"Error processing candidate {match.get('id', 'unknown')}: {e}")
                continue
        
        # Sort by overall score (descending)
        candidate_matches.sort(key=lambda x: x.overall_score, reverse=True)
        
        return candidate_matches[:top_k]
    
    def _extract_role_keywords(self, job_title: str) -> Set[str]:
        """Extract important role keywords from job title."""
        # Common tech role keywords
        role_keywords = {
            "developer", "engineer", "architect", "scientist", "analyst", "designer",
            "manager", "lead", "administrator", "specialist", "consultant",
            "devops", "frontend", "backend", "fullstack", "full stack", "full-stack",
            "mobile", "ios", "android", "web", "cloud", "security", "data",
            "machine learning", "ml", "ai", "artificial intelligence", "ui", "ux",
            "qa", "quality", "test", "automation", "database", "dba"
        }
        
        # Normalize job title
        job_title_lower = job_title.lower()
        
        # Find matches
        found_keywords = set()
        for keyword in role_keywords:
            if keyword in job_title_lower:
                found_keywords.add(keyword)
        
        return found_keywords
    
    def _calculate_role_match(self, candidate_role: str, job_title: str, job_role_keywords: Set[str]) -> float:
        """Calculate how well the candidate's role matches the job title."""
        if not candidate_role or not job_title:
            return 0.0
            
        candidate_role_lower = candidate_role.lower()
        job_title_lower = job_title.lower()
        
        # Exact match
        if candidate_role_lower == job_title_lower:
            return 1.0
            
        # Partial match based on keywords
        candidate_keywords = set()
        for keyword in job_role_keywords:
            if keyword in candidate_role_lower:
                candidate_keywords.add(keyword)
        
        if not job_role_keywords:
            return 0.5  # Default if no role keywords found
            
        return len(candidate_keywords) / len(job_role_keywords)
    
    def _extract_experience_requirement(self, job: JobDescription) -> float:
        """Extract years of experience required from job description."""
        # Look for patterns like "5+ years", "3-5 years", etc.
        for req in job.requirements:
            req_lower = req.lower()
            
            # Look for specific patterns
            patterns = [
                r'(\d+)\+?\s*years?',  # "5+ years", "5 years"
                r'(\d+)[-–]\d+\s*years?',  # "3-5 years"
                r'at least (\d+)\s*years?',  # "at least 3 years"
                r'minimum (\d+)\s*years?'  # "minimum 3 years"
            ]
            
            for pattern in patterns:
                match = re.search(pattern, req_lower)
                if match:
                    return float(match.group(1))
        
        # If not found, infer from experience level
        experience_map = {
            "entry level": 0.0,
            "junior": 1.0,
            "mid-level": 3.0,
            "senior": 5.0,
            "lead": 7.0,
            "principal": 8.0,
            "staff": 8.0,
            "architect": 10.0,
            "expert": 10.0
        }
        
        for level, years in experience_map.items():
            if level in job.experience_level.lower():
                return years
                
        # Default based on general experience level
        if "senior" in job.title.lower():
            return 5.0
        elif "junior" in job.title.lower():
            return 1.0
        elif "lead" in job.title.lower() or "principal" in job.title.lower():
            return 7.0
            
        return 2.0  # Default moderate experience if nothing found
    
    def _get_role_specific_weights(self, job_title: str) -> Dict[str, float]:
        """Get role-specific weights for different factors in the overall score."""
        job_title_lower = job_title.lower()
        
        # Default weights
        default_weights = {
            "similarity": 0.15,
            "skill_match": 0.20,
            "role_match": 0.15,
            "experience": 0.10,
            "skill_proficiency": 0.10,
            "assessment": 0.15,
            "profile_completion": 0.05,
            "activity": 0.10
        }
        
        # Data Science / ML / AI roles - prioritize skills and assessments
        if any(kw in job_title_lower for kw in ["data scientist", "machine learning", "ml", "ai ", "artificial intelligence"]):
            return {
                "similarity": 0.10,
                "skill_match": 0.25,
                "role_match": 0.10,
                "experience": 0.10,
                "skill_proficiency": 0.15,
                "assessment": 0.20,
                "profile_completion": 0.05,
                "activity": 0.05
            }
            
        # Engineering / Development roles - balanced approach
        elif any(kw in job_title_lower for kw in ["engineer", "developer", "programmer", "coder"]):
            return {
                "similarity": 0.15,
                "skill_match": 0.20,
                "role_match": 0.15,
                "experience": 0.10,
                "skill_proficiency": 0.10,
                "assessment": 0.15,
                "profile_completion": 0.05,
                "activity": 0.10
            }
            
        # Leadership roles - prioritize experience and role match
        elif any(kw in job_title_lower for kw in ["lead", "manager", "director", "head", "chief", "architect"]):
            return {
                "similarity": 0.10,
                "skill_match": 0.15,
                "role_match": 0.20,
                "experience": 0.20,
                "skill_proficiency": 0.10,
                "assessment": 0.10,
                "profile_completion": 0.05,
                "activity": 0.10
            }
            
        # Design roles - prioritize portfolio and skills
        elif any(kw in job_title_lower for kw in ["designer", "ui", "ux", "user interface", "user experience"]):
            return {
                "similarity": 0.15,
                "skill_match": 0.25,
                "role_match": 0.10,
                "experience": 0.10,
                "skill_proficiency": 0.15,
                "assessment": 0.10,
                "profile_completion": 0.05,
                "activity": 0.10
            }
        
        return default_weights
    
    def get_candidate_profile(self, candidate_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the full profile of a candidate by their ID.
        
        Args:
            candidate_id: The ID of the candidate
        
        Returns:
            The candidate's full profile or None if not found
        """
        try:
            # This would normally fetch from a database
            # For this example, we're just reading our sample data
            with open('data/sample_candidate.json', 'r') as f:
                candidates = json.load(f)
                
            if isinstance(candidates, list):
                for candidate in candidates:
                    if candidate.get('id') == candidate_id:
                        return candidate
                return None
            elif isinstance(candidates, dict) and candidates.get('id') == candidate_id:
                return candidates
            else:
                return None
                
        except Exception as e:
            print(f"Error fetching candidate profile: {e}")
            return None
    
    def generate_email_template(self, candidate_match: CandidateMatch, job: JobDescription) -> Dict[str, str]:
        """
        Generate an email template for contacting a candidate.
        
        Args:
            candidate_match: The matched candidate
            job: The job description
            
        Returns:
            Dictionary with email subject and body
        """
        candidate_name = candidate_match.candidate_name
        company_name = job.company
        job_title = job.title
        
        subject = f"Opportunity for {job_title} position at {company_name}"
        
        body = f"""Dear {candidate_name},

I hope this email finds you well. I'm reaching out because we are impressed with your background and experience, particularly your skills in {', '.join(candidate_match.matching_skills[:3])}.

We are currently looking for a {job_title} at {company_name} and believe your profile would be a great fit for this role.

Here's a brief overview of what we're looking for:
- {job.requirements[0] if job.requirements else ''}
- {job.requirements[1] if len(job.requirements) > 1 else ''}
- {job.requirements[2] if len(job.requirements) > 2 else ''}

Would you be interested in discussing this opportunity further? If so, please let me know your availability for a brief call in the coming days.

Looking forward to your response.

Best regards,
[Your Name]
Hiring Manager
{company_name}
"""
        
        return {
            "to_email": "candidate@example.com",  # Placeholder - would be replaced with real email
            "subject": subject,
            "body": body
        }