//This is the <div id="books-container"> element:
var booksContainer = $("#books-container");

//Load the /get-books HTML code into booksContainer right away:
booksContainer.load("/get-books");

//This is the <form id="add-book-form"> element:
var addBookForm = $("#add-book-form");

//This function is called when the user tries to submit addBookForm:
function add_book(event) {
    //Do not actually submit the form:
    event.preventDefault();
    //Send a POST AJAX request using the form data to /add-book:
    $.ajax({
        url: "/add-book",
        method: "POST",
        data: addBookForm.serialize(),
        success: function(data, status, xhrObj) {
            //When the request is done, load the new info:
            booksContainer.load("/get-books");
        }
    })
}

//Call add_book whenever the user tries to submit the form:
addBookForm.submit(add_book);

//This is the <form id="add-user-form"> element:
var addUserForm = $("#add-user-form");
//This is the <div id="user-message"> element:
var userMessage = $("#user-message");

//This function is called when the user tries to submit addUserForm:
function add_user(event) {
    //Do not actually submit the form:
    event.preventDefault();
    //Send a POST AJAX request using the form data to /add-user:
    $.ajax({
        url: "/add-user",
        method: "POST",
        data: addUserForm.serialize(),
        success: function(data, status, xhrObj) {
            //When the request is done, put the response from /add-user into userMessage:
            userMessage.text(data);
        }
    })
}

//Call add_user whenever the user tries to submit the form:
addUserForm.submit(add_user);