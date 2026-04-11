/*
script.js file 

-Handles homepage interactivity
-Contains sample post data (which will be replace with a database later)
-Dynamically renders post cards into the feed
-Handles upvote/downvote, hot/new/top sort buttons
-handles community filter dropdown 
*/

//Sample Post Data
const posts = [
    {
        id: 1,
        community: 'Computer Science',
        communityKey: 'cs',
        category: 'internship',
        categoryLabel: 'Internship',
        author: 'u/dev_student',
        time: '2 hours ago',
        title: 'Just landed a summer internship at a FAANG company — here\'s what helped me',
        excerpt: 'After 6 months of grinding LeetCode and doing mock interviews, I finally got the offer. Happy to share what resources I used and what the process looked like.',
        votes: 142,
        comments: 38
    },
    {
        id: 2,
        community: 'Business',
        communityKey: 'business',
        category: 'event',
        categoryLabel: 'Event',
        author: 'u/biz_connect',
        time: '4 hours ago',
        title: 'Career Fair this Thursday — Booth list + tips for first-timers',
        excerpt: 'Over 40 companies will be there including some consulting firms and finance roles. Bring multiple copies of your resume and wear business casual at minimum.',
        votes: 89,
        comments: 21
    },
    {
        id: 3,
        community: 'Engineering',
        communityKey: 'engineering',
        category: 'rating',
        categoryLabel: 'Prof Rating',
        author: 'u/mech_senior',
        time: '5 hours ago',
        title: 'Honest review of Prof. Martinez for Thermodynamics 301',
        excerpt: 'His lectures are dense but incredibly well-organized. The exams are hard but fair — highly recommend going to office hours at least twice before each midterm.',
        votes: 67,
        comments: 14
    },
    {
        id: 4,
        community: 'Biology',
        communityKey: 'biology',
        category: 'question',
        categoryLabel: 'Question',
        author: 'u/bio_junior',
        time: '1 hour ago',
        title: 'Anyone have good notes for Cell Bio midterm next week?',
        excerpt: 'Specifically looking for help on the membrane transport and signal transduction chapters. Would be happy to trade my genetics notes in return.',
        votes: 34,
        comments: 9
    },
    {
        id: 5,
        community: 'Computer Science',
        communityKey: 'cs',
        category: 'question',
        categoryLabel: 'Question',
        author: 'u/cs_freshman',
        time: '30 minutes ago',
        title: 'How do you all manage deadlines across multiple classes?',
        excerpt: 'This semester I have 5 classes and I keep missing small assignments. Looking for any system or app that has actually worked for you.',
        votes: 55,
        comments: 27
    }
];

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
                        <i class="bi bi-share"></i> Share
                    </button>
                    <button class="post-action">
                        <i class="bi bi-bookmark"></i> Save
                    </button>
                </div>
            </div>
        `;
        feed.appendChild(card);
    });

    //Attach vote listeners
    document.querySelectorAll('.vote-btn.upvote').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = parseInt(btn.dataset.id);
            const post = posts.find(p => p.id === id);
            post.votes++;
            document.getElementById(`votes-${id}`).textContent = post.votes;
        });
    });

    document.querySelectorAll('.vote-btn.downvote').forEach(btn => {
        btn.addEventListener('click', () => {
            const id = parseInt(btn.dataset.id);
            const post = posts.find(p => p.id === id);
            post.votes--;
            document.getElementById(`votes-${id}`).textContent = post.votes;
        });
    });
}

//Sort Buttons
document.querySelectorAll('.btn-sort').forEach(btn => {
    btn.addEventListener('click', () => {
        document.querySelectorAll('.btn-sort').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');

        let sorted = [...posts];
        if (btn.dataset.sort === 'new') {
            sorted = sorted.reverse();
        } else if (btn.dataset.sort === 'top') {
            sorted = sorted.sort((a, b) => b.votes - a.votes);
        }
        renderPosts(sorted);
    });
});

//Community Filter
document.getElementById('communityFilter').addEventListener('change', (e) => {
    const val = e.target.value;
    const filtered = val === 'all' ? posts : posts.filter(p => p.communityKey === val);
    renderPosts(filtered);
});

//Create Post Button
document.getElementById('createPostBtn').addEventListener('click', () => {
    alert('Create Post coming soon!');
});

//Todo List Button
document.getElementById('todoBtn').addEventListener('click', () => {
    alert('Todo List section coming soon!');
});

//Initial Render
document.addEventListener('DOMContentLoaded', () => {
    renderPosts(posts);
});
