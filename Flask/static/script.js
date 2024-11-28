let currentPage = 0;

document.addEventListener("DOMContentLoaded", () => {
    loadPage(currentPage);

    document.getElementById("next-button").addEventListener("click", () => {
        loadPage(currentPage + 1);
    });

    document.getElementById("prev-button").addEventListener("click", () => {
        loadPage(currentPage - 1);
    });

    const bookContent = document.getElementById("book-content");
    const popup = document.createElement("div");
    popup.id = "popup";
    popup.innerHTML = `<button id="submit-text">Play Audio</button>`;
    document.body.appendChild(popup);

    let selectedText = ""; // Define selectedText here

    bookContent.addEventListener("mouseup", (event) => {
        selectedText = window.getSelection().toString().trim(); // Assign the selected text
        if (selectedText) {
            const range = window.getSelection().getRangeAt(0);
            const rect = range.getBoundingClientRect();

            popup.style.display = "block";
            popup.style.left = `${rect.left + window.scrollX}px`;
            popup.style.top = `${rect.bottom + window.scrollY}px`;
        } else {
            popup.style.display = "none";
        }
    });

    document.getElementById("submit-text").addEventListener("click", () => {
        if (selectedText) {
            fetch("/submit_text", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ selected_text: selectedText }),
            })
                .then((response) => response.json())
                .then((data) => {
                    console.log("Response from server:", data);
                    popup.style.display = "none"; // Hide popup after submission
                })
                .catch((error) => console.error("Error submitting text:", error));
        }
    });



    document.getElementById("generate-audio").addEventListener("click", () => {
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


