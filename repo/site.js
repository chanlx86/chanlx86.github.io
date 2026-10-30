/* ES5: progressive enhancement only; all release links are static HTML. */
(function () {
    'use strict';
    var ua = navigator.userAgent || '';
    var isIOS = /iPad|iPhone|iPod/.test(ua) || (/Macintosh/.test(ua) && navigator.maxTouchPoints > 1);
    if (/Cydia|Sileo|Zebra/i.test(ua) || /(?:\?|&)view=cydia(?:&|$)/.test(location.search)) {
        document.body.className += ' in-cydia';
    }
    function notice(anchor) {
        var n = document.getElementById('install-notice');
        if (!n) {
            n = document.createElement('div'); n.id = 'install-notice';
            n.className = 'install-notice'; n.setAttribute('role', 'status');
        }
        n.textContent = '请在 iPhone / iPad 的 Safari 中打开此页面安装。电脑可使用下载按钮保存安装包。';
        var target = anchor.closest ? anchor.closest('.install-panel') : null;
        target = target || document.getElementById('software') || document.querySelector('main');
        target.insertBefore(n, target.firstChild);
        if (anchor.getAttribute('data-help')) {
            var more = document.createElement('a');
            more.href = anchor.getAttribute('data-help'); more.textContent = ' 查看详情 ›';
            n.appendChild(more);
        }
    }
    var install = document.querySelectorAll('.ota,.cydia-action');
    for (var i = 0; i < install.length; i++) {
        install[i].addEventListener('click', function (event) {
            if (!isIOS && !/Cydia|Sileo|Zebra/i.test(ua)) { event.preventDefault(); notice(this); }
        }, false);
    }
    var input = document.getElementById('search');
    if (!input) { return; }
    var rows = document.querySelectorAll('.app-row');
    var groups = document.querySelectorAll('[data-section]');
    var buttons = document.querySelectorAll('[data-filter]');
    var filter = 'all';
    function update() {
        var query = input.value.replace(/^\s+|\s+$/g, '').toLowerCase(); var total = 0;
        for (var j = 0; j < rows.length; j++) {
            var row = rows[j];
            var match = (filter === 'all' || row.getAttribute('data-category') === filter) && row.getAttribute('data-search').toLowerCase().indexOf(query) >= 0;
            row.style.display = match ? '' : 'none'; if (match) { total++; }
        }
        for (var k = 0; k < groups.length; k++) {
            var visible = false; var children = groups[k].querySelectorAll('.app-row');
            for (var m = 0; m < children.length; m++) { if (children[m].style.display !== 'none') { visible = true; } }
            groups[k].style.display = visible ? '' : 'none';
        }
        document.getElementById('empty').hidden = total !== 0;
    }
    input.addEventListener('input', update, false);
    for (var j = 0; j < buttons.length; j++) {
        buttons[j].addEventListener('click', function () {
            filter = this.getAttribute('data-filter');
            for (var k = 0; k < buttons.length; k++) {
                var selected = buttons[k] === this; buttons[k].className = selected ? 'selected' : '';
                buttons[k].setAttribute('aria-pressed', selected ? 'true' : 'false');
            }
            update();
        }, false);
    }
}());
