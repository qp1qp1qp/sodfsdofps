// JavaScript для управления полями ввода размеров в админке продуктов

document.addEventListener('DOMContentLoaded', function() {
    // При загрузке страницы обновляем видимость полей размеров
    let unitSelect = document.querySelector('#id_primary_unit');
    if (unitSelect) {
        updateDimensionFields(unitSelect.value);
        
        // Также обновляем при изменении значения
        unitSelect.addEventListener('change', function() {
            updateDimensionFields(this.value);
        });
    }
});

function updateDimensionFields(unitValue) {
    // Получаем родительские элементы полей
    let lengthField = document.querySelector('.field-length').closest('.form-row');
    let widthField = document.querySelector('.field-width').closest('.form-row');
    let thicknessField = document.querySelector('.field-thickness').closest('.form-row');
    
    // Получаем поле количества штук в пачке
    let piecesPerPackageField = document.querySelector('.field-pieces_per_package');
    if (piecesPerPackageField) {
        piecesPerPackageField = piecesPerPackageField.closest('.form-row');
    }
    
    // Устанавливаем видимость в зависимости от единицы измерения
    if (unitValue === 'cubic') {
        // Для кубических метров нужны все три измерения
        lengthField.style.display = 'block';
        widthField.style.display = 'block';
        thicknessField.style.display = 'block';
        
        // Скрываем поле для штук в пачке
        if (piecesPerPackageField) {
            piecesPerPackageField.style.display = 'none';
        }
        
        // Обновляем подсказки
        document.querySelector('label[for="id_length"]').textContent = 'Длина (м):';
        document.querySelector('label[for="id_width"]').textContent = 'Ширина (м):';
        document.querySelector('label[for="id_thickness"]').textContent = 'Толщина (м):';
        
    } else if (unitValue === 'square') {
        // Для квадратных метров нужны длина и ширина
        lengthField.style.display = 'block';
        widthField.style.display = 'block';
        thicknessField.style.display = 'none';
        
        // Показываем поле для штук в пачке только для квадратных метров
        if (piecesPerPackageField) {
            piecesPerPackageField.style.display = 'block';
            
            // Обновляем подсказку для поля штук в пачке
            let packageLabel = document.querySelector('label[for="id_pieces_per_package"]');
            if (packageLabel) {
                packageLabel.textContent = 'Штук в пачке:';
            }
        }
        
        // Обновляем подсказки
        document.querySelector('label[for="id_length"]').textContent = 'Длина (м):';
        document.querySelector('label[for="id_width"]').textContent = 'Ширина (м):';
        
    } else if (unitValue === 'linear') {
        // Для погонных метров нужна только длина
        lengthField.style.display = 'block';
        widthField.style.display = 'none';
        thicknessField.style.display = 'none';
        
        // Скрываем поле для штук в пачке
        if (piecesPerPackageField) {
            piecesPerPackageField.style.display = 'none';
        }
        
        // Обновляем подсказку
        document.querySelector('label[for="id_length"]').textContent = 'Длина (м):';
        
    } else {
        // Для штук показываем все поля для информации
        lengthField.style.display = 'block';
        widthField.style.display = 'block';
        thicknessField.style.display = 'block';
        
        // Скрываем поле для штук в пачке
        if (piecesPerPackageField) {
            piecesPerPackageField.style.display = 'none';
        }
    }
    
    // Обновляем название поля цены в зависимости от единицы измерения
    let priceLabel = document.querySelector('label[for="id_price"]');
    if (priceLabel) {
        if (unitValue === 'cubic') {
            priceLabel.textContent = 'Цена за м³:';
        } else if (unitValue === 'square') {
            priceLabel.textContent = 'Цена за м²:';
        } else if (unitValue === 'linear') {
            priceLabel.textContent = 'Цена за погонный метр:';
        } else {
            priceLabel.textContent = 'Цена за штуку:';
        }
    }
} 