import { $, $$, doc, on, win } from './dom.js';

export function initDeferredFontAwesome() {
    const href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';

    function load() {
        if ($(`link[href="${href}"]`)) return;

        const link = doc.createElement('link');
        link.rel = 'stylesheet';
        link.href = href;
        link.crossOrigin = 'anonymous';
        link.referrerPolicy = 'no-referrer';
        doc.head.appendChild(link);
    }

    if ('requestIdleCallback' in win) {
        win.requestIdleCallback(load, { timeout: 1500 });
    } else {
        win.setTimeout(load, 800);
    }
}

export function initLazyImages() {
    const lazyImages = $$('img[data-src]');
    if (!lazyImages.length || !('IntersectionObserver' in win)) return;

    const observer = new IntersectionObserver((entries) => {
        entries.forEach((entry) => {
            if (!entry.isIntersecting) return;

            const img = entry.target;
            img.src = img.dataset.src;
            img.removeAttribute('data-src');
            observer.unobserve(img);
        });
    }, { rootMargin: '200px 0px' });

    lazyImages.forEach((img) => observer.observe(img));
}

export function initSkipLink() {
    const skipLink = $('.skip-link');
    const main = $('#main-content');
    if (!skipLink || !main) return;

    on(skipLink, 'click', (event) => {
        event.preventDefault();
        main.setAttribute('tabindex', '-1');
        main.focus();
        main.removeAttribute('tabindex');
    });
}
