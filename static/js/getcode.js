document.addEventListener('DOMContentLoaded', function() {
    let rowCounter = 0;

    async function checkCode() {
        const codeInput = document.getElementById('codeInput');
        const code = codeInput.value.trim();

        if (!code) {
            showToast('error', 'Vui lòng nhập mail!');
            return;
        }

        try {
            // Xóa kết quả cũ và hiển thị loading
            const tbody = document.getElementById('resultsBody');
            tbody.innerHTML = '<tr><td colspan="9" style="text-align:center;">⏳ Đang quét...</td></tr>';

            // Gọi API Python để lấy code
            const response = await fetch('/api/get-code', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ 
                    mail_list: code.split('\n') 
                })
            });

            const data = await response.json();
            
            if (data.success) {
                updateResultsTable(data.results);
                showToast('success', 'Quét mail thành công!');
            } else {
                showToast('error', data.message || 'Có lỗi xảy ra!');
            }

        } catch (error) {
            console.error('Error scanning mails:', error);
            showToast('error', 'Có lỗi xảy ra khi quét mail!');
        }
    }

    function updateResultsTable(results) {
        const tbody = document.getElementById('resultsBody');
        tbody.innerHTML = ''; // Clear existing results

        results.forEach((result, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${result.mail || 'N/A'}</td>
                <td>${result.mailadd || 'N/A'}</td>
                <td>${result.from_name || 'N/A'}</td>
                <td>${result.date_str || 'N/A'}</td>
                <td style="max-width: 200px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;" 
                    title="${result.subject || 'N/A'}">${result.subject || 'N/A'}</td>
                <td style="color: ${result.uid ? '#28a745' : '#dc3545'};">${result.uid || 'N/A'}</td>
                <td style="color: ${result.code ? '#28a745' : '#dc3545'};">${result.code || 'N/A'}</td>
                <td style="color: ${getStatusColor(result.status)};">${result.status || 'N/A'}</td>
            `;
            tbody.appendChild(row);
        });
    }

    function getStatusColor(status) {
        if (!status) return '#6c757d'; // grey for N/A
        if (status.includes('❌')) return '#dc3545'; // red for error
        if (status.includes('⚠️')) return '#ffc107'; // yellow for warning
        return '#28a745'; // green for success
    }

    function showToast(type, message) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            toast.remove();
        }, 3000);
    }

    // Add click event listener to submit button
    const submitButton = document.querySelector('.submit-code');
    if (submitButton) {
        submitButton.addEventListener('click', checkCode);
    }

    // Add Enter key handler
    const codeInput = document.getElementById('codeInput');
    if (codeInput) {
        codeInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                checkCode();
            }
        });
    }
});