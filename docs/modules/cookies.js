import { $, doc, win } from './dom.js';
import { runtimeConfig } from './runtime-config.js';

const STORAGE_KEY = 'siteCookieConsent';

function readConsent() {
    try {
        return JSON.parse(win.localStorage.getItem(STORAGE_KEY) || 'null');
    } catch (_error) {
        return null;
    }
}

function writeConsent(value) {
    try {
        win.localStorage.setItem(STORAGE_KEY, JSON.stringify({
            essential: true,
            analytics: Boolean(value.analytics),
            marketing: false,
            updatedAt: new Date().toISOString()
        }));
    } catch (_error) {
        // Consent still works for the current page even if storage is unavailable.
    }
}

export function analyticsConsentGranted() {
    const consent = readConsent();
    return Boolean(consent && consent.analytics);
}

function setHidden(element, hidden) {
    if (!element) return;
    element.hidden = hidden;
}

function setCookieUiState(name, active) {
    doc.body.classList.toggle(name, Boolean(active));
}

function syncToggles(value) {
    const analyticsToggle = $('[data-cookie-analytics-toggle]');
    if (analyticsToggle) analyticsToggle.checked = Boolean(value && value.analytics);
}

function showModal() {
    syncToggles(readConsent());
    hideBanner();
    setCookieUiState('cookie-modal-open', true);
    setHidden($('[data-cookie-modal]'), false);
}

function closeModal() {
    setHidden($('[data-cookie-modal]'), true);
    setCookieUiState('cookie-modal-open', false);
    showBannerIfNeeded();
}

function hideBanner() {
    setHidden($('[data-cookie-consent]'), true);
    setCookieUiState('cookie-consent-open', false);
}

function showBannerIfNeeded() {
    const cookieConfig = runtimeConfig.cookies || {};
    const hasNonEssential = Boolean(cookieConfig.consentRequired || runtimeConfig.analyticsEnabled);
    if (!hasNonEssential || readConsent()) return;
    setHidden($('[data-cookie-consent]'), false);
    setCookieUiState('cookie-consent-open', true);
}

function saveChoice(analytics) {
    writeConsent({ analytics });
    hideBanner();
    closeModal();
    doc.dispatchEvent(new CustomEvent('cookie-consent-updated', {
        detail: { analytics: Boolean(analytics), marketing: false }
    }));
}

export function initCookieConsent() {
    showBannerIfNeeded();

    doc.addEventListener('click', (event) => {
        const target = event.target.closest('[data-cookie-accept],[data-cookie-reject],[data-cookie-manage],[data-cookie-preferences],[data-cookie-save],[data-cookie-close]');
        if (!target) return;

        if (target.matches('[data-cookie-accept]')) {
            saveChoice(true);
            return;
        }

        if (target.matches('[data-cookie-reject]')) {
            saveChoice(false);
            return;
        }

        if (target.matches('[data-cookie-manage],[data-cookie-preferences]')) {
            showModal();
            return;
        }

        if (target.matches('[data-cookie-save]')) {
            const analyticsToggle = $('[data-cookie-analytics-toggle]');
            saveChoice(Boolean(analyticsToggle && analyticsToggle.checked));
            return;
        }

        if (target.matches('[data-cookie-close]')) {
            closeModal();
        }
    });

    doc.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') closeModal();
    });
}
