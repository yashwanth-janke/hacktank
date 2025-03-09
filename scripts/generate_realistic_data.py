import json
import uuid
import os
from datetime import datetime, timedelta
import random
import names
import faker
from faker import Faker

# Initialize Faker
fake = Faker()

# Ensure data directory exists
os.makedirs("data", exist_ok=True)

# Tech roles to generate
TECH_ROLES = [
    {"role": "Full Stack Developer", "specialties": ["React", "Angular", "Vue.js", "Node.js", "PHP", "Ruby on Rails", "Python", "Java", "AWS"]},
    {"role": "Frontend Engineer", "specialties": ["React", "Angular", "Vue.js", "JavaScript", "TypeScript", "UI/UX", "Accessibility"]},
    {"role": "Backend Engineer", "specialties": ["Java", "Python", "Node.js", "C#", "Go", "PHP", "Ruby", "Spring Boot", "Django", "Express"]},
    {"role": "DevOps Engineer", "specialties": ["AWS", "Azure", "GCP", "Docker", "Kubernetes", "Terraform", "CI/CD", "Jenkins", "GitOps"]},
    {"role": "Data Scientist", "specialties": ["Python", "R", "Machine Learning", "Statistics", "NLP", "Deep Learning", "TensorFlow", "PyTorch"]},
    {"role": "Machine Learning Engineer", "specialties": ["TensorFlow", "PyTorch", "Computer Vision", "NLP", "MLOps", "AWS", "Deep Learning"]},
    {"role": "Cloud Architect", "specialties": ["AWS", "Azure", "GCP", "Cloud Security", "Serverless", "Microservices", "Kubernetes"]},
    {"role": "Security Engineer", "specialties": ["Network Security", "Penetration Testing", "Security Auditing", "Encryption", "Threat Analysis"]},
    {"role": "Mobile Developer", "specialties": ["iOS", "Android", "React Native", "Flutter", "Swift", "Kotlin", "Mobile UI Design"]},
    {"role": "QA Engineer", "specialties": ["Automation Testing", "Selenium", "Cypress", "Jest", "Pytest", "Performance Testing", "Manual Testing"]},
    {"role": "UI/UX Designer", "specialties": ["Figma", "Adobe XD", "User Research", "Wireframing", "Prototyping", "Design Systems"]},
    {"role": "Database Administrator", "specialties": ["SQL", "PostgreSQL", "MySQL", "MongoDB", "Oracle", "Performance Tuning", "Data Modeling"]},
    {"role": "Site Reliability Engineer", "specialties": ["Linux", "Monitoring", "Kubernetes", "AWS", "Load Balancing", "Performance Optimization"]},
    {"role": "Blockchain Developer", "specialties": ["Solidity", "Smart Contracts", "Web3.js", "Ethereum", "Hyperledger", "Cryptocurrency"]},
    {"role": "Game Developer", "specialties": ["Unity", "Unreal Engine", "C++", "Game Design", "3D Modeling", "Animation", "Physics"]}
]

# Education institutions
UNIVERSITIES = [
    {"name": "Massachusetts Institute of Technology", "location": "Cambridge, MA"},
    {"name": "Stanford University", "location": "Stanford, CA"},
    {"name": "University of California, Berkeley", "location": "Berkeley, CA"},
    {"name": "Harvard University", "location": "Cambridge, MA"},
    {"name": "California Institute of Technology", "location": "Pasadena, CA"},
    {"name": "University of Washington", "location": "Seattle, WA"},
    {"name": "Carnegie Mellon University", "location": "Pittsburgh, PA"},
    {"name": "University of Texas at Austin", "location": "Austin, TX"},
    {"name": "Georgia Institute of Technology", "location": "Atlanta, GA"},
    {"name": "University of Illinois at Urbana-Champaign", "location": "Urbana, IL"},
    {"name": "University of Michigan", "location": "Ann Arbor, MI"},
    {"name": "Cornell University", "location": "Ithaca, NY"},
    {"name": "University of California, Los Angeles", "location": "Los Angeles, CA"},
    {"name": "University of Pennsylvania", "location": "Philadelphia, PA"},
    {"name": "University of Toronto", "location": "Toronto, Canada"},
    {"name": "Imperial College London", "location": "London, UK"},
    {"name": "ETH Zurich", "location": "Zurich, Switzerland"},
    {"name": "National University of Singapore", "location": "Singapore"},
    {"name": "Indian Institute of Technology", "location": "Mumbai, India"},
    {"name": "University of British Columbia", "location": "Vancouver, Canada"}
]

# Companies
TECH_COMPANIES = [
    "Google", "Amazon", "Microsoft", "Meta", "Apple", "Netflix", "Uber", "Airbnb", "Salesforce",
    "Adobe", "IBM", "Oracle", "Intel", "Cisco", "Spotify", "Shopify", "Stripe", "Square",
    "Twitter", "LinkedIn", "Reddit", "Slack", "Atlassian", "Dropbox", "Twilio", "Snap",
    "TechInnovate", "CloudScale", "FinTech Solutions", "DataSystems Inc.", "AI Innovations",
    "WebSolutions", "InfoTech Corp", "Digital Dynamics", "TechStar", "DevOps Masters",
    "ByteWorks", "CloudNative", "DataInsight Analytics", "FrontendPros", "BackendGenius",
    "CodeCraft", "AlgoExperts", "CyberSafe", "NetGuardian", "QuantumBit", "Vision AI"
]

# Major tech hubs
TECH_LOCATIONS = [
    "San Francisco, CA", "San Jose, CA", "Seattle, WA", "Austin, TX", "Boston, MA", 
    "New York, NY", "Los Angeles, CA", "Denver, CO", "Chicago, IL", "Atlanta, GA",
    "Portland, OR", "Toronto, Canada", "Vancouver, Canada", "London, UK", "Berlin, Germany",
    "Dublin, Ireland", "Amsterdam, Netherlands", "Bangalore, India", "Singapore", "Tel Aviv, Israel",
    "Tokyo, Japan", "Sydney, Australia", "Helsinki, Finland", "Paris, France", "Stockholm, Sweden",
    "Zurich, Switzerland", "Barcelona, Spain", "Seoul, South Korea"
]

# Hire3x specific assessments
HIRE3X_ASSESSMENTS = {
    "Frontend Development": ["JavaScript", "React", "Angular", "Vue.js", "HTML", "CSS", "Web Performance", "Responsive Design"],
    "Backend Development": ["Node.js", "Python", "Java", "C#", "Go", "RESTful APIs", "Microservices", "Express.js", "Flask", "Django"],
    "Database Management": ["SQL", "MongoDB", "PostgreSQL", "MySQL", "Database Design", "Data Modeling", "Query Optimization"],
    "Data Science": ["Python", "R", "Statistics", "Machine Learning", "Data Visualization", "Data Cleaning", "Pandas", "NumPy"],
    "Machine Learning": ["TensorFlow", "PyTorch", "Scikit-learn", "NLP", "Computer Vision", "Deep Learning", "Feature Engineering"],
    "DevOps": ["Docker", "Kubernetes", "CI/CD", "AWS", "Azure", "GCP", "Infrastructure as Code", "Terraform", "Jenkins"],
    "Cloud Architecture": ["AWS", "Azure", "GCP", "Cloud Security", "Serverless", "Microservices", "Distributed Systems"],
    "Cybersecurity": ["Network Security", "Penetration Testing", "Security Auditing", "Encryption", "Access Control", "Threat Analysis"],
    "Mobile Development": ["React Native", "Flutter", "iOS", "Android", "Mobile UI Design", "API Integration", "State Management"],
    "QA Automation": ["Selenium", "Cypress", "Jest", "Pytest", "Test Automation", "Test Planning", "Regression Testing"],
    "UI/UX Design": ["Figma", "Adobe XD", "User Research", "Wireframing", "Prototyping", "Usability Testing", "Design Systems"]
}

def generate_random_id(role_prefix):
    """Generate a random ID for a profile based on role prefix."""
    return f"{role_prefix}{random.randint(1000, 9999)}"

def generate_assessment_data(assessment_type):
    """Generate realistic assessment data for a given type."""
    skills_evaluated = random.sample(HIRE3X_ASSESSMENTS[assessment_type], min(5, len(HIRE3X_ASSESSMENTS[assessment_type])))
    
    # Generate realistic score and percentile
    score = round(random.uniform(60.0, 98.0), 1)
    percentile = round(score - random.uniform(0, 15), 1)  # Percentile is usually slightly lower than the score
    
    # Generate completion times
    allowed_time = random.choice([60, 90, 120, 150, 180])
    efficient_rate = random.uniform(0.5, 0.9)  # More efficient candidates complete faster
    completion_time = int(allowed_time * efficient_rate)
    completion_rate = completion_time / allowed_time
    
    # Generate accuracy and confidence
    accuracy = random.uniform(0.7, 0.98)
    confidence_score = accuracy - random.uniform(0, 0.15)  # Confidence usually correlates with accuracy
    
    # Determine proficiency level based on score
    if score >= 90:
        proficiency_level = "Expert"
    elif score >= 80:
        proficiency_level = "Advanced"
    elif score >= 70:
        proficiency_level = "Intermediate"
    else:
        proficiency_level = "Beginner"
    
    # Certificates earned for high scores
    certificates_earned = None
    if score >= 85:
        certificates = [f"Hire3x {assessment_type} {proficiency_level}"]
        if score >= 90:
            specific_skill = random.choice(skills_evaluated)
            certificates.append(f"Hire3x {specific_skill} Expert")
        certificates_earned = certificates
    
    # Generate taken date
    today = datetime.now()
    days_ago = random.randint(1, 365)
    taken_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d")
    
    return {
        "assessment_id": f"hire3x-{assessment_type.lower().replace(' ', '-')}-{random.randint(100, 999)}",
        "name": f"{assessment_type} Assessment",
        "score": score,
        "percentile": percentile,
        "skills_evaluated": skills_evaluated,
        "completion_time": completion_time,
        "allowed_time": allowed_time,
        "completion_rate": round(completion_rate, 2),
        "accuracy": round(accuracy, 2),
        "confidence_score": round(confidence_score, 2),
        "taken_date": taken_date,
        "proficiency_level": proficiency_level,
        "test_duration_minutes": allowed_time,
        "certificates_earned": certificates_earned
    }

def generate_course_data(category):
    """Generate realistic course data."""
    course_names = {
        "Frontend Development": [
            "Advanced React Patterns & Performance", 
            "Modern JavaScript: ES6 and Beyond",
            "CSS Grid and Flexbox Mastery",
            "Advanced TypeScript for React Developers",
            "Web Performance Optimization",
            "Progressive Web App Development",
            "State Management with Redux and Context API",
            "UI Animation with CSS and JavaScript",
            "Responsive Design for Mobile-First Development"
        ],
        "Backend Development": [
            "Building Scalable APIs with Node.js",
            "Python for Backend Development",
            "Java Spring Boot Masterclass",
            "Microservices Architecture",
            "RESTful API Design Best Practices",
            "GraphQL API Development",
            "Authentication and Authorization Strategies",
            "Database Optimization Techniques",
            "Event-Driven Architecture"
        ],
        "Data Science": [
            "Data Science with Python",
            "Machine Learning Fundamentals",
            "Advanced Data Visualization",
            "Statistical Analysis for Data Science",
            "Natural Language Processing",
            "Time Series Analysis and Forecasting",
            "Deep Learning with TensorFlow",
            "Feature Engineering for Machine Learning",
            "Data Cleaning and Preprocessing"
        ],
        "DevOps": [
            "Docker and Kubernetes in Production",
            "CI/CD Pipeline Implementation",
            "Infrastructure as Code with Terraform",
            "Cloud Migration Strategies",
            "Site Reliability Engineering",
            "Monitoring and Observability",
            "GitOps Workflows",
            "Security in DevOps Pipelines",
            "Performance Optimization for Cloud Applications"
        ],
        "Mobile Development": [
            "React Native for Cross-Platform Apps",
            "Swift for iOS Development",
            "Android App Development with Kotlin",
            "Flutter and Dart Masterclass",
            "Mobile UI/UX Design Patterns",
            "State Management in Mobile Apps",
            "Offline-First Mobile Applications",
            "Publishing and Monetizing Mobile Apps"
        ],
        "Cloud Architecture": [
            "AWS Solutions Architecture",
            "Azure Cloud Infrastructure",
            "GCP Professional Cloud Architect",
            "Multi-Cloud Strategies",
            "Serverless Architecture Patterns",
            "Cloud Security Best Practices",
            "Cost Optimization in the Cloud",
            "Designing Highly Available Systems"
        ],
        "Machine Learning": [
            "Deep Learning Specialization",
            "Computer Vision with PyTorch",
            "Natural Language Processing with BERT",
            "Reinforcement Learning Fundamentals",
            "GANs and Generative Models",
            "MLOps: Model Deployment and Monitoring",
            "Ethics in Machine Learning",
            "Transfer Learning and Fine-Tuning"
        ]
    }
    
    if category not in course_names:
        category = random.choice(list(course_names.keys()))
    
    course_name = random.choice(course_names[category])
    completion_status = random.choices(["Completed", "In Progress"], weights=[0.8, 0.2])[0]
    
    # Generate completion date
    today = datetime.now()
    days_ago = random.randint(30, 365)
    completion_date = (today - timedelta(days=days_ago)).strftime("%Y-%m-%d") if completion_status == "Completed" else None
    
    # Generate assignments data
    assignments_total = random.randint(5, 15)
    assignment_avg_score = round(random.uniform(80.0, 98.0), 1) if completion_status == "Completed" else None
    instructor_evaluation = round(random.uniform(4.0, 5.0), 1) if completion_status == "Completed" else None
    
    # Generate capstone project score for some courses
    capstone_project_score = round(random.uniform(85.0, 98.0), 1) if completion_status == "Completed" and random.random() > 0.5 else None
    
    return {
        "name": course_name,
        "category": category,
        "completion_status": completion_status,
        "completion_date": completion_date,
        "assignments_total": assignments_total,
        "assignment_avg_score": assignment_avg_score,
        "instructor_evaluation": instructor_evaluation,
        "capstone_project_score": capstone_project_score
    }

def generate_skill_validation(skill, assessment_score=None):
    """Generate realistic skill validation data."""
    validation_sources = [
        "Assessment",
        "Assessment + Course Performance",
        "Assessment + Course Performance + Certification",
        "Course Performance",
        "Practical Project"
    ]
    
    if assessment_score:
        validated_level = round(assessment_score / 100, 2)
    else:
        validated_level = round(random.uniform(0.7, 0.95), 2)
    
    confidence_levels = ["High", "Medium", "Low"]
    confidence_weights = [0.7, 0.2, 0.1]
    
    confidence = random.choices(confidence_levels, weights=confidence_weights)[0]
    
    # High confidence skills have higher scores
    base_score = 85 if confidence == "High" else 75 if confidence == "Medium" else 65
    variation = 10
    
    practical_score = round(random.uniform(base_score, base_score + variation), 1)
    theoretical_score = round(random.uniform(base_score - 5, base_score + variation - 5), 1)
    
    return {
        "skill": skill,
        "validation_source": random.choice(validation_sources),
        "validated_level": validated_level,
        "confidence": confidence,
        "practical_application_score": practical_score,
        "theoretical_knowledge_score": theoretical_score
    }

def generate_learning_patterns():
    """Generate realistic learning pattern data."""
    preferred_times = ["Morning", "Afternoon", "Evening", "Late Night"]
    learning_styles = [
        "Practical-focused",
        "Theory-focused",
        "Balanced",
        "Project-based",
        "Self-paced",
        "Social Learning"
    ]
    
    return {
        "preferred_learning_time": random.choice(preferred_times),
        "average_session_duration": random.randint(30, 120),
        "consistency_score": round(random.uniform(0.6, 0.95), 2),
        "completion_tendency": round(random.uniform(0.7, 0.98), 2),
        "learning_style": random.choice(learning_styles)
    }

def generate_education_entry(grad_year, is_master=False):
    """Generate a realistic education entry with GPA/percentage."""
    university = random.choice(UNIVERSITIES)
    
    # Determine degree type
    if is_master:
        degree_type = random.choice(["Master of Science", "Master's", "Master of Engineering", "Master of Arts"])
        fields = ["Computer Science", "Data Science", "Software Engineering", "Information Technology", 
                 "Artificial Intelligence", "Machine Learning", "Cybersecurity", "Human-Computer Interaction"]
    else:
        degree_type = random.choice(["Bachelor of Science", "Bachelor's", "Bachelor of Engineering", "Bachelor of Arts"])
        fields = ["Computer Science", "Computer Engineering", "Software Engineering", "Information Systems",
                 "Electrical Engineering", "Mathematics and Computer Science", "Information Technology"]
    
    field_of_study = random.choice(fields)
    
    # Add GPA or percentage
    use_gpa = random.random() > 0.3  # 70% chance to use GPA system
    if use_gpa:
        gpa = round(random.uniform(3.0, 4.0), 2)
        return {
            "institution": university["name"],
            "location": university["location"],
            "degree": degree_type,
            "field_of_study": field_of_study,
            "graduation_year": grad_year,
            "gpa": gpa
        }
    else:
        percentage = round(random.uniform(75.0, 98.0), 1)
        return {
            "institution": university["name"],
            "location": university["location"],
            "degree": degree_type,
            "field_of_study": field_of_study,
            "graduation_year": grad_year,
            "percentage": percentage
        }
def generate_experience_entry(company, role, is_current, years_ago_ended, duration_years):
    """Generate a realistic experience entry."""
    # Create description based on role
    role_lower = role.lower()
    
    if "full stack" in role_lower:
        description = f"{'Leading' if is_current else 'Led'} development of {'the company\'s' if is_current else 'a'} web application platform using modern technologies and best practices. {'Responsible for' if is_current else 'Handled'} both frontend and backend implementation."
        skills = ["JavaScript", "TypeScript", "React", "Node.js", "Express", "MongoDB", "PostgreSQL", "AWS", "Docker"]
    
    elif "frontend" in role_lower:
        description = f"{'Developing' if is_current else 'Developed'} responsive and accessible user interfaces for {'enterprise' if is_current else 'business'} applications using modern JavaScript frameworks and UI/UX best practices."
        skills = ["JavaScript", "TypeScript", "React", "Vue.js", "Angular", "CSS", "Sass", "Webpack", "Jest"]
    
    elif "backend" in role_lower:
        description = f"{'Designing' if is_current else 'Designed'} and {'implementing' if is_current else 'implemented'} scalable APIs and services for high-traffic applications. {'Managing' if is_current else 'Managed'} database design and optimization."
        skills = ["Java", "Spring Boot", "Python", "Django", "Node.js", "Express", "SQL", "NoSQL", "Microservices"]
    
    elif "data sci" in role_lower:
        description = f"{'Building' if is_current else 'Built'} predictive models and {'performing' if is_current else 'performed'} data analysis to extract business insights. {'Working' if is_current else 'Worked'} with stakeholders to translate business problems into data solutions."
        skills = ["Python", "R", "SQL", "Machine Learning", "Statistical Analysis", "Data Visualization", "Pandas", "TensorFlow"]
    
    elif "machine learning" in role_lower:
        description = f"{'Developing' if is_current else 'Developed'} and {'deploying' if is_current else 'deployed'} machine learning models for production use. {'Optimizing' if is_current else 'Optimized'} model performance and {'implementing' if is_current else 'implemented'} ML pipelines."
        skills = ["Python", "TensorFlow", "PyTorch", "ML Ops", "Data Processing", "Computer Vision", "NLP"]
    
    elif "devops" in role_lower:
        description = f"{'Managing' if is_current else 'Managed'} cloud infrastructure and {'implementing' if is_current else 'implemented'} CI/CD pipelines. {'Responsible for' if is_current else 'Ensured'} system reliability and performance optimization."
        skills = ["AWS", "Kubernetes", "Docker", "Terraform", "Jenkins", "CI/CD", "Monitoring", "Linux"]
    
    else:
        description = f"{'Working' if is_current else 'Worked'} on development and maintenance of software applications. {'Collaborating' if is_current else 'Collaborated'} with cross-functional teams to deliver high-quality products."
        skills = ["Programming", "Software Development", "Agile", "Git", "Testing", "Documentation"]
    
    # Generate random achievements
    achievements_pool = [
        f"Reduced application loading time by {random.randint(20, 60)}%",
        f"Improved system performance by {random.randint(15, 50)}%",
        f"Implemented CI/CD pipeline reducing deployment time by {random.randint(40, 80)}%",
        f"Increased test coverage from {random.randint(40, 60)}% to {random.randint(80, 95)}%",
        f"Optimized database queries reducing response time by {random.randint(30, 70)}%",
        f"Led team of {random.randint(2, 8)} {'developers' if 'develop' in role_lower else 'engineers'}",
        f"Reduced infrastructure costs by {random.randint(20, 40)}%",
        f"Designed and implemented new architecture that scaled to {random.randint(5, 20)}x traffic",
        f"Automated processes saving {random.randint(5, 20)} hours per week",
        f"Built {random.choice(['monitoring', 'analytics', 'reporting'])} system that improved decision-making",
        f"Delivered {random.randint(3, 10)} major features ahead of schedule",
        f"Successfully migrated from {random.choice(['monolith to microservices', 'on-prem to cloud', 'legacy system to modern stack'])}",
        f"Mentored {random.randint(2, 5)} junior team members"
    ]
    
    num_achievements = random.randint(1, 3)
    achievements = random.sample(achievements_pool, num_achievements)
    
    used_skills = random.sample(skills, min(len(skills), random.randint(3, 7)))
    
    return {
        "company": company,
        "role": role,
        "current": is_current,
        "description": description,
        "skills_used": used_skills,
        "achievements": achievements,
        "duration_years": duration_years
    }


def generate_projects(skills, role):
    """Generate realistic projects based on skills and role."""
    num_projects = random.randint(1, 3)
    projects = []
    
    project_types = {
        "Full Stack Developer": [
            "E-commerce Platform", "Collaboration Tool", "Content Management System", 
            "Social Network App", "Project Management Tool", "Customer Portal"
        ],
        "Frontend Engineer": [
            "Design System", "Dashboard UI", "Interactive Visualization", 
            "Progressive Web App", "Responsive Website", "Accessibility Framework"
        ],
        "Backend Engineer": [
            "API Gateway", "Microservice Architecture", "Authentication System", 
            "Data Processing Pipeline", "Message Queue System", "Search Engine"
        ],
        "DevOps Engineer": [
            "CI/CD Pipeline", "Infrastructure as Code", "Monitoring System", 
            "Auto-scaling Configuration", "Disaster Recovery System", "Security Automation"
        ],
        "Data Scientist": [
            "Predictive Model", "Data Visualization Dashboard", "Recommendation System", 
            "Anomaly Detection", "Customer Segmentation", "Forecasting System"
        ],
        "Machine Learning Engineer": [
            "Computer Vision System", "NLP Processing Pipeline", "Sentiment Analysis", 
            "Image Recognition", "Voice Assistant", "Reinforcement Learning Model"
        ]
    }
    
    # Default to Full Stack if role not found
    role_category = next((k for k in project_types.keys() if k.lower() in role.lower()), "Full Stack Developer")
    
    for _ in range(num_projects):
        project_name = random.choice(project_types.get(role_category, project_types["Full Stack Developer"]))
        
        # Create description based on project name
        if "E-commerce" in project_name:
            description = f"Built a scalable e-commerce platform supporting {random.randint(5, 100)}k+ daily active users with features including product catalog, shopping cart, payment integration, and order tracking."
        elif "Collaboration" in project_name:
            description = f"Developed a real-time document collaboration tool with features like concurrent editing, commenting, and version history."
        elif "API" in project_name:
            description = f"Designed and implemented a configurable API gateway with rate limiting, authentication, and monitoring capabilities."
        elif "Predictive Model" in project_name:
            description = f"Created a machine learning model to predict {random.choice(['customer churn', 'product demand', 'price fluctuations', 'user behavior'])} with {random.randint(80, 95)}% accuracy."
        elif "Computer Vision" in project_name:
            description = f"Developed an end-to-end computer vision system for {random.choice(['object detection', 'facial recognition', 'defect identification', 'medical imaging analysis'])}."
        elif "CI/CD" in project_name:
            description = f"Implemented continuous integration and deployment pipeline reducing deployment time from {random.choice(['days to hours', 'hours to minutes', 'days to minutes'])}."
        else:
            description = f"Developed a {random.choice(['high-performance', 'scalable', 'user-friendly', 'efficient'])} {project_name.lower()} that {random.choice(['improved user engagement', 'increased productivity', 'reduced operational costs', 'enhanced data insights'])}."
        
        # Select technologies based on role and skills
        tech_pool = list(skills.keys())
        technologies = random.sample(tech_pool, min(len(tech_pool), random.randint(3, 6)))
        
        # Generate skills gained
        skills_gained_pool = [
            "System Architecture", "Performance Optimization", "User Experience Design",
            "API Design", "Database Optimization", "Security Best Practices",
            "Scalability", "Caching Strategies", "Real-time Communication",
            "Authentication", "Concurrency Management", "Data Modeling",
            "CI/CD", "Cloud Deployment", "Testing Strategies",
            "Monitoring", "Responsive Design", "Accessibility",
            "State Management", "Code Organization", "Documentation",
            "Payment Processing", "Search Optimization", "Data Visualization",
            "Feature Engineering", "Model Training", "Hyperparameter Tuning"
        ]
        
        skills_gained = random.sample(skills_gained_pool, random.randint(2, 4))
        
        projects.append({
            "name": project_name,
            "description": description,
            "technologies": technologies,
            "skills_gained": skills_gained
        })
    
    return projects

def generate_certifications(role):
    """Generate realistic certifications based on role."""
    all_certifications = {
        "AWS": [
            {"name": "AWS Certified Solutions Architect - Associate", "skills_validated": ["AWS Architecture", "Cloud Security", "Scalable Systems"]},
            {"name": "AWS Certified Developer - Associate", "skills_validated": ["AWS Services", "Cloud Development", "Security"]},
            {"name": "AWS Certified DevOps Engineer - Professional", "skills_validated": ["CI/CD", "Infrastructure Automation", "Monitoring", "AWS Services"]}
        ],
        "Azure": [
            {"name": "Microsoft Certified: Azure Solutions Architect", "skills_validated": ["Azure Architecture", "Cloud Design", "Security"]},
            {"name": "Microsoft Certified: Azure Developer Associate", "skills_validated": ["Azure Services", "Cloud Applications", "Azure SDKs"]}
        ],
        "Google Cloud": [
            {"name": "Google Cloud Certified - Professional Cloud Architect", "skills_validated": ["GCP Architecture", "Cloud Solutions", "Security"]}
        ],
        "DevOps": [
            {"name": "Certified Kubernetes Administrator (CKA)", "skills_validated": ["Kubernetes", "Container Orchestration", "Cluster Management"]},
            {"name": "Docker Certified Associate", "skills_validated": ["Docker", "Containerization", "Image Management"]},
            {"name": "HashiCorp Certified Terraform Associate", "skills_validated": ["Terraform", "Infrastructure as Code", "State Management"]}
        ],
        "Data": [
            {"name": "MongoDB Certified Developer", "skills_validated": ["MongoDB Design", "NoSQL", "Database Performance"]},
            {"name": "Cloudera Certified Data Analyst", "skills_validated": ["Big Data", "Data Analysis", "SQL"]},
            {"name": "Microsoft Certified: Azure Data Scientist Associate", "skills_validated": ["Data Science", "Azure ML", "Data Analysis"]}
        ],
        "Programming": [
            {"name": "Oracle Certified Professional, Java SE 11 Programmer", "skills_validated": ["Java", "Object-Oriented Programming", "JVM"]},
            {"name": "Microsoft Certified: .NET Developer", "skills_validated": [".NET Framework", "C#", "ASP.NET"]}
        ],
        "AI/ML": [
            {"name": "TensorFlow Developer Certificate", "skills_validated": ["TensorFlow", "Deep Learning", "Neural Networks"]},
            {"name": "Google Professional Machine Learning Engineer", "skills_validated": ["ML Systems", "MLOps", "Model Deployment"]},
            {"name": "NVIDIA Deep Learning Institute: Computer Vision", "skills_validated": ["Computer Vision", "GPU Acceleration", "Model Deployment"]}
        ],
        "Security": [
            {"name": "Certified Information Systems Security Professional (CISSP)", "skills_validated": ["Security Management", "Risk Management", "Security Architecture"]},
            {"name": "Certified Ethical Hacker (CEH)", "skills_validated": ["Penetration Testing", "Vulnerability Assessment", "Security Tools"]},
            {"name": "CompTIA Security+", "skills_validated": ["Network Security", "Compliance", "Identity Management"]}
        ],
        "Web": [
            {"name": "Professional Front-End Developer Certification", "skills_validated": ["JavaScript", "React", "Performance"]},
            {"name": "Web Accessibility Specialist (WAS)", "skills_validated": ["WCAG Guidelines", "Accessible Design", "Screen Reader Compatibility"]}
        ]
    }
    
    # Determine relevant categories based on role
    role_lower = role.lower()
    relevant_categories = []
    
    if "frontend" in role_lower or "full stack" in role_lower:
        relevant_categories.extend(["Web", "Programming"])
    if "backend" in role_lower or "full stack" in role_lower:
        relevant_categories.extend(["Programming", "Data"])
    if "data" in role_lower or "machine learning" in role_lower:
        relevant_categories.extend(["Data", "AI/ML"])
    if "devops" in role_lower or "cloud" in role_lower:
        relevant_categories.extend(["DevOps", "AWS", "Azure", "Google Cloud"])
    if "security" in role_lower:
        relevant_categories.extend(["Security"])
    
    # Default case if no matching categories
    if not relevant_categories:
        relevant_categories = list(all_certifications.keys())
    
    # Deduplicate categories
    relevant_categories = list(set(relevant_categories))
    
    # Determine number of certifications (0-3)
    num_certs = random.randint(0, 3)
    if num_certs == 0:
        return []
    
    certifications = []
    for _ in range(num_certs):
        # Choose a random category from relevant ones
        category = random.choice(relevant_categories)
        # Choose a random certification from that category
        cert = random.choice(all_certifications[category])
        # Add to list if not already present
        if cert not in certifications:
            certifications.append(cert)
    
    return certifications

def generate_skills_for_role(role):
    """Generate a dictionary of skills and proficiency levels based on role."""
    skills = {}
    
    # Common skills for most tech roles
    common_skills = {
        "Git": (0.7, 0.95),
        "Agile": (0.7, 0.9),
        "Communication": (0.7, 0.95),
        "Problem Solving": (0.75, 0.95)
    }
    
    # Role-specific skills
    role_skills = {}
    
    role_lower = role.lower()
    
    if "full stack" in role_lower:
        role_skills = {
            "JavaScript": (0.8, 0.95),
            "TypeScript": (0.7, 0.9),
            "React": (0.75, 0.95),
            "Node.js": (0.75, 0.9),
            "Express": (0.7, 0.9),
            "HTML/CSS": (0.8, 0.95),
            "MongoDB": (0.7, 0.9),
            "SQL": (0.7, 0.9),
            "RESTful APIs": (0.8, 0.95),
            "AWS": (0.7, 0.9),
            "Docker": (0.6, 0.85),
            "CI/CD": (0.6, 0.85),
            "System Design": (0.7, 0.9)
        }
    
    elif "frontend" in role_lower:
        role_skills = {
            "JavaScript": (0.8, 0.95),
            "TypeScript": (0.7, 0.95),
            "React": (0.75, 0.95),
            "Vue.js": (0.7, 0.9),
            "Angular": (0.7, 0.9),
            "HTML5": (0.8, 0.95),
            "CSS3/SCSS": (0.8, 0.95),
            "Responsive Design": (0.8, 0.95),
            "Web Accessibility": (0.7, 0.9),
            "UI/UX": (0.7, 0.9),
            "Jest": (0.7, 0.9),
            "Webpack": (0.7, 0.9),
            "Performance Optimization": (0.7, 0.9),
            "State Management": (0.7, 0.9)
        }
    
    elif "backend" in role_lower:
        role_skills = {
            "Java": (0.75, 0.95),
            "Spring Boot": (0.7, 0.9),
            "Python": (0.75, 0.95),
            "Django": (0.7, 0.9),
            "Node.js": (0.75, 0.95),
            "Express": (0.7, 0.9),
            "SQL": (0.8, 0.95),
            "NoSQL": (0.7, 0.9),
            "RESTful APIs": (0.8, 0.95),
            "Microservices": (0.7, 0.9),
            "System Design": (0.75, 0.95),
            "API Security": (0.7, 0.9),
            "Database Design": (0.75, 0.95),
            "Performance Tuning": (0.7, 0.9)
        }
    
    elif "data sci" in role_lower:
        role_skills = {
            "Python": (0.8, 0.95),
            "R": (0.7, 0.9),
            "SQL": (0.75, 0.95),
            "Machine Learning": (0.75, 0.95),
            "Statistical Analysis": (0.8, 0.95),
            "Pandas": (0.8, 0.95),
            "NumPy": (0.8, 0.95),
            "SciPy": (0.7, 0.9),
            "Data Visualization": (0.75, 0.95),
            "Feature Engineering": (0.75, 0.9),
            "A/B Testing": (0.7, 0.9),
            "Data Cleaning": (0.8, 0.95),
            "Scikit-learn": (0.75, 0.9),
            "TensorFlow": (0.7, 0.9)
        }
    
    elif "machine learning" in role_lower:
        role_skills = {
            "Python": (0.8, 0.95),
            "TensorFlow": (0.75, 0.95),
            "PyTorch": (0.75, 0.95),
            "Deep Learning": (0.75, 0.95),
            "NLP": (0.7, 0.9),
            "Computer Vision": (0.7, 0.9),
            "Feature Engineering": (0.8, 0.95),
            "MLOps": (0.7, 0.9),
            "Model Deployment": (0.75, 0.9),
            "Data Processing": (0.8, 0.95),
            "Scikit-learn": (0.8, 0.95),
            "Pandas": (0.8, 0.95),
            "NumPy": (0.8, 0.95),
            "Keras": (0.7, 0.9)
        }
    
    elif "devops" in role_lower:
        role_skills = {
            "AWS": (0.75, 0.95),
            "Azure": (0.7, 0.9),
            "GCP": (0.7, 0.9),
            "Docker": (0.8, 0.95),
            "Kubernetes": (0.75, 0.95),
            "CI/CD": (0.8, 0.95),
            "Terraform": (0.75, 0.95),
            "Ansible": (0.7, 0.9),
            "Jenkins": (0.7, 0.9),
            "Linux": (0.8, 0.95),
            "Bash": (0.75, 0.95),
            "Python": (0.7, 0.9),
            "Infrastructure as Code": (0.8, 0.95),
            "Monitoring/Observability": (0.75, 0.95)
        }
    
    else:
        # Default tech skills for other roles
        role_skills = {
            "JavaScript": (0.7, 0.9),
            "Python": (0.7, 0.9),
            "SQL": (0.7, 0.9),
            "HTML/CSS": (0.7, 0.9),
            "System Design": (0.7, 0.9),
            "AWS": (0.7, 0.9)
        }
    
    # Combine common and role-specific skills
    all_skills = {**common_skills, **role_skills}
    
    # Randomly select 70-90% of the skills
    num_skills = random.randint(int(0.7 * len(all_skills)), min(int(0.9 * len(all_skills)), len(all_skills)))
    selected_skills = random.sample(list(all_skills.keys()), num_skills)
    
    # Assign random proficiency levels within the appropriate ranges
    for skill in selected_skills:
        min_val, max_val = all_skills[skill]
        proficiency = round(random.uniform(min_val, max_val), 2)
        skills[skill] = proficiency
    
    return skills

def generate_languages():
    """Generate a set of spoken languages with proficiency levels."""
    all_languages = [
        "English", "Spanish", "French", "German", "Mandarin", "Hindi", "Portuguese", 
        "Japanese", "Arabic", "Russian", "Italian", "Korean", "Dutch", "Swedish", 
        "Hebrew", "Turkish", "Polish", "Vietnamese", "Farsi", "Urdu", "Bengali", 
        "Greek", "Cantonese", "Thai", "Finnish"
    ]
    
    proficiency_levels = ["Native", "Fluent", "Conversational", "Intermediate", "Basic"]
    proficiency_weights = [0.2, 0.2, 0.2, 0.2, 0.2]
    
    # English is almost always included
    languages = {"English": random.choices(proficiency_levels, weights=[0.7, 0.2, 0.05, 0.03, 0.02])[0]}
    
    # Determine how many additional languages (0-3)
    num_additional = random.choices([0, 1, 2, 3], weights=[0.3, 0.4, 0.2, 0.1])[0]
    
    if num_additional > 0:
        additional_languages = random.sample([lang for lang in all_languages if lang != "English"], num_additional)
        for lang in additional_languages:
            languages[lang] = random.choices(proficiency_levels, weights=proficiency_weights)[0]
    
    return languages

def generate_realistic_candidate(index):
    """Generate a realistic candidate profile."""
    # Select a random tech role type
    role_info = random.choice(TECH_ROLES)
    role_type = role_info["role"]
    specialties = role_info["specialties"]
    
    # Determine role prefix for ID
    if "Full Stack" in role_type:
        role_prefix = "fs"
    elif "Frontend" in role_type:
        role_prefix = "fe"
    elif "Backend" in role_type:
        role_prefix = "be"
    elif "DevOps" in role_type:
        role_prefix = "do"
    elif "Data Scientist" in role_type:
        role_prefix = "ds"
    elif "Machine Learning" in role_type:
        role_prefix = "ml"
    elif "Cloud" in role_type:
        role_prefix = "ca"
    elif "Security" in role_type:
        role_prefix = "se"
    elif "Mobile" in role_type:
        role_prefix = "md"
    elif "QA" in role_type:
        role_prefix = "qa"
    elif "UI/UX" in role_type:
        role_prefix = "ux"
    else:
        role_prefix = "tech"
    
    # Generate a random ID
    candidate_id = f"{role_prefix}{random.randint(100, 999)}"
    
    # Generate name
    gender = random.choice(["male", "female"])
    first_name = names.get_first_name(gender=gender)
    last_name = names.get_last_name()
    full_name = f"{first_name} {last_name}"
    
    # Generate contact info
    email = f"{first_name.lower()}.{last_name.lower()}@example.com"
    phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
    
    # Generate online profiles
    github_username = f"{first_name.lower()}{last_name.lower()[0]}"
    linkedin_username = f"{first_name.lower()}-{last_name.lower()}"
    portfolio_domain = random.choice([f"{first_name.lower()}{last_name.lower()}", f"{first_name.lower()}-{last_name.lower()}", f"{first_name.lower()}.{last_name.lower()}"])
    portfolio_tld = random.choice([".dev", ".io", ".com", ".tech", ".me"])
    
    # Generate location
    location = random.choice(TECH_LOCATIONS)
    
    # Generate headline and summary
    specialty = random.choice(specialties)
    secondary_specialty = random.choice([s for s in specialties if s != specialty])
    headline = f"{role_type} specializing in {specialty}, {secondary_specialty}, and {random.choice([s for s in specialties if s != specialty and s != secondary_specialty])}"
    
    years_experience = round(random.uniform(1.0, 15.0), 1)
    
    summary_templates = [
        f"Experienced {role_type.lower()} with {years_experience}+ years of expertise in building {random.choice(['scalable', 'robust', 'high-performance', 'enterprise-grade'])} applications. Proficient in {specialty}, {secondary_specialty}, and various other technologies.",
        f"Results-driven {role_type.lower()} with {years_experience}+ years of experience applying {specialty} and {secondary_specialty} to solve complex business problems. Passionate about {random.choice(['clean code', 'user experience', 'performance optimization', 'scalable architecture'])}.",
        f"Innovative {role_type.lower()} with {years_experience}+ years of hands-on experience developing {random.choice(['web applications', 'enterprise solutions', 'consumer products', 'data pipelines'])}. Strong background in {specialty} and {secondary_specialty}."
    ]
    
    summary = random.choice(summary_templates)
    
    # Generate current role
    company = random.choice(TECH_COMPANIES)
    current_role = f"{random.choice(['Senior ', '', 'Lead '])}{role_type} at {company}"
    
    # Generate education
    current_year = datetime.now().year
    bs_year = current_year - random.randint(int(years_experience) + 2, int(years_experience) + 8)
    ms_year = bs_year + random.randint(2, 4) if random.random() > 0.6 else None  # 40% chance of no master's
    
    education = [generate_education_entry(bs_year, False)]
    if ms_year:
        education.append(generate_education_entry(ms_year, True))
    
    # Sort education by graduation year (most recent first)
    education.sort(key=lambda x: x["graduation_year"], reverse=True)
    
    # Generate experience
    experience = []
    
    # Current job
    experience.append(generate_experience_entry(
        company, 
        current_role.split(" at ")[0],  # Role without company
        True,  # Current
        0,  # Not ended
        random.uniform(0.5, min(3.0, years_experience))  # Duration at current job
    ))
    
    # Previous jobs
    remaining_years = years_experience - experience[0]["duration_years"]
    years_ago_ended = experience[0]["duration_years"]
    
    while remaining_years > 0.5:  # At least 6 months at each job
        job_duration = random.uniform(0.5, min(4.0, remaining_years))
        
        # Previous company can't be the same as current
        prev_company = random.choice([c for c in TECH_COMPANIES if c != company])
        
        # Role title often depends on experience level
        if remaining_years < 2:
            role_title = f"{random.choice(['Junior ', ''])}{role_type}"
        elif remaining_years < 5:
            role_title = role_type
        else:
            role_title = f"{random.choice(['Senior ', 'Lead ', ''])}{role_type}"
        
        experience.append(generate_experience_entry(
            prev_company,
            role_title,
            False,  # Not current
            years_ago_ended,
            job_duration
        ))
        
        remaining_years -= job_duration
        years_ago_ended += job_duration
        company = prev_company  # Update for next iteration
    
    # Generate skills
    skills = generate_skills_for_role(role_type)
    
    # Generate projects
    projects = generate_projects(skills, role_type)
    
    # Generate certifications
    certifications = generate_certifications(role_type)
    
    # Generate languages
    languages = generate_languages()
    
    # Generate Hire3x data
    joined_date = (datetime.now() - timedelta(days=random.randint(30, 730))).strftime("%Y-%m-%d")
    
    # Determine assessment types based on role
    assessment_types = []
    if "Full Stack" in role_type:
        assessment_types = ["Frontend Development", "Backend Development"]
    elif "Frontend" in role_type:
        assessment_types = ["Frontend Development"]
    elif "Backend" in role_type:
        assessment_types = ["Backend Development"]
    elif "DevOps" in role_type:
        assessment_types = ["DevOps", "Cloud Architecture"]
    elif "Data Scientist" in role_type:
        assessment_types = ["Data Science"]
    elif "Machine Learning" in role_type:
        assessment_types = ["Machine Learning", "Data Science"]
    else:
        # Find the closest category
        for assessment_type in HIRE3X_ASSESSMENTS.keys():
            if any(keyword.lower() in role_type.lower() for keyword in assessment_type.split()):
                assessment_types.append(assessment_type)
        
        # Default to Frontend and Backend if no match
        if not assessment_types:
            assessment_types = ["Frontend Development", "Backend Development"]
    
    num_assessments = random.randint(1, len(assessment_types))
    chosen_assessment_types = random.sample(assessment_types, num_assessments)
    
    assessments = [generate_assessment_data(assessment_type) for assessment_type in chosen_assessment_types]
    
    # Generate courses based on assessment types
    courses = []
    for _ in range(random.randint(1, 3)):
        course_category = random.choice(chosen_assessment_types)
        courses.append(generate_course_data(course_category))
    
    # Generate skill validations
    top_skills = sorted(skills.items(), key=lambda x: x[1], reverse=True)[:5]
    skill_validations = [generate_skill_validation(skill, skills[skill] * 100) for skill, _ in top_skills]
    
    # Generate learning patterns
    learning_patterns = generate_learning_patterns()
    
    # Generate availability and preferences
    availability_options = ["Immediately", "2 weeks notice", "1 month notice", "2 months notice", "3 months notice"]
    availability_weights = [0.2, 0.4, 0.3, 0.05, 0.05]
    availability = random.choices(availability_options, weights=availability_weights)[0]
    
    desired_role_options = [
        f"Senior {role_type}",
        f"Lead {role_type}",
        f"{role_type} Manager",
        f"Principal {role_type}",
        f"{role_type}"
    ]
    desired_role = random.choice(desired_role_options)
    
    preferred_work_type_options = ["Remote", "Hybrid", "On-site", "Flexible"]
    preferred_work_type_weights = [0.4, 0.4, 0.1, 0.1]
    preferred_work_type = random.choices(preferred_work_type_options, weights=preferred_work_type_weights)[0]
    
    return {
        "id": candidate_id,
        "name": full_name,
        "email": email,
        "phone": phone,
        "linkedin_url": f"https://linkedin.com/in/{linkedin_username}",
        "github_url": f"https://github.com/{github_username}",
        "portfolio_url": f"https://{portfolio_domain}{portfolio_tld}",
        "location": location,
        "headline": headline,
        "summary": summary,
        "current_role": current_role,
        "years_of_experience": years_experience,
        "education": education,
        "experience": experience,
        "skills": skills,
        "projects": projects,
        "certifications": certifications,
        "languages": languages,
        "hire3x_data": {
            "joined_date": joined_date,
            "profile_completion": random.randint(85, 100),
            "activity_score": random.randint(70, 98),
            "login_frequency": f"{round(random.uniform(1.0, 7.0), 1)} times/week",
            "assessments": assessments,
            "courses": courses,
            "skill_validations": skill_validations,
            "learning_patterns": learning_patterns
        },
        "availability": availability,
        "desired_role": desired_role,
        "preferred_work_type": preferred_work_type
    }

def generate_realistic_candidates(num_candidates=100):
    """Generate a specified number of realistic candidate profiles."""
    candidates = []
    
    for i in range(num_candidates):
        candidate = generate_realistic_candidate(i)
        candidates.append(candidate)
    
    # Save to file
    with open("data/sample_candidates.json", "w") as f:
        json.dump(candidates, f, indent=2)
    
    print(f"Generated {len(candidates)} sample candidates.")
    print("Files saved to data/sample_candidates.json")
    
    return candidates

if __name__ == "__main__":
    # Generate 100 realistic candidates
    generate_realistic_candidates(100)