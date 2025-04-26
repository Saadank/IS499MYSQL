function validateNumericInput(input) {
    input.value = input.value.replace(/[^0-9]/g, '').slice(0, 10);
} 