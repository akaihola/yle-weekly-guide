export const translations = {
    en: {
        'programs-hidden': 'programs hidden',
        program: 'Program',
        'toggle-program': 'Toggle program visibility',
        show: 'Show',
        hide: 'Hide',
        'weekday-1': 'Mon',
        'weekday-2': 'Tue',
        'weekday-3': 'Wed',
        'weekday-4': 'Thu',
        'weekday-5': 'Fri',
        'weekday-6': 'Sat',
        'weekday-7': 'Sun',
    },
    fi: {
        'programs-hidden': 'ohjelmaa piilotettu',
        program: 'Ohjelma',
        'toggle-program': 'Vaihda ohjelman näkyvyyttä',
        show: 'näytä',
        hide: 'piilota',
        'weekday-1': 'ma',
        'weekday-2': 'ti',
        'weekday-3': 'ke',
        'weekday-4': 'to',
        'weekday-5': 'pe',
        'weekday-6': 'la',
        'weekday-7': 'su',
    },
    sv: {
        'programs-hidden': 'program dolda',
        program: 'Program',
        'toggle-program': 'Växla programsynlighet',
        show: 'visa',
        hide: 'dölj',
        'weekday-1': 'mån',
        'weekday-2': 'tis',
        'weekday-3': 'ons',
        'weekday-4': 'tors',
        'weekday-5': 'fre',
        'weekday-6': 'lör',
        'weekday-7': 'sön',
    },
};

export function getTranslation(key) {
    const preferredLang = localStorage.getItem('preferredLanguage');
    const browserLang = navigator.language.split('-')[0];
    const lang =
        preferredLang ||
        (['fi', 'sv'].includes(browserLang) ? browserLang : 'en');
    return translations[lang][key] || translations['en'][key];
}
