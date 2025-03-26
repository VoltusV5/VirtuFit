document.addEventListener("DOMContentLoaded", function() {
    const form = document.getElementById("measurements-form");
    
    if (!form) {
        console.error("Форма не найдена!");
        return;
    }

    form.addEventListener("submit", async function(event) {
        event.preventDefault();
        
        // Блокируем кнопку отправки
        const submitButton = form.querySelector('button[type="submit"]');
        const originalText = submitButton.textContent;
        submitButton.disabled = true;
        submitButton.textContent = "Отправка...";
        
        try {
            // Собираем данные формы
            const formData = new FormData(form);
            const data = Object.fromEntries(formData.entries());
            
            console.log("Отправляемые данные:", data);

            // Отправляем данные
            const response = await fetch("/submit", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            console.log("Ответ сервера:", result);
            
            // Успешная отправка
            alert(result.message || "Данные успешно отправлены!");
            form.reset(); // Очищаем форму после успешной отправки
            
        } catch (error) {
            console.error("Ошибка при отправке:", error);
            alert("Произошла ошибка при отправке данных");
        } finally {
            // Восстанавливаем кнопку
            submitButton.disabled = false;
            submitButton.textContent = originalText;
        }
    });
});