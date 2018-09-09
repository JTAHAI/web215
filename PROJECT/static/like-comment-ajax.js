var likeCommentForm = $("#like-comment-form");
var likeCommentMessage = $("#like-comment-message");

function like_comment(event) {
    event.preventDefault();
    $.ajax({
        url: "/like-comment",
        method: "POST",
        data: likeCommentForm.serialize(),
        success: function(data, status, xhrObj) {
            likeCommentMessage.text(data);
        }
    })
}

likeCommentForm.submit(like_comment);