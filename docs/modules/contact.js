import { $, doc, win } from './dom.js';

const contactIntentOptions = [
    {
        terms: ['single decision', 'only heir', 'sole heir'],
        situation: 'Single decision-maker inherited home',
        role: 'Sole heir or single decision maker',
        urgent: 'Preparing to sell, rent, move in, or renovate'
    },
    {
        terms: ['out-of-state', 'out of state', 'local coordination', 'cannot be there'],
        situation: 'Out-of-state executor or local coordination',
        role: 'Executor or administrator',
        urgent: 'I need local provider coordination from out of town'
    },
    {
        terms: ['belongings', 'inventory', 'item', 'storage', 'shipping', 'donation'],
        situation: 'House full of belongings',
        urgent: 'The house is full of belongings'
    },
    {
        terms: ['urgent bills', 'property risk', 'carrying', 'mortgage', 'tax', 'utility', 'utilities', 'insurance', 'stabilization', 'vacant'],
        situation: 'Urgent bills or property risk',
        urgent: 'Mortgage, taxes, utilities, or insurance'
    },
    {
        terms: ['prearranged', 'plan ahead', 'readiness', 'children'],
        situation: 'Prearranged legacy readiness planning',
        role: 'Parent or homeowner planning ahead',
        urgent: 'Planning before heirs are overwhelmed',
        authority: 'Planning ahead before a death or crisis'
    },
    {
        terms: ['professional', 'referral', 'attorney', 'cpa', 'realtor', 'lender', 'records support'],
        situation: 'Professional referral or records support',
        role: 'Professional referral source'
    },
    {
        terms: ['pricing', 'services', 'estate math', 'free guide', 'worksheet', 'probate'],
        situation: 'Pricing, services, or general estate math'
    }
];

function selectByText(select, text) {
    if (!select || !text || select.value) return false;
    const option = Array.from(select.options).find((item) => item.text === text);
    if (!option) return false;
    select.value = option.text;
    return true;
}

function intentFor(value) {
    const normalized = value.toLowerCase();
    return contactIntentOptions.find((option) => option.terms.some((term) => normalized.includes(term))) || {
        situation: 'I am not sure yet'
    };
}

export function initContactFloatState() {
    const contact = $('#contact');
    const footer = $('.footer');
    const float = $('.whatsapp-float');
    const blockers = [contact, footer].filter(Boolean);

    if (!blockers.length || !float || !('IntersectionObserver' in win)) return;

    const visibleBlockers = new Map();
    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => visibleBlockers.set(entry.target, entry.isIntersecting));
        doc.body.classList.toggle('contact-in-view', Array.from(visibleBlockers.values()).some(Boolean));
    }, {
        threshold: 0.08,
        rootMargin: '-80px 0px -12% 0px'
    });

    blockers.forEach((blocker) => {
        visibleBlockers.set(blocker, false);
        observer.observe(blocker);
    });
}

export function initContactContext() {
    const form = $('[data-form="care-intake"]');
    if (!form || !win.URLSearchParams) return;

    const params = new URLSearchParams(win.location.search || '');
    const interest = (params.get('interest') || '').replace(/\+/g, ' ').trim();
    if (!interest) return;

    const hidden = form.querySelector('input[name="Requested interest"]');
    if (hidden) hidden.value = interest;

    const intent = intentFor(interest);
    selectByText($('#contact-situation'), intent.situation);
    selectByText($('#contact-role'), intent.role);
    selectByText($('#contact-authority'), intent.authority);
    selectByText($('#contact-urgent'), intent.urgent);

    const note = $('[data-contact-context]');
    if (note) {
        note.hidden = false;
        note.textContent = `You clicked about ${interest}. We will use that to focus the free call.`;
    }
}
