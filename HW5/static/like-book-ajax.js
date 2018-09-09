//This is the <form> element:
var likeBookForm = $("form");
//This is the <div id="like-book-message"> element:
var likeBookMessage = $("#like-book-message");

//This function is called when the user tries to submit the form:
function like_book(event) {
    //Do not actually submit the form:
    event.preventDefault();
    //Send a POST AJAX request using the form data to /like-book:
    $.ajax({
        url: "/like-book",
        method: "POST",
        data: likeBookForm.serialize(),
        success: function(data, status, xhrObj) {
            //When the request is done, put the response from /like-book into likeBookMessage:
            likeBookMessage.text(data);
        }
    })
}

//Call like_book whenever the user tries to submit the form:
likeBookForm.submit(like_book);