# Railway Deployment Setup Instructions

## 📋 Required Environment Variables

Configure these environment variables in your Railway project dashboard:

### 🔐 Security Settings

```bash
SECRET_KEY=your-super-secret-key-here-generate-new-one
DEBUG=False
```

**Generate a new SECRET_KEY:**
```bash
python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'
```

### 🌐 Domain Configuration

```bash
# Add your Railway domain and any custom domains
ALLOWED_HOSTS=backend-lamis-production.up.railway.app,yourdomain.com,www.yourdomain.com
```

### 🔗 CORS Configuration

```bash
# Add your frontend domains (localhost for development, production domains for deployment)
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend.vercel.app,https://yourdomain.com
```

### 💾 Database Configuration

Railway automatically provides `DATABASE_URL` when you add a PostgreSQL database plugin.
**No manual configuration needed!**

## 🚀 Setup Steps

### 1. Add PostgreSQL Database
- In Railway dashboard, click "New" → "Database" → "PostgreSQL"
- Railway will automatically set `DATABASE_URL`

### 2. Configure Environment Variables
- Go to your backend service → "Variables" tab
- Add the variables listed above
- Click "Deploy" to apply changes

### 3. Current Configuration

**Backend URL:** `https://backend-lamis-production.up.railway.app`

**Required Variables:**
```bash
# Required
ALLOWED_HOSTS=backend-lamis-production.up.railway.app
SECRET_KEY=<generate-new-key>
DEBUG=False

# Add your frontend domain when deployed
CORS_ALLOWED_ORIGINS=http://localhost:3000,https://your-frontend-domain.vercel.app
```

## ✅ Verify Deployment

After configuring variables, test your API:

```bash
# Should return 200 OK
curl -I https://backend-lamis-production.up.railway.app/api/v1/sections/

# Should return JSON data
curl https://backend-lamis-production.up.railway.app/api/v1/sections/
```

## 🔧 Troubleshooting

### DisallowedHost Error
- Add your Railway domain to `ALLOWED_HOSTS`
- Format: `backend-lamis-production.up.railway.app`

### CORS Error
- Add your frontend domain to `CORS_ALLOWED_ORIGINS`
- Use full URL with protocol: `https://your-frontend.vercel.app`

### Database Connection Error
- Ensure PostgreSQL plugin is added
- Check that `DATABASE_URL` is set automatically by Railway

## 📝 Notes

- Railway provides `DATABASE_URL` automatically - don't override it
- Always use HTTPS in production CORS origins
- Keep `DEBUG=False` in production
- Generate a strong `SECRET_KEY` for production
