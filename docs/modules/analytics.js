import { $, $$, closest, doc, sectionFor, textOf, win } from './dom.js';

const conversionValues = win.CONVERSION_VALUES || {};
export const analyticsEnabled = Boolean(win.ldAnalyticsEnabled && typeof win.gtag === 'function');

function valueFor(key, fallback = 1) {
    const value = Number(conversionValues[key]);
    return Number.isFinite(value) ? value : fallback;
}

export function track(eventName, payload) {
    if (!analyticsEnabled) return;
    win.gtag('event', eventName, payload || {});
}

function trackConversion(label, value) {
    track('conversion', {
        event_category: 'Conversions',
        event_label: label,
        value,
        currency: 'USD'
    });
}

function ctaTypeFor(element) {
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

function trackCta(element) {
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

function trackContactLink(element, href) {
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

function trackServiceCta(element) {
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

function initSectionAnalytics() {
    if (!('IntersectionObserver' in win)) return;

    const seen = new Set();
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting || seen.has(entry.target)) return;

            seen.add(entry.target);
            const sectionName = entry.target.id ||
                String(entry.target.className || '').split(/\s+/).filter(Boolean)[0] ||
                'unknown';

            track('page_view', {
                page_title: `${sectionName} - Legacy Defenders`,
                page_location: `${win.location.href.split('#')[0]}#${sectionName}`,
                event_category: 'Navigation',
                event_label: sectionName,
                section_name: sectionName,
                value: valueFor('journey_phase_view', 3)
            });
            observer.unobserve(entry.target);
        });
    }, { threshold: 0.5, rootMargin: '0px 0px -10% 0px' });

    $$('section[id], .hero').forEach((section) => observer.observe(section));
}

function initServiceCardAnalytics() {
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

function initTimeOnPageAnalytics() {
    [30, 60, 120, 300].forEach((seconds) => {
        win.setTimeout(() => {
            track('time_on_page', {
                event_category: 'Engagement',
                event_label: `${seconds}s`,
                value: seconds
            });
        }, seconds * 1000);
    });
}

export function initAnalytics() {
    if (!analyticsEnabled) return;

    doc.addEventListener('click', (event) => {
        const element = closest(event.target, 'a,button,[role="button"]');
        if (!element) return;

        const href = element.getAttribute('href') || '';
        const ctaType = ctaTypeFor(element);

        trackContactLink(element, href);
        trackCta(element);

        if (ctaType === 'navigation') {
            track('navigation_click', {
                event_category: 'Navigation',
                event_label: textOf(element),
                destination: element.getAttribute('data-destination') || href,
                value: 2
            });
        }

        if (element.matches('.service-cta,.service-card .btn,.package-card .btn,[data-cta="service"],[data-cta="package"]')) {
            trackServiceCta(element);
        }

        if (href.includes('#')) {
            const targetSection = href.split('#').pop() || 'top';
            track('internal_navigation', {
                event_category: 'Navigation',
                event_label: targetSection,
                destination: targetSection
            });
        }
    });

    doc.addEventListener('focusin', (event) => {
        const field = closest(event.target, 'input,textarea,select');
        if (!field || field.type === 'hidden') return;

        const form = field.form;
        if (!form || form.dataset.ldStarted) return;

        form.dataset.ldStarted = 'true';
        track('form_start', {
            event_category: 'Forms',
            event_label: form.id || form.className || 'form',
            field: field.name || field.type,
            value: 2
        });
    });

    doc.addEventListener('focusout', (event) => {
        const field = closest(event.target, 'input,textarea,select');
        if (!field || field.type === 'hidden' || !field.value.trim()) return;

        const form = field.form;
        track('form_field_complete', {
            event_category: 'Forms',
            event_label: form ? (form.id || form.className || 'form') : 'form',
            field: field.name || field.type,
            value: 2
        });
    });

    doc.addEventListener('submit', (event) => {
        const form = event.target;
        if (!(form instanceof HTMLFormElement)) return;

        const formType = form.id || form.className || 'form';
        const amount = valueFor('form_submit', 35);
        track('form_submit', {
            event_category: 'Forms',
            event_label: formType,
            value: amount
        });
        trackConversion('form_submit', amount);
    });

    initSectionAnalytics();
    initServiceCardAnalytics();
    initTimeOnPageAnalytics();

    track('ab_test_exposure', {
        event_category: 'A/B Testing',
        event_label: 'journey_based_services',
        test_variation: 'estate_math_offer',
        psychological_principles: 'clarity,trust,time_cost'
    });
}
