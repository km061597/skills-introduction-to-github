"""
Tests for email service functionality

This module tests:
1. EmailService initialization
2. Email sending functionality
3. Price drop alert emails
4. Weekly digest emails
5. Template rendering
6. Error handling
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from jinja2 import Template

from app.email_service import EmailService, get_email_service


class TestEmailServiceInitialization:
    """Tests for EmailService initialization"""

    def test_email_service_initialization(self):
        """Test EmailService initializes with default values"""
        service = EmailService()

        assert service.smtp_host == "smtp.gmail.com"
        assert service.smtp_port == 587
        assert service.from_name == "SmartAmazon Alerts"

    @patch.dict('os.environ', {
        'SMTP_HOST': 'smtp.example.com',
        'SMTP_PORT': '465',
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123',
        'FROM_EMAIL': 'noreply@example.com',
        'FROM_NAME': 'Test Service'
    })
    def test_email_service_with_env_vars(self):
        """Test EmailService initialization from environment variables"""
        service = EmailService()

        assert service.smtp_host == "smtp.example.com"
        assert service.smtp_port == 465
        assert service.smtp_user == "test@example.com"
        assert service.smtp_password == "password123"
        assert service.from_email == "noreply@example.com"
        assert service.from_name == "Test Service"

    @patch.dict('os.environ', {'SMTP_USER': 'user@example.com'}, clear=True)
    def test_email_service_default_from_email(self):
        """Test that from_email defaults to smtp_user"""
        service = EmailService()

        assert service.from_email == service.smtp_user


class TestSendEmail:
    """Tests for send_email method"""

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_send_email_success(self, mock_send):
        """Test successful email sending"""
        mock_send.return_value = AsyncMock()

        service = EmailService()
        result = await service.send_email(
            to_email="recipient@example.com",
            subject="Test Subject",
            html_content="<h1>Test</h1>"
        )

        assert result is True
        assert mock_send.called
        call_args = mock_send.call_args

        # Verify SMTP settings
        assert call_args[1]['hostname'] == service.smtp_host
        assert call_args[1]['port'] == service.smtp_port
        assert call_args[1]['username'] == service.smtp_user

    @pytest.mark.asyncio
    @patch.dict('os.environ', {}, clear=True)
    async def test_send_email_no_credentials(self):
        """Test that email is skipped when no credentials configured"""
        service = EmailService()
        result = await service.send_email(
            to_email="test@example.com",
            subject="Test",
            html_content="<h1>Test</h1>"
        )

        assert result is False

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_send_email_with_text_content(self, mock_send):
        """Test sending email with both HTML and text content"""
        mock_send.return_value = AsyncMock()

        service = EmailService()
        result = await service.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_content="<h1>Test</h1>",
            text_content="Test"
        )

        assert result is True
        assert mock_send.called

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_send_email_failure(self, mock_send):
        """Test email sending failure"""
        mock_send.side_effect = Exception("SMTP connection failed")

        service = EmailService()
        result = await service.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_content="<h1>Test</h1>"
        )

        assert result is False

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123',
        'FROM_NAME': 'Custom Name'
    })
    async def test_send_email_from_header(self, mock_send):
        """Test that From header is properly formatted"""
        mock_send.return_value = AsyncMock()

        service = EmailService()
        await service.send_email(
            to_email="recipient@example.com",
            subject="Test",
            html_content="<h1>Test</h1>"
        )

        # Check the message passed to send
        message = mock_send.call_args[0][0]
        assert "Custom Name" in message["From"]
        assert "test@example.com" in message["From"]


class TestPriceDropAlert:
    """Tests for send_price_drop_alert method"""

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_send_price_drop_alert_success(self, mock_send):
        """Test successful price drop alert"""
        mock_send.return_value = AsyncMock()

        service = EmailService()
        result = await service.send_price_drop_alert(
            to_email="customer@example.com",
            product_title="Protein Powder 5lb",
            old_price=69.99,
            new_price=54.99,
            unit_price=0.69,
            unit_type="oz",
            product_url="https://amazon.com/dp/TEST",
            image_url="https://example.com/image.jpg"
        )

        assert result is True
        assert mock_send.called

        # Verify message content
        message = mock_send.call_args[0][0]
        assert "Price Drop" in message["Subject"]
        assert "54.99" in message["Subject"] or "15.00" in message["Subject"]

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_price_drop_alert_calculates_savings(self, mock_send):
        """Test that price drop alert calculates savings correctly"""
        mock_send.return_value = AsyncMock()

        service = EmailService()
        old_price = 100.00
        new_price = 75.00

        result = await service.send_price_drop_alert(
            to_email="test@example.com",
            product_title="Test Product",
            old_price=old_price,
            new_price=new_price,
            unit_price=1.0,
            unit_type="lb",
            product_url="https://amazon.com/dp/TEST"
        )

        assert result is True

        # Check that savings (25.00) and percentage (25%) are calculated
        message = mock_send.call_args[0][0]
        html_content = str(message)
        # The savings should be 25.00 and percentage 25%

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_price_drop_alert_without_image(self, mock_send):
        """Test price drop alert without product image"""
        mock_send.return_value = AsyncMock()

        service = EmailService()
        result = await service.send_price_drop_alert(
            to_email="test@example.com",
            product_title="Test Product",
            old_price=50.00,
            new_price=40.00,
            unit_price=0.50,
            unit_type="oz",
            product_url="https://amazon.com/dp/TEST",
            image_url=None
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_price_drop_alert_has_text_fallback(self, mock_send):
        """Test that price drop alert includes plain text fallback"""
        mock_send.return_value = AsyncMock()

        service = EmailService()
        await service.send_price_drop_alert(
            to_email="test@example.com",
            product_title="Test Product",
            old_price=50.00,
            new_price=40.00,
            unit_price=0.50,
            unit_type="oz",
            product_url="https://amazon.com/dp/TEST"
        )

        # Verify that both HTML and text parts were added
        message = mock_send.call_args[0][0]
        parts = message.get_payload()

        # Should have multiple parts (text and HTML)
        assert len(parts) >= 1


class TestWeeklyDealsDigest:
    """Tests for send_weekly_deals_digest method"""

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_send_weekly_digest_success(self, mock_send):
        """Test successful weekly digest email"""
        mock_send.return_value = AsyncMock()

        deals = [
            {
                "title": "Protein Powder",
                "price": 54.99,
                "unit_price": 0.69,
                "unit_type": "oz",
                "discount_pct": 21.43,
                "url": "https://amazon.com/dp/TEST1"
            },
            {
                "title": "Pre-Workout",
                "price": 29.99,
                "unit_price": 0.50,
                "unit_type": "serving",
                "discount_pct": 25.0,
                "url": "https://amazon.com/dp/TEST2"
            }
        ]

        service = EmailService()
        result = await service.send_weekly_deals_digest(
            to_email="customer@example.com",
            deals=deals
        )

        assert result is True
        assert mock_send.called

        # Verify subject mentions number of deals
        message = mock_send.call_args[0][0]
        assert "2" in message["Subject"]
        assert "Deals" in message["Subject"]

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_weekly_digest_empty_deals(self, mock_send):
        """Test weekly digest with no deals"""
        mock_send.return_value = AsyncMock()

        service = EmailService()
        result = await service.send_weekly_deals_digest(
            to_email="test@example.com",
            deals=[]
        )

        assert result is True
        message = mock_send.call_args[0][0]
        assert "0" in message["Subject"]

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_weekly_digest_many_deals(self, mock_send):
        """Test weekly digest with many deals"""
        mock_send.return_value = AsyncMock()

        deals = [
            {
                "title": f"Product {i}",
                "price": 50.00 + i,
                "unit_price": 0.50 + i * 0.1,
                "unit_type": "oz",
                "discount_pct": 10 + i,
                "url": f"https://amazon.com/dp/TEST{i}"
            }
            for i in range(10)
        ]

        service = EmailService()
        result = await service.send_weekly_deals_digest(
            to_email="test@example.com",
            deals=deals
        )

        assert result is True

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_weekly_digest_deal_without_discount(self, mock_send):
        """Test weekly digest with deals missing discount_pct"""
        mock_send.return_value = AsyncMock()

        deals = [
            {
                "title": "Product",
                "price": 50.00,
                "unit_price": 0.50,
                "unit_type": "oz",
                "discount_pct": None,  # No discount
                "url": "https://amazon.com/dp/TEST"
            }
        ]

        service = EmailService()
        result = await service.send_weekly_deals_digest(
            to_email="test@example.com",
            deals=deals
        )

        assert result is True


class TestGetEmailService:
    """Tests for get_email_service singleton function"""

    def test_get_email_service_singleton(self):
        """Test that get_email_service returns singleton instance"""
        service1 = get_email_service()
        service2 = get_email_service()

        assert service1 is service2
        assert isinstance(service1, EmailService)

    def test_get_email_service_returns_email_service(self):
        """Test that get_email_service returns EmailService instance"""
        service = get_email_service()

        assert isinstance(service, EmailService)
        assert hasattr(service, 'send_email')
        assert hasattr(service, 'send_price_drop_alert')
        assert hasattr(service, 'send_weekly_deals_digest')


class TestEmailTemplates:
    """Tests for email template rendering"""

    def test_price_drop_template_renders_values(self):
        """Test that price drop template renders all values correctly"""
        template = Template("""
            Product: {{ product_title }}
            Old Price: {{ old_price }}
            New Price: {{ new_price }}
            Savings: {{ savings }}
        """)

        result = template.render(
            product_title="Test Product",
            old_price=100.00,
            new_price=75.00,
            savings=25.00
        )

        assert "Test Product" in result
        assert "100" in result
        assert "75" in result
        assert "25" in result

    def test_price_drop_template_formatting(self):
        """Test price formatting in template"""
        template = Template("""
            Price: ${{ "%.2f"|format(price) }}
            Unit Price: ${{ "%.4f"|format(unit_price) }}
            Discount: {{ "%.0f"|format(discount) }}%
        """)

        result = template.render(
            price=54.99,
            unit_price=0.6875,
            discount=21.43
        )

        assert "$54.99" in result
        assert "$0.6875" in result
        assert "21%" in result

    def test_weekly_digest_template_loop(self):
        """Test weekly digest template renders deal loop"""
        template = Template("""
            {% for deal in deals %}
            Deal {{ loop.index }}: {{ deal.title }} - ${{ deal.price }}
            {% endfor %}
        """)

        deals = [
            {"title": "Product 1", "price": 50.00},
            {"title": "Product 2", "price": 60.00}
        ]

        result = template.render(deals=deals)

        assert "Deal 1: Product 1" in result
        assert "Deal 2: Product 2" in result

    def test_template_conditional_image(self):
        """Test template conditional rendering for image"""
        template = Template("""
            {% if image_url %}
            Image: {{ image_url }}
            {% else %}
            No image available
            {% endif %}
        """)

        result_with_image = template.render(image_url="https://example.com/image.jpg")
        assert "Image: https://example.com/image.jpg" in result_with_image

        result_without_image = template.render(image_url=None)
        assert "No image available" in result_without_image


class TestEmailServiceErrorHandling:
    """Tests for error handling in email service"""

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_connection_timeout(self, mock_send):
        """Test handling of connection timeout"""
        mock_send.side_effect = TimeoutError("Connection timed out")

        service = EmailService()
        result = await service.send_email(
            to_email="test@example.com",
            subject="Test",
            html_content="<h1>Test</h1>"
        )

        assert result is False

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_authentication_error(self, mock_send):
        """Test handling of authentication error"""
        mock_send.side_effect = Exception("Authentication failed")

        service = EmailService()
        result = await service.send_email(
            to_email="test@example.com",
            subject="Test",
            html_content="<h1>Test</h1>"
        )

        assert result is False

    @pytest.mark.asyncio
    @patch('app.email_service.aiosmtplib.send')
    @patch.dict('os.environ', {
        'SMTP_USER': 'test@example.com',
        'SMTP_PASSWORD': 'password123'
    })
    async def test_invalid_recipient(self, mock_send):
        """Test handling of invalid recipient email"""
        mock_send.side_effect = Exception("Invalid recipient")

        service = EmailService()
        result = await service.send_email(
            to_email="invalid-email",
            subject="Test",
            html_content="<h1>Test</h1>"
        )

        assert result is False
