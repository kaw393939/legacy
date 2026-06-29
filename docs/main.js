/* Legacy Defenders runtime */
(function () {
    'use strict';

    const doc = document;
    const win = window;
    const root = doc.documentElement;
    const analyticsEnabled = Boolean(win.ldAnalyticsEnabled && typeof win.gtag === 'function');
    const conversionValues = win.CONVERSION_VALUES || {};

    const $ = (selector, scope = doc) => scope.querySelector(selector);
    const $$ = (selector, scope = doc) => Array.from(scope.querySelectorAll(selector));
    const on = (target, event, handler, options) => {
        if (target) target.addEventListener(event, handler, options);
    };
    const closest = (target, selector) => {
        if (!target) return null;
        if (target.nodeType === 1) return target.closest(selector);
        return target.parentElement ? target.parentElement.closest(selector) : null;
    };

    function ready(fn) {
        if (doc.readyState === 'loading') {
            doc.addEventListener('DOMContentLoaded', fn, { once: true });
        } else {
            fn();
        }
    }

    function valueFor(key, fallback = 1) {
        const value = Number(conversionValues[key]);
        return Number.isFinite(value) ? value : fallback;
    }

    function track(eventName, payload) {
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

    function textOf(element) {
        return (element && element.textContent ? element.textContent : '').replace(/\s+/g, ' ').trim();
    }

    function sectionFor(element) {
        const explicit = element && element.getAttribute('data-section');
        if (explicit) return explicit;

        const section = element ? element.closest('section,[data-section]') : null;
        if (!section) return 'unknown';

        return section.getAttribute('data-section') ||
            section.id ||
            String(section.className || '').split(/\s+/).filter(Boolean)[0] ||
            'unknown';
    }

    function normalizePath(pathname) {
        return pathname.replace(/\/index\.html$/, '/').replace(/\/$/, '/');
    }

    function samePage(url) {
        return url.origin === win.location.origin &&
            normalizePath(url.pathname) === normalizePath(win.location.pathname);
    }

    function getHashTarget(hash) {
        if (!hash || hash === '#') return null;
        try {
            return doc.getElementById(decodeURIComponent(hash.slice(1)));
        } catch (error) {
            return null;
        }
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
            null;

        if (element.getAttribute('data-cta') === 'package' || card.classList.contains('package-card')) {
            const packageName = packageNameFor(element, card);
            track('package_interest', {
                event_category: 'Packages',
                event_label: packageName,
                package_name: packageName,
                interaction_type: 'cta_click',
                psychological_appeal: psychology,
                value: valueFor('package_interest', 8)
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

    function initAnalytics() {
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

    function initDeferredFontAwesome() {
        const href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';

        function load() {
            if ($(`link[href="${href}"]`)) return;

            const link = doc.createElement('link');
            link.rel = 'stylesheet';
            link.href = href;
            doc.head.appendChild(link);
        }

        on(win, 'load', () => {
            if ('requestIdleCallback' in win) {
                win.requestIdleCallback(load, { timeout: 1600 });
            } else {
                win.setTimeout(load, 800);
            }
        }, { once: true });
    }

    function initMobileMenu() {
        const toggle = $('.mobile-menu-toggle');
        const nav = $('.nav');
        if (!toggle || !nav) return;

        let lastFocus = null;

        function focusableLinks() {
            return $$('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])', nav);
        }

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

    function initSmoothScroll() {
        const header = $('#header') || $('.header');

        function scrollToHash(hash, updateLocation = true, behavior = 'smooth') {
            const target = getHashTarget(hash);
            if (!target) return false;

            const headerHeight = header ? header.offsetHeight : 0;
            const top = Math.max(0, target.getBoundingClientRect().top + win.pageYOffset - headerHeight - 20);

            try {
                win.scrollTo({ top, behavior });
            } catch (error) {
                win.scrollTo(0, top);
            }

            if (updateLocation && win.history && win.history.pushState) {
                win.history.pushState(null, '', hash);
            }

            return true;
        }

        doc.addEventListener('click', (event) => {
            const anchor = closest(event.target, 'a[href*="#"]');
            if (!anchor) return;

            const href = anchor.getAttribute('href');
            if (!href || href === '#') {
                event.preventDefault();
                win.scrollTo({ top: 0, behavior: 'smooth' });
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

        function retryInitialHash() {
            if (!win.location.hash) return;

            let attempts = 0;
            const retry = () => {
                attempts += 1;
                const done = scrollToHash(win.location.hash, false, attempts === 1 ? 'auto' : 'smooth');
                if (!done && attempts < 8) win.setTimeout(retry, 150);
            };

            retry();
        }

        retryInitialHash();
        on(win, 'load', retryInitialHash, { once: true });
    }

    function initScrollState() {
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
        on(scrollTopButton, 'click', () => win.scrollTo({ top: 0, behavior: 'smooth' }));
        update();
    }

    function initContactFloatState() {
        const contact = $('#contact');
        const float = $('.whatsapp-float');
        if (!contact || !float || !('IntersectionObserver' in win)) return;

        const observer = new IntersectionObserver((entries) => {
            doc.body.classList.toggle('contact-in-view', entries.some((entry) => entry.isIntersecting));
        }, {
            threshold: 0.08,
            rootMargin: '-80px 0px -12% 0px'
        });

        observer.observe(contact);
    }

    function initLazyImages() {
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

    function initSkipLink() {
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

    function initFAQ() {
        const items = $$('.faq-item');
        if (!items.length) return;

        const searchInput = $('#faq-search');
        const filters = $$('.category-filter');
        const categories = $$('.faq-category');
        const itemData = items.map((item) => ({
            item,
            category: item.getAttribute('data-category') || '',
            text: textOf(item).toLowerCase(),
            question: $('.faq-question', item),
            answer: $('.faq-answer', item)
        }));

        let selectedCategory = 'all';
        let searchTerm = '';
        let searchTimer = 0;

        function closeItem(data) {
            data.item.classList.remove('active');
            if (data.question) data.question.setAttribute('aria-expanded', 'false');
            if (data.answer) data.answer.style.maxHeight = '0';
        }

        function openItem(data) {
            data.item.classList.add('active');
            if (data.question) data.question.setAttribute('aria-expanded', 'true');
            if (data.answer) data.answer.style.maxHeight = `${data.answer.scrollHeight}px`;
        }

        function dataForItem(item) {
            return itemData.find((data) => data.item === item);
        }

        function applyFilters() {
            itemData.forEach((data) => {
                const categoryMatch = selectedCategory === 'all' || data.category === selectedCategory;
                const searchMatch = !searchTerm || data.text.includes(searchTerm);
                const visible = categoryMatch && searchMatch;

                data.item.classList.toggle('hidden', !visible);
                if (!visible) closeItem(data);
            });

            categories.forEach((category) => {
                const hasVisibleItems = Boolean($('.faq-item:not(.hidden)', category));
                category.style.display = hasVisibleItems ? 'block' : 'none';
            });
        }

        doc.addEventListener('click', (event) => {
            const question = closest(event.target, '.faq-question');
            if (question) {
                event.preventDefault();

                const current = dataForItem(question.closest('.faq-item'));
                if (!current) return;

                const wasOpen = current.item.classList.contains('active');
                itemData.forEach(closeItem);
                if (!wasOpen) openItem(current);

                track('faq_question_click', {
                    event_category: 'FAQ',
                    event_label: textOf(question),
                    question_text: textOf(question),
                    faq_category: current.category
                });
                return;
            }

            const filter = closest(event.target, '.category-filter');
            if (!filter) return;

            selectedCategory = filter.getAttribute('data-category') || 'all';
            filters.forEach((button) => button.classList.toggle('active', button === filter));

            if (searchInput) searchInput.value = '';
            searchTerm = '';
            applyFilters();

            track('faq_category_filter', {
                event_category: 'FAQ',
                event_label: selectedCategory,
                category_selected: selectedCategory
            });
        });

        doc.addEventListener('keydown', (event) => {
            const question = closest(event.target, '.faq-question');
            if (!question || (event.key !== 'Enter' && event.key !== ' ')) return;

            event.preventDefault();
            question.click();
        });

        on(searchInput, 'input', () => {
            searchTerm = searchInput.value.toLowerCase().trim();
            applyFilters();

            if (!analyticsEnabled || searchTerm.length < 3) return;

            win.clearTimeout(searchTimer);
            searchTimer = win.setTimeout(() => {
                track('faq_search', {
                    event_category: 'FAQ',
                    event_label: searchTerm,
                    search_term: searchTerm
                });
            }, 300);
        });
    }

    function initPrintPrep() {
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

    ready(() => {
        initDeferredFontAwesome();
        initAnalytics();
        initMobileMenu();
        initSmoothScroll();
        initScrollState();
        initContactFloatState();
        initLazyImages();
        initSkipLink();
        initFAQ();
        initPrintPrep();
    });
})();
