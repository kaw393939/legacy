import { $, $$, closest, doc, on, textOf, win } from './dom.js';
import { analyticsEnabled, track } from './analytics.js';

export function initFAQ() {
    const items = $$('.faq-item');
    if (!items.length) return;

    const searchInput = $('#faq-search');
    const filters = $$('.category-filter');
    const categories = $$('.faq-category');
    const noResults = $('.faq-no-results');
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

    function updateOpenHeights() {
        itemData.forEach((data) => {
            if (data.item.classList.contains('active') && data.answer) {
                data.answer.style.maxHeight = `${data.answer.scrollHeight}px`;
            }
        });
    }

    function dataForItem(item) {
        return itemData.find((data) => data.item === item);
    }

    function applyFilters() {
        let visibleCount = 0;

        itemData.forEach((data) => {
            const categoryMatch = selectedCategory === 'all' || data.category === selectedCategory;
            const searchMatch = !searchTerm || data.text.includes(searchTerm);
            const visible = categoryMatch && searchMatch;

            data.item.classList.toggle('hidden', !visible);
            if (!visible) closeItem(data);
            if (visible) visibleCount += 1;
        });

        categories.forEach((category) => {
            const hasVisibleItems = Boolean($('.faq-item:not(.hidden)', category));
            category.style.display = hasVisibleItems ? 'block' : 'none';
        });

        if (noResults) noResults.classList.toggle('hidden', visibleCount > 0);
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

    on(win, 'resize', updateOpenHeights, { passive: true });
}
