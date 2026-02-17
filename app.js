/**
 * AI News Dashboard - Application Logic
 * Loads and displays articles from scraped data
 */

(function () {
    // State
    let allArticles = [];
    let savedArticles = [];
    let currentFilter = 'all';
    let searchQuery = '';

    const loadingText = document.getElementById('loading-text');
    const debugLog = document.getElementById('debug-log');

    function log(msg) {
        console.log(msg);
        if (debugLog) {
            debugLog.innerHTML += `<div>${msg}</div>`;
        }
    }

    // DOM Elements
    const articlesGrid = document.getElementById('articles-grid');
    const totalCountEl = document.getElementById('total-count');
    const newCountEl = document.getElementById('new-count');
    const lastUpdatedEl = document.getElementById('last-updated');
    const filterBtns = document.querySelectorAll('.filter-btn');
    const searchInput = document.getElementById('search-input');

    /**
     * Initialize the dashboard
     */
    const supabaseUrl = 'https://lxqrvnvbhqwmqhngpyel.supabase.co';
    const supabaseKey = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imx4cXJ2bnZiaHF3bXFobmdweWVsIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzEzMjk1MTcsImV4cCI6MjA4NjkwNTUxN30.Yq-rb3atJcrRTalkhs0znsRkEGpTPqWt4PQ7n_s2L-k';
    let supabaseClient;

    /**
     * Initialize the dashboard
     */
    async function init() {
        try {
            log('Starting initialization...');

            // Check if Supabase client loaded
            // @ts-ignore
            if (!window.supabase) {
                throw new Error('Supabase library not found in window. Check CDN.');
            }
            log('Supabase library found.');

            // Initialize Supabase
            // @ts-ignore
            supabaseClient = window.supabase.createClient(supabaseUrl, supabaseKey);
            log('Supabase client created.');

            // Load saved articles from localStorage
            loadSavedArticles();
            log('Saved articles loaded.');

            // Fetch articles from Supabase
            log('Fetching articles from DB...');
            const { data, error } = await supabaseClient
                .from('articles')
                .select('*')
                .order('published_date', { ascending: false, nullsFirst: false });

            if (error) {
                log('Supabase error: ' + JSON.stringify(error));
                throw error;
            }

            log(`Fetched ${data ? data.length : 0} articles.`);

            allArticles = data || [];

            // Process articles (calculate new/saved status)
            processArticles();

            // Update stats
            updateStats();

            // Render articles
            renderArticles();

            // Setup interactions
            setupFilters();
            setupSearch();

        } catch (error) {
            console.error('Error loading articles:', error);
            if (loadingText) {
                loadingText.textContent = '⚠️ Error: ' + error.message;
                loadingText.style.color = '#ff6b6b';
            }
            log('Stack: ' + error.stack);
        }
    }

    /**
     * Process articles adding computed fields
     */
    function processArticles() {
        const now = new Date();
        const cutoff = new Date(now.getTime() - (24 * 60 * 60 * 1000));

        allArticles.forEach(article => {
            // Restore saved state
            if (savedArticles.includes(article.id)) {
                article.is_saved = true;
            }

            // Calculate is_new
            if (article.published_date) {
                const pubDate = new Date(article.published_date);
                article.is_new = pubDate >= cutoff;
            } else {
                article.is_new = false;
            }
        });
    }

    /**
     * Load saved articles from LocalStorage
     */
    function loadSavedArticles() {
        const saved = localStorage.getItem('savedArticles');
        if (saved) {
            try {
                savedArticles = JSON.parse(saved);
            } catch (e) {
                console.error('Error parsing saved articles', e);
                savedArticles = [];
            }
        }
    }

    /**
     * Save current savedArticles to LocalStorage
     */
    function persistSavedArticles() {
        localStorage.setItem('savedArticles', JSON.stringify(savedArticles));
    }

    /**
     * Merge saved state with fetched articles
     */
    function mergeSavedState() {
        allArticles.forEach(article => {
            if (savedArticles.includes(article.id)) {
                article.is_saved = true;
            }
        });
    }

    /**
     * Toggle save state of an article
     */
    function toggleSave(articleId, btn) {
        const index = savedArticles.indexOf(articleId);
        const article = allArticles.find(a => a.id === articleId);

        if (index === -1) {
            // Save
            savedArticles.push(articleId);
            if (article) article.is_saved = true;
            btn.classList.add('saved');
            btn.innerHTML = getHeartIcon(true);
        } else {
            // Unsave
            savedArticles.splice(index, 1);
            if (article) article.is_saved = false;
            btn.classList.remove('saved');
            btn.innerHTML = getHeartIcon(false);

            // If currently viewing saved filter, remove card
            if (currentFilter === 'saved') {
                const card = btn.closest('.article-card');
                card.style.opacity = '0';
                card.style.transform = 'scale(0.9)';
                setTimeout(() => renderArticles(), 300);
            }
        }

        persistSavedArticles();
        // Update stats logic could go here if we tracked saved count dynamically
    }

    function getHeartIcon(filled) {
        return filled
            ? '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>'
            : '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>';
    }

    /**
     * Update statistics in header
     */
    /**
     * Update statistics in header
     */
    function updateStats() {
        totalCountEl.textContent = allArticles.length;

        const newCount = allArticles.filter(a => a.is_new).length;
        newCountEl.textContent = newCount;

        // Find most recent scrape time for "Last Updated"
        if (allArticles.length > 0) {
            const dates = allArticles
                .map(a => a.scraped_at)
                .filter(d => d)
                .sort()
                .reverse();

            if (dates.length > 0) {
                const date = new Date(dates[0]);
                lastUpdatedEl.textContent = date.toLocaleString();
            }
        }
    }

    /**
     * Setup filter button event listeners
     */
    function setupFilters() {
        filterBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                // Update active state
                filterBtns.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');

                // Update filter and re-render
                currentFilter = btn.dataset.filter;
                renderArticles();
            });
        });
    }

    /**
     * Setup search input
     */
    function setupSearch() {
        searchInput.addEventListener('input', (e) => {
            searchQuery = e.target.value.toLowerCase().trim();
            renderArticles();
        });
    }

    /**
     * Render articles based on current filter and search
     */
    function renderArticles() {
        // Filter articles
        let filteredArticles = allArticles;

        // Apply Category Filter
        if (currentFilter === 'saved') {
            filteredArticles = allArticles.filter(article => savedArticles.includes(article.id));
        } else if (currentFilter !== 'all') {
            filteredArticles = allArticles.filter(article => article.source === currentFilter);
        }

        // Apply Search
        if (searchQuery) {
            filteredArticles = filteredArticles.filter(article =>
                (article.title && article.title.toLowerCase().includes(searchQuery)) ||
                (article.summary && article.summary.toLowerCase().includes(searchQuery))
            );
        }

        // Clear grid
        articlesGrid.innerHTML = '';

        // Show empty state if no articles
        if (filteredArticles.length === 0) {
            showEmptyState();
            return;
        }

        // Render each article
        filteredArticles.forEach((article, index) => {
            const card = createArticleCard(article);
            articlesGrid.appendChild(card);

            // Stagger animation
            setTimeout(() => {
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 50);
        });
    }

    /**
     * Create article card element
     */
    function createArticleCard(article) {
        const card = document.createElement('div');
        card.className = 'article-card';
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';

        // Source badge class
        const sourceClass = article.source === 'bens_bites' ? 'bens-bites' : 'ai-rundown';
        const sourceName = article.source === 'bens_bites' ? "Ben's Bites" : 'AI Rundown';

        // Check saved state
        const isSaved = savedArticles.includes(article.id);

        // Format date
        let dateStr = 'Date unknown';
        if (article.published_date) {
            try {
                const date = new Date(article.published_date);
                dateStr = date.toLocaleDateString('en-US', {
                    month: 'short',
                    day: 'numeric',
                    year: 'numeric'
                });
            } catch (e) {
                console.error('Error parsing date:', e);
            }
        }

        // Build card HTML
        card.innerHTML = `
        <div class="article-actions">
            <button class="save-btn ${isSaved ? 'saved' : ''}" title="${isSaved ? 'Unsave' : 'Save'}">
                ${getHeartIcon(isSaved)}
            </button>
        </div>
        <div class="article-header">
            <span class="source-badge ${sourceClass}">${sourceName}</span>
            ${article.is_new ? '<span class="new-badge">NEW</span>' : ''}
        </div>
        <h3 class="article-title">${escapeHtml(article.title)}</h3>
        ${article.summary ? `<p class="article-summary">${escapeHtml(article.summary)}</p>` : ''}
        <div class="article-footer">
            <span class="article-date">${dateStr}</span>
            <a href="${article.url}" target="_blank" rel="noopener" class="read-more">Read More →</a>
        </div>
    `;

        // Handle Save Click
        const saveBtn = card.querySelector('.save-btn');
        saveBtn.addEventListener('click', (e) => {
            e.stopPropagation(); // Prevent card click
            toggleSave(article.id, saveBtn);
        });

        // Make entire card clickable
        card.addEventListener('click', (e) => {
            // Don't trigger if clicking the "Read More" link or save button
            if (e.target.classList.contains('read-more') || e.target.closest('.save-btn')) return;
            window.open(article.url, '_blank', 'noopener');
        });

        return card;
    }

    /**
     * Show empty state
     */
    function showEmptyState() {
        articlesGrid.innerHTML = `
        <div class="empty-state">
            <h2>No articles found</h2>
            <p>Try selecting a different filter or run the scrapers to fetch new articles.</p>
        </div>
    `;
    }

    /**
     * Show error message
     */
    function showError(message) {
        articlesGrid.innerHTML = `
        <div class="empty-state">
            <h2>⚠️ Error</h2>
            <p>${escapeHtml(message)}</p>
            <p style="margin-top: 16px;">
                <strong>To get started:</strong><br>
                1. Install dependencies: <code>pip install -r requirements.txt</code><br>
                2. Run scrapers: <code>python run_scrapers.py</code><br>
                3. Refresh this page
            </p>
        </div>
    `;
    }

    /**
     * Escape HTML to prevent XSS
     */
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Initialize on page load
    document.addEventListener('DOMContentLoaded', init);

})();
