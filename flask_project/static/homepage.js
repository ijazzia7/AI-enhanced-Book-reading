const books = [
  {
    title: "The Kite Runner",
    author: "Khaled Husseni",
    imgPath: "static/images/thekiterunner.jpg",
    link: "./book-link",
    category: "fiction",
  },
  {
    title: "Crime and Punishment",
    author: "Fyodor Dostoevsky",
    imgPath: "static/images/crimeandpunishment.jpg",
    link: "./book-link",
    category: "fiction",
  },
  {
    title: "The Prophet",
    author: "Khalil Gibran",
    imgPath: "static/images/theprophet.jpg",
    link: "./book-link",
    category: "fiction",
  },
  {
    title: "To Kill a Mockingbird",
    author: "Harper Lee",
    imgPath: "static/images/mockingbird.png",
    link: "./book-link",
    category: "fiction",
  },
];

// functions

function showBooks(books) {
  // 2. Displaying them on the screen

  // first remove all the existing books
  document.querySelector(".categories-books").innerHTML = "";

  books.forEach((book) => {
    // now show the filtered books
    document.querySelector(
      ".categories-books"
    ).innerHTML += ` <a href='${book.link}' class="book-link">
                  <div class="book-card">
                    <img
                      class="book_images"
                      src='${book.imgPath}'
                      alt="Book 4"
                    />
                    <div class="book-title">${book.title}</div>
                    <div class="book-author">${book.author}</div>
                  </div>
                </a>`;
  });
}

// HTML elements

const categoryItems = Array.from(document.querySelectorAll(".category-item"));

categoryItems.map((categoryItem) => {
  categoryItem.addEventListener("click", () => {
    // removing active class from tab with active class
    document.querySelector(".category-item.active").classList.remove("active");
    // adding active class on clicked tab
    categoryItem.classList.add("active");
    // showing books of seleted tab

    // 1. filtering books as per the selected tab

    let filteredBooks;

    if (categoryItem.textContent === "All") {
      filteredBooks = books;
    } else {
      filteredBooks = books.filter((book) => {
        return book.category === categoryItem.textContent.toLowerCase();
      });
    }

    showBooks(filteredBooks);
  });
});

window.addEventListener("load", () => {
  showBooks(books);
});
