document.addEventListener('DOMContentLoaded', function() {
    var baseMap = L.map('mapid').setView([55.751244, 37.618423], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(baseMap);
    
    document.querySelector('#business-form').addEventListener('submit', function(event) {
        event.preventDefault();
        var formData = new FormData(this);
        fetch('/filter-business', {
            method: 'POST',
            body: formData
        })
        .then(response => response.text())
        .then(data => {
            // Обновляем карту
            baseMap.setView([55.751244, 37.618423], 13); // Центрирование карты после обновления
            baseMap.remove(); // Удаляем старую карту
            document.getElementById('mapid').innerHTML = data; // Вставляем новую карту
        });
    });
});