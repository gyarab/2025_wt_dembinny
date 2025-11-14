// Počkáme, až se načte celý HTML dokument
document.addEventListener("DOMContentLoaded", () => {

    // --- Naše "databáze" košíku ---
    // Použijeme Mapu, aby bylo snadné měnit množství
    // Klíč: název produktu (string), Hodnota: objekt { quantity: number, price: number }
    const cart = new Map();

    // --- Selektory elementů ---
    const allBuyButtons = document.querySelectorAll(".add-to-cart");
    const cartCountDesktop = document.getElementById("cart-count-desktop");
    const cartCountMobile = document.getElementById("cart-count-mobile");
    const cartItemsList = document.getElementById("cart-items-list");
    const emptyCartMessage = document.getElementById("empty-cart-message");
    const cartTotalPrice = document.getElementById("cart-total-price");

    // --- Přidání posluchačů na VŠECHNA tlačítka "Koupit" ---
    allBuyButtons.forEach(button => {
        button.addEventListener("click", (event) => {
            // Získáme data z tlačítka
            const productName = event.target.dataset.productName;
            const productPrice = parseInt(event.target.dataset.price); // převedeme cenu na číslo

            // Přidáme nebo aktualizujeme produkt v Mapě
            if (cart.has(productName)) {
                // Pokud už produkt v košíku je, jen zvýšíme počet
                const item = cart.get(productName);
                item.quantity++;
            } else {
                // Pokud není, vytvoříme nový záznam
                cart.set(productName, { quantity: 1, price: productPrice });
            }

            // Překreslíme celý košík
            updateCartUI();
        });
    });

    // --- Funkce pro překreslení celého košíku ---
    function updateCartUI() {
        // Vyčistíme starý obsah košíku
        cartItemsList.innerHTML = ""; 
        
        let totalItems = 0;
        let totalPrice = 0;

        if (cart.size === 0) {
            // Pokud je košík prázdný, zobrazíme zprávu
            cartItemsList.appendChild(emptyCartMessage);
        } else {
            // Projdeme všechny položky v Mapě a vytvoříme pro ně HTML
            cart.forEach((item, name) => {
                const li = document.createElement("li");
                li.className = "list-group-item d-flex justify-content-between align-items-center flex-wrap";
                
                // Text položky
                const textSpan = document.createElement("span");
                textSpan.className = "mb-2 mb-md-0";
                textSpan.innerHTML = `<strong>${name}</strong> <span class="text-body-secondary">(${item.price} Kč)</span>`;

                // Ovládací tlačítka
                const controlsDiv = document.createElement("div");
                controlsDiv.className = "cart-controls d-flex align-items-center";
                controlsDiv.innerHTML = `
                    <button class="btn btn-sm btn-outline-secondary" data-action="decrease" data-product-name="${name}">-</button>
                    <span class="mx-2">${item.quantity}x</span>
                    <button class="btn btn-sm btn-outline-secondary" data-action="increase" data-product-name="${name}">+</button>
                    <button class="btn btn-sm btn-outline-danger ms-3 d-flex" data-action="remove" data-product-name="${name}">
                        <i class="bi bi-trash-fill"></i><span class="d-none d-sm-inline"> Odstranit</span>
                    </button>
                `;

                li.appendChild(textSpan);
                li.appendChild(controlsDiv);
                cartItemsList.appendChild(li);

                // Počítáme celkové součty
                totalItems += item.quantity;
                totalPrice += item.quantity * item.price;
            });
        }

        // Aktualizujeme počet položek v navigaci
        cartCountDesktop.textContent = totalItems;
        cartCountMobile.textContent = totalItems;

        // Aktualizujeme celkovou cenu
        cartTotalPrice.textContent = `${totalPrice.toLocaleString('cs-CZ')} Kč`;
    }

    // --- Posluchač pro klikání na tlačítka PŘÍMO V KOŠÍKU (+, -, Odstranit) ---
    // Používáme "event delegation", protože tlačítka se dynamicky vytvářejí
    cartItemsList.addEventListener("click", (event) => {
        const target = event.target.closest("button"); // Najdeme nejbližší tlačítko, na které se kliklo

        if (!target) return; // Kliknuto mimo tlačítko

        const action = target.dataset.action;
        const productName = target.dataset.productName;

        if (!action || !productName || !cart.has(productName)) return; // Pojistka

        const item = cart.get(productName);

        switch (action) {
            case "increase":
                item.quantity++;
                break;
            case "decrease":
                item.quantity--;
                if (item.quantity === 0) {
                    cart.delete(productName); // Pokud klesne na 0, smažeme
                }
                break;
            case "remove":
                cart.delete(productName); // Smažeme rovnou
                break;
        }

        // Po každé akci překreslíme košík
        updateCartUI();
    });

});