//Member search
function searchMembers() {
    let input = document.getElementById('memberSearch').value.toLowerCase();
    let cards = document.querySelectorAll('.member-card');
    let noResults = document.getElementById('noResults');
    let visibleCount = 0;

    //Loop throuhg every member card to check for match
    cards.forEach(card => {
        let name = card.querySelector('.member-name').innerText.toLowerCase();
        let role = card.querySelector('.member-role').innerText.toLowerCase();

        if (name.includes(input) || role.includes(input)) {
            card.style.display = "block";
            visibleCount++;
        } else {
            card.style.display = "none";
        }
    });
    //No resoult message
    noResults.style.display = visibleCount === 0 ? "block" : "none";
}

//Filter members based on their specific job role
function filterMembers(role) {
    let cards = document.querySelectorAll('.member-card');
    let buttons = document.querySelectorAll('.filter-btn');
    let noResults = document.getElementById('noResults');
    let visibleCount = 0;
    buttons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.getAttribute('onclick').includes(`'${role}'`)) {
            btn.classList.add('active');
        }
    });

    //Filter cards based on teh data role atribute
    cards.forEach(card => {
        let cardRole = card.getAttribute('data-role') || "";

        if (role === 'all' || cardRole.includes(role)) {
            card.style.display = "block";
            visibleCount++;
        } else {
            card.style.display = "none";
        }
    });
    if (noResults) {
        noResults.style.display = (visibleCount === 0) ? "block" : "none";
    }
}