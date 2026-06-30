import { $, $$, closest, doc, getHashTarget, on, preferredScrollBehavior, root, samePage, scrollToTop, win } from './dom.js';
import { analyticsEnabled, track } from './analytics.js';

export function initMobileMenu() {
    const toggle = $('.mobile-menu-toggle');
    const nav = $('.nav');
    if (!toggle || !nav) return;

    let lastFocus = null;
    const focusableLinks = () => $$('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])', nav);

    function setOpen(open, restoreFocus = true) {
        nav.classList.toggle('active', open);
        toggle.classList.toggle('active', open);
        doc.body.classList.toggle('nav-open', open);
        toggle.setAttribute('aria-expanded', String(open));
        toggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');

        if (open) {
            lastFocus = doc.activeElement;
            const first = focusableLinks()[0];
            if (first) first.focus();
        } else if (restoreFocus && lastFocus && typeof lastFocus.focus === 'function') {
            lastFocus.focus();
            lastFocus = null;
        }
    }

    on(toggle, 'click', () => {
        const open = !nav.classList.contains('active');
        setOpen(open);
        track('mobile_menu_toggle', {
            event_category: 'Navigation',
            event_label: open ? 'open' : 'close'
        });
    });

    on(nav, 'click', (event) => {
        if (closest(event.target, 'a.nav-link')) setOpen(false, false);
    });

    on(doc, 'click', (event) => {
        if (!nav.classList.contains('active')) return;
        if (closest(event.target, '.nav,.mobile-menu-toggle')) return;
        setOpen(false);
    });

    on(doc, 'keydown', (event) => {
        if (!nav.classList.contains('active')) return;

        if (event.key === 'Escape') {
            setOpen(false);
            return;
        }

        if (event.key !== 'Tab') return;

        const nodes = focusableLinks();
        if (!nodes.length) return;

        const first = nodes[0];
        const last = nodes[nodes.length - 1];

        if (event.shiftKey && (doc.activeElement === first || doc.activeElement === nav)) {
            event.preventDefault();
            last.focus();
        } else if (!event.shiftKey && doc.activeElement === last) {
            event.preventDefault();
            first.focus();
        }
    });

    on(win, 'resize', () => {
        if (nav.classList.contains('active') && win.innerWidth > 968) {
            setOpen(false, false);
        }
    }, { passive: true });
}

export function initSmoothScroll() {
    const header = $('#header') || $('.header');
    const scrollOffset = () => (header ? header.offsetHeight : 0) + 16;

    function updateHash(hash) {
        if (!win.history || !win.history.pushState || win.location.hash === hash) return;
        win.history.pushState(null, '', hash);
    }

    function scrollToHash(hash, updateLocation = true, behavior = preferredScrollBehavior()) {
        if (hash === '#header' || hash === '#top') {
            scrollToTop(behavior);
            if (updateLocation) updateHash(hash);
            return true;
        }

        const target = getHashTarget(hash);
        if (!target) return false;

        const top = Math.max(0, target.getBoundingClientRect().top + win.pageYOffset - scrollOffset());
        win.scrollTo({ top, behavior });
        if (updateLocation) updateHash(hash);

        return true;
    }

    doc.addEventListener('click', (event) => {
        const anchor = closest(event.target, 'a[href*="#"]');
        if (!anchor) return;

        const href = anchor.getAttribute('href');
        if (!href || href === '#') {
            event.preventDefault();
            scrollToTop();
            return;
        }

        let url;
        try {
            url = new URL(href, win.location.href);
        } catch (error) {
            return;
        }

        if (!url.hash || !samePage(url)) return;

        event.preventDefault();
        scrollToHash(url.hash);
    });

    on(win, 'popstate', () => {
        if (win.location.hash) {
            scrollToHash(win.location.hash, false, 'auto');
        } else {
            scrollToTop('auto');
        }
    });
}

export function initScrollState() {
    const header = $('#header') || $('.header');
    const scrollTopButton = $('.scroll-top');
    const sections = $$('section[id]');
    const navBySection = new Map();
    let activeNav = null;
    let ticking = false;
    const scrollMarkers = [25, 50, 75, 90, 100];
    const trackedMarkers = new Set();

    $$('.nav-link[href*="#"]').forEach((link) => {
        try {
            const url = new URL(link.getAttribute('href'), win.location.href);
            if (url.hash && samePage(url)) navBySection.set(url.hash.slice(1), link);
        } catch (error) {
            // Ignore malformed hrefs; validator catches local link issues.
        }
    });

    function updateActiveNav(y) {
        if (!sections.length || !navBySection.size) return;

        const position = y + 180;
        let activeId = null;

        for (const section of sections) {
            if (position >= section.offsetTop) activeId = section.id;
        }

        const next = activeId ? navBySection.get(activeId) : null;
        if (!next || next === activeNav) return;

        if (activeNav) activeNav.classList.remove('active');
        next.classList.add('active');
        activeNav = next;
    }

    function updateScrollDepth(y) {
        if (!analyticsEnabled) return;

        const max = Math.max(1, root.scrollHeight - win.innerHeight);
        const percent = Math.min(100, Math.round((y / max) * 100));

        for (const marker of scrollMarkers) {
            if (percent >= marker && !trackedMarkers.has(marker)) {
                trackedMarkers.add(marker);
                track('scroll', {
                    event_category: 'Engagement',
                    event_label: `${marker}%`,
                    value: marker
                });
            }
        }
    }

    function update() {
        ticking = false;
        const y = win.pageYOffset || root.scrollTop || 0;

        if (header) header.classList.toggle('scrolled', y > 100);
        if (scrollTopButton) scrollTopButton.classList.toggle('visible', y > 500);
        updateActiveNav(y);
        updateScrollDepth(y);
    }

    function requestUpdate() {
        if (ticking) return;
        ticking = true;
        win.requestAnimationFrame(update);
    }

    on(win, 'scroll', requestUpdate, { passive: true });
    on(win, 'resize', requestUpdate, { passive: true });
    on(scrollTopButton, 'click', () => scrollToTop());
    update();
}
