import { $$, win } from '../dom.js';
import { track, valueFor } from './core.js';

export function initSectionAnalytics() {
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

export function initTimeOnPageAnalytics() {
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

export function trackExperimentExposure() {
    track('ab_test_exposure', {
        event_category: 'A/B Testing',
        event_label: 'journey_based_services',
        test_variation: 'estate_math_offer',
        psychological_principles: 'clarity,trust,time_cost'
    });
}
