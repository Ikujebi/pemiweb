from flask import request, render_template, abort
from sqlalchemy.orm import joinedload
from sqlalchemy import desc
from database import SessionLocal
from models import SendLog, Recipient, Campaign

def register_sent_routes(app):
    @app.route("/sent_messages")
    def sent_messages():
        try:
            # Query parameters
            page = request.args.get("page", default=1, type=int)
            per_page = request.args.get("per_page", default=20, type=int)
            campaign_id = request.args.get("campaign", default=None, type=int)
            recipient_id = request.args.get("recipient", default=None, type=int)
            sort_by = request.args.get("sort_by", default="id", type=str)
            sort_order = request.args.get("sort_order", default="desc", type=str)

            with SessionLocal() as db:
                query = db.query(SendLog).options(
                    joinedload(SendLog.recipient),
                    joinedload(SendLog.campaign)
                )

                # Apply filters
                if campaign_id:
                    query = query.filter(SendLog.campaign_id == campaign_id)
                if recipient_id:
                    query = query.filter(SendLog.recipient_id == recipient_id)

                # Apply sorting
                sort_column = getattr(SendLog, sort_by, None)
                if sort_column is None:
                    abort(400, description=f"Invalid sort column: {sort_by}")
                if sort_order.lower() == "desc":
                    query = query.order_by(desc(sort_column))
                else:
                    query = query.order_by(sort_column)

                # Pagination
                total_messages = query.count()
                messages = query.offset((page - 1) * per_page).limit(per_page).all()

                # Compute recipient initials safely
                for msg in messages:
                    contact = getattr(msg.recipient, 'email', None) or getattr(msg.recipient, 'phone', None) or ""
                    # Take first letters of first two words
                    msg.recipient_initials = ''.join([n[0].upper() for n in contact.split()[:2]])

            return render_template(
                "sent_messages.html",
                sent_messages=messages,
                page=page,
                per_page=per_page,
                total_messages=total_messages
            )

        except Exception as e:
            return f"Error fetching sent messages: {e}", 500
