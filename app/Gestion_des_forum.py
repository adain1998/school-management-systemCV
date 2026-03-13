import pytz
from pytz import UTC
from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify, current_app
from app.models import db, ForumPost, Notification, Poll, Choice, Post, Reaction, User
from flask_login import current_user, login_required
from app.forms import ForumPostForm, NotificationForm, PollForm
from datetime import datetime
from sqlalchemy import desc, asc
from app.decorators import roles_required
from sqlalchemy.orm import joinedload
from sqlalchemy.exc import SQLAlchemyError
from markupsafe import escape

blueprint_meeting = Blueprint("meeting", __name__)



@blueprint_meeting.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    form = ForumPostForm()

    if form.validate_on_submit():
        post = ForumPost(
            user_id=current_user.id,
            title=form.title.data,
            body=form.body.data
        )
        db.session.add(post)
        db.session.commit()
        flash('Post créé avec succès !', 'success')
        return redirect(url_for(request.url))

    # Pagination
    page = request.args.get('page', 1, type=int)
    pagination = ForumPost.query.order_by(ForumPost.timestamp.desc()).paginate(page=page, per_page=10)
    posts = pagination.items

    return render_template(
        'forum.html',
        form=form,
        posts=posts,
        pagination=pagination
    )



@blueprint_meeting.route('/posts/<int:post_id>/react', methods=['POST'])
@login_required
def react_to_post(post_id):
    data = request.get_json()
    reaction_type = data.get('reaction')

    valid_reactions = ['like', 'love', 'haha', 'wow', 'sad', 'angry']
    if reaction_type not in valid_reactions:
        return jsonify({'error': 'Type de réaction invalide'}), 400

    post = Post.query.get_or_404(post_id)
    now_utc = datetime.now(pytz.UTC)

    # Vérifier si l'utilisateur a déjà réagi
    reaction = Reaction.query.filter_by(user_id=current_user.id, post_id=post_id).first()

    if reaction:
        reaction.reaction_type = reaction_type
        reaction.timestamp = now_utc
    else:
        reaction = Reaction(
            user_id=current_user.id,
            post_id=post.id,
            reaction_type=reaction_type,
            timestamp=now_utc
        )
        db.session.add(reaction)

    db.session.commit()

    # Statistiques : compter les réactions par type pour ce post
    from sqlalchemy import func
    counts = db.session.query(
        Reaction.reaction_type,
        func.count(Reaction.id)
    ).filter_by(post_id=post.id).group_by(Reaction.reaction_type).all()

    reaction_counts = {r_type: 0 for r_type in valid_reactions}
    for r_type, count in counts:
        reaction_counts[r_type] = count

    return jsonify({
        'message': 'Réaction enregistrée',
        'reaction_type': reaction.reaction_type,
        'timestamp': reaction.timestamp.isoformat(),
        'reaction_counts': reaction_counts,
        'post_id': post.id
    })



@blueprint_meeting.route('/forum/filter', methods=['GET', 'POST'])
def filter_forum():
    form = ForumPostForm()
    filter_column = request.args.get('filter_column', 'timestamp')
    filter_value = request.args.get('filter_value', '').strip()
    order = request.args.get('order', 'asc')
    page = request.args.get('page', 1, type=int)
    per_page = 10

    allowed_filters = ['timestamp', 'title', 'body', 'author']

    if filter_column not in allowed_filters:
        return jsonify({'error': 'Colonne de filtrage invalide'}), 400

    # Utilisation de joinedload pour précharger les utilisateurs liés
    query = ForumPost.query.options(joinedload(ForumPost.user))

    # Appliquer les filtres selon la colonne
    if filter_column == 'title':
        query = query.filter(ForumPost.title.ilike(f'%{filter_value}%'))
    elif filter_column == 'body':
        query = query.filter(ForumPost.body.ilike(f'%{filter_value}%'))
    elif filter_column == 'timestamp':
        if filter_value:
            try:
                date_obj = datetime.fromisoformat(filter_value)
                query = query.filter(ForumPost.timestamp >= date_obj)
            except ValueError:
                return jsonify({'error': 'Format de date invalide. Utilisez YYYY-MM-DD.'}), 400
    elif filter_column == 'author':
        # Jointure correcte sur ForumPost. User pour filtrer par username
        query = query.join(ForumPost.user).filter(User.username.ilike(f'%{filter_value}%'))

    # Détermination de la colonne de tri
    sort_attr = getattr(ForumPost, 'timestamp') if filter_column == 'author' else getattr(ForumPost, filter_column)

    # Appliquer le tri
    if order == 'desc':
        query = query.order_by(desc(sort_attr))
    else:
        query = query.order_by(asc(sort_attr))

    # Pagination
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    forumposts = pagination.items

    return render_template(
        'filtered_forum.jinja.html',
        form=form,
        forumposts=forumposts,
        pagination=pagination,
        filter_applied=True,
        filter_column=filter_column,
        filter_value=filter_value,
        order=order
    )



@blueprint_meeting.route('/notifications/filter', methods=['GET', 'POST'])
@login_required
def filter_notifications():
    # Récupération des paramètres via form (GET ou POST)
    form = NotificationForm(request.args)

    # Colonnes autorisées pour filtrage
    valid_columns = ['due_date', 'title', 'description']

    # Valeurs par défaut
    filter_column = form.filter_by.data if form.filter_by.data in valid_columns else 'due_date'
    order = form.order.data if form.order.data in ['asc', 'desc'] else 'asc'

    try:
        page = int(request.args.get('page', 1))
        if page < 1:
            raise ValueError
    except (ValueError, TypeError):
        page = 1  # page par défaut en cas d'erreur

    per_page = 10

    # Construction de la requête avec gestion de l'ordre
    query = Notification.query
    try:
        column_attr = getattr(Notification, filter_column)
    except AttributeError:
        flash('Colonne de filtrage invalide, utilisation de la valeur par défaut.', 'warning')
        column_attr = Notification.due_date

    if order == 'desc':
        query = query.order_by(desc(column_attr))
    else:
        query = query.order_by(column_attr)

    # Pagination sécurisée
    try:
        pagination = query.paginate(page=page, per_page=per_page)
    except Exception as e:
        flash(f'Erreur lors de la pagination, affichage de la première page.:{e}', 'error')
        pagination = query.paginate(page=1, per_page=per_page)

    notifications = pagination.items

    return render_template('Notification.jinja.html', form=form, notifications=notifications, pagination=pagination)



@blueprint_meeting.route('/create_poll', methods=['GET', 'POST'])
@roles_required('enseignant', 'admin', 'superadmin')
@login_required
def create_poll():
    form = PollForm()

    if form.validate_on_submit():
        try:
            # Validation supplémentaire : éviter une date de fin dans le passé
            if form.end_date.data.replace(tzinfo=UTC) < datetime.now(UTC):
                flash("La date de fin ne peut pas être dans le passé.", "warning")
                return render_template('sondage.html', form=form)

            # Création du sondage
            poll = Poll(
                question=escape(form.question.data.strip()),
                end_date=form.end_date.data
            )

            # Traitement et validation des choix
            choice_texts = set()
            for choice_form in form.choices:
                text = escape(choice_form.choice_text.data.strip())
                if not text:
                    flash("Un des choix est vide. Veuillez remplir tous les choix.", "danger")
                    return render_template('sondage.html', form=form)
                if text in choice_texts:
                    flash(f"Le choix '{text}' est dupliqué. Veuillez entrer des choix uniques.", "danger")
                    return render_template('sondage.html', form=form)
                choice_texts.add(text)
                poll.choices.append(Choice(choice_text=text))

            if not poll.choices:
                flash("Le sondage doit contenir au moins un choix.", "warning")
                return render_template('sondage.html', form=form)

            # Enregistrement dans la base de données
            db.session.add(poll)
            db.session.commit()

            flash("Sondage créé avec succès !", "success")
            return redirect(url_for('meeting.create_poll'))

        except SQLAlchemyError as e:
            db.session.rollback()
            current_app.logger.error(f"Erreur lors de la création du sondage : {e}")
            flash("Une erreur est survenue lors de la création du sondage. Veuillez réessayer.", "danger")
            return render_template('sondage.html', form=form), 500

    return render_template('sondage.html', form=form)
