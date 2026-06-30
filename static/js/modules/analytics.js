import { closest, doc, textOf } from './dom.js';
import { analyticsEnabled, track } from './analytics/core.js';
import {
    ctaTypeFor,
    initServiceCardAnalytics,
    trackContactLink,
    trackCta,
    trackServiceCta
} from './analytics/cta.js';
import { initSectionAnalytics, initTimeOnPageAnalytics, trackExperimentExposure } from './analytics/engagement.js';
import { initFormAnalytics } from './analytics/forms.js';

export { analyticsEnabled, track };

function initClickAnalytics() {
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
}

export function initAnalytics() {
    if (!analyticsEnabled) return;

    initClickAnalytics();
    initFormAnalytics();
    initSectionAnalytics();
    initServiceCardAnalytics();
    initTimeOnPageAnalytics();
    trackExperimentExposure();
}
