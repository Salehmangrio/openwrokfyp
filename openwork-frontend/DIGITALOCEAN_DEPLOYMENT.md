# DigitalOcean Droplet Deployment Guide for OpenWork Frontend

## Prerequisites

Assuming you have:
- DigitalOcean Droplet running Ubuntu 20.04+
- nginx installed and running
- SSL certificate from Let's Encrypt (via Certbot)
- Backend API running on localhost:5000 (optional)
- Both openworkfyp.me and www.openworkfyp.me DNS A records pointing to your Droplet IP

---

## Step 1: Update Nginx Configuration

The `_redirects` and `_headers` files created earlier are **Netlify-specific** and won't work on nginx. Replace them with proper nginx config.

### Option A: Quick Setup (Copy-Paste)

1. SSH into your Droplet:
```bash
ssh root@your_droplet_ip
```

2. Backup your current nginx config:
```bash
sudo cp /etc/nginx/sites-available/openworkfyp.me /etc/nginx/sites-available/openworkfyp.me.backup
```

3. Edit the nginx config:
```bash
sudo nano /etc/nginx/sites-available/openworkfyp.me
```

4. Replace the entire file with the contents from [nginx.conf.example](nginx.conf.example) (located in this repo's root)

5. Verify nginx syntax:
```bash
sudo nginx -t
```

6. Reload nginx:
```bash
sudo systemctl reload nginx
```

### Option B: Manual Setup (If you want to understand each step)

Key configurations needed:

```nginx
# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name openworkfyp.me www.openworkfyp.me;
    return 301 https://www.openworkfyp.me$request_uri;
}

# Redirect apex domain (openworkfyp.me) to www
server {
    listen 443 ssl http2;
    server_name openworkfyp.me;
    return 301 https://www.openworkfyp.me$request_uri;
}

# Main server block
server {
    listen 443 ssl http2;
    server_name www.openworkfyp.me;
    root /var/www/openwork/dist;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;
    add_header X-Content-Type-Options "nosniff" always;

    # SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # robots.txt and sitemap.xml
    location = /robots.txt {
        add_header Content-Type "text/plain";
    }
    location = /sitemap.xml {
        add_header Content-Type "application/xml";
    }
}
```

---

## Step 2: Deploy Frontend Build

1. On your local machine, build the frontend:
```bash
cd openwork-frontend
npm run build
```

2. Upload the `dist/` folder to your Droplet:
```bash
# Using SCP
scp -r dist/* root@your_droplet_ip:/var/www/openwork/dist/

# OR using rsync (faster for updates)
rsync -avz dist/ root@your_droplet_ip:/var/www/openwork/dist/
```

3. Set correct permissions:
```bash
ssh root@your_droplet_ip
sudo chown -R www-data:www-data /var/www/openwork/dist
sudo chmod -R 755 /var/www/openwork/dist
```

---

## Step 3: Verify SSL Certificate

Ensure your Let's Encrypt certificate is valid:

```bash
sudo certbot certificates

# Output should show:
# Certificate Name: openworkfyp.me
# Domains: openworkfyp.me, www.openworkfyp.me
# Expiry Date: [future date]
```

If certificate is missing, run:
```bash
sudo certbot certonly --nginx -d openworkfyp.me -d www.openworkfyp.me
```

---

## Step 4: Test Deployment

### Local Testing
```bash
# Verify meta tags are in the HTML
curl https://www.openworkfyp.me | head -50

# Should see:
# <title>OpenWork — Decentralized Job Marketplace on Blockchain</title>
# <meta property="og:url" content="https://www.openworkfyp.me/" />
```

### Test Domain Redirect
```bash
# Should 301 redirect to www
curl -I https://openworkfyp.me/

# Should return:
# HTTP/2 301
# location: https://www.openworkfyp.me/
```

### Test Static Files
```bash
# robots.txt
curl https://www.openworkfyp.me/robots.txt

# sitemap.xml
curl https://www.openworkfyp.me/sitemap.xml

# manifest.json
curl https://www.openworkfyp.me/manifest.json
```

### Test Security Headers
```bash
curl -I https://www.openworkfyp.me

# Should see:
# Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
# X-Content-Type-Options: nosniff
# X-Frame-Options: SAMEORIGIN
```

---

## Step 5: Submit to Google Search Console

1. Go to https://search.google.com/search-console
2. Select your property (if already added) or add new: `https://www.openworkfyp.me`
3. Verify ownership (if new property)
4. Go to **Sitemaps** in left menu
5. Enter: `https://www.openworkfyp.me/sitemap.xml`
6. Click **Submit**
7. Use **URL Inspection** to test pages

---

## Step 6: Monitor Nginx Logs

Watch for issues in real-time:

```bash
# Access logs
sudo tail -f /var/nginx/log/access.log

# Error logs
sudo tail -f /var/nginx/log/error.log

# Or use journalctl
sudo journalctl -u nginx -f
```

---

## Troubleshooting

### Issue: 404 on /jobs, /about, /blog (SPA routing not working)
**Solution:** Ensure `try_files $uri $uri/ /index.html;` is in the `/` location block

### Issue: robots.txt returns HTML instead of plain text
**Solution:** Add `add_header Content-Type "text/plain";` in robots.txt location block

### Issue: HSTS header not showing
**Solution:** Make sure line is: `add_header Strict-Transport-Security "max-age=31536000; includeSubDomains; preload" always;`

### Issue: SSL certificate not found
**Solution:** Run `sudo certbot certonly --nginx -d openworkfyp.me -d www.openworkfyp.me`

### Issue: API requests failing (if you have backend)
**Solution:** Ensure backend is running on port 5000 and proxy_pass is configured correctly

---

## Regular Maintenance

### Update Frontend (New Deploy)
```bash
# Local: Build new version
npm run build

# Upload to Droplet
rsync -avz dist/ root@your_droplet_ip:/var/www/openwork/dist/

# Reload nginx (usually cached, no reload needed)
ssh root@your_droplet_ip sudo systemctl reload nginx
```

### Renew SSL Certificate (Automatic with certbot)
```bash
# Check renewal status
sudo certbot renew --dry-run

# Manual renewal
sudo certbot renew --force-renewal
```

### Monitor Performance
```bash
# Check disk space
df -h /var/www

# Check nginx status
sudo systemctl status nginx

# Check CPU/Memory
htop
```

---

## Related Files

- `nginx.conf.example` - Complete nginx configuration template
- `public/robots.txt` - Crawler rules
- `public/sitemap.xml` - URL list for crawlers
- `public/manifest.json` - PWA manifest
- `index.html` - Updated with meta tags and JSON-LD

---

## Next Steps: Pre-rendering

The current setup still serves an SPA shell. To unlock full SEO with Google indexing:

1. Read `SEO_PRERENDERING_GUIDE.md`
2. Implement pre-rendering with `@vitejs/plugin-ssr`
3. This will generate static `.html` files for each public route
4. Google will then crawl and index your pages properly

Without pre-rendering, Google sees blank pages despite your meta tags being in the shell.
