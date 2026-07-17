from flask import Flask, render_template, redirect, url_for, flash, request, jsonify
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from config import Config
from models import db, User, Book, Review
from forms import RegisterForm, LoginForm, ReviewForm
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Seed Data ───────────────────────────────────────────────────────────────

def seed_database():
    if User.query.first() is not None:
        return

    users_data = [
        {'username': 'rahim', 'email': 'rahim@example.com', 'password': 'password123'},
        {'username': 'karim', 'email': 'karim@example.com', 'password': 'password123'},
        {'username': 'sumaiya', 'email': 'sumaiya@example.com', 'password': 'password123'},
    ]
    users = []
    for u in users_data:
        user = User(
            username=u['username'],
            email=u['email'],
            password=generate_password_hash(u['password']),
            joined_date=datetime(2024, 1, 15)
        )
        db.session.add(user)
        users.append(user)
    db.session.commit()

    books_data = [
        {
            'title': 'The Alchemist',
            'author': 'Paulo Coelho',
            'genre': 'Fiction',
            'description': 'The Alchemist is a mystical story about an Andalusian shepherd boy named Santiago who yearns to travel in search of a worldly treasure. His quest will lead him to riches far different — and far more satisfying — than he ever imagined. Santiago\'s journey teaches us about the essential wisdom of listening to our hearts, learning to read the omens strewn along life\'s path, and above all, following our dreams.',
            'cover_image': 'https://images.unsplash.com/photo-1544947950-fa07a98d237f?w=400&h=600&fit=crop'
        },
        {
            'title': '1984',
            'author': 'George Orwell',
            'genre': 'Dystopian',
            'description': 'Among the seminal texts of the 20th century, Nineteen Eighty-Four is a rare work that grows more haunting as its dystopian proscriptions have become combatably combated reality. Published in 1949, the book offers political satirist George Orwell\'s terrifying vision of a totalitarian future in which everything and everyone is slave to a tyrannical regime led by Big Brother.',
            'cover_image': 'https://images.unsplash.com/photo-1543002588-bfa74002ed7e?w=400&h=600&fit=crop'
        },
        {
            'title': 'To Kill a Mockingbird',
            'author': 'Harper Lee',
            'genre': 'Classic',
            'description': 'A gripping, heart-wrenching, and wholly remarkable tale of coming-of-age in a South poisoned by virulent prejudice. It views a world of great beauty and savage inequities through the eyes of a young girl, as her father — a crusading local lawyer — risks everything to defend a Black man falsely accused of a terrible crime.',
            'cover_image': 'https://images.unsplash.com/photo-1497633762265-9d179a990aa6?w=400&h=600&fit=crop'
        },
        {
            'title': 'The Great Gatsby',
            'author': 'F. Scott Fitzgerald',
            'genre': 'Classic',
            'description': 'The Great Gatsby, F. Scott Fitzgerald\'s third book, stands as the supreme achievement of his career. This exemplary novel of the Jazz Age has been acclaimed by generations of readers. The story of the mysteriously wealthy Jay Gatsby and his love for the beautiful Daisy Buchanan is an exquisitely crafted tale of America in the 1920s.',
            'cover_image': 'https://images.unsplash.com/photo-1476275466078-4007374efbbe?w=400&h=600&fit=crop'
        },
        {
            'title': 'Sapiens: A Brief History of Humankind',
            'author': 'Yuval Noah Harari',
            'genre': 'Non-Fiction',
            'description': 'In Sapiens, Dr. Yuval Noah Harari spans the whole of human history, from the very first humans to walk the earth to the radical — and sometimes devastating — breakthroughs of the Cognitive, Agricultural, and Scientific Revolutions. Drawing on insights from biology, anthropology, paleontology, and economics, he explores how the currents of history have shaped our human societies.',
            'cover_image': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=400&h=600&fit=crop'
        },
        {
            'title': 'Dune',
            'author': 'Frank Herbert',
            'genre': 'Science Fiction',
            'description': 'Set on the desert planet Arrakis, Dune is the story of the boy Paul Atreides, heir to a noble family tasked with ruling an inhospitable world where the only thing of value is the spice melange — a drug capable of extending life and expanding consciousness. Coveted across the known universe, melange is a prize worth killing for.',
            'cover_image': 'https://images.unsplash.com/photo-1618666012174-83b441c0bc76?w=400&h=600&fit=crop'
        },
        {
            'title': 'The Catcher in the Rye',
            'author': 'J.D. Salinger',
            'genre': 'Fiction',
            'description': 'The hero-narrator of The Catcher in the Rye is an ancient child of sixteen, a native New Yorker named Holden Caulfield. Through circumstances that tend to preclude adult, secondhand description, he leaves his prep school in Pennsylvania and goes underground in New York City for three days.',
            'cover_image': 'https://images.unsplash.com/photo-1524995997946-a1c2e315a42f?w=400&h=600&fit=crop'
        },
        {
            'title': 'Brave New World',
            'author': 'Aldous Huxley',
            'genre': 'Dystopian',
            'description': 'Aldous Huxley\'s profoundly important dystopian novel depicts a future society that is both chillingly prescient and deeply entertaining. Citizens are engineered through artificial wombs and childhood indoctrination into predetermined classes. A powerful work of speculative fiction that has riveted the attention of generations of readers.',
            'cover_image': 'https://images.unsplash.com/photo-1509021436665-8f07dbf5bf1d?w=400&h=600&fit=crop'
        },
        {
            'title': 'The Hobbit',
            'author': 'J.R.R. Tolkien',
            'genre': 'Fantasy',
            'description': 'Bilbo Baggins is a hobbit who enjoys a comfortable, unambitious life, rarely travelling further than the pantry of his hobbit-hole in Bag End. But his contentment is disturbed when the wizard, Gandalf, and thirteen dwarves arrive on his doorstep one day to whisk him away on an unexpected journey.',
            'cover_image': 'https://images.unsplash.com/photo-1621351183012-e2f9972dd9bf?w=400&h=600&fit=crop'
        },
        {
            'title': 'Educated',
            'author': 'Tara Westover',
            'genre': 'Memoir',
            'description': 'Born to survivalists in the mountains of Idaho, Tara Westover was seventeen the first time she set foot in a classroom. Her memoir is a coming-of-age story that gets to the heart of what an education is and what it offers: the perspective to see one\'s life through new eyes and the will to change it.',
            'cover_image': 'https://images.unsplash.com/photo-1481627834876-b7833e8f5570?w=400&h=600&fit=crop'
        },
        {
            'title': 'The Midnight Library',
            'author': 'Matt Haig',
            'genre': 'Fiction',
            'description': 'Between life and death there is a library, and within that library, the shelves go on forever. Every book provides a chance to try another life you could have lived. Nora Seed finds herself in the Midnight Library, where she can live as many lives as she wants, exploring every possibility.',
            'cover_image': 'https://images.unsplash.com/photo-1541963463532-d68292c34b19?w=400&h=600&fit=crop'
        },
        {
            'title': 'Atomic Habits',
            'author': 'James Clear',
            'genre': 'Self-Help',
            'description': 'No matter your goals, Atomic Habits offers a proven framework for improving — every day. James Clear, one of the world\'s leading experts on habit formation, reveals practical strategies that will teach you exactly how to form good habits, break bad ones, and master the tiny behaviors that lead to remarkable results.',
            'cover_image': 'https://images.unsplash.com/photo-1589829085413-56de8ae18c73?w=400&h=600&fit=crop'
        },
    ]

    books = []
    for b in books_data:
        book = Book(
            title=b['title'],
            author=b['author'],
            genre=b['genre'],
            description=b['description'],
            cover_image=b['cover_image']
        )
        db.session.add(book)
        books.append(book)
    db.session.commit()

    reviews_data = [
        {'user_idx': 0, 'book_idx': 0, 'rating': 5, 'review_text': 'A masterpiece that teaches us to follow our dreams. The journey of Santiago is both inspiring and thought-provoking. Every page resonates with wisdom and the prose is beautifully simple yet profound.'},
        {'user_idx': 1, 'book_idx': 0, 'rating': 4, 'review_text': 'An enchanting tale about discovering one\'s personal legend. The storytelling is captivating, though some may find the philosophical elements a bit heavy-handed. Still, a must-read.'},
        {'user_idx': 2, 'book_idx': 1, 'rating': 5, 'review_text': 'Orwell\'s vision of a totalitarian future is as relevant today as ever. The way he constructs the world of Oceania is terrifyingly believable. A chilling and essential read.'},
        {'user_idx': 0, 'book_idx': 1, 'rating': 5, 'review_text': 'A prophetic warning about surveillance and authoritarian control. The concept of doublethink and newspeak are incredibly prescient. This book changed how I think about freedom.'},
        {'user_idx': 1, 'book_idx': 2, 'rating': 5, 'review_text': 'A timeless classic that addresses racial injustice with grace and moral clarity. Scout\'s innocent perspective makes the themes even more powerful. Atticus Finch is one of literature\'s greatest characters.'},
        {'user_idx': 2, 'book_idx': 3, 'rating': 4, 'review_text': 'Fitzgerald\'s prose is absolutely gorgeous. The tragic story of Gatsby and Daisy captures the hollow pursuit of the American Dream beautifully. The symbolism is rich and layered.'},
        {'user_idx': 0, 'book_idx': 4, 'rating': 5, 'review_text': 'A sweeping narrative that connects biology, history, and philosophy. Harari has a gift for making complex ideas accessible and entertaining. This book fundamentally changed my understanding of humanity.'},
        {'user_idx': 1, 'book_idx': 5, 'rating': 5, 'review_text': 'The world-building in Dune is unparalleled. Herbert created an entire ecosystem, religion, and political system that feels completely real. The themes of ecology and power are incredibly relevant.'},
        {'user_idx': 2, 'book_idx': 6, 'rating': 4, 'review_text': 'Holden Caulfield\'s voice is unmistakable — raw, funny, and deeply alienated. Salinger captured teenage angst in a way that still resonates decades later. A defining novel of growing up.'},
        {'user_idx': 0, 'book_idx': 7, 'rating': 4, 'review_text': 'Huxley\'s dystopia of pleasure and conformity is arguably more relevant than Orwell\'s. The idea that people would willingly give up freedom for comfort is chillingly accurate to our social media age.'},
        {'user_idx': 1, 'book_idx': 8, 'rating': 5, 'review_text': 'A perfect adventure story for all ages. Tolkien\'s world-building is magical and Bilbo\'s journey from a comfort-loving hobbit to a true hero is deeply satisfying. The prose is warm and witty.'},
        {'user_idx': 2, 'book_idx': 9, 'rating': 5, 'review_text': 'An extraordinary memoir about the transformative power of education. Westover\'s story is both harrowing and inspiring. It shows that knowledge truly can set you free from the most constrained circumstances.'},
        {'user_idx': 0, 'book_idx': 10, 'rating': 4, 'review_text': 'A beautiful and imaginative exploration of regret and possibility. The concept of the Midnight Library is brilliant. Haig weaves philosophical questions into a deeply human story.'},
        {'user_idx': 1, 'book_idx': 11, 'rating': 5, 'review_text': 'The most practical and actionable book on habits I\'ve ever read. Clear breaks down the science of behavior change into simple, powerful strategies. I\'ve already started applying the 1% rule to my daily life.'},
        {'user_idx': 2, 'book_idx': 2, 'rating': 5, 'review_text': 'I read this in school and revisited it as an adult — it only gets better. The moral courage of Atticus Finch and the innocence of Scout create a powerful contrast that illuminates the best and worst of human nature.'},
    ]

    for r in reviews_data:
        review = Review(
            rating=r['rating'],
            review_text=r['review_text'],
            created_at=datetime(2024, 6, 15),
            user_id=users[r['user_idx']].id,
            book_id=books[r['book_idx']].id
        )
        db.session.add(review)

    db.session.commit()
    print('✅ Database seeded successfully!')


# ─── Routes ──────────────────────────────────────────────────────────────────

@app.route('/')
def home():
    featured_books = Book.query.outerjoin(Review).group_by(Book.id).order_by(
        db.func.coalesce(db.func.avg(Review.rating), 0).desc()
    ).limit(4).all()

    latest_reviews = Review.query.order_by(Review.created_at.desc()).limit(6).all()
    total_books = Book.query.count()
    total_reviews = Review.query.count()
    total_users = User.query.count()

    return render_template('home.html',
                           featured_books=featured_books,
                           latest_reviews=latest_reviews,
                           total_books=total_books,
                           total_reviews=total_reviews,
                           total_users=total_users)


@app.route('/books')
def books():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    genre_filter = request.args.get('genre', '')
    search_query = request.args.get('q', '')
    sort_by = request.args.get('sort', 'title')

    query = Book.query

    if genre_filter:
        query = query.filter(Book.genre.ilike(f'%{genre_filter}%'))

    if search_query:
        query = query.filter(
            db.or_(
                Book.title.ilike(f'%{search_query}%'),
                Book.author.ilike(f'%{search_query}%')
            )
        )

    if sort_by == 'rating':
        query = query.outerjoin(Review).group_by(Book.id).order_by(
            db.func.coalesce(db.func.avg(Review.rating), 0).desc()
        )
    elif sort_by == 'title':
        query = query.order_by(Book.title.asc())
    elif sort_by == 'author':
        query = query.order_by(Book.author.asc())

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    genres = [g[0] for g in db.session.query(Book.genre).distinct().order_by(Book.genre).all()]

    return render_template('books.html',
                           books=pagination.items,
                           pagination=pagination,
                           genres=genres,
                           current_genre=genre_filter,
                           search_query=search_query,
                           sort_by=sort_by)


@app.route('/book/<int:book_id>', methods=['GET', 'POST'])
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    form = ReviewForm()

    if form.validate_on_submit() and current_user.is_authenticated:
        existing_review = Review.query.filter_by(
            user_id=current_user.id, book_id=book.id
        ).first()

        if existing_review:
            flash('You have already reviewed this book. You can edit your review below.', 'warning')
            return redirect(url_for('book_detail', book_id=book.id))

        review = Review(
            rating=form.rating.data,
            review_text=form.review_text.data,
            user_id=current_user.id,
            book_id=book.id
        )
        db.session.add(review)
        db.session.commit()
        flash('Your review has been submitted!', 'success')
        return redirect(url_for('book_detail', book_id=book.id))

    reviews = Review.query.filter_by(book_id=book.id).order_by(Review.created_at.desc()).all()
    return render_template('book_detail.html', book=book, reviews=reviews, form=form)


@app.route('/review/edit/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Review.query.get_or_404(review_id)

    if review.user_id != current_user.id:
        flash('You can only edit your own reviews.', 'danger')
        return redirect(url_for('home'))

    form = ReviewForm(obj=review)

    if form.validate_on_submit():
        review.rating = form.rating.data
        review.review_text = form.review_text.data
        review.created_at = datetime.utcnow()
        db.session.commit()
        flash('Your review has been updated!', 'success')
        return redirect(url_for('book_detail', book_id=review.book_id))

    return render_template('edit_review.html', form=form, review=review)


@app.route('/review/delete/<int:review_id>', methods=['POST'])
@login_required
def delete_review(review_id):
    review = Review.query.get_or_404(review_id)

    if review.user_id != current_user.id:
        flash('You can only delete your own reviews.', 'danger')
        return redirect(url_for('home'))

    book_id = review.book_id
    db.session.delete(review)
    db.session.commit()
    flash('Your review has been deleted.', 'success')
    return redirect(url_for('book_detail', book_id=book_id))


@app.route('/profile/<username>')
def profile(username):
    user = User.query.filter_by(username=username).first_or_404()
    reviews = Review.query.filter_by(user_id=user.id).order_by(Review.created_at.desc()).all()
    return render_template('profile.html', profile_user=user, reviews=reviews)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = RegisterForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            password=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully! Please log in.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            next_page = request.args.get('next')
            flash(f'Welcome back, {user.username}!', 'success')
            return redirect(next_page or url_for('home'))
        else:
            flash('Invalid email or password.', 'danger')

    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))


@app.route('/search')
def search():
    query = request.args.get('q', '')
    if not query:
        return redirect(url_for('books'))

    books = Book.query.filter(
        db.or_(
            Book.title.ilike(f'%{query}%'),
            Book.author.ilike(f'%{query}%'),
            Book.genre.ilike(f'%{query}%')
        )
    ).all()

    return render_template('books.html', books=books, search_query=query)


# ─── Error Handlers ──────────────────────────────────────────────────────────

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500


# ─── Context Processor ───────────────────────────────────────────────────────

@app.context_processor
def inject_globals():
    return {
        'genres': [g[0] for g in db.session.query(Book.genre).distinct().order_by(Book.genre).all()]
    }


# ─── Main ────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=False, host='0.0.0.0', port=5000)