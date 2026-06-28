/* ===================================
   Legacy Defenders - Interactive Features
   =================================== */

// Wait for DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    
    // ===================================
    // Enhanced Analytics Setup
    // ===================================
    
    // Track all CTA buttons
    function initCTATracking() {
        // Primary CTAs (Book Property Visit, Contact buttons)
        document.querySelectorAll('[data-cta="primary"], .cta-primary, .btn-primary').forEach(button => {
            button.addEventListener('click', function(e) {
                const section = this.getAttribute('data-section') || this.closest('section')?.className.split(' ')[0] || 'unknown';
                const ctaText = this.textContent.trim();
                const destination = this.getAttribute('href') || this.getAttribute('data-destination') || 'unknown';
                
                trackCTAClick('primary_cta', section, ctaText, destination);
            });
        });

        // Secondary CTAs (View Services, Get Quote)
        document.querySelectorAll('[data-cta="secondary"], .cta-secondary, .btn-secondary, .btn-outline').forEach(button => {
            button.addEventListener('click', function(e) {
                const section = this.getAttribute('data-section') || this.closest('section')?.className.split(' ')[0] || 'unknown';
                const ctaText = this.textContent.trim();
                const destination = this.getAttribute('href') || this.getAttribute('data-destination') || 'unknown';
                
                trackCTAClick('secondary_cta', section, ctaText, destination);
            });
        });

        // Service-specific CTAs
        document.querySelectorAll('.service-card .btn, .service-cta, [data-cta="service"]').forEach(button => {
            button.addEventListener('click', function(e) {
                const serviceCard = this.closest('.service-card');
                const serviceName = this.getAttribute('data-service') || 
                                  serviceCard?.querySelector('.service-title, h3')?.textContent.trim() || 'unknown';
                const ctaText = this.textContent.trim();
                const psychology = this.getAttribute('data-psychology') || 
                                 serviceCard?.getAttribute('data-psychology') || 'none';
                
                trackCTAClick('service_inquiry', serviceName, ctaText, this.getAttribute('href') || '#contact');
                trackServiceInterest(serviceName, 'cta_click', psychology);
            });
        });

        // Package-specific CTAs with psychological tracking
        document.querySelectorAll('.package-card .btn, [data-cta="package"]').forEach(button => {
            button.addEventListener('click', function(e) {
                const packageCard = this.closest('.package-card');
                const packageName = this.getAttribute('data-package') || 
                                  packageCard?.querySelector('.service-title, h4')?.textContent.trim() || 'unknown';
                const ctaText = this.textContent.trim();
                const psychology = this.getAttribute('data-psychology') || 
                                 packageCard?.getAttribute('data-psychology') || 'none';
                
                trackCTAClick('package_inquiry', packageName, ctaText, this.getAttribute('href') || '#contact');
                trackPackageInterest(packageName, 'cta_click', psychology);
            });
        });

        // WhatsApp and phone links
        document.querySelectorAll('a[href*="wa.me"], a[href*="whatsapp"], a[href^="tel:"]').forEach(link => {
            link.addEventListener('click', function(e) {
                const method = this.href.includes('wa.me') || this.href.includes('whatsapp') ? 'WhatsApp' : 'Phone';
                const source = this.getAttribute('data-section') || 
                              this.closest('section')?.className.split(' ')[0] || 'navigation';
                
                trackContactMethod(method, source);
            });
        });

        // Email links
        document.querySelectorAll('a[href^="mailto:"]').forEach(link => {
            link.addEventListener('click', function(e) {
                const source = this.getAttribute('data-section') || 
                              this.closest('section')?.className.split(' ')[0] || 'navigation';
                
                gtag('event', 'email_click', {
                    event_category: 'Contact',
                    event_label: 'Email',
                    source: source,
                    value: 15
                });
            });
        });

        // Social media links
        document.querySelectorAll('[data-cta="social"]').forEach(link => {
            link.addEventListener('click', function(e) {
                const platform = this.getAttribute('data-platform') || 'unknown';
                const source = this.getAttribute('data-section') || 'unknown';
                
                gtag('event', 'social_click', {
                    event_category: 'Social Media',
                    event_label: platform,
                    source: source,
                    value: 3
                });
            });
        });

        // Navigation links
        document.querySelectorAll('[data-cta="navigation"]').forEach(link => {
            link.addEventListener('click', function(e) {
                const destination = this.getAttribute('data-destination') || this.getAttribute('href');
                
                gtag('event', 'navigation_click', {
                    event_category: 'Navigation',
                    event_label: this.textContent.trim(),
                    destination: destination,
                    value: 2
                });
            });
        });
    }

    // Track section visibility (for single-page navigation)
    function initSectionTracking() {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const sectionName = entry.target.id || entry.target.className.split(' ')[0] || 'unknown';
                    trackSectionView(sectionName);
                }
            });
        }, {
            threshold: 0.5, // Track when 50% of section is visible
            rootMargin: '0px 0px -10% 0px'
        });

        document.querySelectorAll('section, .hero, .services, .testimonials').forEach(section => {
            observer.observe(section);
        });
    }

    // Track scroll depth
    function initScrollTracking() {
        let scrollDepthMarkers = [25, 50, 75, 90, 100];
        let trackedMarkers = new Set();

        window.addEventListener('scroll', function() {
            const scrollPercent = Math.round((window.scrollY / (document.documentElement.scrollHeight - window.innerHeight)) * 100);
            
            scrollDepthMarkers.forEach(marker => {
                if (scrollPercent >= marker && !trackedMarkers.has(marker)) {
                    trackedMarkers.add(marker);
                    trackScrollDepth(marker);
                }
            });
        });
    }

    // Track form interactions
    function initFormTracking() {
        document.querySelectorAll('form').forEach(form => {
            const formType = form.id || form.className || 'contact-form';
            
            // Track form start
            form.addEventListener('focusin', function(e) {
                if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') {
                    trackFormInteraction(formType, 'start', e.target.name || e.target.type);
                }
            }, { once: true });

            // Track form submission
            form.addEventListener('submit', function(e) {
                trackFormInteraction(formType, 'submit', 'complete');
                
                // Track as conversion
                gtag('event', 'conversion', {
                    event_category: 'Forms',
                    event_label: formType,
                    value: 20
                });
            });

            // Track field completions
            form.querySelectorAll('input, textarea, select').forEach(field => {
                field.addEventListener('blur', function() {
                    if (this.value.trim() !== '') {
                        trackFormInteraction(formType, 'field_complete', this.name || this.type);
                    }
                });
            });
        });
    }

    // Track service card interactions with journey phases
    function initServiceTracking() {
        document.querySelectorAll('.service-card').forEach(card => {
            const serviceName = card.querySelector('.service-title, h3, h4')?.textContent.trim() || 'unknown';
            const phase = card.getAttribute('data-phase') || 'unknown';
            const isPackage = card.hasAttribute('data-package');
            
            // Track hover/focus interest with phase context
            card.addEventListener('mouseenter', function() {
                if (isPackage) {
                    trackPackageInterest(serviceName, 'hover');
                } else {
                    trackServiceInterest(serviceName, 'hover', phase);
                }
            });

            // Track detailed view with phase context
            card.addEventListener('click', function(e) {
                // Only track if not clicking a CTA button
                if (!e.target.closest('.btn, .cta')) {
                    if (isPackage) {
                        trackPackageInterest(serviceName, 'card_click');
                    } else {
                        trackServiceInterest(serviceName, 'card_click', phase);
                    }
                }
            });
        });

        // Track journey phase section views
        document.querySelectorAll('.journey-phase').forEach(phase => {
            const phaseType = phase.getAttribute('data-phase') || 'unknown';
            const phaseTitle = phase.querySelector('.phase-title')?.textContent.trim() || phaseType;
            
            // Create intersection observer for phase visibility
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        gtag('event', 'journey_phase_view', {
                            event_category: 'Journey',
                            event_label: phaseType,
                            phase_title: phaseTitle,
                            phase_type: phaseType
                        });
                    }
                });
            }, { threshold: 0.5 });
            
            observer.observe(phase);
        });
    }

    // Enhanced navigation tracking
    function initNavigationTracking() {
        document.querySelectorAll('a[href^="#"]').forEach(link => {
            link.addEventListener('click', function(e) {
                const targetSection = this.getAttribute('href').replace('#', '');
                
                gtag('event', 'internal_navigation', {
                    event_category: 'Navigation',
                    event_label: targetSection,
                    destination: targetSection
                });
            });
        });
    }

    function initResponsiveTables() {
        document.querySelectorAll('.content-page table').forEach(table => {
            if (table.classList.contains('responsive-table-ready')) return;

            const headerCells = Array.from(table.querySelectorAll('thead th'));
            const headers = headerCells.map(header => header.textContent.trim()).filter(Boolean);

            if (!headers.length) return;

            table.classList.add('responsive-table-ready');

            table.querySelectorAll('tbody tr').forEach(row => {
                Array.from(row.children).forEach((cell, index) => {
                    const fallback = index === 0 ? 'Item' : `Detail ${index + 1}`;
                    cell.setAttribute('data-label', headers[index] || fallback);

                    if (!cell.textContent.trim()) {
                        cell.classList.add('table-cell-empty');
                    }
                });
            });
        });
    }

    function initContactFloatState() {
        const contactSection = document.getElementById('contact');
        const whatsappFloat = document.querySelector('.whatsapp-float');

        if (!contactSection || !whatsappFloat || !('IntersectionObserver' in window)) return;

        const contactObserver = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                document.body.classList.toggle('contact-in-view', entry.isIntersecting);
            });
        }, {
            threshold: 0.08,
            rootMargin: '-80px 0px -12% 0px'
        });

        contactObserver.observe(contactSection);
    }

    // Initialize all tracking
    initCTATracking();
    initSectionTracking();
    initScrollTracking();
    initFormTracking();
    initServiceTracking();
    initNavigationTracking();
    initResponsiveTables();
    initContactFloatState();

    // ===================================
    // Mobile Menu Toggle
    // ===================================
    const mobileMenuToggle = document.querySelector('.mobile-menu-toggle');
    const nav = document.querySelector('.nav');
    const navLinks = document.querySelectorAll('.nav-link');
    
    if (mobileMenuToggle && nav) {
        let lastFocus = null;

        const setMenuOpen = (open) => {
            nav.classList.toggle('active', open);
            mobileMenuToggle.classList.toggle('active', open);
            document.body.classList.toggle('nav-open', open);

            mobileMenuToggle.setAttribute('aria-expanded', open ? 'true' : 'false');
            mobileMenuToggle.setAttribute('aria-label', open ? 'Close menu' : 'Open menu');

            if (open) {
                lastFocus = document.activeElement;
            }

            if (open) {
                // Focus the first link for accessibility
                const firstLink = nav.querySelector('a.nav-link');
                if (firstLink) firstLink.focus();
            } else if (lastFocus && typeof lastFocus.focus === 'function') {
                // Restore focus (especially important for keyboard users)
                lastFocus.focus();
                lastFocus = null;
            }
        };

        mobileMenuToggle.addEventListener('click', function() {
            const isOpen = nav.classList.contains('active');
            setMenuOpen(!isOpen);
            
            // Track mobile menu usage
            if (typeof gtag !== 'undefined') {
                gtag('event', 'mobile_menu_toggle', {
                    event_category: 'Navigation',
                    event_label: nav.classList.contains('active') ? 'open' : 'close'
                });
            }
        });
        
        // Close mobile menu when clicking on a link
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                setMenuOpen(false);
            });
        });

        // Close when clicking outside nav
        document.addEventListener('click', function(e) {
            if (!nav.classList.contains('active')) return;
            if (e.target.closest('.nav')) return;
            if (e.target.closest('.mobile-menu-toggle')) return;
            setMenuOpen(false);
        });

        // Close on Escape
        document.addEventListener('keydown', function(e) {
            if (e.key !== 'Escape') return;
            if (!nav.classList.contains('active')) return;
            setMenuOpen(false);
        });

        // Trap focus inside the open mobile nav
        document.addEventListener('keydown', function(e) {
            if (!nav.classList.contains('active')) return;
            if (e.key !== 'Tab') return;

            const focusable = nav.querySelectorAll('a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])');
            if (!focusable.length) return;

            const first = focusable[0];
            const last = focusable[focusable.length - 1];
            const active = document.activeElement;

            if (e.shiftKey) {
                if (active === first || active === nav) {
                    e.preventDefault();
                    last.focus();
                }
            } else {
                if (active === last) {
                    e.preventDefault();
                    first.focus();
                }
            }
        });

        // If user rotates / resizes back to desktop, ensure menu is closed
        window.addEventListener('resize', function() {
            if (!nav.classList.contains('active')) return;
            if (window.innerWidth > 968) {
                setMenuOpen(false);
            }
        });
    }
    
    // ===================================
    // Header Scroll Effect
    // ===================================
    const header = document.getElementById('header') || document.querySelector('.header');
    let lastScroll = 0;
    
    if (header) {
        window.addEventListener('scroll', function() {
            const currentScroll = window.pageYOffset;
            
            if (currentScroll > 100) {
                header.classList.add('scrolled');
            } else {
                header.classList.remove('scrolled');
            }
            
            lastScroll = currentScroll;
        });
    }
    
    // ===================================
    // Smooth Scroll for Anchor Links
    // ===================================
    function getHashTarget(hash) {
        if (!hash || hash === '#') return null;
        const id = decodeURIComponent(hash.slice(1));
        return document.getElementById(id);
    }

    function scrollToHashTarget(hash, updateLocation = true, behavior = 'smooth') {
        const target = getHashTarget(hash);
        if (!target) return false;

        const headerHeight = header ? header.offsetHeight : 0;
        const targetPosition = target.getBoundingClientRect().top + window.pageYOffset - headerHeight - 20;
        const scrollTop = Math.max(0, targetPosition);
        const scrollRoot = document.scrollingElement || document.documentElement || document.body;

        try {
            window.scrollTo({
                top: scrollTop,
                behavior: behavior
            });
        } catch (error) {
            window.scrollTo(0, scrollTop);
        }

        if (scrollRoot && typeof scrollRoot.scrollTo === 'function') {
            try {
                scrollRoot.scrollTo({
                    top: scrollTop,
                    behavior: behavior
                });
            } catch (error) {
                scrollRoot.scrollTo(0, scrollTop);
            }
        }

        window.setTimeout(() => {
            const currentTop = scrollRoot ? scrollRoot.scrollTop : window.pageYOffset;
            const targetStillFar = Math.abs(target.getBoundingClientRect().top - headerHeight - 20) > 120;

            if (Math.abs(currentTop - scrollTop) > 120 && targetStillFar) {
                try {
                    if (scrollRoot) scrollRoot.scrollTop = scrollTop;
                } catch (error) {
                    // Some embedded browser shells expose a read-only scrollTop.
                }

                try {
                    target.scrollIntoView({
                        block: 'start',
                        behavior: behavior
                    });
                } catch (error) {
                    target.scrollIntoView(true);
                }
            }
        }, 250);

        if (updateLocation && window.history && window.history.pushState) {
            window.history.pushState(null, '', hash);
        }

        return true;
    }

    document.querySelectorAll('a[href*="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const href = this.getAttribute('href');

            // Scroll to top if href is just "#"
            if (href === '#') {
                e.preventDefault();
                window.scrollTo({
                    top: 0,
                    behavior: 'smooth'
                });
                return;
            }

            const url = new URL(href, window.location.href);
            const currentPath = window.location.pathname.replace(/\/$/, '/');
            const targetPath = url.pathname.replace(/\/$/, '/');

            if (url.origin === window.location.origin && targetPath === currentPath && url.hash) {
                e.preventDefault();
                scrollToHashTarget(url.hash);
            }
        });
    });

    function retryInitialHashScroll() {
        if (!window.location.hash) return;

        let attempts = 0;
        const maxAttempts = 24;

        const retry = () => {
            if (!window.location.hash) return;

            attempts += 1;
            scrollToHashTarget(window.location.hash, false, 'auto');

            if (attempts < maxAttempts) {
                window.setTimeout(retry, 250);
            }
        };

        retry();
    }

    retryInitialHashScroll();
    window.addEventListener('load', retryInitialHashScroll);
    
    // ===================================
    // Scroll to Top Button
    // ===================================
    const scrollTopBtn = document.querySelector('.scroll-top');
    
    if (scrollTopBtn) {
        window.addEventListener('scroll', function() {
            if (window.pageYOffset > 500) {
                scrollTopBtn.classList.add('visible');
            } else {
                scrollTopBtn.classList.remove('visible');
            }
        });
        
        scrollTopBtn.addEventListener('click', function() {
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // ===================================
    // Intersection Observer for Animations
    // ===================================
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -100px 0px'
    };
    
    const observer = new IntersectionObserver(function(entries) {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animatedElements = document.querySelectorAll('.service-showcase-item, .why-card, .testimonial-card, .value-prop-item');
    animatedElements.forEach(el => {
        el.style.opacity = '0';
        el.style.transform = 'translateY(30px)';
        el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(el);
    });
    
    // ===================================
    // WhatsApp Click Tracking (for analytics)
    // ===================================
    const whatsappButtons = document.querySelectorAll('[href*="wa.me"], [href*="whatsapp"]');
    whatsappButtons.forEach(button => {
        button.addEventListener('click', function() {
            // Track WhatsApp click (add your analytics code here)
            console.log('WhatsApp button clicked');
            
            // You can add Google Analytics event tracking:
            // if (typeof gtag !== 'undefined') {
            //     gtag('event', 'whatsapp_click', {
            //         'event_category': 'engagement',
            //         'event_label': 'WhatsApp Contact'
            //     });
            // }
        });
    });
    
    // ===================================
    // Phone Click Tracking
    // ===================================
    const phoneLinks = document.querySelectorAll('[href^="tel:"]');
    phoneLinks.forEach(link => {
        link.addEventListener('click', function() {
            console.log('Phone link clicked');
            
            // Add analytics tracking here if needed
        });
    });
    
    // ===================================
    // Form Submission Handling (if contact form exists)
    // ===================================
    const contactForm = document.querySelector('.contact-form');
    const formMessage = document.getElementById('formMessage');
    
    if (contactForm) {
        contactForm.addEventListener('submit', async function(e) {
            e.preventDefault();
            
            // Validate required fields
            const requiredFields = this.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.style.borderColor = '#dc3545';
                } else {
                    field.style.borderColor = '';
                }
            });
            
            if (!isValid) {
                showFormMessage('Please fill in all required fields.', 'error');
                return;
            }
            
            // Show loading state
            const submitBtn = this.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.disabled = true;
            submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Sending...';
            
            // Submit form to Formspree
            try {
                const formData = new FormData(this);
                const response = await fetch(this.action, {
                    method: 'POST',
                    body: formData,
                    headers: {
                        'Accept': 'application/json'
                    }
                });
                
                if (response.ok) {
                    showFormMessage('Thank you! We\'ll respond within 24 hours.', 'success');
                    this.reset();
                    
                    // Track conversion
                    if (typeof gtag !== 'undefined') {
                        gtag('event', 'form_submission', {
                            'event_category': 'Contact',
                            'event_label': 'Contact Form'
                        });
                    }
                } else {
                    throw new Error('Form submission failed');
                }
            } catch (error) {
                showFormMessage('Something went wrong. Please try again or call us directly.', 'error');
            } finally {
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalText;
            }
        });
    }
    
    function showFormMessage(message, type) {
        if (formMessage) {
            formMessage.textContent = message;
            formMessage.className = 'form-message ' + type;
            formMessage.style.display = 'block';
            
            // Auto-hide success messages after 5 seconds
            if (type === 'success') {
                setTimeout(() => {
                    formMessage.style.display = 'none';
                }, 5000);
            }
        }
    }
    
    // ===================================
    // Social Share Functionality
    // ===================================
    window.shareOnSocial = function(platform) {
        const url = window.location.href;
        const title = document.title;
        let shareUrl = '';
        
        switch(platform) {
            case 'facebook':
                shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(url)}`;
                break;
            case 'twitter':
                shareUrl = `https://twitter.com/intent/tweet?url=${encodeURIComponent(url)}&text=${encodeURIComponent(title)}`;
                break;
            case 'linkedin':
                shareUrl = `https://www.linkedin.com/shareArticle?mini=true&url=${encodeURIComponent(url)}&title=${encodeURIComponent(title)}`;
                break;
            case 'whatsapp':
                shareUrl = `https://wa.me/?text=${encodeURIComponent(title + ' ' + url)}`;
                break;
        }
        
        if (shareUrl) {
            window.open(shareUrl, '_blank', 'width=600,height=400');
        }
    };
    
    // ===================================
    // Lazy Loading Images (improve performance)
    // ===================================
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver(function(entries) {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                        img.removeAttribute('data-src');
                        imageObserver.unobserve(img);
                    }
                }
            });
        });
        
        // Observe all images with data-src attribute
        const lazyImages = document.querySelectorAll('img[data-src]');
        lazyImages.forEach(img => imageObserver.observe(img));
    }
    
    // ===================================
    // Active Navigation Link Based on Scroll Position
    // ===================================
    const sections = document.querySelectorAll('section[id]');
    
    function highlightNavOnScroll() {
        const scrollPos = window.pageYOffset + 200;
        
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.offsetHeight;
            const sectionId = section.getAttribute('id');
            
            if (scrollPos >= sectionTop && scrollPos < sectionTop + sectionHeight) {
                document.querySelectorAll('.nav-link').forEach(link => {
                    link.classList.remove('active');
                    const linkHref = link.getAttribute('href');
                    if (linkHref === `#${sectionId}` || linkHref === `/#${sectionId}`) {
                        link.classList.add('active');
                    }
                });
            }
        });
    }
    
    window.addEventListener('scroll', highlightNavOnScroll);
    
    // ===================================
    // Testimonial Carousel Auto-rotate (if implemented)
    // ===================================
    // This is a placeholder for future testimonial carousel functionality
    
    // ===================================
    // Print Page Optimization
    // ===================================
    window.addEventListener('beforeprint', function() {
        // Expand any collapsed sections before printing
        console.log('Preparing page for printing...');
    });
    
    // ===================================
    // Accessibility: Skip to Main Content
    // ===================================
    const skipLink = document.querySelector('.skip-to-main');
    if (skipLink) {
        skipLink.addEventListener('click', function(e) {
            e.preventDefault();
            const mainContent = document.getElementById('main-content');
            if (mainContent) {
                mainContent.setAttribute('tabindex', '-1');
                mainContent.focus();
                mainContent.removeAttribute('tabindex');
            }
        });
    }
    
    // ===================================
    // FAQ Accordion - Fortune 100 Professional Implementation
    // ===================================
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    if (faqQuestions.length > 0) {
        faqQuestions.forEach(question => {
            question.addEventListener('click', function(e) {
                e.preventDefault();
                
                const faqItem = this.closest('.faq-item');
                const faqAnswer = faqItem.querySelector('.faq-answer');
                const isActive = faqItem.classList.contains('active');
                const wasExpanded = this.getAttribute('aria-expanded') === 'true';
                
                // Close all FAQ items
                document.querySelectorAll('.faq-item').forEach(item => {
                    item.classList.remove('active');
                    const btn = item.querySelector('.faq-question');
                    const answer = item.querySelector('.faq-answer');
                    btn.setAttribute('aria-expanded', 'false');
                    if (answer) {
                        answer.style.maxHeight = '0';
                    }
                });
                
                // Toggle current item (if it wasn't already open)
                if (!wasExpanded) {
                    faqItem.classList.add('active');
                    this.setAttribute('aria-expanded', 'true');
                    
                    // Set max-height to the scroll height for smooth animation
                    if (faqAnswer) {
                        faqAnswer.style.maxHeight = faqAnswer.scrollHeight + 'px';
                    }
                }
            });
            
            // Keyboard accessibility
            question.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.click();
                }
            });
        });
        
        console.log(`FAQ Accordion initialized: ${faqQuestions.length} questions`);
    }
    
    // ===================================
    // Enhanced FAQ Features (Search & Filtering)
    // ===================================
    initEnhancedFAQ();
    
    function initEnhancedFAQ() {
        const searchInput = document.getElementById('faq-search');
        const categoryFilters = document.querySelectorAll('.category-filter');
        const faqItems = document.querySelectorAll('.faq-item[data-category]');
        const faqCategories = document.querySelectorAll('.faq-category');
        
        // FAQ Search functionality
        if (searchInput) {
            searchInput.addEventListener('input', function() {
                const searchTerm = this.value.toLowerCase().trim();
                
                faqItems.forEach(item => {
                    const question = item.querySelector('.faq-question span').textContent.toLowerCase();
                    const answer = item.querySelector('.faq-answer').textContent.toLowerCase();
                    const matches = question.includes(searchTerm) || answer.includes(searchTerm);
                    
                    if (searchTerm === '' || matches) {
                        item.classList.remove('hidden');
                    } else {
                        item.classList.add('hidden');
                        // Close the item if it's open and being hidden
                        item.classList.remove('active');
                        const btn = item.querySelector('.faq-question');
                        const answer = item.querySelector('.faq-answer');
                        btn.setAttribute('aria-expanded', 'false');
                        if (answer) {
                            answer.style.maxHeight = '0';
                        }
                    }
                });
                
                // Show/hide category headers based on visible items
                faqCategories.forEach(category => {
                    const categoryItems = category.querySelectorAll('.faq-item:not(.hidden)');
                    if (categoryItems.length === 0) {
                        category.style.display = 'none';
                    } else {
                        category.style.display = 'block';
                    }
                });
                
                // Track search usage
                if (searchTerm.length >= 3) {
                    gtag('event', 'faq_search', {
                        event_category: 'FAQ',
                        event_label: searchTerm,
                        search_term: searchTerm
                    });
                }
            });
        }
        
        // FAQ Category filtering
        if (categoryFilters.length > 0) {
            categoryFilters.forEach(filter => {
                filter.addEventListener('click', function() {
                    const selectedCategory = this.getAttribute('data-category');
                    
                    // Update active filter
                    categoryFilters.forEach(f => f.classList.remove('active'));
                    this.classList.add('active');
                    
                    // Clear search when switching categories
                    if (searchInput) {
                        searchInput.value = '';
                    }
                    
                    // Show/hide items and categories based on selection
                    if (selectedCategory === 'all') {
                        faqItems.forEach(item => item.classList.remove('hidden'));
                        faqCategories.forEach(category => category.style.display = 'block');
                    } else {
                        faqItems.forEach(item => {
                            if (item.getAttribute('data-category') === selectedCategory) {
                                item.classList.remove('hidden');
                            } else {
                                item.classList.add('hidden');
                                // Close the item if it's open and being hidden
                                item.classList.remove('active');
                                const btn = item.querySelector('.faq-question');
                                const answer = item.querySelector('.faq-answer');
                                btn.setAttribute('aria-expanded', 'false');
                                if (answer) {
                                    answer.style.maxHeight = '0';
                                }
                            }
                        });
                        
                        faqCategories.forEach(category => {
                            const categoryKey = category.getAttribute('data-category');
                            if (categoryKey === selectedCategory) {
                                category.style.display = 'block';
                            } else {
                                category.style.display = 'none';
                            }
                        });
                    }
                    
                    // Track category selection
                    gtag('event', 'faq_category_filter', {
                        event_category: 'FAQ',
                        event_label: selectedCategory,
                        category_selected: selectedCategory
                    });
                });
            });
        }
        
        // Track FAQ engagement
        faqItems.forEach(item => {
            const question = item.querySelector('.faq-question');
            if (question) {
                question.addEventListener('click', function() {
                    const questionText = this.querySelector('span').textContent;
                    const category = item.getAttribute('data-category');
                    
                    gtag('event', 'faq_question_click', {
                        event_category: 'FAQ',
                        event_label: questionText,
                        question_text: questionText,
                        faq_category: category
                    });
                });
            }
        });
        
        console.log(`Enhanced FAQ initialized: ${faqItems.length} items with search and filtering`);
    }
    
    // ===================================
    // Service Page Price Calculator (if on services page)
    // ===================================
    // This can be expanded for a pricing calculator
    
    console.log('Legacy Defenders website loaded successfully!');
});

// ===================================
// Utility Functions
// ===================================

// Format phone number for display
function formatPhoneNumber(phoneNumber) {
    const cleaned = ('' + phoneNumber).replace(/\D/g, '');
    const match = cleaned.match(/^1?(\d{3})(\d{3})(\d{4})$/);
    if (match) {
        return '(' + match[1] + ') ' + match[2] + '-' + match[3];
    }
    return phoneNumber;
}

// Check if element is in viewport
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

// Debounce function for performance
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// ===================================
// Analytics Tracking Helper Functions
// ===================================

// Track CTA button clicks with enhanced data
function trackCTAClick(ctaType, section, ctaText, destination) {
    gtag('event', 'cta_click', {
        event_category: 'CTA',
        event_label: ctaType,
        cta_type: ctaType,
        section: section,
        cta_text: ctaText,
        destination: destination,
        value: CONVERSION_VALUES[ctaType] || 1
    });
}

// Track service interest with psychological context
function trackServiceInterest(serviceName, interactionType, psychology = null) {
    gtag('event', 'service_interest', {
        event_category: 'Services',
        event_label: serviceName,
        service_name: serviceName,
        interaction_type: interactionType,
        psychological_appeal: psychology,
        value: CONVERSION_VALUES.service_interest || 1
    });
    
    // Track psychological optimization effectiveness
    if (psychology) {
        gtag('event', 'psychological_element_interaction', {
            event_category: 'Psychology',
            event_label: psychology,
            element_type: 'service',
            service_name: serviceName,
            interaction_type: interactionType
        });
    }
}

// Track package interest with psychological context
function trackPackageInterest(packageName, interactionType, psychology = null) {
    gtag('event', 'package_interest', {
        event_category: 'Packages',
        event_label: packageName,
        package_name: packageName,
        interaction_type: interactionType,
        psychological_appeal: psychology,
        value: CONVERSION_VALUES.package_interest || 3
    });
    
    // Track psychological optimization effectiveness
    if (psychology) {
        gtag('event', 'psychological_element_interaction', {
            event_category: 'Psychology',
            event_label: psychology,
            element_type: 'package',
            package_name: packageName,
            interaction_type: interactionType
        });
    }
    
    // Track choice architecture effectiveness
    trackChoiceArchitecture(packageName, psychology);
}

// Track journey progression through phases
function trackJourneyProgression(fromPhase, toPhase) {
    gtag('event', 'journey_progression', {
        event_category: 'Journey',
        event_label: `${fromPhase}_to_${toPhase}`,
        from_phase: fromPhase,
        to_phase: toPhase,
        value: CONVERSION_VALUES.journey_progression || 2
    });
}

// Track choice architecture effectiveness (Rule of 3, Goldilocks Effect, Decoy Effect)
function trackChoiceArchitecture(choice, psychology) {
    const architectureType = getArchitectureType(choice, psychology);
    
    gtag('event', 'choice_architecture', {
        event_category: 'Psychology',
        event_label: architectureType,
        choice_made: choice,
        psychological_appeal: psychology,
        architecture_type: architectureType
    });
}

// Determine which psychological principle was triggered
function getArchitectureType(choice, psychology) {
    if (psychology && psychology.includes('Most Popular')) {
        return 'goldilocks_effect';
    } else if (psychology && psychology.includes('Decoy')) {
        return 'decoy_effect';
    } else if (psychology && psychology.includes('Entry')) {
        return 'entry_point';
    }
    return 'rule_of_three';
}

// Track A/B test performance for psychological optimization
function trackPsychologicalOptimization() {
    gtag('event', 'ab_test_exposure', {
        event_category: 'A/B Testing',
        event_label: 'journey_based_3_services',
        test_variation: 'psychological_3_services',
        service_count: 3,
        package_count: 3,
        psychological_principles: 'rule_of_three,goldilocks_effect,decoy_effect'
    });
}

// Initialize psychological optimization tracking on page load
document.addEventListener('DOMContentLoaded', function() {
    trackPsychologicalOptimization();
});

