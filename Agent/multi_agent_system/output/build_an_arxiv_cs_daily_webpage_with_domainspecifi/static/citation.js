// Citation handling and copy functionality

document.addEventListener('DOMContentLoaded', () => {
    // Add event listeners to all copy buttons
    const copyButtons = document.querySelectorAll('.copy-btn');
    
    copyButtons.forEach(button => {
        button.addEventListener('click', () => {
            const targetId = button.getAttribute('data-target');
            const targetElement = document.getElementById(targetId);
            
            if (targetElement) {
                // Get text content based on element type
                let textToCopy;
                if (targetElement.tagName === 'PRE') {
                    textToCopy = targetElement.textContent;
                } else {
                    textToCopy = targetElement.innerText;
                }
                
                // Copy to clipboard
                navigator.clipboard.writeText(textToCopy)
                    .then(() => {
                        // Show feedback
                        const originalText = button.textContent;
                        button.textContent = 'Copied!';
                        button.style.backgroundColor = '#28a745'; // Success color
                        
                        setTimeout(() => {
                            button.textContent = originalText;
                            button.style.backgroundColor = '';
                        }, 2000);
                    })
                    .catch(err => {
                        console.error('Failed to copy: ', err);
                        alert('Failed to copy citation. Please try again.');
                    });
            }
        });
    });
});
