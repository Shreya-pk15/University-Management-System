document.addEventListener('DOMContentLoaded', () => {
    const topic = 'business'; // Change this value to load different topics

    fetch(`data/${topic}.json`)
        .then(response => response.json())
        .then(jsonData => {
            document.getElementById('program-title').textContent = jsonData.title;
            document.getElementById('program-description').textContent = jsonData.description;

            const facultyList = document.getElementById('faculty-list');
            facultyList.innerHTML = ''; // Clear any existing content
            
            jsonData.faculty.forEach(member => {
                const facultyDiv = document.createElement('div');
                facultyDiv.className = 'faculty-member';
                
                facultyDiv.innerHTML = `
                    <h2>${member.name}</h2>
                    <img src="images/${topic}/${member.image}" alt="${member.name}" style="width: 100px; height: 100px;">
                    <p>Phone: ${member.phone}</p>
                    <p>Subject: ${member.subject}</p>
                    <p>Experience: ${member.experience}</p>
                `;
                
                facultyList.appendChild(facultyDiv);
            });
        })
        .catch(error => console.error('Error loading JSON data:', error));
});
