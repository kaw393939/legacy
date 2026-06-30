import { win } from '../dom.js';
import { analyticsConsentGranted } from '../cookies.js';
import { runtimeConfig } from '../runtime-config.js';

const conversionValues = runtimeConfig.conversionValues || {};
const measurementId = (runtimeConfig.analytics || {}).measurementId || 'G-KE98KY192J';

export const analyticsEnabled = Boolean(runtimeConfig.analyticsEnabled);

function loadGtagScript() {
    if (win.document.querySelector(`script[src*="${measurementId}"]`)) return;

    const script = win.document.createElement('script');
    script.async = true;
    script.src = `https://www.googletagmanager.com/gtag/js?id=${encodeURIComponent(measurementId)}`;
    win.document.head.appendChild(script);
}

function ensureGtag() {
    if (!analyticsEnabled || !analyticsConsentGranted()) return false;

    loadGtagScript();
    win.dataLayer = win.dataLayer || [];
    if (typeof win.gtag !== 'function') {
        win.gtag = function gtag() {
            win.dataLayer.push(arguments);
        };
        win.gtag('js', new Date());
        win.gtag('config', measurementId, {
            page_title: document.title,
            custom_map: {
                custom_parameter_1: 'cta_type',
                custom_parameter_2: 'section_name'
            },
            enhanced_conversions: true,
            send_page_view: true,
            conversion_linker: true
        });
    }

    return typeof win.gtag === 'function';
}

export function valueFor(key, fallback = 1) {
    const value = Number(conversionValues[key]);
    return Number.isFinite(value) ? value : fallback;
}

export function track(eventName, payload) {
    if (!ensureGtag()) return;
    win.gtag('event', eventName, payload || {});
}

export function trackConversion(label, value) {
    track('conversion', {
        event_category: 'Conversions',
        event_label: label,
        value,
        currency: 'USD'
    });
}
