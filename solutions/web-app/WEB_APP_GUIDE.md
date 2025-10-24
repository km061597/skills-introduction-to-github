# 🌐 Web-Based Excel to PDF Converter

## Overview
A modern, browser-based solution that requires no software installation on client machines. Perfect for teams and shared environments!

## ✨ Key Features

### 🎨 Beautiful Interface
- **Modern responsive design** - Works on desktop, tablet, and mobile
- **Drag-and-drop upload** - Simply drop your Excel file
- **Real-time feedback** - Instant analysis and visual feedback
- **Interactive sheet selection** - Click cards to select/deselect

### 🧠 Smart Analysis
- **Automatic detection** of optimal settings
- **Visual sheet cards** with key metrics
- **Intelligent recommendations** based on data
- **Live progress tracking**

### 🔒 Secure & Private
- **Server-side processing** - No client-side dependencies
- **Temporary files only** - Auto-cleanup after session
- **No data retention** - Files deleted after processing
- **Session-based** - Private to each user

### 🚀 Easy Deployment
- **Single command startup** - Just run and go
- **No database required** - Stateless design
- **Cross-platform** - Works on any OS
- **Docker-ready** - Easy containerization

---

## 🚀 Quick Start

### Installation

```bash
# Navigate to the web-app folder
cd solutions/web-app

# Create virtual environment (recommended)
python3 -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

### Access the Application

Once started, open your browser and go to:
```
http://localhost:5000
```

The application will be accessible to:
- **Localhost only**: Just you
- **Local network**: Change host to `0.0.0.0` (default)

---

## 📖 Usage Guide

### Step 1: Upload Excel File

**Method 1 - Drag & Drop:**
1. Drag your Excel file from file explorer
2. Drop it onto the upload area
3. Wait for automatic analysis

**Method 2 - Click to Browse:**
1. Click the upload area
2. Select your Excel file
3. Click "Open"

**Supported formats:**
- `.xlsx` - Excel 2007+
- `.xlsm` - Macro-enabled workbooks
- `.xls` - Excel 97-2003 (legacy)

**File size limit:** 50 MB

### Step 2: Review Sheet Analysis

After upload, you'll see:
- **Sheet cards** with metrics for each sheet
- **Rows & columns** count
- **Estimated pages** in final PDF
- **Data density** percentage
- **Recommended orientation** (Portrait/Landscape)

### Step 3: Select Sheets

**To select individual sheets:**
- Click any sheet card to toggle selection
- Selected cards turn green
- Click again to deselect

**To select all sheets:**
- Click "Select All Sheets" button
- Click again to deselect all

### Step 4: Customize Settings

**Orientation:**
- **Auto** - Application decides (recommended)
- **Portrait** - Vertical layout
- **Landscape** - Horizontal layout

**Scale:**
- Percentage to scale content (25-200%)
- 100% = no scaling
- <100% = shrink (fit more)
- >100% = enlarge (fewer items per page)

**Margins (in inches):**
- **Left/Right**: Default 0.5"
- **Top/Bottom**: Default 0.75"
- Smaller = more content
- Larger = more whitespace

**Options:**
- **Include Headers/Footers**: Adds page numbers, dates, sheet names
- **Print Gridlines**: Shows cell borders (good for data tables)

### Step 5: Generate PDF

1. Click "🎯 Generate PDF" button
2. Wait for progress bar to complete
3. PDF will automatically download
4. Check your browser's download folder

### Step 6: Upload New File (Optional)

- Click "🔄 Upload New File" to start over
- Or refresh the page

---

## 🏗️ Deployment Options

### Option 1: Local Development (Default)

```bash
python app.py
```

Access at: `http://localhost:5000`

### Option 2: Production Server (Gunicorn)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

**Explanation:**
- `-w 4` - 4 worker processes
- `-b 0.0.0.0:5000` - Bind to all interfaces, port 5000

### Option 3: Docker Container

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]
```

Build and run:

```bash
# Build image
docker build -t excel-to-pdf .

# Run container
docker run -p 5000:5000 excel-to-pdf
```

Access at: `http://localhost:5000`

### Option 4: Cloud Deployment

#### Heroku:

```bash
# Create Procfile
echo "web: gunicorn app:app" > Procfile

# Create runtime.txt
echo "python-3.11.0" > runtime.txt

# Deploy
heroku create your-app-name
git push heroku main
```

#### AWS (Elastic Beanstalk):

```bash
# Install EB CLI
pip install awsebcli

# Initialize
eb init -p python-3.11 excel-to-pdf

# Create environment
eb create excel-to-pdf-env

# Deploy
eb deploy
```

#### DigitalOcean App Platform:

1. Connect GitHub repository
2. Select Python app
3. Set build command: `pip install -r requirements.txt`
4. Set run command: `gunicorn -w 4 -b 0.0.0.0:8080 app:app`
5. Deploy!

---

## 🔧 Configuration

### Environment Variables

Create `.env` file:

```bash
# Flask settings
FLASK_ENV=production
FLASK_SECRET_KEY=your-secret-key-here

# File size limit (in bytes)
MAX_CONTENT_LENGTH=52428800  # 50MB

# Session timeout (in hours)
SESSION_LIFETIME=2

# Upload folder
UPLOAD_FOLDER=/tmp/uploads
PDF_FOLDER=/tmp/pdfs
```

Load in `app.py`:

```python
from dotenv import load_dotenv
load_dotenv()

app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
```

### Custom Port

Change in `app.py`:

```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)  # Change port
```

### File Size Limit

Change in `app.py`:

```python
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB
```

---

## 🛡️ Security Best Practices

### For Production:

1. **Disable Debug Mode:**
   ```python
   app.run(debug=False)
   ```

2. **Use Strong Secret Key:**
   ```python
   import secrets
   app.secret_key = secrets.token_hex(32)
   ```

3. **Add HTTPS:**
   - Use Let's Encrypt SSL certificate
   - Configure nginx/Apache as reverse proxy

4. **Implement Rate Limiting:**
   ```bash
   pip install flask-limiter
   ```

   ```python
   from flask_limiter import Limiter

   limiter = Limiter(
       app,
       key_func=lambda: request.remote_addr,
       default_limits=["100 per hour"]
   )
   ```

5. **File Validation:**
   - Already implemented: file extension check
   - Consider adding: file size check, virus scanning

6. **Cleanup Old Files:**
   ```python
   import atexit
   import shutil

   def cleanup():
       shutil.rmtree(app.config['UPLOAD_FOLDER'])
       shutil.rmtree(app.config['PDF_FOLDER'])

   atexit.register(cleanup)
   ```

7. **Add Authentication (Optional):**
   ```bash
   pip install flask-login
   ```

---

## 📊 Monitoring & Logging

### Add Logging:

```python
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

@app.route('/upload', methods=['POST'])
def upload_file():
    logging.info(f"File upload from {request.remote_addr}")
    # ... rest of code
```

### Health Check Endpoint:

Already included:
```
GET /health
```

Returns:
```json
{
  "status": "healthy",
  "pdf_available": true
}
```

---

## 🐛 Troubleshooting

### Issue: "Address already in use"

**Cause:** Port 5000 is occupied

**Solution:**
```bash
# Find process using port
lsof -i :5000

# Kill process
kill -9 <PID>

# Or use different port
python app.py --port 8080
```

### Issue: Upload fails with large files

**Cause:** Size limit or timeout

**Solution:**
```python
# Increase limits
app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024
```

### Issue: PDF generation hangs

**Cause:** Large Excel file or memory issue

**Solution:**
- Process sheets individually
- Increase server memory
- Implement async processing with Celery

### Issue: "Module not found"

**Solution:**
```bash
pip install --upgrade -r requirements.txt
```

### Issue: Temporary files fill up disk

**Solution:**
Implement automatic cleanup:

```python
from apscheduler.schedulers.background import BackgroundScheduler
import time

def cleanup_old_files():
    """Delete files older than 2 hours"""
    now = time.time()
    for folder in [app.config['UPLOAD_FOLDER'], app.config['PDF_FOLDER']]:
        for file in os.listdir(folder):
            filepath = os.path.join(folder, file)
            if os.path.getmtime(filepath) < now - 7200:  # 2 hours
                os.remove(filepath)

scheduler = BackgroundScheduler()
scheduler.add_job(cleanup_old_files, 'interval', hours=1)
scheduler.start()
```

---

## 🚀 Advanced Features

### Feature 1: Email PDF

Add email functionality:

```python
from flask_mail import Mail, Message

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True

mail = Mail(app)

@app.route('/email-pdf', methods=['POST'])
def email_pdf():
    email = request.json['email']
    msg = Message('Your PDF', recipients=[email])
    with open(session['pdf_path'], 'rb') as f:
        msg.attach('report.pdf', 'application/pdf', f.read())
    mail.send(msg)
    return jsonify({'success': True})
```

### Feature 2: PDF Preview

Add preview before download:

```html
<button onclick="previewPDF()">👁️ Preview</button>

<script>
function previewPDF() {
    window.open(`/preview/${pdfId}`, '_blank');
}
</script>
```

### Feature 3: Batch Processing

Process multiple files:

```python
@app.route('/batch-upload', methods=['POST'])
def batch_upload():
    files = request.files.getlist('files')
    results = []
    for file in files:
        # Process each file
        result = process_file(file)
        results.append(result)
    return jsonify(results)
```

---

## 📈 Performance Optimization

### 1. Caching

```python
from flask_caching import Cache

cache = Cache(app, config={'CACHE_TYPE': 'simple'})

@app.route('/analyze/<file_id>')
@cache.cached(timeout=300)
def get_analysis(file_id):
    # Cached for 5 minutes
    return analysis
```

### 2. Async Processing

```python
from celery import Celery

celery = Celery(app.name, broker='redis://localhost:6379')

@celery.task
def generate_pdf_async(file_path, settings):
    # Long-running task
    return pdf_path
```

### 3. Compression

```python
from flask_compress import Compress

Compress(app)
```

---

## 🎯 Use Cases

### Corporate Environment
- **Deploy on internal server**
- **Restrict to company network**
- **Add SSO authentication**
- **Centralized PDF generation**

### Remote Teams
- **Deploy on cloud platform**
- **Share URL with team**
- **No software installation needed**
- **Works on any device**

### Client Portal
- **Embed in existing web app**
- **White-label interface**
- **API integration**
- **Custom branding**

---

## 🤝 Contributing

Improvements welcome:
1. Fork repository
2. Create feature branch
3. Make changes
4. Add tests
5. Submit pull request

---

## 📄 License

Open source - see LICENSE file

---

## 💡 Pro Tips

1. **Use Chrome/Firefox** - Best compatibility
2. **Enable JavaScript** - Required for interface
3. **Stable internet** - For cloud deployments
4. **Modern browser** - For best experience
5. **Test locally first** - Before deploying

---

Happy converting! 🎉

For issues or questions, check the troubleshooting section or create an issue on GitHub.
