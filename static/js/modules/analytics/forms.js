import { closest, doc } from '../dom.js';
import { track, trackConversion, valueFor } from './core.js';

export function initFormAnalytics() {
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
}
