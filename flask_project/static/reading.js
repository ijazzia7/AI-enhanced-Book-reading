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
const highlightedWords = {};
const highlightButton = document.getElementById("highlight-button");
const bookmarkedPages = [];
const highlightedTexts = {};






let currentPage = 0;
function loadPage(pageNum) {
    fetch(`/get_page/${pageNum}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.page1) {
          bookContentEl1.innerHTML = `<p>${data.page1}</p>`;
          bookContentEl2.innerHTML = `<p>${data.page2}</p>`;
          console.log(data.page1)
          on_page = data.chap
          chapter_title = data.chapterName
          if (on_page!='none'){
          display_title(on_page, chapter_title)
        }
          prevButton.disabled = data.prev_page < 0;
          nextButton.disabled = data.next_page === null;
          // Re-highlight all processed words on this page
          for (let word in highlightedWords) {
            highlightAllOccurrences(word, highlightedWords[word]);
          }
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
        highlightedWords[st.toLowerCase()] = data.LLM_output;
        highlightAllOccurrences(st, data.LLM_output);
      })
      .catch((error) => console.error("Popup Action Error:", error));
  }


// Recursively highlights all occurrences of a word within the bookContentEl.
function highlightAllOccurrences(word, meaning) {
  removeHighlights(bookContentEl1, word);
  removeHighlights(bookContentEl2, word);
  highlightTextNodes(bookContentEl1, word, meaning);
  highlightTextNodes(bookContentEl2, word, meaning);

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

  const addBtn = document.querySelector("#addNotesBtn");

addBtn.addEventListener("click", ()=>{
    let stickyCont = document.querySelector(".sticky-container");
    let stickySingle = document.createElement('div');
    stickySingle.classList.add('sticky');
    stickySingle.contentEditable = "true";
    stickySingle.setAttribute = ("role","textbox");
    stickySingle.innerHTML = "Write me<br>"
    stickyCont.appendChild(stickySingle);
  
    // Delete button
    let close = document.createElement('span');
    close.classList.add('close');
    close.innerHTML = "X";
    close.contentEditable = "false";
    stickySingle.appendChild(close);
  
    // Delete function. used "for" to bind delete button with 
    // coresponding stickynote
    let stickies = document.getElementsByClassName("sticky");
    let xs = document.getElementsByClassName("close");

    for (let i = 0; i < stickies.length; i++){
        xs[i].addEventListener("click", ()=> {
            console.log(stickies.length);
            stickies[i].style.display = "none";
        });
    }
    
    function randomNumber(min, max) { 
      return Math.random() * (max - min) + min; 
    }
    let angle = randomNumber(-3,3);
    stickySingle.style.transform = "rotate(" + angle+"deg)";
  
    let color = randomNumber(1,720);
    stickySingle.style.filter = "hue-rotate(" + color +"deg)";
});





 // FLIPPIMNG PAGES ---------------------------------
 
 



  // ANNOTATION SECTION ---------------------------------

