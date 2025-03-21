document.addEventListener("DOMContentLoaded", () => {
  // --- Cache DOM Elements ---
  const bookContentEl = document.getElementById("book-content");
  const nextButton = document.getElementById("next-button");
  const prevButton = document.getElementById("prev-button");
  const messageInput = document.getElementById("message-input");
  const chatSendButton = document.getElementById("chat-send-button");
  const chatBox = document.getElementById("chat-box");
  const audioPlayer = document.getElementById("audio-player");
  const pgnum = document.getElementById("page_num");

  page_num;

  // Side Panel Tabs
  // tab btns
  const tabChatBtn = document.getElementById("tab-chat");
  const tabInsightsBtn = document.getElementById("tab-insights");
  const tabVisualizationBtn = document.getElementById("tab-visualization");

  // tabVisualizationBtn.addEventListener("click", () => {
  // });

  const chatContainer = document.getElementById("chat-container");
  const insightsContainer = document.getElementById("insights-container");
  const visContainer = document.getElementById("visual-container");


  // Create and append popup element
  const popup = createPopup();
  document.body.appendChild(popup);

  // --- Global Variables ---
  let currentPage = 0;
  let selectedText = "";
  let selectedParagraph = "";
  // Store processed words (keyed in lowercase) with their meaning
  const highlightedWords = {};

  // --- Tab Switching ---
  tabChatBtn.addEventListener("click", () => {
    tabChatBtn.classList.add("active");
    tabInsightsBtn.classList.remove("active");
    tabVisualizationBtn.classList.remove("active");

    chatContainer.style.display = "block";
    insightsContainer.style.display = "none";
    visContainer.style.display = "none";
  });

  tabInsightsBtn.addEventListener("click", () => {
    tabInsightsBtn.classList.add("active");
    tabChatBtn.classList.remove("active");
    tabVisualizationBtn.classList.remove("active");

    insightsContainer.style.display = "block";
    chatContainer.style.display = "none";
    visContainer.style.display = "none";

  });

  tabVisualizationBtn.addEventListener("click", () => {
    tabVisualizationBtn.classList.add("active");

    tabInsightsBtn.classList.remove("active");
    tabChatBtn.classList.remove("active");

    visContainer.style.display = "block";
    chatContainer.style.display = "none";
    insightsContainer.style.display = "none";

  });

  // --- Page Navigation ---
  loadPage(currentPage);
  nextButton.addEventListener("click", () => {
    loadPage(++currentPage);
  });
  prevButton.addEventListener("click", () => {
    loadPage(--currentPage);
  });

  // --- Text Selection & Popup Positioning ---
  bookContentEl.addEventListener("mouseup", (event) => {
    // Allow a slight delay for selection to register
    setTimeout(() => {
      selectedText = window.getSelection().toString().trim();
      console.log("Selected Text:", selectedText);
      if (selectedText) {
        const selection = window.getSelection();
        if (selection.rangeCount > 0) {
          const range = selection.getRangeAt(0);
          const rect = range.getBoundingClientRect();
          // Determine the paragraph containing the selection
          const fullText = bookContentEl.innerText || bookContentEl.textContent;
          const paragraphs = fullText.split(/\n+/);
          const index = paragraphs.findIndex((para) =>
            para.includes(selectedText)
          );
          selectedParagraph = index !== -1 ? paragraphs[index] : "";
          // Position and show the popup
          popup.style.display = "flex";
          popup.style.left = `${rect.left + window.scrollX}px`;
          popup.style.top = `${rect.bottom + window.scrollY}px`;
        }
      } else {
        popup.style.display = "none";
      }
    }, 10);
  });

  document.addEventListener("mousedown", (event) => {
    if (!popup.contains(event.target)) {
      popup.style.display = "none";
    }
  });

  // --- Popup Button Actions ---
  document.getElementById("simple-meaning").addEventListener("click", () => {
    handlePopupAction(
      "/simple_meaning",
      { selected_text: selectedText },
      "Simple Meaning"
    );
  });
  document
    .getElementById("contextual-meaning")
    .addEventListener("click", () => {
      handlePopupAction(
        "/contextual_meaning",
        { selected_text: selectedText, selected_paragraph: selectedParagraph },
        "Context Meaning"
      );
    });
  document.getElementById("create-sentence").addEventListener("click", () => {
    handlePopupAction(
      "/create_sentence",
      { selected_text: selectedText },
      "Sentence"
    );
  });
  document.getElementById("generate-audio").addEventListener("click", () => {
    handleAudioGeneration();
  });


document.getElementById("vis-para").addEventListener("click", () => {
  console.log('Hello')
  fetch("/get-image", { method: "POST" })
    .then(response => response.json())
    .then(data => {
      appendVis(data)
    })
    .catch(error => console.error("Error:", error));
  
  });


  // --- Chat Functionality ---
  chatSendButton.addEventListener("click", () => {
    const question = messageInput.value.trim();
    if (!question) return;
    fetch("/chat_book", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, page_number: currentPage }),
    })
      .then((response) => response.json())
      .then((data) => {
        appendChatMessage("You", question, chatBox);
        appendChatMessage("Bot", data.chat_reply, chatBox);
        messageInput.value = "";
        chatBox.scrollTop = chatBox.scrollHeight;
      })
      .catch((error) => console.error("Chat Error:", error));
  });

  // --- Function Definitions ---

  function createPopup() {
    const popupEl = document.createElement("div");
    popupEl.id = "popup";
    popupEl.innerHTML = `
          <button class="popup_buttons" id="simple-meaning">Meaning</button>
          <button class="popup_buttons" id="contextual-meaning">Context Meaning</button>
          <button class="popup_buttons" id="create-sentence">Sentence</button>
          <button class="popup_buttons" id="generate-audio">Speak</button>
          <button class="popup_buttons" id="vis-para">Visualize Para</button>

      `;
    return popupEl;
  }

  // Loads a page from the backend and re-applies existing highlights.
  function loadPage(pageNum) {
    fetch(`/get_page/${pageNum}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.page) {
          bookContentEl.innerHTML = `<p>${data.page}</p>`;
          currentPage = pageNum;
          pgnum.style.display = "block"; // Make sure it's visible
          pgnum.textContent = currentPage;

          prevButton.disabled = data.prev_page < 0;
          nextButton.disabled = data.next_page === null;
          // Re-highlight all processed words on this page
          for (let word in highlightedWords) {
            highlightAllOccurrences(word, highlightedWords[word]);
          }
        } else {
          bookContentEl.innerHTML = "<p>End of Book</p>";
        }
      })
      .catch((error) => console.error("Load Page Error:", error));
  }

  // Appends generated insight to the global Insights container.
  function appendInsight(title, content) {
    const insightDiv = document.createElement("div");
    insightDiv.style.borderBottom = "1px dashed #ccc";
    insightDiv.style.padding = "8px";
    insightDiv.style.marginBottom = "8px";
    const titleEl = document.createElement("strong");
    titleEl.textContent = title;
    const contentEl = document.createElement("p");
    contentEl.textContent = content;
    insightDiv.appendChild(titleEl);
    insightDiv.appendChild(contentEl);
    insightsContainer.appendChild(insightDiv);
  }

 // Appends generated insight to the global Insights container.
  function appendVis(data) {
    const img = document.createElement("img");
    img.src = data.image;
    visContainer.appendChild(img);
  }


  // Handles popup actions for LLM functions, stores mapping, and highlights globally.
  function handlePopupAction(url, payload, resultTitle) {
    if (!selectedText) return;
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        //document.getElementById("popup-text").textContent = data.LLM_output;
        appendInsight(resultTitle, data.LLM_output);
        // Save mapping (case-insensitive)
        highlightedWords[selectedText.toLowerCase()] = data.LLM_output;
        // Recursively highlight all occurrences on the current page
        highlightAllOccurrences(selectedText, data.LLM_output);
        popup.style.display = "none";
      })
      .catch((error) => console.error("Popup Action Error:", error));
  }

  // Recursively highlights all occurrences of a word within the bookContentEl.
  function highlightAllOccurrences(word, meaning) {
    // First remove any existing highlights for this word.
    removeHighlights(bookContentEl, word);
    // Then traverse text nodes and wrap matches.
    highlightTextNodes(bookContentEl, word, meaning);
  }

  // Recursively traverse element's child nodes and wrap text matching the word.
  function highlightTextNodes(element, word, meaning) {
    if (element.nodeType === Node.TEXT_NODE) {
      const regex = new RegExp(`\\b(${escapeRegExp(word)})\\b`, "gi");
      if (regex.test(element.nodeValue)) {
        const frag = document.createDocumentFragment();
        const parts = element.nodeValue.split(regex);
        parts.forEach((part) => {
          if (regex.test(part)) {
            const span = document.createElement("span");
            span.className = "highlighted-word";
            span.setAttribute("data-tooltip", meaning);
            span.textContent = part;
            span.addEventListener("click", (e) => {
              e.stopPropagation();
              span.classList.toggle("show-tooltip");
            });
            frag.appendChild(span);
          } else {
            frag.appendChild(document.createTextNode(part));
          }
        });
        element.parentNode.replaceChild(frag, element);
      }
    } else if (element.nodeType === Node.ELEMENT_NODE) {
      Array.from(element.childNodes).forEach((child) => {
        highlightTextNodes(child, word, meaning);
      });
    }
  }

  // Removes existing highlights for the given word.
  function removeHighlights(element, word) {
    const spans = element.querySelectorAll("span.highlighted-word");
    spans.forEach((span) => {
      if (span.textContent.toLowerCase() === word.toLowerCase()) {
        const parent = span.parentNode;
        while (span.firstChild) {
          parent.insertBefore(span.firstChild, span);
        }
        parent.removeChild(span);
      }
    });
  }

  // Escapes special regex characters in a string.
  function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  // Handles audio generation for the selected text.
  function handleAudioGeneration() {
    if (!selectedText) {
      alert("Please highlight some text first!");
      return;
    }
    fetch("/generate_audio", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: selectedText }),
    })
      .then((response) => {
        if (!response.ok) throw new Error("Error generating audio");
        return response.blob();
      })
      .then((blob) => {
        const audioUrl = URL.createObjectURL(blob);
        audioPlayer.src = audioUrl;
        audioPlayer.style.display = "block";
        audioPlayer.play();
      })
      .catch((error) => console.error("Audio Error:", error));
  }

  // Appends a chat message to the chat box as a chat bubble.
  function appendChatMessage(sender, message, container) {
    const messageContainer = document.createElement("div");
    messageContainer.classList.add("chat-message");
    if (sender === "You") {
      messageContainer.classList.add("you");
      messageContainer.innerHTML = `
          <div class="chat-icon user-icon"><i class="fas fa-user"></i></div>
          <div class="chat-text">${message}</div>
        `;
    } else {
      messageContainer.classList.add("bot");
      messageContainer.innerHTML = `
          <div class="chat-icon bot-icon"><i class="fas fa-robot"></i></div>
          <div class="chat-text">${message}</div>
        `;
    }
    container.appendChild(messageContainer);
  }
});

// ----------------------------------------------------------------------------

const recordButton = document.getElementById("record-audio-button");
let mediaRecorder = null;
let audioChunks = [];
let isRecording = false;
let prevTranscription = "";

// Create a recording indicator element and append it to the input container
const recordIndicator = document.createElement("span");
recordIndicator.id = "recording-indicator";
recordIndicator.textContent = "Recording...";
recordIndicator.style.display = "none"; // initially hidden
recordIndicator.style.marginLeft = "10px"; // adjust styling as needed
document.getElementById("input-container").appendChild(recordIndicator);

recordButton.addEventListener("click", () => {
  if (!isRecording) {
    // Start recording
    navigator.mediaDevices.getUserMedia({ audio: true })
      .then(stream => {
        mediaRecorder = new MediaRecorder(stream);
        audioChunks = [];       // reset the accumulated audio
        prevTranscription = ""; // reset previous transcription
        
        mediaRecorder.addEventListener("dataavailable", event => {
          if (event.data.size > 0) {
            // Accumulate chunks over time
            audioChunks.push(event.data);
            // Create a blob of all recorded audio so far
            const accumulatedBlob = new Blob(audioChunks, { type: 'audio/wav' });
            const formData = new FormData();
            formData.append("audio", accumulatedBlob, "accumulated.wav");

            // Send the accumulated audio for transcription
            fetch("/transcribe_audio", {
              method: "POST",
              body: formData
            })
            .then(response => response.json())
            .then(data => {
              if (data.transcription) {
                const fullTranscription = data.transcription;
                // Compute the new text (if the transcription is cumulative)
                let newPart = "";
                if (fullTranscription.startsWith(prevTranscription)) {
                  newPart = fullTranscription.substring(prevTranscription.length);
                } else {
                  // Fallback: replace previous transcription entirely
                  newPart = fullTranscription;
                }
                prevTranscription = fullTranscription;
                // Update the chat input with the cumulative transcription
                document.getElementById("message-input").value = fullTranscription;
              } else if (data.error) {
                console.error("Transcription error:", data.error);
              }
            })
            .catch(error => console.error("Error:", error));
          }
        });

        mediaRecorder.addEventListener("start", () => {
          recordIndicator.style.display = "inline";
          recordButton.textContent = "Stop";
          recordButton.style.color = 'white'
          isRecording = true;
        });

        mediaRecorder.addEventListener("stop", () => {
          recordIndicator.style.display = "none";
          recordButton.textContent = "Voice";
          isRecording = false;
        });

        // Start recording, requesting a new data chunk every 2000ms
        mediaRecorder.start(2000);
        console.log("Recording started...");
      })
      .catch(error => console.error("Microphone error:", error));
  } else {
    // Stop recording when the button is clicked again
    if (mediaRecorder && mediaRecorder.state === "recording") {
      mediaRecorder.stop();
      console.log("Recording stopped.");
    }
  }
});


// -------------------------------------------------------------------------------------------------------


