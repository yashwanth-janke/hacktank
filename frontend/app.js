// Frontend JavaScript for Hire3x Candidate Matching System
const API_URL = 'http://localhost:8000/api';

// DOM Elements
const jobForm = document.getElementById('job-description-form');
const uploadForm = document.getElementById('upload-form');
const requiredSkillsList = document.getElementById('required-skills-list');
const requirementsList = document.getElementById('requirements-list');
const responsibilitiesList = document.getElementById('responsibilities-list');
const candidatesList = document.getElementById('candidates-list');
const resultCount = document.getElementById('result-count');
const candidateCountBadge = document.getElementById('candidate-count-badge');
const loading = document.getElementById('loading');
const noResults = document.getElementById('no-results');
const resultsContainer = document.getElementById('results-container');
const resetFormBtn = document.getElementById('reset-form-btn');
const exportResultsBtn = document.getElementById('export-results-btn');

// Dynamic fields
const addSkillBtn = document.querySelector('.add-skill-btn');
const addRequirementBtn = document.querySelector('.add-requirement-btn');
const addResponsibilityBtn = document.querySelector('.add-responsibility-btn');

// Current job data
let currentJob = null;
let matchedCandidates = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupDynamicFields();
    setupEventListeners();
    fetchCandidateCount();
});

// Setup event listeners
function setupEventListeners() {
    // Job form submission
    jobForm.addEventListener('submit', handleJobFormSubmit);
    
    // Upload form submission
    uploadForm.addEventListener('submit', handleUploadFormSubmit);
    
    // Reset form button
    resetFormBtn.addEventListener('click', resetJobForm);
    
    // Export results button
    exportResultsBtn.addEventListener('click', exportResultsAsPDF);
}

// Setup dynamic fields (skills, requirements, responsibilities)
function setupDynamicFields() {
    // Required Skills
    addSkillBtn.addEventListener('click', () => {
        const input = document.querySelector('.required-skill-input');
        const skill = input.value.trim();
        
        if (skill) {
            addSkillTag(skill);
            input.value = '';
            input.focus();
        }
    });
    
    document.querySelector('.required-skill-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addSkillBtn.click();
        }
    });
    
    // Requirements
    addRequirementBtn.addEventListener('click', () => {
        const input = document.querySelector('.requirement-input');
        const requirement = input.value.trim();
        
        if (requirement) {
            addRequirement(requirement);
            input.value = '';
            input.focus();
        }
    });
    
    document.querySelector('.requirement-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addRequirementBtn.click();
        }
    });
    
    // Responsibilities
    addResponsibilityBtn.addEventListener('click', () => {
        const input = document.querySelector('.responsibility-input');
        const responsibility = input.value.trim();
        
        if (responsibility) {
            addResponsibility(responsibility);
            input.value = '';
            input.focus();
        }
    });
    
    document.querySelector('.responsibility-input').addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            addResponsibilityBtn.click();
        }
    });
}

// Add skill tag
function addSkillTag(skill) {
    const tag = document.createElement('div');
    tag.className = 'bg-indigo-100 text-indigo-800 px-3 py-1 rounded-full text-sm flex items-center';
    
    const text = document.createElement('span');
    text.textContent = skill;
    
    const removeBtn = document.createElement('button');
    removeBtn.className = 'ml-2 text-indigo-500 hover:text-indigo-700 focus:outline-none';
    removeBtn.innerHTML = '&times;';
    removeBtn.addEventListener('click', () => tag.remove());
    
    tag.appendChild(text);
    tag.appendChild(removeBtn);
    
    requiredSkillsList.appendChild(tag);
}

// Add requirement
function addRequirement(requirement) {
    const item = document.createElement('div');
    item.className = 'flex items-center space-x-2';
    
    const text = document.createElement('div');
    text.className = 'flex-grow bg-gray-50 p-2 rounded';
    text.textContent = requirement;
    
    const removeBtn = document.createElement('button');
    removeBtn.className = 'text-red-500 hover:text-red-700 focus:outline-none';
    removeBtn.innerHTML = '&times;';
    removeBtn.addEventListener('click', () => item.remove());
    
    item.appendChild(text);
    item.appendChild(removeBtn);
    
    requirementsList.appendChild(item);
}

// Add responsibility
function addResponsibility(responsibility) {
    const item = document.createElement('div');
    item.className = 'flex items-center space-x-2';
    
    const text = document.createElement('div');
    text.className = 'flex-grow bg-gray-50 p-2 rounded';
    text.textContent = responsibility;
    
    const removeBtn = document.createElement('button');
    removeBtn.className = 'text-red-500 hover:text-red-700 focus:outline-none';
    removeBtn.innerHTML = '&times;';
    removeBtn.addEventListener('click', () => item.remove());
    
    item.appendChild(text);
    item.appendChild(removeBtn);
    
    responsibilitiesList.appendChild(item);
}

// Handle job form submission
async function handleJobFormSubmit(e) {
    e.preventDefault();
    
    // Show loading
    loading.classList.remove('hidden');
    resultsContainer.classList.add('hidden');
    noResults.classList.add('hidden');
    
    // Collect form data
    const jobData = getJobFormData();
    
    // Store current job for later use
    currentJob = jobData;
    
    try {
        // Call API
        const queryParams = new URLSearchParams({
            top_k: document.getElementById('top-k').value
        });
        
        const minExperience = document.getElementById('min-experience').value;
        if (minExperience) {
            queryParams.append('min_experience', minExperience);
        }
        
        const locationFilter = document.getElementById('location-filter').value;
        if (locationFilter) {
            queryParams.append('location_filter', locationFilter);
        }
        
        const minAssessmentScore = document.getElementById('min-assessment-score').value;
        if (minAssessmentScore) {
            queryParams.append('min_assessment_score', minAssessmentScore);
        }
        
        const response = await fetch(`${API_URL}/jobs/match/?${queryParams.toString()}`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(jobData)
        });
        
        if (!response.ok) {
            throw new Error(`API request failed with status ${response.status}`);
        }
        
        const matches = await response.json();
        matchedCandidates = matches;
        
        // Display results
        displayResults(matches);
    } catch (error) {
        console.error('Error:', error);
        resultsContainer.classList.add('hidden');
        loading.classList.add('hidden');
        
        noResults.innerHTML = `
            <div class="bg-white p-6 rounded-lg shadow-md text-center">
                <svg class="h-12 w-12 text-red-400 mx-auto mb-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
                <h3 class="text-lg font-medium text-gray-900">Error</h3>
                <p class="mt-2 text-gray-500">${error.message}</p>
            </div>
        `;
        noResults.classList.remove('hidden');
    } finally {
        // Hide loading
        loading.classList.add('hidden');
        // Scroll to results
        document.getElementById('candidates-section').scrollIntoView({ behavior: 'smooth' });
    }
}

// Get job form data
function getJobFormData() {
    // Basic info
    const jobTitle = document.getElementById('job-title').value;
    const company = document.getElementById('company').value;
    const location = document.getElementById('location').value;
    const remoteOption = document.getElementById('remote-option').value;
    const experienceLevel = document.getElementById('experience-level').value;
    const employmentType = document.getElementById('employment-type').value;
    const description = document.getElementById('description').value;
    
    // Required skills
    const requiredSkills = Array.from(requiredSkillsList.children).map(tag => tag.querySelector('span').textContent);
    
    // Requirements
    const requirements = Array.from(requirementsList.children).map(item => item.querySelector('div').textContent);
    
    // Responsibilities
    const responsibilities = Array.from(responsibilitiesList.children).map(item => item.querySelector('div').textContent);
    
    // Hire3x assessments
    const hire3xAssessmentsSelect = document.getElementById('hire3x-assessments');
    const requiredAssessments = Array.from(hire3xAssessmentsSelect.selectedOptions).map(option => option.value);
    
    // Min assessment score
    const minAssessmentScore = document.getElementById('min-assessment-score').value;
    
    return {
        id: `job-${Date.now()}`,
        title: jobTitle,
        company: company,
        location: location,
        remote_option: remoteOption,
        description: description,
        required_skills: requiredSkills,
        requirements: requirements,
        responsibilities: responsibilities,
        required_assessments: requiredAssessments,
        min_assessment_score: minAssessmentScore ? parseFloat(minAssessmentScore) : null,
        experience_level: experienceLevel,
        employment_type: employmentType
    };
}

// Display results
function displayResults(candidates) {
    if (candidates.length === 0) {
        resultsContainer.classList.add('hidden');
        noResults.classList.remove('hidden');
        return;
    }
    
    // Update result count
    resultCount.textContent = candidates.length;
    
    // Clear previous results
    candidatesList.innerHTML = '';
    
    // Display candidates
    candidates.forEach((candidate, index) => {
        const card = createCandidateCard(candidate, index);
        candidatesList.appendChild(card);
    });
    
    // Show results
    resultsContainer.classList.remove('hidden');
    noResults.classList.add('hidden');
}

// Create candidate card
function createCandidateCard(candidate, index) {
    const card = document.createElement('div');
    card.className = 'bg-white rounded-lg shadow-md overflow-hidden';
    
    // Calculate score color based on overall score
    let scoreColor = 'text-red-600';
    if (candidate.overall_score >= 0.8) {
        scoreColor = 'text-green-600';
    } else if (candidate.overall_score >= 0.6) {
        scoreColor = 'text-yellow-600';
    }
    
    // Format skills for display
    const topMatchingSkills = candidate.matching_skills.slice(0, 5);
    const matchingSkillsHTML = topMatchingSkills.map(skill => 
        `<span class="inline-block bg-indigo-100 text-indigo-800 rounded-full px-3 py-1 text-sm font-semibold mr-2 mb-2">${skill}</span>`
    ).join('');
    
    // Prepare ranking factors for tooltip
    const rankingFactorsHTML = Object.entries(candidate.ranking_factors)
        .map(([key, value]) => `${key.replace(/_/g, ' ')}: ${(value * 100).toFixed(0)}%`)
        .join('<br>');
    
    // Construct card HTML
    card.innerHTML = `
        <div class="border-b border-gray-200 p-4 flex flex-col sm:flex-row justify-between items-start sm:items-center">
            <div>
                <h3 class="text-lg font-medium text-gray-900">${candidate.candidate_name}</h3>
                <p class="text-sm text-gray-500">${candidate.headline || candidate.current_role}</p>
            </div>
            <div class="mt-2 sm:mt-0 flex items-center">
                <span class="tooltip">
                    <span class="inline-flex items-center justify-center w-12 h-12 rounded-full bg-gray-100">
                        <span class="text-xl font-semibold ${scoreColor}">${Math.round(candidate.overall_score * 100)}</span>
                    </span>
                    <span class="tooltip-text">
                        Match score: ${Math.round(candidate.overall_score * 100)}%<br>
                        ${rankingFactorsHTML}
                    </span>
                </span>
                <button data-candidate-id="${candidate.candidate_id}" class="view-profile-btn ml-4 bg-indigo-600 text-white py-2 px-4 rounded hover:bg-indigo-700 transition duration-200">
                    View Profile
                </button>
            </div>
        </div>
        <div class="p-4">
            <div class="mb-4">
                <div class="flex items-start">
                    <div class="flex-1">
                        <div class="flex items-center">
                            <svg class="h-5 w-5 text-gray-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 13.255A23.931 23.931 0 0112 15c-3.183 0-6.22-.62-9-1.745M16 6V4a2 2 0 00-2-2h-4a2 2 0 00-2 2v2m4 6h.01M5 20h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                            </svg>
                            <span class="text-sm text-gray-700">${candidate.current_role}</span>
                        </div>
                        <div class="flex items-center mt-2">
                            <svg class="h-5 w-5 text-gray-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                            </svg>
                            <span class="text-sm text-gray-700">${candidate.location}</span>
                        </div>
                        <div class="flex items-center mt-2">
                            <svg class="h-5 w-5 text-gray-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                            </svg>
                            <span class="text-sm text-gray-700">${candidate.years_of_experience} years experience</span>
                        </div>
                    </div>
                    <div class="flex-1">
                        <div class="metrics-badge p-3 rounded bg-gray-100">
                            <p class="text-sm font-medium text-gray-700">Hire3x Assessment</p>
                            <div class="mt-1 flex items-center">
                                <svg class="h-5 w-5 text-indigo-500 mr-1" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                                </svg>
                                <span class="text-sm font-semibold text-gray-900">+${(candidate.assessment_bonus * 100).toFixed(0)}% Score Boost</span>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
            <div>
                <h4 class="text-sm font-medium text-gray-700 mb-2">Matching Skills</h4>
                <div class="flex flex-wrap">
                    ${matchingSkillsHTML || '<span class="text-sm text-gray-500">No matching skills found</span>'}
                </div>
            </div>
            <div class="mt-4 flex justify-between items-center">
                <div class="flex space-x-2">
                    ${candidate.github_url ? `<a href="${candidate.github_url}" target="_blank" class="text-gray-500 hover:text-gray-700">
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                        </svg>
                    </a>` : ''}
                    ${candidate.linkedin_url ? `<a href="${candidate.linkedin_url}" target="_blank" class="text-gray-500 hover:text-gray-700">
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                        </svg>
                    </a>` : ''}
                    ${candidate.portfolio_url ? `<a href="${candidate.portfolio_url}" target="_blank" class="text-gray-500 hover:text-gray-700">
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                        </svg>
                    </a>` : ''}
                </div>
            </div>
        </div>
    `;
    
    // Add event listener for view profile button
    setTimeout(() => {
        const viewProfileBtn = card.querySelector('.view-profile-btn');
        if (viewProfileBtn) {
            viewProfileBtn.addEventListener('click', () => {
                const candidateId = viewProfileBtn.getAttribute('data-candidate-id');
                showCandidateProfile(candidateId);
            });
        }
    }, 0);
    
    return card;
}

// Show candidate profile
async function showCandidateProfile(candidateId) {
    try {
        // Fetch candidate profile
        const response = await fetch(`${API_URL}/candidates/${candidateId}`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch candidate profile. Status: ${response.status}`);
        }
        
        const candidateProfile = await response.json();
        
        // Create modal for candidate profile
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50';
        modal.id = 'candidate-profile-modal';
        
        // Create modal content
        modal.innerHTML = createProfileModalContent(candidateProfile);
        
        // Add to document
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden'; // Prevent scrolling
        
        // Add event listeners
        setTimeout(() => {
            // Close modal
            const closeBtn = document.getElementById('close-profile-modal');
            closeBtn.addEventListener('click', () => {
                document.body.removeChild(modal);
                document.body.style.overflow = '';
            });
            
            // Generate email button
            const generateEmailBtn = document.getElementById('generate-email-btn');
            generateEmailBtn.addEventListener('click', () => {
                generateEmail(candidateId);
            });
            
            // Export PDF button
            const exportPdfBtn = document.getElementById('export-profile-pdf');
            exportPdfBtn.addEventListener('click', () => {
                exportCandidateProfileAsPDF(candidateId);
            });
        }, 0);
        
    } catch (error) {
        console.error('Error fetching candidate profile:', error);
        alert('Failed to load candidate profile. Please try again.');
    }
}

// Create profile modal content
function createProfileModalContent(profile) {
    // Format work experience
    const workExperienceHTML = profile.experience ? profile.experience.map(exp => {
        return `
            <div class="mb-4">
                <div class="flex justify-between">
                    <h4 class="text-md font-medium text-gray-900">${exp.role}</h4>
                    <span class="text-sm text-gray-500">${exp.start_date} - ${exp.end_date || 'Present'}</span>
                </div>
                <p class="text-sm text-gray-700">${exp.company}</p>
                <p class="mt-2 text-sm text-gray-600">${exp.description}</p>
                ${exp.achievements ? `
                    <div class="mt-2">
                        <p class="text-sm font-medium text-gray-700">Achievements:</p>
                        <ul class="mt-1 ml-4 list-disc text-sm text-gray-600">
                            ${exp.achievements.map(achievement => `<li>${achievement}</li>`).join('')}
                        </ul>
                    </div>
                ` : ''}
                ${exp.skills_used ? `
                    <div class="mt-2 flex flex-wrap">
                        ${exp.skills_used.map(skill => `
                            <span class="inline-block bg-gray-100 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 mr-2 mb-2">
                                ${skill}
                            </span>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }).join('') : '<p class="text-gray-500">No work experience provided</p>';
    
    // Format education
    const educationHTML = profile.education ? profile.education.map(edu => {
        return `
            <div class="mb-4">
                <h4 class="text-md font-medium text-gray-900">${edu.degree} in ${edu.field_of_study}</h4>
                <p class="text-sm text-gray-700">${edu.institution}</p>
                <p class="text-sm text-gray-500">Graduated: ${edu.graduation_year}</p>
            </div>
        `;
    }).join('') : '<p class="text-gray-500">No education details provided</p>';
    
    // Format skills
    const skillsHTML = profile.skills ? Object.entries(profile.skills).map(([skill, level]) => {
        const percentage = Math.round(level * 100);
        return `
            <div class="mb-3">
                <div class="flex justify-between items-center mb-1">
                    <span class="text-sm font-medium text-gray-700">${skill}</span>
                    <span class="text-sm text-gray-500">${percentage}%</span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                    <div class="bg-indigo-600 h-2 rounded-full" style="width: ${percentage}%"></div>
                </div>
            </div>
        `;
    }).join('') : '<p class="text-gray-500">No skills provided</p>';
    
    // Format projects
    const projectsHTML = profile.projects ? profile.projects.map(project => {
        return `
            <div class="mb-4">
                <h4 class="text-md font-medium text-gray-900">${project.name}</h4>
                <p class="mt-1 text-sm text-gray-600">${project.description}</p>
                <div class="mt-2 flex flex-wrap">
                    ${project.technologies.map(tech => `
                        <span class="inline-block bg-gray-100 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 mr-2 mb-2">
                            ${tech}
                        </span>
                    `).join('')}
                </div>
                ${project.url ? `<a href="${project.url}" target="_blank" class="text-sm text-indigo-600 hover:text-indigo-900 mt-2 inline-block">View Project</a>` : ''}
            </div>
        `;
    }).join('') : '<p class="text-gray-500">No projects provided</p>';
    
    // Format Hire3x assessments
    const assessmentsHTML = profile.hire3x_data && profile.hire3x_data.assessments ? profile.hire3x_data.assessments.map(assessment => {
        const completionRate = (assessment.completion_time / assessment.allowed_time) * 100;
        const efficiencyScore = Math.round((1 - assessment.completion_rate) * 100);
        
        return `
            <div class="mb-6 bg-indigo-50 p-4 rounded-lg">
                <div class="flex justify-between items-start">
                    <h4 class="text-md font-medium text-gray-900">${assessment.name}</h4>
                    <div class="flex items-center">
                        <span class="inline-flex items-center justify-center w-10 h-10 rounded-full bg-indigo-100">
                            <span class="text-md font-semibold text-indigo-800">${Math.round(assessment.score)}</span>
                        </span>
                        <span class="ml-1 text-sm text-gray-500">${assessment.percentile}th percentile</span>
                    </div>
                </div>
                <div class="mt-3 grid grid-cols-1 sm:grid-cols-3 gap-3">
                    <div class="bg-white p-3 rounded">
                        <p class="text-xs text-gray-500">Completion Time</p>
                        <p class="text-sm font-medium text-gray-900">${assessment.completion_time} min <span class="text-xs text-gray-500">of ${assessment.allowed_time} min</span></p>
                        <div class="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                            <div class="bg-green-500 h-1.5 rounded-full" style="width: ${completionRate}%"></div>
                        </div>
                        <p class="mt-1 text-xs text-gray-500">${efficiencyScore}% efficiency</p>
                    </div>
                    <div class="bg-white p-3 rounded">
                        <p class="text-xs text-gray-500">Accuracy</p>
                        <p class="text-sm font-medium text-gray-900">${Math.round(assessment.accuracy * 100)}%</p>
                        <div class="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                            <div class="bg-blue-500 h-1.5 rounded-full" style="width: ${assessment.accuracy * 100}%"></div>
                        </div>
                    </div>
                    <div class="bg-white p-3 rounded">
                        <p class="text-xs text-gray-500">Confidence</p>
                        <p class="text-sm font-medium text-gray-900">${Math.round(assessment.confidence_score * 100)}%</p>
                        <div class="mt-1 w-full bg-gray-200 rounded-full h-1.5">
                            <div class="bg-purple-500 h-1.5 rounded-full" style="width: ${assessment.confidence_score * 100}%"></div>
                        </div>
                    </div>
                </div>
                <div class="mt-3">
                    <p class="text-xs text-gray-500">Skills Evaluated</p>
                    <div class="mt-1 flex flex-wrap">
                        ${assessment.skills_evaluated.map(skill => `
                            <span class="inline-block bg-indigo-100 rounded-full px-3 py-1 text-xs font-semibold text-indigo-700 mr-2 mb-2">
                                ${skill}
                            </span>
                        `).join('')}
                    </div>
                </div>
            </div>
        `;
    }).join('') : '<p class="text-gray-500">No Hire3x assessments completed</p>';
    
    // Main profile modal HTML
    return `
        <div class="bg-white rounded-lg shadow-xl max-w-6xl w-full max-h-[90vh] overflow-hidden">
            <div class="flex justify-between items-start p-6 border-b border-gray-200">
                <div>
                    <h2 class="text-2xl font-bold text-gray-900">${profile.name}</h2>
                    <p class="text-gray-600">${profile.headline || profile.current_role}</p>
                </div>
                <button id="close-profile-modal" class="text-gray-400 hover:text-gray-500">
                    <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                    </svg>
                </button>
            </div>
            
            <div class="overflow-y-auto p-6" style="max-height: calc(90vh - 80px);">
                <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
                    <!-- Left Column - Personal Info and Skills -->
                    <div class="lg:col-span-1">
                        <div class="bg-gray-50 p-4 rounded-lg mb-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">Contact Information</h3>
                            <div class="space-y-2">
                                <div class="flex items-center">
                                    <svg class="h-5 w-5 text-gray-400 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                                    </svg>
                                    <span class="text-gray-600">${profile.email}</span>
                                </div>
                                ${profile.phone ? `
                                <div class="flex items-center">
                                    <svg class="h-5 w-5 text-gray-400 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z" />
                                    </svg>
                                    <span class="text-gray-600">${profile.phone}</span>
                                </div>
                                ` : ''}
                                <div class="flex items-center">
                                    <svg class="h-5 w-5 text-gray-400 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                                    </svg>
                                    <span class="text-gray-600">${profile.location}</span>
                                </div>
                            </div>
                            
                            <div class="mt-4 pt-4 border-t border-gray-200">
                                <h4 class="text-md font-medium text-gray-900 mb-2">Professional Links</h4>
                                <div class="space-y-2">
                                    ${profile.linkedin_url ? `
                                    <div class="flex items-center">
                                        <svg class="h-5 w-5 text-blue-600 mr-2" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
                                            <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                                        </svg>
                                        <a href="${profile.linkedin_url}" target="_blank" class="text-indigo-600 hover:text-indigo-900">LinkedIn</a>
                                    </div>
                                    ` : ''}
                                    ${profile.github_url ? `
                                    <div class="flex items-center">
                                        <svg class="h-5 w-5 text-gray-800 mr-2" xmlns="http://www.w3.org/2000/svg" fill="currentColor" viewBox="0 0 24 24">
                                            <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                                        </svg>
                                        <a href="${profile.github_url}" target="_blank" class="text-indigo-600 hover:text-indigo-900">GitHub</a>
                                    </div>
                                    ` : ''}
                                    ${profile.portfolio_url ? `
                                    <div class="flex items-center">
                                        <svg class="h-5 w-5 text-gray-500 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
                                        </svg>
                                        <a href="${profile.portfolio_url}" target="_blank" class="text-indigo-600 hover:text-indigo-900">Portfolio</a>
                                    </div>
                                    ` : ''}
                                </div>
                            </div>
                        </div>
                        
                        <div class="mb-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">Skills</h3>
                            <div class="bg-white p-4 rounded-lg shadow-sm">
                                ${skillsHTML}
                            </div>
                        </div>
                        
                        ${profile.languages ? `
                        <div class="mb-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">Languages</h3>
                            <div class="bg-white p-4 rounded-lg shadow-sm">
                                ${Object.entries(profile.languages).map(([language, proficiency]) => `
                                    <div class="mb-2">
                                        <p class="text-sm font-medium text-gray-700">${language} <span class="text-gray-500">(${proficiency})</span></p>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                        ` : ''}
                        
                        <div class="mb-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">Education</h3>
                            <div class="bg-white p-4 rounded-lg shadow-sm">
                                ${educationHTML}
                            </div>
                        </div>
                    </div>
                    
                    <!-- Right Column - Experience, Projects, and Assessments -->
                    <div class="lg:col-span-2">
                        <div class="mb-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">Summary</h3>
                            <div class="bg-white p-4 rounded-lg shadow-sm">
                                <p class="text-gray-700">${profile.summary}</p>
                            </div>
                        </div>
                        
                        <div class="mb-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">Work Experience</h3>
                            <div class="bg-white p-4 rounded-lg shadow-sm divide-y divide-gray-200">
                                ${workExperienceHTML}
                            </div>
                        </div>
                        
                        ${profile.projects ? `
                        <div class="mb-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">Projects</h3>
                            <div class="bg-white p-4 rounded-lg shadow-sm divide-y divide-gray-200">
                                ${projectsHTML}
                            </div>
                        </div>
                        ` : ''}
                        
                        ${profile.hire3x_data ? `
                        <div class="mb-6">
                            <h3 class="text-lg font-medium text-gray-900 mb-3">Hire3x Assessments</h3>
                            <div>
                                ${assessmentsHTML}
                            </div>
                        </div>
                        ` : ''}
                    </div>
                </div>
            </div>
            
            <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
                <div>
                    <button id="export-profile-pdf" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        <svg class="h-5 w-5 mr-2 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                        </svg>
                        Export as PDF
                    </button>
                </div>
                <button id="generate-email-btn" class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                    <svg class="h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                    </svg>
                    Generate Email
                </button>
            </div>
        </div>
    `;
}

// Generate email for candidate
async function generateEmail(candidateId) {
    try {
        // Check if we have a current job
        if (!currentJob) {
            alert('Please submit a job search first to generate an email.');
            return;
        }
        
        // Call API to generate email
        const response = await fetch(`${API_URL}/email/generate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                candidate_id: candidateId,
                job: currentJob
            })
        });
        
        if (!response.ok) {
            throw new Error(`Failed to generate email. Status: ${response.status}`);
        }
        
        const emailData = await response.json();
        
        // Create modal for email
        const modal = document.createElement('div');
        modal.className = 'fixed inset-0 bg-gray-500 bg-opacity-75 flex items-center justify-center z-50';
        modal.id = 'email-template-modal';
        
        // Create modal content
        modal.innerHTML = `
            <div class="bg-white rounded-lg shadow-xl max-w-2xl w-full overflow-hidden">
                <div class="flex justify-between items-start p-6 border-b border-gray-200">
                    <h2 class="text-xl font-bold text-gray-900">Email Template</h2>
                    <button id="close-email-modal" class="text-gray-400 hover:text-gray-500">
                        <svg class="h-6 w-6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
                        </svg>
                    </button>
                </div>
                
                <div class="p-6">
                    <div class="mb-4">
                        <label for="email-to" class="block text-sm font-medium text-gray-700">To</label>
                        <input type="text" id="email-to" value="${emailData.to_email}" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                    </div>
                    
                    <div class="mb-4">
                        <label for="email-subject" class="block text-sm font-medium text-gray-700">Subject</label>
                        <input type="text" id="email-subject" value="${emailData.subject}" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">
                    </div>
                    
                    <div>
                        <label for="email-body" class="block text-sm font-medium text-gray-700">Body</label>
                        <textarea id="email-body" rows="10" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:ring-indigo-500 focus:border-indigo-500 sm:text-sm">${emailData.body}</textarea>
                    </div>
                </div>
                
                <div class="px-6 py-4 bg-gray-50 border-t border-gray-200 flex justify-between">
                    <button id="copy-email-btn" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        <svg class="h-5 w-5 mr-2 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        Copy to Clipboard
                    </button>
                    <button id="send-email-btn" class="inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500">
                        <svg class="h-5 w-5 mr-2" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                        </svg>
                        Send Email
                    </button>
                </div>
            </div>
        `;
        
        // Add to document
        document.body.appendChild(modal);
        document.body.style.overflow = 'hidden'; // Prevent scrolling
        
        // Add event listeners
        setTimeout(() => {
            // Close modal
            const closeBtn = document.getElementById('close-email-modal');
            closeBtn.addEventListener('click', () => {
                document.body.removeChild(modal);
                document.body.style.overflow = '';
            });
            
            // Copy to clipboard
            const copyBtn = document.getElementById('copy-email-btn');
            copyBtn.addEventListener('click', () => {
                const subject = document.getElementById('email-subject').value;
                const body = document.getElementById('email-body').value;
                
                const emailText = `Subject: ${subject}\n\n${body}`;
                
                navigator.clipboard.writeText(emailText)
                    .then(() => {
                        copyBtn.innerHTML = `
                            <svg class="h-5 w-5 mr-2 text-green-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                            </svg>
                            Copied!
                        `;
                        setTimeout(() => {
                            copyBtn.innerHTML = `
                                <svg class="h-5 w-5 mr-2 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2" />
                                </svg>
                                Copy to Clipboard
                            `;
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Failed to copy text: ', err);
                        alert('Failed to copy to clipboard');
                    });
            });
            
            // Send email
            const sendBtn = document.getElementById('send-email-btn');
            sendBtn.addEventListener('click', () => {
                const to = document.getElementById('email-to').value;
                const subject = document.getElementById('email-subject').value;
                const body = document.getElementById('email-body').value;
                
                // Open default mail client with the email
                window.location.href = `mailto:${to}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
            });
        }, 0);
        
    } catch (error) {
        console.error('Error generating email:', error);
        alert('Failed to generate email. Please try again.');
    }
}

// Export candidate profile as PDF
async function exportCandidateProfileAsPDF(candidateId) {
    try {
        // Call API to generate PDF
        const response = await fetch(`${API_URL}/candidates/export-pdf/${candidateId}`, {
            method: 'POST'
        });
        
        if (!response.ok) {
            throw new Error(`Failed to generate PDF. Status: ${response.status}`);
        }
        
        const data = await response.json();
        
        // Download PDF
        if (data.filename) {
            window.open(`${API_URL}/candidates/pdf/${candidateId}`, '_blank');
        } else {
            throw new Error('PDF generation failed');
        }
    } catch (error) {
        console.error('Error exporting profile as PDF:', error);
        alert('Failed to export profile as PDF. Please try again.');
    }
}

// Export search results as PDF
async function exportResultsAsPDF() {
    if (!matchedCandidates || matchedCandidates.length === 0) {
        alert('No candidates to export');
        return;
    }
    
    // Create PDF content
    let pdfContent = `
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; }
                h1 { color: #4f46e5; }
                .candidate { margin-bottom: 20px; padding: 10px; border: 1px solid #e5e7eb; }
                .name { font-size: 18px; font-weight: bold; }
                .role { color: #6b7280; }
                .score { float: right; font-weight: bold; }
                .skills { margin-top: 10px; }
                .skill { display: inline-block; background-color: #e0e7ff; color: #4f46e5; 
                        padding: 3px 8px; margin: 2px; border-radius: 10px; font-size: 12px; }
            </style>
        </head>
        <body>
            <h1>Candidate Search Results</h1>
            <p>Job Title: ${currentJob?.title || 'Not specified'}</p>
            <p>Company: ${currentJob?.company || 'Not specified'}</p>
            <p>Date: ${new Date().toLocaleDateString()}</p>
            <hr/>
    `;
    
    matchedCandidates.forEach((candidate, index) => {
        const skillsHtml = candidate.matching_skills
            .map(skill => `<span class="skill">${skill}</span>`)
            .join(' ');
        
        pdfContent += `
            <div class="candidate">
                <div>
                    <span class="name">${index + 1}. ${candidate.candidate_name}</span>
                    <span class="score">${Math.round(candidate.overall_score * 100)}%</span>
                </div>
                <div class="role">${candidate.current_role}</div>
                <div>${candidate.location} | ${candidate.years_of_experience} years experience</div>
                <div class="skills">
                    <strong>Matching Skills:</strong> ${skillsHtml}
                </div>
            </div>
        `;
    });
    
    pdfContent += `
        </body>
        </html>
    `;
    
    // Create a Blob from the HTML content
    const blob = new Blob([pdfContent], { type: 'text/html' });
    
    // Create a URL for the Blob
    const url = URL.createObjectURL(blob);
    
    // Create an iframe to print the content
    const printFrame = document.createElement('iframe');
    printFrame.style.position = 'fixed';
    printFrame.style.top = '0';
    printFrame.style.left = '0';
    printFrame.style.width = '100%';
    printFrame.style.height = '100%';
    printFrame.style.zIndex = '-1000';
    
    document.body.appendChild(printFrame);
    
    printFrame.onload = function() {
        printFrame.contentWindow.focus();
        printFrame.contentWindow.print();
        
        // Clean up
        URL.revokeObjectURL(url);
        setTimeout(() => {
            document.body.removeChild(printFrame);
        }, 1000);
    };
    
    printFrame.src = url;
}

// Handle upload form submission
async function handleUploadFormSubmit(e) {
    e.preventDefault();
    
    const fileInput = document.getElementById('candidate-file');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('Please select a file to upload');
        return;
    }
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    try {
        // Show visual feedback during upload
        const uploadStatus = document.getElementById('upload-status');
        const uploadMessage = document.getElementById('upload-message');
        
        uploadMessage.textContent = 'Uploading...';
        uploadStatus.className = uploadStatus.className.replace('hidden', '');
        
        // Call API
        const response = await fetch(`${API_URL}/candidates/upload/`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error(`Upload failed with status ${response.status}`);
        }
        
        const result = await response.json();
        
        // Show success message
        uploadMessage.textContent = result.message;
        
        // Reset form
        fileInput.value = '';
        
        // Update candidate count
        fetchCandidateCount();
        
        // Hide status after 5 seconds
        setTimeout(() => {
            uploadStatus.className += ' hidden';
        }, 5000);
        
    } catch (error) {
        console.error('Error:', error);
        
        // Show error message
        const uploadStatus = document.getElementById('upload-status');
        const uploadMessage = document.getElementById('upload-message');
        
        uploadStatus.className = uploadStatus.className.replace('bg-green-50 border-green-400', 'bg-red-50 border-red-400');
        uploadStatus.querySelector('svg').className = uploadStatus.querySelector('svg').className.replace('text-green-400', 'text-red-400');
        uploadMessage.className = uploadMessage.className.replace('text-green-800', 'text-red-800');
        
        uploadMessage.textContent = `Upload failed: ${error.message}`;
        uploadStatus.className = uploadStatus.className.replace('hidden', '');
        
        // Hide status after 5 seconds
        setTimeout(() => {
            uploadStatus.className += ' hidden';
        }, 5000);
    }
}

// Fetch candidate count
async function fetchCandidateCount() {
    try {
        const response = await fetch(`${API_URL}/candidates/count/`);
        
        if (!response.ok) {
            throw new Error(`Failed to fetch count with status ${response.status}`);
        }
        
        const data = await response.json();
        candidateCountBadge.textContent = data.count;
    } catch (error) {
        console.error('Error fetching candidate count:', error);
        candidateCountBadge.textContent = '?';
    }
}

// Reset job form
function resetJobForm() {
    // Reset basic fields
    document.getElementById('job-title').value = '';
    document.getElementById('company').value = '';
    document.getElementById('location').value = '';
    document.getElementById('remote-option').selectedIndex = 0;
    document.getElementById('experience-level').selectedIndex = 0;
    document.getElementById('employment-type').selectedIndex = 0;
    document.getElementById('description').value = '';
    document.getElementById('min-assessment-score').value = '';
    document.getElementById('top-k').value = '10';
    document.getElementById('min-experience').value = '';
    document.getElementById('location-filter').value = '';
    
    // Reset multi-select
    const assessmentsSelect = document.getElementById('hire3x-assessments');
    for (let i = 0; i < assessmentsSelect.options.length; i++) {
        assessmentsSelect.options[i].selected = false;
    }
    
    // Clear dynamic lists
    requiredSkillsList.innerHTML = '';
    requirementsList.innerHTML = '';
    responsibilitiesList.innerHTML = '';
    
    // Focus on first field
    document.getElementById('job-title').focus();
}