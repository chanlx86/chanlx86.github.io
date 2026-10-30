/* ES5 only; downloads and navigation work without this enhancement. */
(function () {
    'use strict';
    var search = document.getElementById('search');
    if (!search) { return; }
    var cards = document.querySelectorAll('.app-card');
    var buttons = document.querySelectorAll('[data-filter]');
    var filter = 'all';
    function update() {
        var query = search.value.replace(/^\s+|\s+$/g, '').toLowerCase();
        var count = 0;
        for (var i = 0; i < cards.length; i++) {
            var card = cards[i];
            var match = (filter === 'all' || card.getAttribute('data-category') === filter) && card.getAttribute('data-search').toLowerCase().indexOf(query) !== -1;
            card.style.display = match ? '' : 'none';
            if (match) { count++; }
        }
        document.getElementById('empty').hidden = count !== 0;
    }
    search.addEventListener('input', update, false);
    for (var i = 0; i < buttons.length; i++) {
        buttons[i].addEventListener('click', function () {
            filter = this.getAttribute('data-filter');
            for (var j = 0; j < buttons.length; j++) {
                var selected = buttons[j] === this;
                buttons[j].className = selected ? 'selected' : '';
                buttons[j].setAttribute('aria-pressed', selected ? 'true' : 'false');
            }
            update();
        }, false);
    }
}());
