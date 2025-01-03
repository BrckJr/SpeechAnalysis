const languageFiles = {
  en: "/static/lang/en.json",
  de: "/static/lang/de.json",
  es: "/static/lang/es.json"
};

let currentLanguage = 'en'; // Default language

window.loadLanguage = loadLanguage; // Expose the function globally to avoid ReferenceError

// Attach event listeners
document.getElementById('btn_en').addEventListener('click', () => loadLanguage('en'));
document.getElementById('btn_de').addEventListener('click', () => loadLanguage('de'));
document.getElementById('btn_es').addEventListener('click', () => loadLanguage('es'));

// Function to load the language data and update text
export function loadLanguage(lang) {
  currentLanguage = lang;
  fetch(languageFiles[lang])
    .then(response => response.json())
    .then(data => {
      updateText(data);
    });
}

// Function to set up language switcher buttons
export function setupLangSwitcherButtons(enButton, deButton, esButton) {
  // Event listener for the German button
  deButton.addEventListener('click', () => {
    loadLanguage('de'); // Load German language file
  });

  // Event listener for the English button
  enButton.addEventListener('click', () => {
    loadLanguage('en'); // Load English language file
  });

  // Event listener for the Spanish button
  esButton.addEventListener('click', () => {
    loadLanguage('es'); // Load English language file
  });

  // Optionally, load the default language on initial load (e.g., English)
  loadLanguage(currentLanguage);
}

// Function to update text content based on the loaded language data
function updateText(translations) {
    document.querySelectorAll('[data-i18n]').forEach(element => {
        const key = element.getAttribute('data-i18n');
        if (translations[key]) {
            let translatedText = translations[key];

            // Replace placeholders with dynamic values from data attributes
            Object.entries(element.dataset).forEach(([dataKey, dataValue]) => {
                const placeholder = `{{${dataKey.replace('i18n-', '')}}}`;
                translatedText = translatedText.replace(placeholder, dataValue);
            });

            // Set the translated text with placeholders replaced
            element.innerHTML = translatedText;
        }
    });
}


