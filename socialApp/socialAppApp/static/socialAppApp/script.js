/*
script.js file

-Handles homepage interactivity
-Reads posts from Django template JSON (replaces hardcoded sample data)
-Dynamically renders post cards into the feed
-Handles upvote/downvote, hot/new/top sort buttons
-Handles community filter dropdown
*/

// Read posts injected by Django's json_script filter
const dbPostsEl = document.getElementById('db-posts-data');
let allPosts = dbPostsEl ? JSON.parse(dbPostsEl.textContent) : [];

//Render Posts
function renderPosts(postList) {
    const feed = document.getElementById('postsFeed');
    feed.innerHTML = '';

    if (postList.length === 0) {
        feed.innerHTML = `
            <div class="text-center py-5 text-muted">
                <i class="bi bi-inbox" style="font-size:2rem;"></i>
                <p class="mt-2">No posts found.</p>
            </div>`;
        return;
    }

    postList.forEach(post => {
        const card = document.createElement('div');
        card.className = 'post-card';
        card.innerHTML = `
            <div class="vote-col">
                <button class="vote-btn upvote" data-id="${post.id}">
                    <i class="bi bi-arrow-up-circle"></i>
                </button>
                <span class="vote-count" id="votes-${post.id}">${post.votes}</span>
                <button class="vote-btn downvote" data-id="${post.id}">
                    <i class="bi bi-arrow-down-circle"></i>
                </button>
            </div>
            <div class="post-content">
                <div class="post-meta">
                    <span class="community-badge">
                        <i class="bi bi-people-fill"></i> ${post.community}
                    </span>
                    <span class="category-badge cat-${post.category}">${post.categoryLabel}</span>
                    <span class="post-author">Posted by ${post.author} · ${post.time}</span>
                </div>
                <div class="post-title">${post.title}</div>
                <div class="post-excerpt">${post.excerpt}</div>
                <div class="post-footer">
                    <button class="post-action">
                        <i class="bi bi-chat-left-text"></i> ${post.comments} Comments
                    </button>
                    <button class="post-action">
                        <i class="bi bi-bookmark"></i> Save
                    </button>
                </div>
            </div>
        `;
        feed.appendChild(card);
    });

    // Local vote listeners (persistence added in a later commit)
    document.querySelectorAll('.vote-btn.upvote').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = parseInt(btn.dataset.id);
            const post = allPosts.find(p => p.id === id);
            if (post) {
                post.votes++;
                document.getElementById(`votes-${id}`).textContent = post.votes;
            }
        });
    });

    document.querySelectorAll('.vote-btn.downvote').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = parseInt(btn.dataset.id);
            const post = allPosts.find(p => p.id === id);
            if (post) {
                post.votes--;
                document.getElementById(`votes-${id}`).textContent = post.votes;
            }
        });
    });
}

//Sort Buttons
document.querySelectorAll('.btn-sort').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-sort').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        const now = Date.now();

        function hotScore(post) {
            const ageHours = (now - new Date(post.timestamp).getTime()) / 3_600_000;
            return post.votes / Math.pow(ageHours + 2, 1.5);
        }

        let sorted = [...allPosts];
        if (btn.dataset.sort === 'hot') {
            sorted.sort((a, b) => hotScore(b) - hotScore(a));
        } else if (btn.dataset.sort === 'new') {
            sorted.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        } else if (btn.dataset.sort === 'top') {
            sorted.sort((a, b) => b.votes - a.votes);
        }
        renderPosts(sorted);
    });
});

//Community Filter
const communityFilterEl = document.getElementById('communityFilter');
if (communityFilterEl) {
    communityFilterEl.addEventListener('change', (e) => {
        const val = e.target.value;
        const filtered = val === 'all' ? allPosts : allPosts.filter(p => p.communityKey === val);
        renderPosts(filtered);
    });
}

//Todo List Button
document.getElementById('todoBtn').addEventListener('click', () => {
    alert('Todo List section coming soon!');
});

//Initial Render
document.addEventListener('DOMContentLoaded', () => {
    renderPosts(allPosts);
});
