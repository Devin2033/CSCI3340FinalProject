/*
script.js file

-Handles homepage interactivity
-Reads posts from Django template JSON
-Dynamically renders post cards into the feed
-Handles upvote/downvote with backend persistence and debounce
-Handles save/unsave with backend persistence
-Handles hot/new/top sort buttons
-Handles community filter dropdown
*/

const dbPostsEl = document.getElementById('db-posts-data');
let allPosts = dbPostsEl ? JSON.parse(dbPostsEl.textContent) : [];

function getCsrfToken() {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : '';
}

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
        const bookmarkIcon = post.saved ? 'bi-bookmark-fill' : 'bi-bookmark';
        const saveLabel    = post.saved ? 'Saved' : 'Save';
        const upActive     = post.voted === 'up'   ? 'voted-up'   : '';
        const downActive   = post.voted === 'down' ? 'voted-down' : '';
        const titleHtml = post.detailUrl
            ? `<a href="${post.detailUrl}" class="post-title-link">${post.title}</a>`
            : `<div class="post-title">${post.title}</div>`;
        card.innerHTML = `
            <div class="vote-col">
                <button class="vote-btn upvote ${upActive}" data-id="${post.id}">
                    <i class="bi bi-arrow-up-circle${post.voted === 'up' ? '-fill' : ''}"></i>
                </button>
                <span class="vote-count" id="votes-${post.id}">${post.votes}</span>
                <button class="vote-btn downvote ${downActive}" data-id="${post.id}">
                    <i class="bi bi-arrow-down-circle${post.voted === 'down' ? '-fill' : ''}"></i>
                </button>
            </div>
            <div class="post-content">
                <div class="post-meta">
                    <span class="community-badge">
                        <i class="bi bi-people-fill"></i> ${post.community}
                    </span>
                    <span class="category-badge cat-${post.category}">${post.categoryLabel}</span>
                    <span class="post-author">Posted by ${post.author} · ${post.time}${post.edited ? ' · <em>edited</em>' : ''}</span>
                </div>
                <div class="post-title">${titleHtml}</div>
                <div class="post-excerpt">${post.excerpt}</div>
                <div class="post-footer">
                    <a href="${post.detailUrl || '#'}" class="post-action text-decoration-none">
                        <i class="bi bi-chat-left-text"></i> ${post.comments} Comments
                    </a>
                    <button class="post-action save-btn" data-id="${post.id}">
                        <i class="bi ${bookmarkIcon}"></i> ${saveLabel}
                    </button>
                    ${post.author === currentUsername ? `
                    <span class="your-post-badge">Your post</span>
                    <button class="post-action text-danger delete-post-btn" data-id="${post.id}">
                        <i class="bi bi-trash"></i> Delete
                    </button>` : ''}
                </div>
            </div>
        `;
        feed.appendChild(card);
    });

    //Save listeners
    document.querySelectorAll('.save-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            const id   = btn.dataset.id;
            const post = allPosts.find(p => String(p.id) === id);
            const res  = await fetch(`/post/${id}/save/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() },
            });
            const data = await res.json();
            if (post) post.saved = data.saved;
            const icon = btn.querySelector('i');
            icon.className = `bi ${data.saved ? 'bi-bookmark-fill' : 'bi-bookmark'}`;
            btn.childNodes[btn.childNodes.length - 1].textContent = ` ${data.saved ? 'Saved' : 'Save'}`;
        });
    });

    //Vote listeners with debounce
    async function handleVote(btn, direction) {
        const id      = btn.dataset.id;
        const post    = allPosts.find(p => String(p.id) === id);
        const card    = btn.closest('.post-card');
        const upBtn   = card.querySelector('.vote-btn.upvote');
        const downBtn = card.querySelector('.vote-btn.downvote');

        upBtn.disabled   = true;
        downBtn.disabled = true;

        try {
            const res = await fetch(`/post/${id}/vote/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCsrfToken(),
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: `direction=${direction}`,
            });
            const data = await res.json();
            if (post) post.voted = data.voted;

            document.getElementById(`votes-${id}`).textContent = data.votes;

            upBtn.classList.toggle('voted-up', data.voted === 'up');
            upBtn.querySelector('i').className = `bi bi-arrow-up-circle${data.voted === 'up' ? '-fill' : ''}`;
            downBtn.classList.toggle('voted-down', data.voted === 'down');
            downBtn.querySelector('i').className = `bi bi-arrow-down-circle${data.voted === 'down' ? '-fill' : ''}`;
        } finally {
            upBtn.disabled   = false;
            downBtn.disabled = false;
        }
    }

    document.querySelectorAll('.vote-btn.upvote').forEach(btn => {
        btn.addEventListener('click', () => handleVote(btn, 'up'));
    });
    document.querySelectorAll('.vote-btn.downvote').forEach(btn => {
        btn.addEventListener('click', () => handleVote(btn, 'down'));
    });

    document.querySelectorAll('.delete-post-btn').forEach(btn => {
        btn.addEventListener('click', async () => {
            if (!confirm('Are you sure you want to delete this post? This cannot be undone.')) return;
            const id  = btn.dataset.id;
            const res = await fetch(`/post/${id}/delete/`, {
                method: 'POST',
                headers: { 'X-CSRFToken': getCsrfToken() },
            });
            if (res.ok) {
                btn.closest('.post-card').remove();
                allPosts = allPosts.filter(p => String(p.id) !== id);
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
        const val      = e.target.value;
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
