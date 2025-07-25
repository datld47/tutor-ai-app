
document.addEventListener('DOMContentLoaded', () => {

console.log('bắt đầu my_latex.js')


const mathInput = document.getElementById('math-input');
const latexOutput = document.getElementById('latex-output');
const copyButton = document.getElementById('copy-latex-button');
const messageBox = document.getElementById('message-box');
const toolbarButtons = document.querySelectorAll('.toolbar-button');

 customElements.whenDefined('math-field').then(() => {

        console.log('2. customElements.whenDefined("math-field") đã được giải quyết. Thẻ MathLive đã sẵn sàng!');
 });

const upgradedMathInput = document.getElementById('math-input');

if (upgradedMathInput) {
    //     // Explicitly set default mode to 'math'
    
    upgradedMathInput.defaultMode = 'math';

    // Update LaTeX output whenever the math field changes

    // console.log(upgradedMathInput.value)

    upgradedMathInput.addEventListener('input', () => {
        latexOutput.textContent = upgradedMathInput.value; // Get the LaTeX string
        hideMessage(); // Hide message on new input
    });

    //Set initial LaTeX output
    latexOutput.textContent = upgradedMathInput.value;

    setTimeout(() => {
        upgradedMathInput.focus();
    }, 100); // 100ms delay

        // Toolbar button functionality
        toolbarButtons.forEach(button => {
            button.addEventListener('click', () => {
                const latexCommand = button.dataset.latex;
                if (latexCommand) {
                    // Insert the LaTeX command into the math field
                    // MathLive will automatically place the cursor in the right spot
                    upgradedMathInput.insert(latexCommand, { focus: 'right' });
                    upgradedMathInput.focus(); // Keep focus on the math field
                }
            });
        });
    } 
    else
    {
        console.error("Error: math-field element not found after custom element definition.");
    }

// // Copy to clipboard functionality
// if (copyButton) {
//     copyButton.addEventListener('click', () => {
//         const latexText = latexOutput.textContent;
//         if (latexText) {
//             // Use document.execCommand('copy') for better iframe compatibility
//             const textarea = document.createElement('textarea');
//             textarea.value = latexText;
//             document.body.appendChild(textarea);
//             textarea.select();
//             try {
//                 document.execCommand('copy');
//                 showMessage('Đã sao chép LaTeX vào clipboard!');
//             } catch (err) {
//                 console.error('Failed to copy LaTeX: ', err);
//                 showMessage('Không thể sao chép. Vui lòng sao chép thủ công.');
//             }
//             document.body.removeChild(textarea);
//         } else {
//             showMessage('Không có gì để sao chép.');
//         }
//     });
// }

// // Function to show message box
function showMessage(msg) {
    messageBox.textContent = msg;
    messageBox.classList.add('show');
    setTimeout(() => {
        hideMessage();
    }, 3000); // Hide after 3 seconds
}

// // Function to hide message box
function hideMessage() {
    messageBox.classList.remove('show');
    // Use setTimeout to ensure display: none happens after transition
    setTimeout(() => {
        messageBox.style.display = 'none';
    }, 300); // Match CSS transition duration
}


});
