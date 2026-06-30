import { $, closest, doc, sectionFor, textOf } from '../dom.js';
import { track, trackConversion, valueFor } from './core.js';

export function ctaTypeFor(element) {
    const raw = element.getAttribute('data-cta');
    if (raw === 'primary') return 'primary_cta';
    if (raw === 'secondary') return 'secondary_cta';
    if (raw === 'service') return 'service_inquiry';
    if (raw === 'package') return 'package_cta';
    if (raw) return raw;
    if (element.classList.contains('btn-primary')) return 'primary_cta';
    if (element.classList.contains('btn-outline') || element.classList.contains('btn-secondary')) return 'secondary_cta';
    return null;
}

function serviceNameFor(element, card) {
    return element.getAttribute('data-service') ||
        (card && card.getAttribute('data-service')) ||
        textOf($('.service-title, h3, h4', card || doc)) ||
        'unknown';
}

function packageNameFor(element, card) {
    return element.getAttribute('data-package') ||
        (card && card.getAttribute('data-package')) ||
        textOf($('.service-title, h3, h4', card || doc)) ||
        'unknown';
}

export function trackCta(element) {
    const type = ctaTypeFor(element);
    if (!type || type === 'navigation' || type === 'social') return;

    const destination = element.getAttribute('href') ||
        element.getAttribute('data-destination') ||
        'unknown';
    const amount = valueFor(type, 5);

    track('cta_click', {
        event_category: 'CTA',
        event_label: textOf(element),
        cta_type: type,
        section_name: sectionFor(element),
        destination,
        value: amount
    });

    if (['primary_cta', 'service_inquiry', 'phone_call', 'whatsapp', 'form_submit'].includes(type)) {
        trackConversion(type, amount);
    }
}

export function trackContactLink(element, href) {
    const isWhatsApp = href.includes('wa.me') || href.toLowerCase().includes('whatsapp');
    const isPhone = href.startsWith('tel:');
    const isEmail = href.startsWith('mailto:');

    if (!isWhatsApp && !isPhone && !isEmail) return;

    if (isEmail) {
        track('email_click', {
            event_category: 'Contact',
            event_label: 'Email',
            source: sectionFor(element),
            value: valueFor('email_click', 15)
        });
        return;
    }

    const label = isWhatsApp ? 'WhatsApp' : 'Phone';
    const key = isWhatsApp ? 'whatsapp' : 'phone_call';
    const amount = valueFor(key, isWhatsApp ? 28 : 30);

    track('contact_method', {
        event_category: 'Contact',
        event_label: label,
        source: sectionFor(element),
        value: amount
    });
    trackConversion(key, amount);
}

export function trackServiceCta(element) {
    const card = element.closest('.service-card,.package-card');
    if (!card) return;

    const psychology = element.getAttribute('data-psychology') ||
        card.getAttribute('data-psychology') ||
        'unknown';

    if (element.getAttribute('data-cta') === 'package' || card.classList.contains('package-card')) {
        const packageName = packageNameFor(element, card);
        track('package_interest', {
            event_category: 'Packages',
            event_label: packageName,
            package_name: packageName,
            interaction_type: 'cta_click',
            psychological_appeal: psychology,
            value: valueFor('package_interest', 5)
        });
        return;
    }

    const serviceName = serviceNameFor(element, card);
    track('service_interest', {
        event_category: 'Services',
        event_label: serviceName,
        service_name: serviceName,
        interaction_type: 'cta_click',
        psychological_appeal: psychology,
        value: valueFor('service_interest', 5)
    });
}

export function initServiceCardAnalytics() {
    doc.addEventListener('mouseover', (event) => {
        const card = closest(event.target, '.service-card,.package-card');
        if (!card || card.contains(event.relatedTarget)) return;

        const isPackage = card.classList.contains('package-card') || card.hasAttribute('data-package');
        const name = isPackage ? packageNameFor(card, card) : serviceNameFor(card, card);
        track(isPackage ? 'package_interest' : 'service_interest', {
            event_category: isPackage ? 'Packages' : 'Services',
            event_label: name,
            interaction_type: 'hover',
            value: valueFor(isPackage ? 'package_interest' : 'service_interest', 5)
        });
    });

    doc.addEventListener('click', (event) => {
        const card = closest(event.target, '.service-card,.package-card');
        if (!card || closest(event.target, '.btn,.cta,.service-cta')) return;

        const isPackage = card.classList.contains('package-card') || card.hasAttribute('data-package');
        const name = isPackage ? packageNameFor(card, card) : serviceNameFor(card, card);
        track(isPackage ? 'package_interest' : 'service_interest', {
            event_category: isPackage ? 'Packages' : 'Services',
            event_label: name,
            interaction_type: 'card_click',
            value: valueFor(isPackage ? 'package_interest' : 'service_interest', 5)
        });
    });
}
