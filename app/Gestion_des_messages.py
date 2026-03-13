from flask import Blueprint, render_template, redirect, flash, url_for, request, abort
from flask_login import login_required, current_user
from app.forms import MessageForm, SchoolInfoForm, EditInfoForm, ForumPostForm
from app.models import db, Message, User, SchoolInfo, ForumPost
from werkzeug.exceptions import HTTPException

blueprint_mes = Blueprint('mes', __name__)


@blueprint_mes.route('/messages', methods=['GET', 'POST'])
@login_required
def messages():
    form = MessageForm()
    if form.validate_on_submit():
        recipient = User.query.filter_by(username=form.recipient.data).first()
        if recipient and recipient != current_user:
            msg = Message(sender=current_user, recipient=recipient, body=form.body.data)
            db.session.add(msg)
            db.session.commit()
            flash('Message sent successfully!', 'success')
        else:
            flash('Recipient not found.', 'danger')
        return redirect(url_for('mes.messages'))
    sent_messages = Message.query.filter_by(sender=current_user).all()
    received_messages = Message.query.filter_by(recipient=current_user).all()
    return render_template('message.html', form=form,
                           sent_messages=sent_messages, received_messages=received_messages)



@blueprint_mes.route('/messages/filter', methods=['GET', 'POST'])
@login_required
def filter_messages(msgs):
    try:
        filter_by = request.args.get('filter_by')
        order = request.args.get('order')
        # Validation des entrées
        if filter_by not in ['timestamp', 'sender_id', 'body', 'recipient_id']:
            raise ValueError("Critère de filtrage invalide.")

        if order not in ['asc', 'desc']:
            raise ValueError("Ordre invalide.")

        # Logique pour récupérer les messages en fonction du filtre
        msgs = get_filtered_messages(filter_by, order)
        if msgs is None or len(msgs) == 0:
            return render_template('filtrer_messages.html', msg="Aucun message trouvé")

    except ValueError as e:
        error = str(e)
        return render_template('filtrer_messages.html', error=error)
    except Exception as e:

        return render_template('filtrer_messages.html', msgs=msgs, error=str(e))



@blueprint_mes.route('/MessageService')
def get_filtered_messages(filter_by, order):
    query = Message.query
    if filter_by == 'timestamp':
        query = query.order_by(Message.timestamp.asc() if order == 'asc' else Message.timestamp.desc())
    elif filter_by == 'sender_id':
        query = query.order_by(Message.sender_id.asc() if order == 'asc' else Message.sender_id.desc())
    elif filter_by == 'body':
        query = query.order_by(Message.body.asc() if order == 'asc' else Message.body.desc())
    elif filter_by == 'recepient_id ':
        query = query.order_by(Message.recipient_id.asc() if order == 'asc' else Message.recipient_id.desc())
    return query.all()



@blueprint_mes.route('/messages/<int:messege_id>/mark-as-read', methods=['POST'])
def mark_as_read(message_id):
    message = Message.query.get_or_404(message_id)
    message.read = True
    db.session.commit()
    return redirect(url_for('mes.messages'))



@blueprint_mes.route('/messages/<int:messege_id>/delete', methods=['POST'])
def delete_message(message_id):
    message = Message.query.get_or_404(message_id)
    db.session.delete()
    db.session.commit()
    return redirect(url_for('mes.messages', message=message))



@blueprint_mes.route('/info', methods=['GET', 'POST'])
@login_required
def info():
    form = SchoolInfoForm()
    if form.validate_on_submit():
        info_generate = SchoolInfo(title=form.title.data, content=form.content.data)
        db.session.add(info_generate)
        db.session.commit()
        flash('Information posted successfully!', 'success')
        return redirect(url_for('mes.info'))
    infos = SchoolInfo.query.all()
    return render_template('info.html', form=form, infos=infos)



@blueprint_mes.route('/info/edit/<int:info_id>', methods=['GET', 'POST'])
@login_required
def edit_info(info_id):
    info_editer = SchoolInfo.query.get_or_404(info_id)
    form = EditInfoForm()
    if form.validate_on_submit():
        info.title = form.title.data
        info.content = form.content.data
        db.session.commit()
        flash('Information updated successfully!', 'success')
        return redirect(url_for('mes.info'))
    elif request.method == 'GET':
        form.title.data = info.title
        form.content.data = info.content
    return render_template('edit_info.html', form=form, info_editer=info_editer)



@blueprint_mes.route('/info/delete/<int:info_id>', methods=['POST'])
@login_required
def delete_info(info_id):
    info_supprimer = SchoolInfo.query.get_or_404(info_id)
    db.session.delete(info_supprimer)
    db.session.commit()
    flash('Information deleted successfully!', 'success')
    return redirect(url_for('mes.info'))



@blueprint_mes.route('/information/filter', methods=['GET', 'POST'])
@login_required
def filter_info():
    form = SchoolInfoForm()
    filter_by = request.args.get('filter_by', 'timestamp')
    order = request.args.get('order', 'asc')
    infos = SchoolInfo.query.order_by(SchoolInfo, filter_by, order)
    return render_template('info.html', form=form, infos=infos)



@blueprint_mes.route('/forum/edit/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = ForumPostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.body = form.body.data
        db.session.commit()
        flash('Post updated successfully!', 'success')
        return redirect(url_for('meeting.forum'))
    elif request.method == 'GET':
        form.title.data = post.title
        form.body.data = post.body
    return render_template('edit_post.html', form=form, post=post)



@blueprint_mes.route('/forum/delete/<int:post_id>', methods=['POST'])
@login_required
def delete_post(post_id):
    post = ForumPost.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Post deleted successfully!', 'success')
    return redirect(url_for('mes.handle_exception'))



@blueprint_mes.errorhandler(HTTPException)
def handle_exception(e):
    if request.path.startswith('/post'):
        template = 'error_post.html'
    else:
        template = 'error.html'
    return render_template(template, error=e), e.code