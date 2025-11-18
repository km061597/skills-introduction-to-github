"""
Email service for price alerts and notifications

Sends HTML emails using aiosmtplib with Jinja2 templates
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
from typing import List, Optional
import os

from .logging_config import get_logger


logger = get_logger(__name__)


class EmailService:
    """
    Email service for sending notifications
    """

    def __init__(self):
        """
        Initialize email service with SMTP configuration
        """
        self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.smtp_user = os.getenv("SMTP_USER", "")
        self.smtp_password = os.getenv("SMTP_PASSWORD", "")
        self.from_email = os.getenv("FROM_EMAIL", self.smtp_user)
        self.from_name = os.getenv("FROM_NAME", "SmartAmazon Alerts")

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """
        Send an email

        Args:
            to_email: Recipient email address
            subject: Email subject
            html_content: HTML email body
            text_content: Plain text email body (fallback)

        Returns:
            True if sent successfully, False otherwise
        """
        if not self.smtp_user or not self.smtp_password:
            logger.warning("SMTP credentials not configured, skipping email")
            return False

        try:
            # Create message
            message = MIMEMultipart("alternative")
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email
            message["Subject"] = subject

            # Add text and HTML parts
            if text_content:
                text_part = MIMEText(text_content, "plain")
                message.attach(text_part)

            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                start_tls=True
            )

            logger.info(
                f"Email sent successfully to {to_email}",
                extra={'extra_data': {'recipient': to_email, 'subject': subject}}
            )

            return True

        except Exception as e:
            logger.error(
                f"Failed to send email to {to_email}: {e}",
                extra={'extra_data': {'recipient': to_email, 'error': str(e)}},
                exc_info=True
            )
            return False

    async def send_price_drop_alert(
        self,
        to_email: str,
        product_title: str,
        old_price: float,
        new_price: float,
        unit_price: float,
        unit_type: str,
        product_url: str,
        image_url: Optional[str] = None
    ) -> bool:
        """
        Send a price drop alert email

        Args:
            to_email: Recipient email
            product_title: Product title
            old_price: Previous price
            new_price: New (lower) price
            unit_price: Unit price ($/oz, etc.)
            unit_type: Unit type (oz, count, etc.)
            product_url: Link to product
            image_url: Product image URL

        Returns:
            True if sent successfully
        """
        savings = old_price - new_price
        savings_pct = (savings / old_price) * 100

        html_template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #0066cc; color: white; padding: 20px; text-align: center; }
        .content { background: #f9f9f9; padding: 20px; }
        .product { background: white; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .product-image { max-width: 200px; height: auto; }
        .price-old { text-decoration: line-through; color: #999; font-size: 18px; }
        .price-new { color: #00aa00; font-size: 28px; font-weight: bold; }
        .savings { background: #ff3333; color: white; padding: 10px; border-radius: 5px; display: inline-block; }
        .button { background: #0066cc; color: white; padding: 15px 30px; text-decoration: none; border-radius: 5px; display: inline-block; margin: 20px 0; }
        .footer { text-align: center; color: #999; font-size: 12px; margin-top: 30px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 Price Drop Alert!</h1>
        </div>

        <div class="content">
            <div class="product">
                {% if image_url %}
                <img src="{{ image_url }}" alt="{{ product_title }}" class="product-image">
                {% endif %}

                <h2>{{ product_title }}</h2>

                <p>
                    <span class="price-old">${{ "%.2f"|format(old_price) }}</span>
                    →
                    <span class="price-new">${{ "%.2f"|format(new_price) }}</span>
                </p>

                <p>
                    <strong>Unit Price:</strong> ${{ "%.4f"|format(unit_price) }}/{{ unit_type }}
                </p>

                <div class="savings">
                    Save ${{ "%.2f"|format(savings) }} ({{ "%.0f"|format(savings_pct) }}% OFF!)
                </div>

                <p>
                    <a href="{{ product_url }}" class="button">View on Amazon →</a>
                </p>
            </div>

            <p><strong>💡 Why you're seeing this:</strong> This product dropped below your target price!</p>

            <p><em>Act fast - deals like this don't last long!</em></p>
        </div>

        <div class="footer">
            <p>You're receiving this because you set a price alert for this product.</p>
            <p><a href="#">Manage your alerts</a> | <a href="#">Unsubscribe</a></p>
            <p>© 2025 SmartAmazon. We earn from qualifying purchases.</p>
        </div>
    </div>
</body>
</html>
        """)

        html_content = html_template.render(
            product_title=product_title,
            old_price=old_price,
            new_price=new_price,
            unit_price=unit_price,
            unit_type=unit_type,
            savings=savings,
            savings_pct=savings_pct,
            product_url=product_url,
            image_url=image_url
        )

        text_content = f"""
Price Drop Alert!

{product_title}

Was: ${old_price:.2f}
Now: ${new_price:.2f}

Save ${savings:.2f} ({savings_pct:.0f}% OFF!)

Unit Price: ${unit_price:.4f}/{unit_type}

View on Amazon: {product_url}

---
You're receiving this because you set a price alert for this product.
        """

        subject = f"🔥 Price Drop: {product_title} - Save ${savings:.2f}!"

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content,
            text_content=text_content
        )

    async def send_weekly_deals_digest(
        self,
        to_email: str,
        deals: List[dict]
    ) -> bool:
        """
        Send weekly deals digest email

        Args:
            to_email: Recipient email
            deals: List of deal dictionaries

        Returns:
            True if sent successfully
        """
        html_template = Template("""
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background: #0066cc; color: white; padding: 20px; text-align: center; }
        .deal { background: white; padding: 15px; margin: 15px 0; border: 1px solid #ddd; border-radius: 5px; }
        .deal-title { font-size: 16px; font-weight: bold; color: #333; }
        .deal-price { color: #00aa00; font-size: 20px; font-weight: bold; }
        .deal-badge { background: #ff3333; color: white; padding: 5px 10px; border-radius: 3px; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Your Weekly Deals Digest</h1>
            <p>Top deals this week - just for you!</p>
        </div>

        <div class="content">
            <p>We found {{ deals|length }} amazing deals this week:</p>

            {% for deal in deals %}
            <div class="deal">
                <div class="deal-title">{{ deal.title }}</div>
                <div class="deal-price">${{ "%.2f"|format(deal.price) }}</div>
                <p>${{ "%.4f"|format(deal.unit_price) }}/{{ deal.unit_type }}</p>
                {% if deal.discount_pct %}
                <span class="deal-badge">{{ "%.0f"|format(deal.discount_pct) }}% OFF</span>
                {% endif %}
                <p><a href="{{ deal.url }}">View on Amazon →</a></p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
        """)

        html_content = html_template.render(deals=deals)

        subject = f"📊 Your Weekly Deals Digest - {len(deals)} Amazing Deals"

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )


# Global email service instance
_email_service = None


def get_email_service() -> EmailService:
    """
    Get global email service instance

    Returns:
        EmailService instance
    """
    global _email_service
    if _email_service is None:
        _email_service = EmailService()
    return _email_service
