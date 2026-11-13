"""
BrewBean Coffee Analytics System — Marketing Campaign Management Routes
"""

from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from app.models.campaign import (
    get_all_campaigns, get_campaign_by_id, get_campaign_performance_metrics,
    get_marketing_summary_kpis, create_campaign, update_campaign
)
from app.models.sale import get_all_sales

marketing_bp = Blueprint('marketing', __name__)

@marketing_bp.route('/marketing', methods=['GET'])
def list_campaigns():
    """
    Renders the Marketing Campaign Management directory & ROI metrics dashboard.
    """
    search_query = request.args.get('search', '').strip()
    channel_filter = request.args.get('channel', '').strip()
    status_filter = request.args.get('status', '').strip()

    try:
        kpis = get_marketing_summary_kpis()
        campaigns = get_all_campaigns(
            search_query=search_query,
            channel_filter=channel_filter,
            status_filter=status_filter
        )
        return render_template(
            'marketing.html',
            campaigns=campaigns,
            kpis=kpis,
            search_query=search_query,
            channel_filter=channel_filter,
            status_filter=status_filter
        )
    except Exception as e:
        flash(f"Error loading marketing campaigns: {str(e)}", "danger")
        return render_template('marketing.html', campaigns=[], kpis={}, search_query='')

@marketing_bp.route('/marketing/add', methods=['POST'])
def add_campaign():
    """
    Handles addition of a new marketing campaign.
    Validates start_date, end_date (end_date >= start_date), budget >= 0, actual_spend >= 0.
    """
    campaign_name = request.form.get('campaign_name', '').strip()
    channel = request.form.get('channel', 'Other').strip()
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()
    budget = request.form.get('budget', '0.0').strip()
    actual_spend = request.form.get('actual_spend', '0.0').strip()
    target_audience = request.form.get('target_audience', '').strip()
    status = request.form.get('status', 'Planned').strip()

    if not campaign_name:
        flash("Campaign name is required.", "warning")
        return redirect(url_for('marketing.list_campaigns'))

    if not start_date or not end_date:
        flash("Start date and End date are required.", "warning")
        return redirect(url_for('marketing.list_campaigns'))

    try:
        s_dt = datetime.strptime(start_date, '%Y-%m-%d')
        e_dt = datetime.strptime(end_date, '%Y-%m-%d')
        if e_dt < s_dt:
            flash("End date cannot be earlier than start date.", "warning")
            return redirect(url_for('marketing.list_campaigns'))
    except ValueError:
        flash("Invalid date format supplied.", "danger")
        return redirect(url_for('marketing.list_campaigns'))

    try:
        b_val = float(budget or 0)
        s_val = float(actual_spend or 0)
        if b_val < 0 or s_val < 0:
            flash("Budget and Actual Spend must be non-negative values.", "warning")
            return redirect(url_for('marketing.list_campaigns'))
    except ValueError:
        flash("Invalid numeric value for budget or actual spend.", "danger")
        return redirect(url_for('marketing.list_campaigns'))

    try:
        create_campaign(campaign_name, channel, start_date, end_date, budget, actual_spend, target_audience, status)
        flash(f"Marketing campaign '{campaign_name}' created successfully!", "success")
    except Exception as e:
        flash(f"Failed to create campaign: {str(e)}", "danger")

    return redirect(url_for('marketing.list_campaigns'))

@marketing_bp.route('/marketing/edit/<int:campaign_id>', methods=['POST'])
def edit_campaign(campaign_id):
    """
    Handles updates to an existing marketing campaign.
    """
    campaign_name = request.form.get('campaign_name', '').strip()
    channel = request.form.get('channel', 'Other').strip()
    start_date = request.form.get('start_date', '').strip()
    end_date = request.form.get('end_date', '').strip()
    budget = request.form.get('budget', '0.0').strip()
    actual_spend = request.form.get('actual_spend', '0.0').strip()
    target_audience = request.form.get('target_audience', '').strip()
    status = request.form.get('status', 'Planned').strip()

    if not campaign_name:
        flash("Campaign name cannot be empty.", "warning")
        return redirect(url_for('marketing.list_campaigns'))

    try:
        s_dt = datetime.strptime(start_date, '%Y-%m-%d')
        e_dt = datetime.strptime(end_date, '%Y-%m-%d')
        if e_dt < s_dt:
            flash("End date cannot be earlier than start date.", "warning")
            return redirect(url_for('marketing.list_campaigns'))
    except ValueError:
        flash("Invalid date format supplied.", "danger")
        return redirect(url_for('marketing.list_campaigns'))

    try:
        updated = update_campaign(campaign_id, campaign_name, channel, start_date, end_date, budget, actual_spend, target_audience, status)
        if updated:
            flash("Campaign updated successfully!", "success")
        else:
            flash("Campaign record not found.", "warning")
    except Exception as e:
        flash(f"Failed to update campaign: {str(e)}", "danger")

    return redirect(url_for('marketing.list_campaigns'))

@marketing_bp.route('/marketing/<int:campaign_id>', methods=['GET'])
def view_campaign(campaign_id):
    """
    Renders detailed performance view for a single campaign showing attributed financial metrics and linked sales log.
    """
    try:
        campaign = get_campaign_by_id(campaign_id)
        if not campaign:
            flash("Campaign not found.", "warning")
            return redirect(url_for('marketing.list_campaigns'))

        metrics = get_campaign_performance_metrics(campaign_id)

        # Retrieve sales linked to this campaign
        linked_sales = get_all_sales()
        linked_sales = [s for s in linked_sales if s.get('campaign_id') == campaign_id]

        return render_template(
            'campaign_detail.html',
            campaign=campaign,
            metrics=metrics,
            linked_sales=linked_sales
        )
    except Exception as e:
        flash(f"Error loading campaign details: {str(e)}", "danger")
        return redirect(url_for('marketing.list_campaigns'))
