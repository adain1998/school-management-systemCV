from flask import Blueprint, render_template, flash, redirect, url_for, request
from app.models import db, ForumPost, Notification, Poll, Choice
from flask_login import current_user, login_required
from app.forms import ForumPostForm, NotificationForm, PollForm
from datetime import datetime
from sqlalchemy import desc

meeting = Blueprint("meeting", __name__)


@meeting.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    form = ForumPostForm()
    if form.validate_on_submit():
        post = ForumPost(user_id=current_user.id, title=form.title.data, body=form.body.data)
        db.session.add(post)
        db.session.commit()
        flash('Post created successfully!', 'success')
        return redirect(url_for('main.forum'))
    posts = ForumPost.query.all()
    return render_template('forum.html', form=form, posts=posts)


@meeting.route('/forum/filter', methods=['GET', 'POST'])
def filter_forum():
    form = ForumPostForm()
    filter_colmun = request.args.get('filter_colmun', 'timestamp')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    allowed_filters = ['timestamp', 'tilte', 'body']
    value = datetime
    if filter_colmun not in allowed_filters:
        return 'invalid filter column', 400
    query = ForumPost.query
    query = query.filter_by(**{filter_colmun: value})
    if order == 'desc':
        query = query.order_by(desc(getattr(ForumPost, filter_colmun)))
    else:
        query = query.order_by(desc(getattr(ForumPost, filter_colmun)))
    pagination = query.paginate(page=page, per_page=per_page)
    forumpost = pagination.items
    forumposts = query.all()
    return render_template('forum.html', form=form, forumposts=forumposts, forumpost=forumpost, pagination=pagination)



@meeting.route('/notifications/filter', methods=['GET', 'POST'])
@login_required
def filter_notifications():
    form = NotificationForm(request.args)
    filter_column = form.filter_by.data or 'due_date'
    order = form.order.data or 'asc'
    page = request.args.get('page', 1, type=int)
    per_page = 10

    if filter_column not in ['due_date', 'title', 'description']:
        return 'Colonne de filtrage invalide', 400

    query = Notification.query
    if order == 'desc':
        query = query.order_by(desc(getattr(Notification, filter_column)))
    else:
        query = query.order_by(getattr(Notification, filter_column))

    pagination = query.paginate(page=page, per_page=per_page)
    notifications = pagination.items

    return render_template('Notification.html', form=form, notifications=notifications, pagination=pagination)



@meeting.route('/create_poll', methods=['GET', 'POST'])
def create_poll():
    form = PollForm()
    if form.validate_on_submit():
        # Créer le sondage sans le commettre immédiatement
        poll = Poll(question=form.question.data, end_date=form.end_date.data)

        # Ajouter les choix au sondage
        for choice_form in form.choices:
            choice = Choice(choice_text=choice_form.choice_text.data)
            poll.choices.append(choice)

        # Ajouter le sondage (avec ses choix) à la session et commettre
        db.session.add(poll)
        db.session.commit()

        flash('Sondage créé avec succès !', 'success')
        return redirect(url_for('create_poll'))
    return render_template('sondage.html', form=form)

# code reserve forum post
"""@meeting.route('/notifications/filter', methods=['GET', 'POST'])
@login_required
def filter_notifications():
    form = NotificationForm()
    filter_column = request.args.get('filter_by', 'due_date')
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 10
    allowed_filters = ['due_date', 'tilte', 'description']
    value = str
    if filter_column not in allowed_filters:
        return 'invalid filter column', 400
    query = Notification.query
    query = query.filter_by(**{filter_column: value})
    if order == 'desc':
        query = query.order_by(desc(getattr(Notification, filter_column)))
    else:
        query = query.order_by(desc(getattr(Notification, filter_column)))
    pagination = query.paginate(page=page, per_page=per_page)
    notifica = pagination.items
    notification = query.all()
    return render_template('Notification.html',
                           form=form, notificationt=notification, notifica=notifica)"""

