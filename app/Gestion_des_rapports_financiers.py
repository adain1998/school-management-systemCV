# Imports standards de Python
from datetime import datetime, timedelta

# Imports tiers
from flask import Blueprint, render_template, redirect, flash, url_for, send_file, Response

import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO
import base64

# Imports locaux
from app.models import db, Finance, Report
from app.admin_decorateur import admin_required
from app.forms import ReportForm, ReportFilterForm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import io

blueprint_rapport = Blueprint('rapport', __name__)


@blueprint_rapport.route("/generate_report/<string:report_type>")
@admin_required
def generate_report(report_type, start_date=None):
    form = ReportForm()
    if form.validate_on_submit():
        report_type = form.report_type.data
        start_date = form.start_date.data
    try:
        if start_date is None:
            start_date = datetime.now().date()
        else:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()

        end_date = datetime.now().date()

        if report_type == 'daily':
            end_date = start_date
        elif report_type == 'weekly':
            start_date = end_date - timedelta(days=7)
        elif report_type == 'monthly':
            start_date = end_date.replace(day=1)
            end_date = (end_date.replace(month=end_date.month + 1, day=1) - timedelta(days=1))
        elif report_type == 'quarterly':
            current_month = end_date.month
            start_month = current_month - (current_month % 3) + 1
            start_date = end_date.replace(month=start_month, day=1)
            end_date = (end_date.replace(month=start_month + 3, day=1) - timedelta(days=1))
        elif report_type == 'semi_annually':
            current_month = end_date.month
            start_month = current_month - (current_month % 6) + 1
            start_date = end_date.replace(month=start_month, day=1)
            end_date = (end_date.replace(month=start_month + 6, day=1) - timedelta(days=1))
        elif report_type == 'annually':
            start_date = end_date.replace(month=1, day=1)
            end_date = end_date.replace(month=12, day=31)
        else:
            flash('Invalid report type!', 'danger')
            return redirect(url_for(''))

        total_amount = db.session.query(db.func.sum(Finance.amount)).filter(
            Finance.date.between(start_date, end_date)).scalar()

        if total_amount is None:
            total_amount = 0

        report = Report(report_type=report_type, start_date=start_date, end_date=end_date, total_amount=total_amount)
        db.session.add(report)
        db.session.commit()

        flash(f'{report_type.capitalize()} report generated successfully!', 'success')
    except Exception as e:
        flash(f'Error generating report: {str(e)}', 'danger')
        flash(f'{report_type.capitalize()} report generated successfully!', 'success')
        return redirect(url_for('home'))
    return render_template('generate_report.html', form=form)



@blueprint_rapport.route("/download_report/<int:report_id>")
@admin_required
def download_report(report_id):
    report = Report.query.get_or_404(report_id)
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    pdf.drawString(100, 750, f"Report Type: {report.report_type}")
    pdf.drawString(100, 730, f"Start Date: {report.start_date}")
    pdf.drawString(100, 710, f"End Date: {report.end_date}")
    pdf.drawString(100, 690, f"Total Amount: {report.total_amount}")
    pdf.showPage()
    pdf.save()
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{report.report_type}_report.pdf",
                     mimetype='application/pdf')



@blueprint_rapport.route("/export_reports")
@admin_required
def export_reports():
    reports = Report.query.all()
    data = [{
        'Report Type': report.report_type,
        'Start Date': report.start_date,
        'End Date': report.end_date,
        'Total Amount': report.total_amount
    } for report in reports]
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition": "attachment; filename=reports.csv"}
    )



@blueprint_rapport.route("/view_report_graph/<int:report_id>")
@admin_required
def view_report_graph(report_id):
    report = Report.query.get_or_404(report_id)
    fig, ax = plt.subplots()
    ax.bar(['Total Amount'], [report.total_amount])
    ax.set_title(f'{report.report_type.capitalize()} Report')
    ax.set_ylabel('Amount')
    buffer = BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    graph = base64.b64encode(image_png).decode('utf-8')
    return render_template('view_report_graph.html', graph=graph)



@blueprint_rapport.route("/view_reports", methods=['GET', 'POST'])
@admin_required
def view_reports():
    form = ReportFilterForm()
    query = Report.query
    if form.validate_on_submit():
        if form.report_type.data != 'all':
            query = query.filter_by(report_type=form.report_type.data)
        if form.start_date.data:
            query = query.filter(Report.start_date >= form.start_date.data)
        if form.end_date.data:
            query = query.filter(Report.end_date <= form.end_date.data)
    reports = query.all()
    return render_template('view_reports.html', form=form, reports=reports)
