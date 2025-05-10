document.addEventListener("DOMContentLoaded", () => {
  
});
const nextButton = document.getElementById("next-button");
const prevButton = document.getElementById("prev-button");

const bookContentEl1 = document.getElementById("book-content-1");
const bookContentEl2 = document.getElementById("book-content-2");
const pageN1 = document.getElementById("page-number-1");
const pageN2 = document.getElementById("page-number-2");
let selectedText = "";
let selectedParagraph = "";
const highlightedWordsBlue = {};
const highlightedWordsRed = {};

const highlightButton = document.getElementById("highlight-button");
const bookmarkedPages = [];
const highlightedTexts = {};


let characters_list = [];
let characters_list_updated=[];
const overlay2 = document.getElementById("modalOverlay");
const modal = overlay2.querySelector(".modal");
const closeButton = modal.querySelector(".modal-close");
const prevButton2 = modal.querySelector(".prev");
const nextButton2 = modal.querySelector(".next");
const titleEl = modal.querySelector("#modalTitle");
const descEl = modal.querySelector("#modalDesc");
const imgEl = modal.querySelector("#modalImg");
const contentEl = modal.querySelector(".modal-content");
let setTo=false;
let newDescriptions = {};
let knownCharacters = new Set();




let currentPage = 0;
function loadPage(pageNum) {
    fetch(`/get_page/${pageNum}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.page1) {
          bookContentEl1.innerHTML = `<p>${data.page1}</p>`;
          bookContentEl2.innerHTML = `<p>${data.page2}</p>`;
          on_page = data.chap;
          chapter_title = data.chapterName;
          characters_list = data.characters;
          if (on_page!='none'){
          display_title(on_page, chapter_title)
        }
          prevButton.disabled = data.prev_page < 0;
          nextButton.disabled = data.next_page === null;

          // Re-highlight all processed words on this page
          for (let word in highlightedWordsBlue) {
            highlightAllOccurrences(word, highlightedWordsBlue[word], false);
          }
          for (let word in highlightedWordsRed) {
            highlightAllOccurrences(word, highlightedWordsRed[word], true);
          }
          console.log(characters_list);
          // CHECK IF A NEW CHARACTER IS FOUND

          let newFound = false;
          for (let char of characters_list) {
            if (!knownCharacters.has(char)) {
              knownCharacters.add(char);
              newFound = true;
            }
          }

          const badge = document.getElementById("charBadge");
          if (newFound) {
            badge.style.display = "inline";
          }


          
          if (characters_list=='none') 
          {
            setTo=true;      
          }

          else
          {
            if (data.next_page%10 == 0) 
            {
              p2 = data.next_page
              p1 = p2 - 10
              const updateAllDescriptions = async () =>
              {
                  for (let i = 0; i < characters_list_updated.length; i++) {
                  let char = characters_list_updated[i]['name'];
                  let currentDesc = characters_list_updated[i]['description'];
                  output = await updateCharacterDescription(currentDesc, char, p1, p2)
                  newDescriptions[char] = output;
                };
                              
                package = buildOrUpdateCharacters({
                  names: characters_list,
                  existingCharacters: characters_list_updated,
                  descriptions: newDescriptions,
                  update: true
                });   
                characters_list_updated = package['characterList']
                newDescriptions = package['descriptionsAll']
              }
              updateAllDescriptions();
            }   
             
            else
            {
              package = buildOrUpdateCharacters({ names: characters_list, descriptions: newDescriptions});
              characters_list_updated = package['characterList']
              newDescriptions = package['descriptionsAll']
              setTo=false;
              
            }
          }

          document.getElementById("charactersButton").addEventListener("click", () => openModal(0, setTo));
          closeButton.addEventListener("click", closeModal);
          overlay2.addEventListener("click", (e) => {
          if (e.target === overlay2) closeModal();});
          nextButton2.addEventListener("click", showNext);
          prevButton2.addEventListener("click", showPrev);

          
        } else {
          bookContentEl1.innerHTML = "<p>End of Book</p>";
        }
        if (bookmarkedPages.includes(pageNum))
        {document.getElementById("displayBookmark").style.display = "block";}
        else
        {document.getElementById("displayBookmark").style.display = "none";}

        if (highlightedTexts[pageNum]) {
          reHighlight(pageNum);
        }

        if (highlightedTexts[pageNum + 1]) {
          reHighlight(pageNum+1);
        }


      })
      .catch((error) => console.error("Load Page Error:", error));
  }

  // FUNCTION FOR CHAPTER TITLE DISPLAY
  function display_title(on_page, chapter_title) {
    const title = document.createElement("h2")
    title.className = "chapter-title";
    title.textContent = chapter_title;

    if (on_page === "one") {
      const wrapper = document.getElementById("book-content-1");
      wrapper.prepend(title)
    } 
    else if (on_page === "two") {
      const wrapper = document.getElementById("book-content-2"); 
      wrapper.prepend(title)
    }



  }




  loadPage(currentPage);
  nextButton.addEventListener("click", () => {
    currentPage += 2;
    loadPage(currentPage);
    pageN1.innerHTML = `<p>${currentPage+1}</p>`;
    pageN2.innerHTML = `<p>${currentPage+2}</p>`;

  });
  prevButton.addEventListener("click", () => {
    currentPage -= 2;
    loadPage(currentPage);
    pageN1.innerHTML = `<p>${currentPage+1}</p>`;
    pageN2.innerHTML = `<p>${currentPage+2}</p>`;

  });


  attachTextSelectionHandler(bookContentEl1);
  attachTextSelectionHandler(bookContentEl2);


  document.getElementById("simple-meaning").addEventListener("click", () => {
    handlePopupAction(
      "/simple_meaning",
      { selected_text: selectedText },
      "Simple Meaning"
    );
  });

  document.getElementById("contextual-meaning")
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
  fetch("/get-image", { method: "POST" })
    .then(response => response.json())
    .then(data => {
      appendVis(data)
    })
    .catch(error => console.error("Error:", error));
  
  });







// function to get highlighted text

  function attachTextSelectionHandler(bookContentEl) {
    bookContentEl.addEventListener("mouseup", (event) => {
      setTimeout(() => {
        selectedText = window.getSelection().toString().trim();
        selectedParagraph = "";
  
        if (selectedText) {
          const selection = window.getSelection();
          if (selection.rangeCount > 0) {
            const range = selection.getRangeAt(0);
            const rect = range.getBoundingClientRect(); // Only needed if you're using position
            
            const fullText = bookContentEl.innerText || bookContentEl.textContent;
            const paragraphs = fullText.split(/\n+/);
            const index = paragraphs.findIndex((para) =>
              para.includes(selectedText)
            );
            selectedParagraph = index !== -1 ? paragraphs[index] : "";
          }
        }
  

        return selectedText;
      }, 10);
    });
  }



// function to use popup buttons
  
  function handlePopupAction(url, payload, resultTitle) {
    st = selectedText
    if (!st) return;
    fetch(url, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    })
      .then((response) => response.json())
      .then((data) => {
        // appendInsight(resultTitle, data.LLM_output);
        highlightedWordsBlue[st.toLowerCase()] = data.LLM_output;
        highlightAllOccurrences(st, data.LLM_output, false);
      })
      .catch((error) => console.error("Popup Action Error:", error));
  }


// Recursively highlights all occurrences of a word within the bookContentEl.
function highlightAllOccurrences(word, meaning, useRed) {
  removeHighlights(bookContentEl1, word);
  removeHighlights(bookContentEl2, word);
  highlightTextNodes(bookContentEl1, word, meaning, useRed);
  highlightTextNodes(bookContentEl2, word, meaning, useRed);
  
}

// Escapes special regex characters in a string.
function escapeRegExp(string) {
  return string.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
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





let blueTooltipLocked = false;
let redTooltipLocked = false;

function highlightTextNodes(element, word, meaning, useRed) {
  if (element.nodeType === Node.TEXT_NODE) {
    const regex = new RegExp(`\\b(${escapeRegExp(word)})\\b`, "gi");
    if (regex.test(element.nodeValue)) {
      const frag = document.createDocumentFragment();
      const parts = element.nodeValue.split(regex);
      parts.forEach((part) => {
        if (regex.test(part)) {
          if (useRed)
          {
            const span = document.createElement("span");
            span.className = "highlighted-word-red";
            span.textContent = part;
            // Only mark the word, tooltip will be outside
            span.setAttribute("data-meaning", meaning);
            frag.appendChild(span);
          }
          else
          { 
            const span = document.createElement("span");
            span.className = "highlighted-word";
            span.textContent = part;
            // Only mark the word, tooltip will be outside
            span.setAttribute("data-meaning", meaning);
            frag.appendChild(span);
          }

        } else {
          frag.appendChild(document.createTextNode(part));
        }
      });
      element.parentNode.replaceChild(frag, element);
    }
  } else if (element.nodeType === Node.ELEMENT_NODE) {
    Array.from(element.childNodes).forEach((child) => {
      highlightTextNodes(child, word, meaning, useRed);
      
    });
  }
}





document.addEventListener('mouseover', function(e) {
  if (e.target.classList.contains('highlighted-word-red')) {
    if (!redTooltipLocked) {
      const tooltip = document.getElementById('fixed-tooltip-dictionary');
      tooltip.innerHTML = e.target.getAttribute('data-meaning');
      tooltip.classList.add('show');
    }
  }
});

document.addEventListener('mouseout', function(e) {
  if (e.target.classList.contains('highlighted-word-red')) {
    if (!redTooltipLocked) {
      const tooltip = document.getElementById('fixed-tooltip-dictionary');
      tooltip.classList.remove('show');
    }
  }
});

// Click to lock/unlock
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('highlighted-word-red')) {
    redTooltipLocked = !redTooltipLocked; // toggle lock
    const tooltip = document.getElementById('fixed-tooltip-dictionary');
    tooltip.innerHTML = e.target.getAttribute('data-meaning');
    tooltip.classList.add('show');
  } else {
    if (redTooltipLocked) {
      redTooltipLocked = false;
      const tooltip = document.getElementById('fixed-tooltip-dictionary');
      tooltip.classList.remove('show');
    }
  }
});




// Hover behavior
document.addEventListener('mouseover', function(e) {
  if (e.target.classList.contains('highlighted-word')) {
    if (!blueTooltipLocked) {
      const tooltip = document.getElementById('fixed-tooltip-ai');
      tooltip.innerHTML = e.target.getAttribute('data-meaning');
      tooltip.classList.add('show');
    }
  }
});

document.addEventListener('mouseout', function(e) {
  if (e.target.classList.contains('highlighted-word')) {
    if (!blueTooltipLocked) {
      const tooltip = document.getElementById('fixed-tooltip-ai');
      tooltip.classList.remove('show');
    }
  }
});

// Click to lock/unlock
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('highlighted-word')) {
    blueTooltipLocked = !blueTooltipLocked; // toggle lock
    const tooltip = document.getElementById('fixed-tooltip-ai');
    tooltip.innerHTML = e.target.getAttribute('data-meaning');
    tooltip.classList.add('show');
  } else {
    if (blueTooltipLocked) {
      blueTooltipLocked = false;
      const tooltip = document.getElementById('fixed-tooltip-ai');
      tooltip.classList.remove('show');
    }
  }
});



//  FOR CHARACTERS HIGHLITING AND DESCRIPTION

// function highlightTextNodesTest(element, word, useRed) {
//   if (element.nodeType === Node.TEXT_NODE) {
//     const regex = new RegExp(`\\b(${escapeRegExp(word)})\\b`, "gi");
//     if (regex.test(element.nodeValue)) {
//       const frag = document.createDocumentFragment();
//       const parts = element.nodeValue.split(regex);
//       parts.forEach((part) => {
//         if (regex.test(part)) {
//           console.log(part)
//           console.log('nuenuiebrfdbrh')

//         } else {
//           frag.appendChild(document.createTextNode(part));
//         }
//       });
//       element.parentNode.replaceChild(frag, element);
//     }
//   } else if (element.nodeType === Node.ELEMENT_NODE) {
//     Array.from(element.childNodes).forEach((child) => {
//       highlightTextNodesTest(child, word, useRed);
      
//     });
//   }
// }

// function highlightAllOccurrencesTest(word, useRed)
// {
//   highlightTextNodesTest(bookContentEl1, word, useRed);
//   highlightTextNodesTest(bookContentEl2, word, useRed);
// }












  // For HIGHLITING

function getNodePath(node) {
  const path = [];
  while (node && node !== document.body) {
    const parent = node.parentNode;
    if (!parent) break;
    const index = Array.from(parent.childNodes).indexOf(node);
    path.unshift(index);
    node = parent;
  }
  return path;
}

function resolveNodePath(path) {
  let node = document.body;
  for (const idx of path) {
    node = node.childNodes[idx];
    if (!node) break;
  }
  return node;
}



function reHighlight(pageNum) {
  const entries = highlightedTexts[pageNum] || [];
  entries.forEach(entry => {
    const startNode = resolveNodePath(entry.start.nodePath);
    const endNode = resolveNodePath(entry.end.nodePath);

    if (!startNode || !endNode) return;

    const range = document.createRange();
    range.setStart(startNode, entry.start.offset);
    range.setEnd(endNode, entry.end.offset);
    applyHighlight(range);
  });
}


function applyHighlight(range) {
  const span = document.createElement("span");
  span.classList.add("highlighted-text");
  span.textContent = range.toString();
  range.deleteContents();
  range.insertNode(span);
}



highlightButton.addEventListener("click", () => {
  const st = window.getSelection().toString();
  if (!st) return;

  const range = window.getSelection().getRangeAt(0);
  const start = { nodePath: getNodePath(range.startContainer), offset: range.startOffset };
  const end = { nodePath: getNodePath(range.endContainer), offset: range.endOffset };

  const parentDiv = range.startContainer.parentElement.closest("div").id;
  let targetPage;
  if (parentDiv === "book-content-1") {
    targetPage = currentPage;
  } else {
    targetPage = currentPage + 1;
  }

  applyHighlight(range);
  if (!highlightedTexts[targetPage]) {
    highlightedTexts[targetPage] = [];
  }
  highlightedTexts[targetPage].push({ start, end, st});
  window.getSelection().removeAllRanges();

});












// Bookmark
const bookmarkButton = document.getElementById("bookmark-button");
const bookmark = document.getElementById("displayBookmark");
bookmarkButton.addEventListener("click", () => {
  bookmark.style.display = "block";
  bookmarkedPages.push(currentPage);
  bookmarkedPages.push(currentPage+1);
});





  // NOTES LOGIC

//   const addBtn = document.querySelector("#addNotesBtn");

// addBtn.addEventListener("click", ()=>{
//     let stickyCont = document.querySelector(".sticky-container");
//     let stickySingle = document.createElement('div');
//     stickySingle.classList.add('sticky');
//     stickySingle.contentEditable = "true";
//     stickySingle.setAttribute = ("role","textbox");
//     stickySingle.innerHTML = "Write me<br>"
//     stickyCont.appendChild(stickySingle);
  
//     // Delete button
//     let close = document.createElement('span');
//     close.classList.add('close');
//     close.innerHTML = "X";
//     close.contentEditable = "false";
//     stickySingle.appendChild(close);
  
//     // Delete function. used "for" to bind delete button with 
//     // coresponding stickynote
//     let stickies = document.getElementsByClassName("sticky");
//     let xs = document.getElementsByClassName("close");

//     for (let i = 0; i < stickies.length; i++){
//         xs[i].addEventListener("click", ()=> {
//             stickies[i].style.display = "none";
//         });
//     }
    
//     function randomNumber(min, max) { 
//       return Math.random() * (max - min) + min; 
//     }
//     let angle = randomNumber(-3,3);
//     stickySingle.style.transform = "rotate(" + angle+"deg)";
  
//     let color = randomNumber(1,720);
//     stickySingle.style.filter = "hue-rotate(" + color +"deg)";
// });
// Get the elements
// Get the elements
// Get the elements
const addBtn = document.querySelector("#addNotesBtn");
const overlay = document.querySelector("#overlay");

// When the user clicks the "Add Note" button
// When the user clicks the "Add Note" button
addBtn.addEventListener("click", () => {
  // Show the overlay
  overlay.style.display = "block";

  let stickyCont = document.querySelector(".sticky-container");
  let stickySingle = document.createElement("div");
  stickySingle.classList.add("sticky");

  stickySingle.contentEditable = "true";
  stickySingle.setAttribute("role", "textbox");
  stickySingle.innerHTML = "Write me<br>";

  stickyCont.appendChild(stickySingle);

  // Add a close button to remove the sticky note
  let close = document.createElement("span");
  close.classList.add("close");
  close.innerHTML = "X";
  close.contentEditable = "false";
  stickySingle.appendChild(close);

  // Close button functionality
  close.addEventListener("click", () => {
    stickySingle.style.display = "none";
    overlay.style.display = "none"; // Hide the overlay
  });

  // Function for random rotation and color of sticky note
  function randomNumber(min, max) {
    return Math.random() * (max - min) + min;
  }
  let angle = randomNumber(-3, 3);
  stickySingle.style.transform = "rotate(" + angle + "deg)";

  let color = randomNumber(1, 720);
  stickySingle.style.filter = "hue-rotate(" + color + "deg)";

  // Add a Finish button to stop editing and move the note
  let finishBtn = document.createElement("button");
  finishBtn.innerHTML = "Finish Note";
  finishBtn.classList.add("finish-btn");
  finishBtn.setAttribute("contenteditable", "false"); // Ensure it's not editable
  stickySingle.appendChild(finishBtn);
  // When the user clicks Finish, hide the overlay and shrink the sticky note
  finishBtn.addEventListener("click", () => {
    stickySingle.classList.add("hide"); // Shrink the sticky note into a circle
    overlay.style.display = "none"; // Hide the overlay
    makeDraggable(stickySingle); // Enable drag functionality on the dot
  });

  // Listen for focus to remove overlay and center the sticky note
  stickySingle.addEventListener("focus", () => {
    // The overlay stays visible when editing, no action needed here
  });

  // Listen for blur (when editing is done) and hide the overlay
  stickySingle.addEventListener("blur", () => {
    // If you want, you could hide the overlay after finishing writing.
  });

  // Allow clicking on the dot to reopen the sticky note
  stickySingle.addEventListener("click", () => {
    if (stickySingle.classList.contains("hide")) {
      // Only allow reopening if the note is currently in the dot form
      stickySingle.classList.remove("hide"); // Reopen the sticky note
      stickySingle.style.position = "absolute"; // Make sure it stays in place when opened again
      stickySingle.style.transition = "all 0.5s ease-out"; // Smooth transition
    }
  });
});

// Make the sticky note draggable
function makeDraggable(note) {
  let isDragging = false;
  let offsetX, offsetY;

  note.addEventListener("mousedown", (e) => {
    isDragging = true;
    offsetX = e.clientX - note.getBoundingClientRect().left;
    offsetY = e.clientY - note.getBoundingClientRect().top;
    note.style.transition = "none"; // Disable transition during drag
  });

  document.addEventListener("mousemove", (e) => {
    if (isDragging) {
      note.style.position = "absolute";
      note.style.left = `${e.clientX - offsetX}px`;
      note.style.top = `${e.clientY - offsetY}px`;
    }
  });

  document.addEventListener("mouseup", () => {
    if (isDragging) {
      isDragging = false;
      note.style.transition = "all 0.5s ease-in-out"; // Enable transition after drag
    }
  });
}












 // Dictionary button

 function handlePopupActionForDictionary() {
  st = selectedText
  if (!st) return;
  fetch('/dictionary', {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(st),
  })
    .then((response) => response.json())
    .then((data) => {
      highlightedWordsRed[st.toLowerCase()] = data.def;
      highlightAllOccurrences(st, data.def, true);
    })
    .catch((error) => console.error("Popup Action Error:", error));
}

 
 document.getElementById("dictionaryBtn").addEventListener("click", () => {
  handlePopupActionForDictionary();
});




 // Popup for characters
function buildOrUpdateCharacters({ 
  names, 
  existingCharacters = [], 
  images = {}, 
  descriptions = {}, 
  update = false 
}) {
  
  const charactersMap = {};



  
  // Start with existing characters if updating
  if (update) {
    for (const char of existingCharacters) {
      charactersMap[char.name] = { ...char };
    }
  }
  
  // Process each name
  for (const name of names) {
    const image = images[name] || `https://dummyimage.com/500x250/cccccc/000000&text=${encodeURIComponent(name)}`
    const description = descriptions[name] || `${name} is a character whose story is yet to be written.`;

    if (update && charactersMap[name]) {
      // Update existing character
      charactersMap[name].image = image;
      charactersMap[name].description = description;
    } else {
      // Add new character
      charactersMap[name] = {
        name,
        image,
        description
      };
    }
  }
  const characterList = Object.values(charactersMap);
  const descriptionsAll = {};
  for (const char of characterList) {
    descriptionsAll[char.name] = char.description;
  }

  // Return updated character list
  return { characterList, descriptionsAll };
}


let currentIndex = 0;
let lastFocused = null;



function openModal(index = 0, forNone=false) {
  document.getElementById("charBadge").style.display = "none";
  lastFocused = document.activeElement;
  currentIndex = index;
  if (forNone)
  {updateContentForNone()}
  else
  {updateContent()};
  overlay2.classList.add("active");
  closeButton.focus();
  document.body.style.overflow = "hidden";
  document.addEventListener("keydown", handleKeyDown);
}

function closeModal() {
  overlay2.classList.remove("active");
  document.body.style.overflow = "";
  if (lastFocused) lastFocused.focus();
  document.removeEventListener("keydown", handleKeyDown);
}

function updateContent() {
  const char = characters_list_updated[currentIndex];
  imgEl.src = char.image;
  imgEl.alt = "Portrait of " + char.name;
  titleEl.textContent = char.name;
  descEl.textContent = char.description;
}
function updateContentForNone() {
  imgEl.src = 'https://dummyimage.com/500x250/cccccc/000000&text=No+Characters';
  imgEl.alt = "No characters found yet ";
  titleEl.textContent = 'No major characters found yet';
  descEl.textContent = 'No character data available at this time.';
}

function showNext() {
  if (currentIndex < characters_list_updated.length - 1) {
    currentIndex++;
    animateContentChange();
  }
}

function showPrev() {
  if (currentIndex > 0) {
    currentIndex--;
    animateContentChange();
  }
}

function animateContentChange() {
  contentEl.classList.add("fade-out");
  contentEl.addEventListener(
    "transitionend",
    function handler() {
      updateContent();
      contentEl.classList.remove("fade-out");
      contentEl.removeEventListener("transitionend", handler);
    },
    { once: true }
  );
}

function handleKeyDown(e) {
  if (e.key === "Escape") closeModal();
  if (e.key === "ArrowRight") showNext();
  if (e.key === "ArrowLeft") showPrev();
  if (e.key === "Tab") {
    const focusables = modal.querySelectorAll("button");
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }
}


// UPDATE CHARACTERS FUNCTION

async function updateCharacterDescription(currentDesc, char, p1, p2) {
  try {
      const response = await fetch('/updateCharacter', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({
              current_desc: currentDesc,
              char: char,
              p1: p1,
              p2: p2
          })
      });

      const data = await response.json();
      return data.output;
  } catch (error) {
      console.error('Error updating character:', error);
  }
}

// const openBtn = document.getElementById('charactersButton');
// const closeBtn = document.getElementById('closePopup');
// const overlay2 = document.getElementById('popupOverlay');

// openBtn.addEventListener('click', () => {
//   const popupTitle = overlay2.querySelector('h2');
//   const popupMessage = overlay2.querySelector('p');
//   popupTitle.textContent = 'DUMMY TITLE';
//   // popupMessage.textContent = 'DUMMY MESSAGE THIS NOTHING ELSE DONT LOOK FOR SOMETHING ELSE';
//   popupMessage.textContent = characters_list;
//   overlay2.classList.remove('hidden');
//   requestAnimationFrame(() => overlay2.classList.add('show'));
// });

// closeBtn.addEventListener('click', () => {
//   overlay2.classList.remove('show');
//   setTimeout(() => overlay2.classList.add('hidden'), 400); // Match the CSS transition duration
// });




// CHATBOT SECTION -------------------------------------

const bot = document.getElementById("chatbot"),
toggle = document.getElementById("toggle"),
msgs = document.getElementById("messages"),
input = document.getElementById("input"),
send = document.getElementById("send");

toggle.addEventListener("click", () =>
bot.classList.toggle("chatbot--open")
);

function appendMessage(text, role) {
const li = document.createElement("li");
li.className = role;
const arrow = document.createElement("div");
arrow.className = "chatbot__arrow";
const msg = document.createElement("div");
msg.className = "chatbot__message";
msg.textContent = text;
li.appendChild(arrow);
li.appendChild(msg);
msgs.appendChild(li);
msgs.parentNode.scrollTop = msgs.parentNode.scrollHeight;
}

function showLoader() {
const li = document.createElement("li");
li.className = "is-ai";
const arrow = document.createElement("div");
arrow.className = "chatbot__arrow";
const loader = document.createElement("div");
loader.className = "loader";
for (let i = 0; i < 3; i++) {
  const dot = document.createElement("div");
  dot.className = "loader__dot";
  loader.appendChild(dot);
}
li.appendChild(arrow);
li.appendChild(loader);
msgs.appendChild(li);
msgs.parentNode.scrollTop = msgs.parentNode.scrollHeight;
return li;
}

send.addEventListener("click", () => {
  const question = input.value.trim();
  if (!question) return;

  appendMessage(question, "is-user");
  input.value = "";

  const loaderLi = showLoader();

  fetch("/chat_book", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question, page_number: currentPage }) // Make sure `currentPage` is defined
  })
    .then((response) => response.json())
    .then((data) => {
      loaderLi.remove();
      const reply = data.chat_reply || "Sorry, I didn’t quite get that.";
      appendMessage(reply, "is-ai");
    })
    .catch((error) => {
      loaderLi.remove();
      console.error("Chat Error:", error);
      appendMessage("Oops, something went wrong. Please try again.", "is-ai");
    });
});

input.addEventListener("keypress", (e) => {
if (e.key === "Enter") send.click();
});


 // FLIPPIMNG PAGES ---------------------------------
 
 



  // ANNOTATION SECTION ---------------------------------

