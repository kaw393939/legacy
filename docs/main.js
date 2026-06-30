/* Legacy Defenders runtime */
import { ready } from './modules/dom.js';
import { initDeferredFontAwesome, initLazyImages, initSkipLink } from './modules/assets.js';
import { initAnalytics } from './modules/analytics.js';
import { initContactContext, initContactFloatState } from './modules/contact.js';
import { initFAQ } from './modules/faq.js';
import { initMobileMenu, initScrollState, initSmoothScroll } from './modules/navigation.js';
import { initPrintActions, initPrintPrep } from './modules/print.js';

ready(() => {
    initDeferredFontAwesome();
    initAnalytics();
    initMobileMenu();
    initSmoothScroll();
    initScrollState();
    initContactFloatState();
    initContactContext();
    initLazyImages();
    initSkipLink();
    initFAQ();
    initPrintActions();
    initPrintPrep();
});
