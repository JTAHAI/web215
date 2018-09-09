var editCommentForm = $("#edit-comment-form");
var editCommentMessage = $("#edit-comment-message");

var nameInput = $("[name=name]");
var commentInput = $("[name=comment]");

function edit_comment(event) {
    event.preventDefault();

    if (nameInput.val().length > 50) {
        editCommentMessage.text("The new name is more than 50 characters!");
        return;
    }
    else if (commentInput.val().length > 1000) {
        editCommentMessage.text("The new comment is more than 1000 characters!");
        return;
    }
    else {
        editCommentMessage.text("");
    }

    $.ajax({
        url: "/edit-comment",
        method: "POST",
        data: editCommentForm.serialize(),
        success: function(data, status, xhrObj) {
            editCommentMessage.text(data);
        }
    })
}

editCommentForm.submit(edit_comment);