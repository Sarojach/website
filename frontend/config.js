// Configuration for API endpoints
const CONFIG = {
    API_BASE_URL: 'http://localhost:5000/api',  // Development
    // API_BASE_URL: 'https://your-domain.com/api',  // Production
    ADMIN_API_KEY: ''  // Set this for admin operations
};

// Fetch projects from backend
async function loadProjects() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/projects`);
        if (!response.ok) throw new Error('Failed to load projects');
        
        const data = await response.json();
        console.log('Projects loaded:', data.projects);
        return data.projects;
    } catch (error) {
        console.error('Error loading projects:', error);
        return [];
    }
}

// Fetch skills from backend
async function loadSkills() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/skills`);
        if (!response.ok) throw new Error('Failed to load skills');
        
        const data = await response.json();
        console.log('Skills loaded:', data.skills);
        return data.skills;
    } catch (error) {
        console.error('Error loading skills:', error);
        return {};
    }
}

// Fetch experiences from backend
async function loadExperiences() {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/experiences`);
        if (!response.ok) throw new Error('Failed to load experiences');
        
        const data = await response.json();
        console.log('Experiences loaded:', data);
        return data;
    } catch (error) {
        console.error('Error loading experiences:', error);
        return [];
    }
}

// Submit contact form to backend
async function submitContact(formData) {
    try {
        const response = await fetch(`${CONFIG.API_BASE_URL}/contact`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData)
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.error || 'Failed to send message');
        }
        
        const result = await response.json();
        return result;
    } catch (error) {
        console.error('Error submitting contact:', error);
        throw error;
    }
}