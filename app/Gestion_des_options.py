from flask import Blueprint, render_template, request, redirect, url_for, flash
from models import db, Option

opt = Blueprint('opt', __name__)


@opt.route('/options')
def view_options():
    options = Option.query.all()
    return render_template('option.html', options=options)


@opt.route('/add_option', methods=['POST'])
def add_option():
    name = request.form['name']
    new_option = Option(name=name)
    db.session.add(new_option)
    db.session.commit()
    flash('Option added successfully!', 'success')
    return redirect(url_for('view_options'))


@opt.route('/edit_option/<int:id>', methods=['GET', 'POST'])
def edit_option():
    option = Option.query.get_or_404(id)
    if request.method == ['POST']:
        option.name = request.form['name']
        db.session.commit()
        flash('Option updated successfully!', 'success')
        return redirect(url_for('view_options'))
    return render_template('edit_option.html', option=option)


@opt.route('/delete_option/<int:id>', 'DELETE')
def delete_option():
    option = Option.query.get_or_404(id)
    db.session.delete(option)
    db.session.commit()
    flash('Option deleted successfully!', 'success')
    return redirect(url_for('view_options'))
