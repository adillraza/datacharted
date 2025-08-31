# 🚀 DataCharted Development Guide

## 📱 **Local Development Server Options**

Your DataCharted app can now be accessed locally even when you close the terminal! Choose from these options:

### **Option 1: Quick Start (Interactive)**
```bash
./start_dev.sh
```
- ✅ **Simple**: Just run the script
- ✅ **Interactive**: See logs in real-time
- ❌ **Terminal Required**: Must keep terminal open
- 💡 **Best for**: Active development and debugging

### **Option 2: Background Server (Recommended)**
```bash
./start_dev_background.sh
```
- ✅ **Persistent**: Server keeps running after closing terminal
- ✅ **Always Accessible**: `http://localhost:5000` always works
- ✅ **Logs Saved**: All output saved to `dev_server.log`
- 💡 **Best for**: Daily development workflow

### **Option 3: macOS Auto-Start (Advanced)**
```bash
# Install the Launch Agent
cp com.datacharted.devserver.plist ~/Library/LaunchAgents/
launchctl load ~/Library/LaunchAgents/com.datacharted.devserver.plist
```
- ✅ **Automatic**: Starts when you log in
- ✅ **Persistent**: Always running
- ❌ **Complex**: Requires setup
- 💡 **Best for**: Set-and-forget development

## 🎯 **Quick Start (Recommended)**

1. **Start the server in background:**
   ```bash
   ./start_dev_background.sh
   ```

2. **Your app is now accessible at:**
   - 🌐 **Local**: http://localhost:5000
   - 🌐 **Network**: http://192.168.18.176:5000

3. **Close your terminal** - the server keeps running!

4. **When you're done developing:**
   ```bash
   ./stop_dev.sh
   ```

## 📊 **Server Management Commands**

### **Check Server Status**
```bash
# Check if Flask is running
ps aux | grep flask

# View live logs
tail -f dev_server.log

# Check what's using port 5000
lsof -i :5000
```

### **Stop the Server**
```bash
./stop_dev.sh
```

### **Restart the Server**
```bash
./stop_dev.sh
./start_dev_background.sh
```

## 🔧 **Development Workflow**

### **Daily Development:**
1. **Morning**: `./start_dev_background.sh`
2. **Code**: Make changes to your app
3. **Test**: Visit `http://localhost:5000`
4. **Evening**: `./stop_dev.sh`

### **Making Changes:**
- **Frontend**: Changes auto-reload (Flask debug mode)
- **Backend**: Restart server: `./stop_dev.sh && ./start_dev_background.sh`
- **Database**: Use `flask db upgrade` if needed

## 🐛 **Troubleshooting**

### **Port Already in Use**
```bash
# Find what's using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or just restart
./stop_dev.sh && ./start_dev_background.sh
```

### **Server Not Starting**
```bash
# Check logs
cat dev_server.log

# Verify virtual environment
source venv/bin/activate
python -c "import flask; print('Flask OK')"
```

### **Can't Access from Other Devices**
- Ensure `--host=0.0.0.0` is set (already configured)
- Check your firewall settings
- Verify the IP address: `ifconfig | grep inet`

## 🌟 **Benefits of Background Development**

1. **Always Accessible**: Your app is available 24/7 during development
2. **No Terminal Dependency**: Close terminals, switch workspaces, restart apps
3. **Persistent Development**: Server survives system restarts (with Launch Agent)
4. **Easy Testing**: Test on mobile devices, other computers, etc.
5. **Professional Workflow**: Mimics production environment

## 📱 **Access Your App From:**

- **Your Mac**: http://localhost:5000
- **Your Phone**: http://192.168.18.176:5000
- **Other Computers**: http://192.168.18.176:5000
- **Virtual Machines**: http://192.168.18.176:5000

## 🎉 **You're All Set!**

Your DataCharted development environment is now **always accessible** and **professional-grade**! 

**Happy coding! 🚀**
