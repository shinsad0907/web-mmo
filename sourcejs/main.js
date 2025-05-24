// Tab switching for product detail
document.addEventListener('DOMContentLoaded', function () {
    // Tab switching
    document.querySelectorAll('.detail-tabs').forEach(function (tabGroup) {
        const buttons = tabGroup.querySelectorAll('.tab-button');
        buttons.forEach(btn => {
            btn.addEventListener('click', function () {
                buttons.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const tabId = btn.getAttribute('data-tab');
                document.querySelectorAll('.tab-pane').forEach(pane => {
                    pane.classList.toggle('active', pane.id === tabId);
                });
            });
        });
    });

    // Flash message close
    document.querySelectorAll('.close-flash').forEach(function (btn) {
        btn.addEventListener('click', function () {
            btn.parentElement.style.display = 'none';
        });
    });

    // Fade-in on scroll
    function revealOnScroll() {
        document.querySelectorAll('.fade-in').forEach(function (el) {
            const rect = el.getBoundingClientRect();
            if (rect.top < window.innerHeight - 60) {
                el.classList.add('visible');
            }
        });
    }
    window.addEventListener('scroll', revealOnScroll);
    revealOnScroll();

    // Recharge amount & total update
    const amountRadios = document.querySelectorAll('input[name="amount"]');
    const selectedAmount = document.getElementById('selected-amount');
    const totalAmount = document.getElementById('total-amount');
    if (amountRadios.length && selectedAmount && totalAmount) {
        amountRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                let val = parseInt(radio.value).toLocaleString('vi-VN') + ' VNĐ';
                selectedAmount.textContent = val;
                totalAmount.textContent = val;
            });
        });
    }
});