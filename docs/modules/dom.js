export const doc = document;
export const win = window;
export const root = doc.documentElement;

export const $ = (selector, scope = doc) => scope.querySelector(selector);
export const $$ = (selector, scope = doc) => Array.from(scope.querySelectorAll(selector));

export function on(target, event, handler, options) {
    if (target) target.addEventListener(event, handler, options);
}

export function closest(target, selector) {
    if (!target) return null;
    if (target.nodeType === 1) return target.closest(selector);
    return target.parentElement ? target.parentElement.closest(selector) : null;
}

export function ready(fn) {
    if (doc.readyState === 'loading') {
        doc.addEventListener('DOMContentLoaded', fn, { once: true });
    } else {
        fn();
    }
}

export function textOf(element) {
    return (element && element.textContent ? element.textContent : '').replace(/\s+/g, ' ').trim();
}

export function normalizePath(pathname) {
    return pathname.replace(/\/index\.html$/, '/').replace(/\/$/, '/');
}

export function samePage(url) {
    return url.origin === win.location.origin &&
        normalizePath(url.pathname) === normalizePath(win.location.pathname);
}

export function getHashTarget(hash) {
    if (!hash || hash === '#') return null;
    try {
        return doc.getElementById(decodeURIComponent(hash.slice(1)));
    } catch (error) {
        return null;
    }
}

export function preferredScrollBehavior() {
    return win.matchMedia && win.matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth';
}

export function scrollToTop(behavior = preferredScrollBehavior()) {
    win.scrollTo({ top: 0, behavior });
}

export function sectionFor(element) {
    const explicit = element && element.getAttribute('data-section');
    if (explicit) return explicit;

    const section = element ? element.closest('section,[data-section]') : null;
    if (!section) return 'unknown';

    return section.getAttribute('data-section') ||
        section.id ||
        String(section.className || '').split(/\s+/).filter(Boolean)[0] ||
        'unknown';
}
