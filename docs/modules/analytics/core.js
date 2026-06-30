import { win } from '../dom.js';

const conversionValues = win.CONVERSION_VALUES || {};

export const analyticsEnabled = Boolean(win.ldAnalyticsEnabled && typeof win.gtag === 'function');

export function valueFor(key, fallback = 1) {
    const value = Number(conversionValues[key]);
    return Number.isFinite(value) ? value : fallback;
}

export function track(eventName, payload) {
    if (!analyticsEnabled) return;
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
