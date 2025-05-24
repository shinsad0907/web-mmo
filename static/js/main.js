document.addEventListener('DOMContentLoaded', function () {
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

    // Buy button click effect (demo)
    document.querySelectorAll('.buy-button').forEach(button => {
        button.addEventListener('click', function (e) {
            if (button.tagName === 'A') return; // skip link
            button.innerHTML = 'Đang xử lý...';
            button.style.background = 'linear-gradient(45deg, #00ff00, #00ffff)';
            setTimeout(() => {
                alert('Cảm ơn bạn đã quan tâm! Vui lòng đăng nhập để mua hàng.');
                button.innerHTML = 'Mua Ngay';
                button.style.background = 'linear-gradient(45deg, #ff00ff, #00ffff)';
            }, 1000);
        });
    });
});
// ...existing code...

// Tab switching for product detail
document.addEventListener('DOMContentLoaded', function () {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabPanes = document.querySelectorAll('.tab-pane');
    tabButtons.forEach(btn => {
        btn.addEventListener('click', function () {
            // Remove active from all
            tabButtons.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            // Add active to clicked
            btn.classList.add('active');
            const tabId = btn.getAttribute('data-tab');
            const pane = document.getElementById(tabId);
            if (pane) pane.classList.add('active');
        });
    });
});