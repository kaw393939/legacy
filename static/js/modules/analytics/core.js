import { win } from '../dom.js';
import { runtimeConfig } from '../runtime-config.js';

const conversionValues = runtimeConfig.conversionValues || {};

export const analyticsEnabled = Boolean(runtimeConfig.analyticsEnabled);

function ensureGtag() {
    if (!analyticsEnabled) return false;

    win.dataLayer = win.dataLayer || [];
    if (typeof win.gtag !== 'function') {
        win.gtag = function gtag() {
            win.dataLayer.push(arguments);
        };
        win.gtag('js', new Date());
        win.gtag('config', 'G-KE98KY192J', {
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
