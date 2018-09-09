//This is the <div id="comments-container"> element:
var commentsContainer = $("#comments-container");

//Load the /get-books HTML code into booksContainer right away:
commentsContainer.load("/get-comments");

//This is the <form id="add-comment-form"> element:
var addCommentForm = $("#add-comment-form");

//This function is called when the user tries to submit addCommentForm:
function add_comment(event) {
    //Do not actually submit the form:
    event.preventDefault();
    //Send a POST AJAX request using the form data to /add-comment:
    $.ajax({
        url: "/add-comment",
        method: "POST",
        data: addCommentForm.serialize(),
        success: function(data, status, xhrObj) {
            //When the request is done, load the new info:
            commentsContainer.load("/get-comments");
        }
    })
}

//Call add_comment whenever the user tries to submit the form:
addCommentsForm.submit(add_comment);

