# 🚀 Local Development Guide

## ✅ **Setup Complete!**

Your local development environment is now ready. Here's how to use it:

## 🖥️ **Running the Development Server**

### **Quick Start**
```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Start the development server
export FLASK_APP=run.py
export FLASK_ENV=development
python run.py
```

### **Alternative Method**
```bash
# All in one command
source venv/bin/activate && export FLASK_APP=run.py && export FLASK_ENV=development && python run.py
```

## 🌐 **Accessing Your Local Site**

- **Main Website**: http://localhost:5000
- **Admin Panel**: http://localhost:5000/admin
- **Login Page**: http://localhost:5000/auth/login

## 👤 **Local Admin Credentials**

- **Email**: `admin@localhost`
- **Password**: `admin123`

## 📁 **Local Files**

- **Database**: `app_dev_local.db` (SQLite file in project root)
- **Environment**: `.env` (local configuration)
- **Virtual Environment**: `venv/` directory

## 🔄 **Development Workflow**

### **Making Changes**
1. **Edit Templates**: Changes in `app/templates/` auto-reload
2. **Edit Python Code**: Changes in `app/` auto-reload
3. **View Changes**: Refresh browser to see updates
4. **Check Console**: Watch terminal for errors

### **Testing Your Changes**
1. **Home Page**: Visit http://localhost:5000 to see your new design
2. **Services Section**: Scroll down to see the services you added
3. **Testimonials**: Check the testimonial slider
4. **Admin Panel**: Test admin functionality at http://localhost:5000/admin

## 🛠️ **Common Development Tasks**

### **Database Operations**
```bash
# Create new migration (after model changes)
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Reset database (careful - deletes all data!)
rm app_dev_local.db
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### **Adding New Dependencies**
```bash
# Install new package
pip install package-name

# Update requirements
pip freeze > requirements.txt
```

### **Debugging**
- **Flask Debug Mode**: Enabled automatically in development
- **Error Pages**: Detailed error information shown in browser
- **Console Logs**: Check terminal for print statements and errors
- **Database Browser**: Use DB Browser for SQLite to inspect `app_dev_local.db`

## 📝 **Making Template Changes**

### **Current Home Page Structure**
```
app/templates/main/index.html
├── Hero Section (with stats)
├── 3-Step Process Section
├── Services Section (6 services)
├── Testimonials Slider (5 testimonials)
└── Contact Form CTA
```

### **Editing Services**
- **Location**: Lines 130-240 in `app/templates/main/index.html`
- **Structure**: Each service is a Bootstrap card with icon, title, description
- **Icons**: Using Font Awesome icons
- **Colors**: Using your teal brand colors

### **Editing Testimonials**
- **Location**: Lines 242-393 in `app/templates/main/index.html`
- **Structure**: Bootstrap carousel with 5 testimonials
- **Images**: Currently using placeholder images
- **Navigation**: Automatic sliding + manual controls

## 🎨 **Styling & Branding**

### **Brand Colors (in base.html)**
- **Primary Teal**: `#00B4D8`
- **Secondary Teal**: `#0077B6`
- **Accent Blue**: `#0096C7`
- **Accent Yellow**: `#FFD700`
- **Accent Orange**: `#FF6B35`

### **CSS Location**
- **Main Styles**: `app/templates/base.html` (lines 13-200+)
- **Bootstrap**: CDN loaded (Bootstrap 5.3.0)
- **Icons**: Font Awesome 6.4.0

## 🚀 **Deployment Workflow**

### **Local → Production Process**
1. **Test Locally**: Make sure everything works at http://localhost:5000
2. **Commit Changes**: `git add . && git commit -m "Description"`
3. **Push to GitHub**: `git push origin main`
4. **Auto-Deploy**: GitHub Actions automatically deploys to production

### **Safe Development Practice**
```bash
# 1. Make changes locally
# 2. Test thoroughly
# 3. Commit with descriptive message
git add app/templates/main/index.html
git commit -m "Update services section with new content"

# 4. Push when ready
git push origin main
```

## 🔧 **Troubleshooting**

### **Common Issues**

**Port Already in Use**
```bash
# Kill process on port 5000
lsof -ti:5000 | xargs kill -9
```

**Database Errors**
```bash
# Reset local database
rm app_dev_local.db
python setup_local_dev.py
```

**Import Errors**
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Template Not Updating**
- Hard refresh browser (Cmd+Shift+R on Mac)
- Check terminal for template errors
- Restart Flask server

### **Getting Help**
- **Flask Docs**: https://flask.palletsprojects.com/
- **Bootstrap Docs**: https://getbootstrap.com/docs/5.3/
- **Font Awesome Icons**: https://fontawesome.com/icons

## 📊 **Next Steps**

Now that your local environment is set up, you can:

1. **Review the new home page** at http://localhost:5000
2. **Customize the services** with your actual content
3. **Update testimonials** with real client feedback
4. **Test all functionality** before deploying
5. **Create individual service pages** when ready

**Happy coding! 🎉**
