(function($) {
    $(document).ready(function() {
        console.log("Product characteristic validation JS loaded");
        
        // Функция для проверки формы перед отправкой
        function validateProductCharacteristics() {
            var isValid = true;
            
            // Проходим по всем инлайн-формам характеристик
            $('.dynamic-productcharacteristic_set').each(function() {
                var $row = $(this);
                var $characteristicSelect = $row.find('select[name$="-characteristic"]');
                var $valueSelect = $row.find('select[name$="-characteristic_value"]');
                
                // Пропускаем удаленные строки (отмеченные для удаления)
                if ($row.find('input[name$="-DELETE"]').prop('checked')) {
                    return;
                }
                
                // Если выбрана характеристика, но не выбрано значение
                if ($characteristicSelect.val() && !$valueSelect.val()) {
                    isValid = false;
                    
                    // Подсвечиваем проблемное поле
                    $valueSelect.css('border-color', 'red');
                    
                    // Добавляем сообщение об ошибке
                    if ($row.find('.error-message').length === 0) {
                        $valueSelect.after('<p class="error-message" style="color: red; margin: 5px 0;">Необходимо указать значение</p>');
                    }
                } else {
                    // Убираем подсветку и сообщение, если все в порядке
                    $valueSelect.css('border-color', '');
                    $row.find('.error-message').remove();
                }
            });
            
            // Если есть ошибки, показываем предупреждение
            if (!isValid) {
                alert('Для некоторых характеристик не указаны значения. Пожалуйста, заполните все поля или удалите неполные характеристики.');
                return false;
            }
            
            return true;
        }
        
        // Добавляем обработчик события отправки формы
        $(document).on('submit', 'form', function(e) {
            if ($('.dynamic-productcharacteristic_set').length) {
                if (!validateProductCharacteristics()) {
                    e.preventDefault();
                    return false;
                }
            }
        });
        
        // Динамическое обновление выбора значений при выборе характеристики
        $(document).on('change', 'select[name$="-characteristic"]', function() {
            var $characteristicSelect = $(this);
            var $row = $characteristicSelect.closest('.dynamic-productcharacteristic_set');
            var $valueSelect = $row.find('select[name$="-characteristic_value"]');
            
            // Удаляем предыдущие ошибки при изменении характеристики
            $row.find('.error-message').remove();
            $valueSelect.css('border-color', '');
            
            // Если характеристика не выбрана, очищаем выбор значения
            if (!$characteristicSelect.val()) {
                $valueSelect.html('<option value="">---------</option>');
                return;
            }
            
            // Добавляем индикатор загрузки
            $valueSelect.html('<option value="">Загрузка...</option>');
            
            // Фильтруем значения через стандартный Django admin
            var characteristicId = $characteristicSelect.val();
            var url = '/admin/products/characteristicvalue/?characteristic__id__exact=' + characteristicId;
            
            $.get(url)
                .done(function(response) {
                    // Извлекаем список значений из HTML-ответа
                    var $tempDiv = $('<div>').html(response);
                    var options = [];
                    
                    // Добавляем пустую опцию
                    options.push('<option value="">---------</option>');
                    
                    // Находим таблицу результатов
                    $tempDiv.find('#result_list tbody tr').each(function() {
                        var valueId = $(this).find('input[name="form-INITIAL_FORMS"]').val();
                        var valueText = $(this).find('th').text().trim();
                        
                        // Используем data-id атрибут для строки
                        valueId = $(this).attr('data-object-id') || $(this).attr('id');
                        
                        if (valueId && valueText) {
                            options.push('<option value="' + valueId + '">' + valueText + '</option>');
                        }
                    });
                    
                    // Если не нашли через новый интерфейс, пробуем через старый
                    if (options.length <= 1) {
                        $tempDiv.find('#changelist-form tbody tr').each(function() {
                            // Получаем ID из первой колонки (checkbox)
                            var checkbox = $(this).find('td input[type="checkbox"]');
                            var valueId = checkbox.val();
                            // Получаем текст из первой колонки с данными
                            var valueText = $(this).find('th').first().text().trim();
                            
                            if (valueId && valueText) {
                                options.push('<option value="' + valueId + '">' + valueText + '</option>');
                            }
                        });
                    }
                    
                    // Если все еще нет значений, добавляем сообщение
                    if (options.length <= 1) {
                        options.push('<option value="">Нет доступных значений</option>');
                    }
                    
                    // Обновляем select
                    $valueSelect.html(options.join(''));
                })
                .fail(function() {
                    // В случае ошибки
                    $valueSelect.html('<option value="">Ошибка загрузки</option>');
                });
        });
        
        // Упрощенный вариант, без AJAX-фильтрации значений
        function bindCharacteristicHandler() {
            $('.dynamic-productcharacteristic_set select[name$="-characteristic"]').each(function() {
                // Если уже выбрана характеристика, проверяем значение
                var $characteristicSelect = $(this);
                var $row = $characteristicSelect.closest('.dynamic-productcharacteristic_set');
                var $valueSelect = $row.find('select[name$="-characteristic_value"]');
                
                if ($characteristicSelect.val() && !$valueSelect.val()) {
                    $valueSelect.css('border-color', 'red');
                    if ($row.find('.error-message').length === 0) {
                        $valueSelect.after('<p class="error-message" style="color: red; margin: 5px 0;">Необходимо указать значение</p>');
                    }
                }
            });
        }
        
        // Привязываем события к inline-добавлению
        $('.add-row a').click(function() {
            // Задержка для добавления новой строки
            setTimeout(bindCharacteristicHandler, 100);
        });
        
        // Первоначальная проверка
        bindCharacteristicHandler();
    });
})(django.jQuery); 