// Delete:Ajax (click the delete icon or click the delete nav)
$('.delete-nav').click(function(event) {
    event.preventDefault();
    const delete_url = $(this).attr("href");
    $.ajax(
        {
            method: "GET",
            url: delete_url,
            data: {}
        }
    )
    // success
    .done( () => {
        const index_url = $('.index-nav').attr("href");
        window.location.href = index_url;
    })
    // fail
    .fail( () => {
        alert('Deletion Failed')
    })
})
