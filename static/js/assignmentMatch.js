// Teacher-Student assignment matching functionality

document.addEventListener('DOMContentLoaded', function() {
    // Add listeners to filter controls if they exist
    setupAreaFilter();
    setupSubjectFilter();
    setupGenderFilter();
    
    // Initialize match score visualizations
    initMatchScores();
});

// Setup area filter
function setupAreaFilter() {
    const areaFilter = document.getElementById('areaFilter');
    if (!areaFilter) return;
    
    areaFilter.addEventListener('input', filterTeachers);
}

// Setup subject filter
function setupSubjectFilter() {
    const subjectFilter = document.getElementById('subjectFilter');
    if (!subjectFilter) return;
    
    subjectFilter.addEventListener('change', filterTeachers);
}

// Setup gender filter
function setupGenderFilter() {
    const genderFilter = document.getElementById('genderFilter');
    if (!genderFilter) return;
    
    genderFilter.addEventListener('change', filterTeachers);
}

// Filter teachers based on selected criteria
function filterTeachers() {
    const areaFilter = document.getElementById('areaFilter');
    const subjectFilter = document.getElementById('subjectFilter');
    const genderFilter = document.getElementById('genderFilter');
    
    if (!areaFilter && !subjectFilter && !genderFilter) return;
    
    const area = areaFilter ? areaFilter.value.toLowerCase() : '';
    const subject = subjectFilter ? subjectFilter.value : '';
    const gender = genderFilter ? genderFilter.value : '';
    
    const teacherCards = document.querySelectorAll('.teacher-card');
    
    teacherCards.forEach(card => {
        let show = true;
        
        // Check area filter
        if (area && card.dataset.areas) {
            const areas = JSON.parse(card.dataset.areas);
            const areaMatch = areas.some(a => a.toLowerCase().includes(area));
            if (!areaMatch) show = false;
        }
        
        // Check subject filter
        if (subject && card.dataset.subjects) {
            const subjects = JSON.parse(card.dataset.subjects);
            if (!subjects.includes(subject)) show = false;
        }
        
        // Check gender filter
        if (gender && card.dataset.gender) {
            if (gender !== 'ANY' && gender !== card.dataset.gender) show = false;
        }
        
        // Show or hide card
        if (show) {
            card.classList.remove('d-none');
        } else {
            card.classList.add('d-none');
        }
    });
    
    // Update counter
    updateVisibleCount();
}

// Update count of visible teachers
function updateVisibleCount() {
    const visibleCount = document.querySelectorAll('.teacher-card:not(.d-none)').length;
    const totalCount = document.querySelectorAll('.teacher-card').length;
    
    const countElement = document.getElementById('teacherCount');
    if (countElement) {
        countElement.textContent = `Showing ${visibleCount} of ${totalCount} teachers`;
    }
}

// Initialize match score visualizations
function initMatchScores() {
    const matchScoreElements = document.querySelectorAll('.match-score-bar');
    
    matchScoreElements.forEach(element => {
        const score = parseInt(element.dataset.score || 0);
        
        // Set width of the match score bar
        element.style.width = `${score}%`;
        
        // Set color based on score
        if (score >= 80) {
            element.classList.add('bg-success');
        } else if (score >= 50) {
            element.classList.add('bg-warning');
        } else {
            element.classList.add('bg-danger');
        }
    });
}

// Update matching teacher selection when changed
function updateTeacherSelection(select) {
    const selectedOption = select.options[select.selectedIndex];
    const teacherId = select.value;
    const matchScore = selectedOption.getAttribute('data-match-score');
    
    // Update display elements if they exist
    const matchScoreElement = document.getElementById('selectedMatchScore');
    if (matchScoreElement) {
        matchScoreElement.textContent = matchScore;
        
        // Update color based on score
        matchScoreElement.className = 'badge'; // Reset classes
        
        if (parseInt(matchScore) >= 80) {
            matchScoreElement.classList.add('bg-success');
        } else if (parseInt(matchScore) >= 50) {
            matchScoreElement.classList.add('bg-warning');
        } else {
            matchScoreElement.classList.add('bg-danger');
        }
    }
    
    // Show teacher details card
    if (teacherId) {
        document.querySelectorAll('.teacher-detail-card').forEach(card => {
            if (card.dataset.teacherId === teacherId) {
                card.classList.remove('d-none');
            } else {
                card.classList.add('d-none');
            }
        });
    }
}

// Display matched areas between student and teacher
function displayMatchedAreas(studentArea, teacherAreas) {
    const matchedAreasContainer = document.getElementById('matchedAreas');
    if (!matchedAreasContainer) return;
    
    // Clear current content
    matchedAreasContainer.innerHTML = '';
    
    // Convert to lowercase for case-insensitive matching
    const studentAreaLower = studentArea.toLowerCase();
    
    // Parse teacher areas
    let teacherAreasList;
    try {
        teacherAreasList = typeof teacherAreas === 'string' ? JSON.parse(teacherAreas) : teacherAreas;
    } catch (e) {
        console.error('Error parsing teacher areas:', e);
        return;
    }
    
    // Find matches
    const matches = teacherAreasList.filter(area => 
        studentAreaLower.includes(area.toLowerCase()) || 
        area.toLowerCase().includes(studentAreaLower)
    );
    
    // Create badges for matches
    if (matches.length > 0) {
        matches.forEach(area => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-success me-1 mb-1';
            badge.textContent = area;
            matchedAreasContainer.appendChild(badge);
        });
    } else {
        // No direct match, but show nearby areas
        const heading = document.createElement('small');
        heading.className = 'text-muted d-block mb-2';
        heading.textContent = 'No exact match, but teacher works in these areas:';
        matchedAreasContainer.appendChild(heading);
        
        teacherAreasList.slice(0, 3).forEach(area => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-secondary me-1 mb-1';
            badge.textContent = area;
            matchedAreasContainer.appendChild(badge);
        });
    }
}

// Display matched subjects between student and teacher
function displayMatchedSubjects(studentSubjects, teacherSubjects) {
    const matchedSubjectsContainer = document.getElementById('matchedSubjects');
    if (!matchedSubjectsContainer) return;
    
    // Clear current content
    matchedSubjectsContainer.innerHTML = '';
    
    // Parse subjects
    let studentSubjectsList, teacherSubjectsList;
    try {
        studentSubjectsList = typeof studentSubjects === 'string' ? JSON.parse(studentSubjects) : studentSubjects;
        teacherSubjectsList = typeof teacherSubjects === 'string' ? JSON.parse(teacherSubjects) : teacherSubjects;
    } catch (e) {
        console.error('Error parsing subjects:', e);
        return;
    }
    
    // Find matches
    const matches = studentSubjectsList.filter(subject => teacherSubjectsList.includes(subject));
    
    // Create badges for matches
    if (matches.length > 0) {
        matches.forEach(subject => {
            const badge = document.createElement('span');
            badge.className = 'badge bg-success me-1 mb-1';
            badge.textContent = subject;
            matchedSubjectsContainer.appendChild(badge);
        });
        
        // Add match percentage
        const matchPercentage = Math.round((matches.length / studentSubjectsList.length) * 100);
        const percentageTag = document.createElement('div');
        percentageTag.className = 'small mt-2';
        percentageTag.textContent = `${matchPercentage}% subject match`;
        matchedSubjectsContainer.appendChild(percentageTag);
    } else {
        // No matches
        const noMatchText = document.createElement('div');
        noMatchText.className = 'text-danger small';
        noMatchText.textContent = 'No matching subjects found!';
        matchedSubjectsContainer.appendChild(noMatchText);
    }
}
