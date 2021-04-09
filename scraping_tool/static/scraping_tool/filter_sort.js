// Filter
const search = document.querySelector('.search input');

const filterMails = (term, mails) => {

    Array.from(mails.children)
        // Filtering condtions
        .filter((mail) => !mail.getElementsByTagName('h6')[0].textContent.toLowerCase().includes(term))
        .forEach((mail) => mail.classList.add('filtered'));

    Array.from(mails.children)
        .filter((mail) => mail.getElementsByTagName('h6')[0].textContent.toLowerCase().includes(term))
        .forEach((mail) => mail.classList.remove('filtered'));

};

search.addEventListener('keyup', () => {
    // Remove spaces and convert to lower cases
    const term = search.value.trim().toLowerCase();
    filterMails(term, scheduled_items);
    filterMails(term, unscheduled_items);
});

// Sort by date
const sort_by_date = (element) => {
    const parent = document.getElementById(element);
    const items = parent.children;
    for (let i = items.length - 1; i >= 0; i--) {
        parent.insertAdjacentElement('beforeend', items[i]);
    }
}

// for scheduled_items
$('.sort-btn-scheduled').click(function() {
    $('.sort-btn-scheduled').toggle();
    sort_by_date('scheduled-items')
})

// for unscheduled_items
$('.sort-btn-unscheduled').click(function() {
    $('.sort-btn-unscheduled').toggle();
    sort_by_date('unscheduled-items')
})
