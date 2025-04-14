document.addEventListener("DOMContentLoaded", function () {
    const customerSelect = document.getElementById("customer-select");
    const newCustomerInput = document.getElementById("new-customer");
    const productsContainer = document.getElementById("products-container");
    const materialsContainer = document.getElementById("materials-container");
    const form = document.getElementById("bid-form");
    const fileInput = document.getElementById("file-upload");

    // Загрузка списка заказчиков
    fetch("/customers/")
        .then(response => response.json())
        .then(data => {
            customerSelect.innerHTML = `<option value="">Выберите заказчика</option>`;
            data.forEach(customer => {
                const option = document.createElement("option");
                option.value = customer.id;
                option.textContent = customer.name;
                customerSelect.appendChild(option);
            });
            const newOption = document.createElement("option");
            newOption.value = "new";
            newOption.textContent = "Добавить нового";
            customerSelect.appendChild(newOption);
        });

    // Показывать поле нового заказчика
    customerSelect.addEventListener("change", function () {
        newCustomerInput.style.display = this.value === "new" ? "block" : "none";
    });

//-----------------------------------------------------------------------------------------------------------

    // Добавление изделия
    document.getElementById("add-product").addEventListener("click", function () {
        const productRow = document.createElement("div");
        productRow.classList.add("product-row");

        // Первая строка: изделие и его поля
        const productContainer = document.createElement("div");
        productContainer.classList.add("product-container");
        // Поле выбора изделия
        const productSelect = document.createElement("select");
        productSelect.classList.add("product-select");

        productContainer.appendChild(productSelect);
        productRow.appendChild(productContainer);

        // Вторая строка: материалы и их поля
        const materialContainer = document.createElement("div");
        materialContainer.classList.add("material-container");
        productRow.appendChild(materialContainer);

        // Контейнер для листов
        const sheetsContainer = document.createElement("div");
        sheetsContainer.classList.add("sheets-container");
        productRow.appendChild(sheetsContainer);

        // Контейнер для цехов и сотрудников
        const assignmentContainer = document.createElement("div");
        assignmentContainer.classList.add("assignment-container");
        productRow.appendChild(assignmentContainer);

        productsContainer.appendChild(productRow);
        // Загрузка списка изделий
        fetch("/products/")
        .then(response => response.json())
        .then(data => {
            productSelect.innerHTML = `<option value="">Выберите продукт</option>`;
            data.forEach(product => {
                const option = document.createElement("option");
                option.value = product.value;  
                option.textContent = product.label;  
                productSelect.appendChild(option);
            });

        });

        // Обработчик смены изделия
        productSelect.addEventListener("change", function () {
            handleProductChange(this.value, sheetsContainer, assignmentContainer);
            const customProfileField = productContainer.querySelector(".custom-profile-type");

            // Удаляем поле нестандартного профиля, если оно есть, и выбран продукт не "Профиля"
            if (customProfileField) {
                customProfileField.remove();
            }

            loadProductFields(this.value, productContainer);
            loadMaterialFields(this.value, materialContainer);

        });



    });



    // Удаление последнего изделия
    document.getElementById("remove-product").addEventListener("click", function () {
        const lastProduct = productsContainer.lastElementChild;
        if (lastProduct) {
            productsContainer.removeChild(lastProduct);
        }
    });


    // Загрузка полей изделия
    function loadProductFields(productType, container) {
        console.log(`🔄 Загрузка полей для изделия: ${productType}`);

        // Удаляем старые поля изделия и материала
        container.querySelector(".product-fields")?.remove();


        fetch(`/products/${productType}/fields`)
            .then(response => response.json())
            .then(fields => {
                const fieldContainer = document.createElement("div");
                fieldContainer.classList.add("product-fields");

                fields.forEach(field => {
                    let input;
                    if (field.type === "select") {
                        input = document.createElement("select");
                        input.dataset.placeholder = field.label;
                        const placeholderOption = document.createElement("option");
                        placeholderOption.value = "";
                        placeholderOption.textContent = field.label;
                        placeholderOption.disabled = true;
                        placeholderOption.selected = true;
                        input.appendChild(placeholderOption);
                        field.options.forEach(option => {
                            const opt = document.createElement("option");
                            opt.value = option.value;
                            opt.textContent = option.label;
                            input.appendChild(opt);
                        });
                        // Если это поле "Тип профиля", добавляем обработчик выбора
                        if (field.name === "profile_type_id") {
                            input.addEventListener("change", function () {
                                handleProfileTypeChange(this, container);
                            });
                        }
                        if (field.name === "cassette_type_id") {
                            input.addEventListener("change", function () {
                                handleCassetteTypeChange(this, container);
                            });
                        }
                    } else if (field.type === "checkbox") {
                        const label = document.createElement("label");
                        input = document.createElement("input");
                        input.type = "checkbox";
                        input.name = field.name;
                    
                        label.appendChild(input);
                        label.appendChild(document.createTextNode(field.label + " ")); // Текст после чекбокса
                        fieldContainer.appendChild(label);
                    } else {
                        input = document.createElement("input");
                        input.type = field.type;
                        input.placeholder = field.label;
                    }
                    input.name = field.name;

                    fieldContainer.appendChild(input);
                });

                container.appendChild(fieldContainer);

            });
    }

    // Функция обработки выбора типа профиля
    function handleProfileTypeChange(selectElement, container) {
        const customProfileField = container.querySelector(".custom-profile-type");
        console.log(`🔄 Обработка выбора типа профиля: ${selectElement.value}`);
        

        // Если уже существует поле ввода "не стандартного" профиля, удаляем его
        if (customProfileField) {
            customProfileField.remove();
        }

        if (selectElement.value === "11") { // OTHER - это значение для "Не стандарт"
            console.log("Выбран нестандартный профиль, добавляем поле ввода");

            const customFieldContainer = document.createElement("div");
            customFieldContainer.classList.add("custom-profile-type");

            const input = document.createElement("input");
            input.type = "text";
            input.name = "custom_profile_type";
            input.placeholder = "Введите тип профиля...";

            customFieldContainer.appendChild(input);
            selectElement.parentNode.insertBefore(customFieldContainer, selectElement.nextSibling);
        }
    }

    // Функция обработки выбора типа кассет
    function handleCassetteTypeChange(selectElement, container) {
        const customCassetteField = container.querySelector(".custom-cassette-type");
        console.log(`🔄 Обработка выбора типа кассет: ${selectElement.value}`);
        

        // Если уже существует поле ввода "не стандартного" профиля, удаляем его
        if (customCassetteField) {
            customCassetteField.remove();
        }

        if (selectElement.value === "OTHER") { // OTHER - это значение для "Не стандарт"
            console.log("Выбран нестандартный профиль, добавляем поле ввода");

            const customFieldContainer = document.createElement("div");
            customFieldContainer.classList.add("custom-cassette-type");

            const input = document.createElement("input");
            input.type = "text";
            input.name = "custom_cassette_type";
            input.placeholder = "Введите описание:";

            customFieldContainer.appendChild(input);
            selectElement.parentNode.insertBefore(customFieldContainer, selectElement.nextSibling);
        }
    }
//-----------------------------------------------------------------------------------------------------
    // Загрузка форм материала
    function loadMaterialFields(productId, container) {
        console.log(`🔄 Загрузка форм материала для изделия: ${productId}`);

        // Удаляем старый материал
        container.querySelector(".material-fields")?.remove();
        container.querySelector(".material-type")?.remove();
        container.querySelector(".material-thickness")?.remove();
        container.querySelector(".material-color")?.remove();
        container.querySelector(".material-paintable")?.remove();
        

        const materialContainer = document.createElement("div");
        materialContainer.classList.add("material-fields");
        
        fetch(`/material/forms/${productId}`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) return;

    
                const materialSelect = document.createElement("select");
                materialSelect.classList.add("material-select");
                materialSelect.innerHTML = `<option value="">Выберите форму</option>`;
                

                data.forEach(material => {
                    const option = document.createElement("option");
                    option.value = material.name;
                    option.textContent = material.value;
                    materialSelect.appendChild(option);
                });

                materialContainer.appendChild(materialSelect);
                container.appendChild(materialContainer);

                // Автоматически загружаем первый тип материала
                const firstMaterial = data[0]?.name;
                if (firstMaterial) {
                    loadMaterialTypes(productId, firstMaterial, container);
                }

                materialSelect.addEventListener("change", function () {
                    loadMaterialTypes(productId, this.value, container);
                });
            });
    }

    // Загрузка типов материала
    function loadMaterialTypes(productId, form, container) {
        console.log(`🔄 Загрузка типов материала для изделия ${productId} и формы ${form}`);

        // Удаляем старый выбор типа материала
        container.querySelector(".material-type")?.remove();
        container.querySelector(".material-color")?.remove();
        container.querySelector(".material-paintable")?.remove();

        fetch(`/material/types/${productId}/${form}`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) return;

                const typeSelect = document.createElement("select");
                typeSelect.classList.add("material-type");
                typeSelect.innerHTML = `<option value="">Выберите тип</option>`;
                

                
                data.forEach(type => {
                    const option = document.createElement("option");
                    option.value = type.name;
                    option.textContent = type.value;
                    typeSelect.appendChild(option);
                });

                container.appendChild(typeSelect);

                // Автоматически загружаем первую доступную толщину материала
                const firstType = data[0]?.name;
                if (firstType) {
                    loadMaterialThickness(productId, firstType, container);
                }

                typeSelect.addEventListener("change", function () {
                    loadMaterialThickness(productId, this.value, container);
                });

            })
            .catch(error => console.error("Ошибка при загрузке типов материала:", error));
    }

    // Загрузка толщины материала
    function loadMaterialThickness(productId, type, container) {
        console.log(`🔄 Загрузка толщины материала для типа: ${type}`);

        // Удаляем старый выбор толщины
        container.querySelector(".material-thickness")?.remove();
        container.querySelector(".material-color")?.remove();
        container.querySelector(".material-paintable")?.remove();

        fetch(`/material/thickness/${type}`)
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) return;

                const thicknessSelect = document.createElement("select");
                thicknessSelect.classList.add("material-thickness");
                thicknessSelect.innerHTML = `<option value="">Выберите толщину</option>`;
                
                
                data.forEach(thickness => {
                    const option = document.createElement("option");
                    option.value = thickness.name;
                    option.textContent = thickness.value;
                    thicknessSelect.appendChild(option);
                });

                container.appendChild(thicknessSelect);
                                            // Если выбран материал кассеты, фасонка, линейные панели, листы - добавляем дополнительные поля
            if (["CASSETTE", "FACING", "LINEAR_PANEL", "SHEET", "OTHER"].includes(productId)) {
                console.log(`🔄 Загрузка полей материала для изделия ${productId} и формы ${form}`);
                addColorAndPaintableFields(container);
            }
            });
    }

    // Функция добавления полей для цвета и краски
    function addColorAndPaintableFields(container) {
        const colorFieldContainer = document.createElement("div");
        colorFieldContainer.classList.add("material-color");

        const colorInput = document.createElement("input");
        colorInput.type = "text";
        colorInput.name = "material_color";
        colorInput.placeholder = "Введите цвет материала";
        
        colorFieldContainer.appendChild(colorInput);
        container.appendChild(colorFieldContainer);

        const paintableFieldContainer = document.createElement("div");
        paintableFieldContainer.classList.add("material-paintable");

        const paintableCheckbox = document.createElement("input");
        paintableCheckbox.type = "checkbox";
        paintableCheckbox.name = "material_paintable";
        
        const paintableLabel = document.createElement("label");
        paintableLabel.appendChild(paintableCheckbox);
        paintableLabel.appendChild(document.createTextNode("Красится ли материал?"));

        paintableFieldContainer.appendChild(paintableLabel);
        container.appendChild(paintableFieldContainer);
    }

    // Функция обработки смены изделия
    function handleProductChange(productId, sheetsContainer, assignmentContainer) {
        // Очищаем контейнеры
        sheetsContainer.innerHTML = "";
        assignmentContainer.innerHTML = "";

        // Проверяем, если выбраны "Кассеты" или "Листы"
        if (productId === "CASSETTE" || productId === "SHEET") {
            addSheetsControls(sheetsContainer);
        }

        // Добавляем контейнер для выбора цехов и сотрудников
        addAssignmentFields(assignmentContainer);
        
    }

    // Функция добавления кнопок для листов
    function addSheetsControls(container) {
        const addButton = document.createElement("button");
        addButton.textContent = "Добавить лист";
        addButton.addEventListener("click", function () {
            addSheetFields(container);
        });

        const removeButton = document.createElement("button");
        removeButton.textContent = "Удалить лист";
        removeButton.addEventListener("click", function () {
            const lastSheet = container.querySelector(".sheet-fields:last-child");
            if (lastSheet) lastSheet.remove();
        });

        container.appendChild(addButton);
        container.appendChild(removeButton);
    }
        // Функция добавления полей для листов
        function addSheetFields(container) {
            const sheetDiv = document.createElement("div");
            sheetDiv.classList.add("sheet-fields");
    
            const widthInput = document.createElement("input");
            widthInput.type = "number";
            widthInput.placeholder = "Ширина листа";
    
            const lengthInput = document.createElement("input");
            lengthInput.type = "number";
            lengthInput.placeholder = "Длина листа";
    
            const quantityInput = document.createElement("input");
            quantityInput.type = "number";
            quantityInput.placeholder = "Количество листов";
    
            sheetDiv.appendChild(widthInput);
            sheetDiv.appendChild(lengthInput);
            sheetDiv.appendChild(quantityInput);
            container.appendChild(sheetDiv);
        }
    
        // Функция добавления полей для выбора цехов и сотрудников
        function addAssignmentFields(container) {
            const urgencySelect = document.createElement("select");
            urgencySelect.innerHTML = `<option value="">Выберите срочность</option>`
            fetch("/urgency/")
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) return;
                data.forEach(urgency => {
                    const option = document.createElement("option");
                    option.value = urgency;
                    option.textContent = urgency;
                    urgencySelect.appendChild(option);
                    });
            });
            container.appendChild(urgencySelect);
            const workshopSelect = document.createElement("select");
            workshopSelect.multiple = true;
            workshopSelect.innerHTML = "";
            fetch("/workshops/")
                .then(response => response.json())
                .then(data => {
                    if (data.length === 0) return;
                    data.forEach(workshop => {
                        const option = document.createElement("option");
                        option.value = workshop.id;
                        option.textContent = workshop.name;
                        workshopSelect.appendChild(option);
                        });
                });
    
            const employeeSelect = document.createElement("select");
            employeeSelect.multiple = true;
            employeeSelect.innerHTML = "";
            fetch("/employee/")
            .then(response => response.json())
            .then(data => {
                if (data.length === 0) return;
                data.forEach(employee => {
                    const option = document.createElement("option");
                    option.value = employee.id;
                    option.textContent = employee.name + " " + employee.firstname;
                    employeeSelect.appendChild(option);
                    });
            });
    
            container.appendChild(document.createTextNode("Назначить цех:"));
            container.appendChild(workshopSelect);
            container.appendChild(document.createTextNode("Назначить сотрудников:"));
            container.appendChild(employeeSelect);
            // Добавляем поле для комментариев

            const commentInput = document.createElement("textarea");
            commentInput.name = "comment";
            commentInput.placeholder = "Введите комментарий...";
            commentInput.rows = 3;
            commentInput.style.width = "100%";

            container.appendChild(commentInput);
        }

            

//-----------------------------------------------------------------------------------------------------
form.addEventListener("submit", async function (event) {
    event.preventDefault();

    const formData = new FormData(form);
    const newCustomerName = newCustomerInput.value.trim();

    const workshopSelect = document.querySelector(".assignment-container select[multiple]:nth-of-type(2)");
    const employeeSelect = document.querySelector(".assignment-container select[multiple]:nth-of-type(3)");

    const workshops = Array.from(workshopSelect?.selectedOptions || []).map(option => option.value);
    const employees = Array.from(employeeSelect?.selectedOptions || []).map(option => option.value);

    const urgency = document.querySelector(".assignment-container select")?.value || "";
    const comment = document.querySelector("textarea[name='comment']")?.value || "";

    const products = [];
    document.querySelectorAll(".product-row").forEach(productRow => {
        const product_id = productRow.querySelector(".product-select")?.value;
        const material = productRow.querySelector(".material-select")?.value;
        const material_type = productRow.querySelector(".material-type")?.value;
        const thickness = productRow.querySelector(".material-thickness")?.value;
        const material_color = productRow.querySelector("input[name='material_color']")?.value || "";
        const material_paintable = productRow.querySelector("input[name='material_paintable']")?.checked ?? false;

        // Общие детали (в product_details)
        const product_details = {};
        productRow.querySelectorAll(".product-fields input, .product-fields select").forEach(input => {
            if (input.name) {
                product_details[input.name] = input.value;
            }
        });

        // Пользовательский тип профиля
        const customProfileField = productRow.querySelector("input[name='custom_profile_type']");
        if (customProfileField) {
            product_details["custom_profile_type"] = customProfileField.value;
        }

        // Листы
        const sheets = [];
        productRow.querySelectorAll(".sheet-fields").forEach(sheet => {
            const width = sheet.querySelector("input[placeholder='Ширина листа']")?.value;
            const length = sheet.querySelector("input[placeholder='Длина листа']")?.value;
            const quantity = sheet.querySelector("input[placeholder='Количество листов']")?.value;

            if (width && length && quantity) {
                sheets.push({ width, length, quantity });
            }
        });

        const quantity = productRow.querySelector("input[name='product_quantity']")?.value || "0";

        const productData = {
            product_id,
            product_details,
            material,
            material_type,
            thickness,
            material_color,
            material_paintable,
            sheets: sheets.length > 0 ? sheets : [],
            urgency,
            workshops,
            employees,
            comment: comment
        };

        products.push(productData);
    });

    const bidData = {
        task_number: formData.get("task_number"),
        customer_id: formData.get("customer_id"),
        manager: formData.get("manager"),
        files: Array.from(fileInput.files).map(file => file.name),
        products
    };

    if (customerSelect.value === "new" && newCustomerName) {
        bidData.customer = newCustomerName;
    }

    try {
        const sendData = new FormData();
        sendData.append("bid_data", JSON.stringify(bidData));
        Array.from(fileInput.files).forEach(file => sendData.append("files", file));

        const response = await fetch("/bids/create/", {
            method: "POST",
            body: sendData
        });

        const result = await response.json();
        const messageElement = document.getElementById("server-message");
        if (response.ok) {
            messageElement.textContent = result.message;
            messageElement.style.color = "green";
        } else {
            messageElement.textContent = result.detail || "Неизвестная ошибка";
            messageElement.style.color = "red";
        }
    } catch (error) {
        const messageElement = document.getElementById("server-message");
        messageElement.textContent = "Ошибка при отправке формы";
        messageElement.style.color = "red";
        console.error("❌ Ошибка при запросе:", error);
    }
});
});
