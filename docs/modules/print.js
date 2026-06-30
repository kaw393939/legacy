import { $, $$, closest, doc, on, win } from './dom.js';

export function initPrintPrep() {
    on(win, 'beforeprint', () => {
        $$('.faq-item').forEach((item) => {
            const answer = $('.faq-answer', item);
            const question = $('.faq-question', item);
            item.classList.add('active');
            if (question) question.setAttribute('aria-expanded', 'true');
            if (answer) answer.style.maxHeight = 'none';
        });
    });
}

export function initPrintActions() {
    doc.addEventListener('click', (event) => {
        const trigger = closest(event.target, '[data-print-page]');
        if (!trigger) return;

        event.preventDefault();
        win.print();
    });
}
