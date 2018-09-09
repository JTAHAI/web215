var commentsContainer = $("#comments-container");

commentsContainer.load("/get-comments");

var addCommentForm = $("form");

function post_info(event) {
    event.preventDefault();
    $.ajax({
        url: "/add-comment",
        method: "POST",
        data: addCommentForm.serialize(),
        success: function(data, status, xhrObj) {
            dataComments.load("/get-comments");
        }
    })
}

addCommentForm.submit(post_info);