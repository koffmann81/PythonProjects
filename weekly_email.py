import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from data_processor import get_current_week_dataframe, format_dataframe_for_email, get_schedule_summary

def send_weekly_turnus_report():
    try:
        print("🔄 Generating weekly turnus report…")

        # Generate the current week dataframe (current + next 3 weeks)
        df = get_current_week_dataframe()

        if df.empty:
            print("⚠️ No data available for current period")
            return

        # Format for email
        html_table, text_table = format_dataframe_for_email(df)

        # Get summary statistics
        summary = get_schedule_summary(df)

        # Email configuration
        smtp_server = "smtp.gmail.com"
        port = 587
        sender_email = os.environ.get('SENDER_EMAIL')
        sender_password = os.environ.get('EMAIL_PASSWORD')
        receiver_email = os.environ.get('RECEIVER_EMAIL')

        if not all([sender_email, sender_password, receiver_email]):
            raise ValueError("Missing email configuration. Check environment variables or GitHub secrets.")

        # Create message
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"📅 Weekly Turnus Schedule - {datetime.now().strftime('%d/%m/%Y')}"
        msg["From"] = sender_email
        msg["To"] = receiver_email

        # Create plain text version
        text_content = f"""
# WEEKLY TURNUS SCHEDULE

Generated: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} UTC
Date Range: {summary.get('date_range', 'N/A')}
Total Weeks: {summary.get('total_weeks', 0)}

SCHEDULE:
{text_table}

SHIFT DISTRIBUTION:
{summary.get('shift_distribution', {})}

-----

This is your automated weekly turnus report.
Generated from: koffmann81-pythonprojects-turnus
"""

        # Create HTML version
        shift_dist_html = ""
        if 'shift_distribution' in summary:
            shift_items = [
                f"<li><strong>{shift}:</strong> {count} times</li>"
                for shift, count in summary['shift_distribution'].items()
            ]
            shift_dist_html = f"<ul>{''.join(shift_items)}</ul>"

        html_content = f"""
<html>
<head>
<style>
body {{ font-family: Arial, sans-serif; margin: 20px; }}
h2 {{ color: #2E86AB; border-bottom: 2px solid #2E86AB; padding-bottom: 10px; }}
h3 {{ color: #A23B72; margin-top: 30px; }}
table {{ border-collapse: collapse; width: 100%; margin: 20px 0; }}
th, td {{ border: 1px solid #ddd; padding: 8px; text-align: center; }}
th {{ background-color: #f2f2f2; font-weight: bold; }}
tr:nth-child(even) {{ background-color: #f9f9f9; }}
.info-box {{ background-color: #e8f4f8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
.footer {{ margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; font-size: 12px; color: #666; }}
</style>
</head>
<body>
<h2>📅 Weekly Turnus Schedule</h2>

<div class="info-box">
<strong>Generated:</strong> {datetime.now().strftime('%d/%m/%Y %H:%M:%S')} UTC<br>
<strong>Date Range:</strong> {summary.get('date_range', 'N/A')}<br>
<strong>Total Weeks:</strong> {summary.get('total_weeks', 0)}
</div>

<h3>📊 Your Schedule</h3>
{html_table}

<h3>📈 Shift Distribution</h3>
{shift_dist_html}

<div class="footer">
<p>This is your automated weekly turnus report.<br>
Generated from: <em>koffmann81-pythonprojects-turnus</em></p>
</div>
</body>
</html>
"""

        # Attach parts
        text_part = MIMEText(text_content, "plain", "utf-8")
        html_part = MIMEText(html_content, "html", "utf-8")
        msg.attach(text_part)
        msg.attach(html_part)

        # Send email
        print(f"📧 Sending email to {receiver_email}...")
        with smtplib.SMTP(smtp_server, port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print("✅ Weekly turnus report sent successfully!")
        print(f"📊 Sent {len(df)} weeks of schedule data")

    except Exception as e:
        print(f"❌ Error sending weekly report: {str(e)}")
        # Do not raise error to avoid GitHub Actions failure

if __name__ == "__main__":
    send_weekly_turnus_report()
