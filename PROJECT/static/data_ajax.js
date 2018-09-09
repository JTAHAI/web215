var commentsContainer = $("#comments-container");

commentsContainer.load("/get-comments");

var addCommentForm = $("#add-comment-form");

function add_comment(event) {
    event.preventDefault();
    $.ajax({
        url: "/add-comment",
        method: "POST",
        data: addCommentForm.serialize(),
        success: function(data, status, xhrObj) {
            commentsContainer.load("/get-comments");
        }
    })
}

addCommentForm.submit(add_comment);

var addUserForm = $("#add-user-form");
var userMessage = $("#user-message");

function add_user(event) {
    event.preventDefault();
    $.ajax({
        url: "/add-user",
        method: "POST",
        data: addUserForm.serialize(),
        success: function(data, status, xhrObj) {
            userMessage.text(data);
        }
    })
}

addUserForm.submit(add_user);