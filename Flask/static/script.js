

    const bookContent = document.getElementById("book-content");
    const popup = document.createElement("div");
    popup.id = "popup";
    popup.innerHTML = `
    <div id="button-container">
        <button class="popup_buttons" id="simple-meaning">Meaning</button>
        <button class="popup_buttons" id="contextual-meaning">Context Meaning</button>
        <button class="popup_buttons" id="create-sentence">Sentence</button>
    </div>
    <div id="popup-text" style="margin-top: 10px; font-size: 14px; color: #333;"></div>`;
    document.body.appendChild(popup);


    document.addEventListener("DOMContentLoaded", () => {
        let currentPage = 0;
        const pageResults = {}; // Object to store results for each page
        const bookContent = document.getElementById("book-content");
        const resultsContainer = document.createElement("div");
    
        resultsContainer.id = "results-container";
        resultsContainer.style.border = "1px solid #ccc";
        resultsContainer.style.margin = "20px";
        resultsContainer.style.padding = "10px";
        resultsContainer.style.maxHeight = "300px";
        resultsContainer.style.overflowY = "auto";
        document.body.appendChild(resultsContainer);
    
        loadPage(currentPage);
    
        document.getElementById("next-button").addEventListener("click", () => {
            saveCurrentResults();
            loadPage(++currentPage);
        });
    
        document.getElementById("prev-button").addEventListener("click", () => {
            saveCurrentResults();
            loadPage(--currentPage);
        });


        function loadPage(pageNum) {
            fetch(`/get_page/${pageNum}`)
                .then(response => response.json())
                .then(data => {
                    if (data.page) {
                        document.getElementById("book-content").innerHTML = `<p>${data.page}</p>`;
                        currentPage = pageNum;
    
                        // Clear results container and populate with stored results for the current page
                        resultsContainer.innerHTML = "";
                        if (pageResults[currentPage]) {
                            pageResults[currentPage].forEach(result => appendResult(result.title, result.content));
                        }
    
                        document.getElementById("prev-button").disabled = (data.prev_page < 0);
                        document.getElementById("next-button").disabled = (data.next_page === null);
                    } else {
                        document.getElementById("book-content").innerHTML = "<p>End of Book</p>";
                    }
                })
                .catch(error => console.error("Error loading page:", error));
        }
    


    function appendResult(title, content) {
        const resultDiv = document.createElement("div");
        resultDiv.style.borderBottom = "1px dashed #ccc";
        resultDiv.style.padding = "10px";
        resultDiv.style.marginBottom = "10px";

        const titleEl = document.createElement("strong");
        titleEl.textContent = title;

        const contentEl = document.createElement("p");
        contentEl.textContent = content;

        resultDiv.appendChild(titleEl);
        resultDiv.appendChild(contentEl);

        resultsContainer.appendChild(resultDiv);
    }

    function saveCurrentResults() {
        // Save the current page's results into the pageResults object
        const currentResults = Array.from(resultsContainer.children).map(resultDiv => ({
            title: resultDiv.querySelector("strong").textContent,
            content: resultDiv.querySelector("p").textContent,
        }));
        pageResults[currentPage] = currentResults;
    }


    

    let selectedText = ""; // Define selectedText here
    let paragraph = ""; // Define selectedText here

    bookContent.addEventListener("mouseup", (event) => {
        selectedText = window.getSelection().toString().trim(); // Assign the selected text
        if (selectedText) {
            const range = window.getSelection().getRangeAt(0);
            const rect = range.getBoundingClientRect();

            const fullText = bookContent.innerText || bookContent.textContent;
            const paragraphs = fullText.split(/\n+/); // Split by line breaks
            const selectedParagraphIndex = paragraphs.findIndex((para) =>
                para.includes(selectedText)
            );
            //console.log("selectedParagraphIndex:", selectedParagraphIndex);
            paragraph = paragraphs[selectedParagraphIndex]
            //console.log("Selected Text:", selectedText);
            //console.log("Context Paragraph:", paragraph);


            popup.style.display = "flex";
            popup.style.flexDirection = "column";
            popup.style.justifyContent = "space-between";
            popup.style.left = `${rect.left + window.scrollX}px`;
            popup.style.top = `${rect.bottom + window.scrollY}px`;
        } else {
            popup.style.display = "none";
        }
    });


// ------------------------------------------------------------------------------------------------
    document.getElementById("simple-meaning").addEventListener("click", async () => {
        if (selectedText) {
            const response = await fetch("/simple_meaning", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ selected_text: selectedText }),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Response from server:", data.LLM_output);
                    const popupText = document.getElementById("popup-text");
                    popupText.textContent = data.LLM_output;
                    appendResult("Simple Meaning", data.LLM_output);
                    popup.style.display = "none";
                })
                .catch((error) => console.error("Error submitting text:", error));

        }
    });



    document.getElementById("contextual-meaning").addEventListener("click", () => {
        if (selectedText) {
            fetch("/contextual_meaning", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ selected_text: selectedText,selected_paragraph:paragraph}),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Response from server:", data.LLM_output);
                    const popupText = document.getElementById("popup-text");
                    popupText.textContent = data.LLM_output;
                    appendResult("Context Meaning", data.LLM_output);
                    popup.style.display = "none";
                })
                .catch((error) => console.error("Error submitting text:", error));
        }
    });



    document.getElementById("create-sentence").addEventListener("click", () => {
        if (selectedText) {
            fetch("/create_sentence", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ selected_text: selectedText }),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Response from server:", data.LLM_output);
                    const popupText = document.getElementById("popup-text");
                    popupText.textContent = data.LLM_output;
                    appendResult("Sentence", data.LLM_output);
                    popup.style.display = "none";
                })
                .catch((error) => console.error("Error submitting text:", error));
        }
    });

// ------------------------------------------------------------------------------------------------






   /* document.getElementById("generate-audio").addEventListener("click", () => {
        const audioPlayer = document.getElementById("audio-player");
    
        if (!selectedText) {
            alert("Please highlight some text first!");
            return;
        }
    
        fetch("/generate_audio", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text: selectedText }) // Use the selected text
        })
        .then(response => {
            if (!response.ok) {
                throw new Error("Error generating audio");
            }
            return response.blob();
        })
        .then(blob => {
            const audioUrl = URL.createObjectURL(blob);
            audioPlayer.src = audioUrl;
            audioPlayer.style.display = "block";
            audioPlayer.play();
        })
        .catch(error => console.error("Error:", error));
    });

*/





    document.addEventListener("mousedown", (event) => {
        if (!popup.contains(event.target)) {
            popup.style.display = "none";
        }
    });
});

function loadPage(pageNum) {
    fetch(`/get_page/${pageNum}`)
        .then(response => response.json())
        .then(data => {
            if (data.page) {
                document.getElementById("book-content").innerHTML = `<p>${data.page}</p>`;
                currentPage = pageNum;

                document.getElementById("prev-button").disabled = (data.prev_page < 0);
                document.getElementById("next-button").disabled = (data.next_page === null);
            } else {
                document.getElementById("book-content").innerHTML = "<p>End of Book</p>";
            }
        })
        .catch(error => console.error("Error loading page:", error));
}


