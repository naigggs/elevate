$(document).ready(function () {
    const searchInput = $('#search-input');
    const searchResults = $('#search-results');

    searchInput.on('input', function () {
        const query = searchInput.val().trim();
        if (query.length > 0) {
            // Send an AJAX request to your Django view to fetch search results
            $.ajax({
                url: '/search_user/',
                data: { 'q': query },
                success: function (data) {
                    // Display the search results in the dropdown
                    searchResults.html(data);
                    searchResults.show();
                }
            });
        } else {
            // Clear and hide the dropdown if the input is empty
            searchResults.empty();
            searchResults.hide();
        }
    });

    // Handle selecting a search result (optional)
    searchResults.on('click', 'li', function () {
        searchInput.val($(this).text());
        searchResults.empty();
        searchResults.hide();
    });
});