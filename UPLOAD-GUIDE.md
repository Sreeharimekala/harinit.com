# Harinit Website — Upload Guide for GoDaddy

## Files Included
- index.html    → Home page
- platform.html → Platform page
- services.html → Services page
- about.html    → About page
- contact.html  → Contact page

---

## How to Upload to GoDaddy (File Manager Method)

### Step 1: Log into GoDaddy
1. Go to godaddy.com and sign in
2. Go to **My Products** → find your hosting → click **Manage**

### Step 2: Open File Manager
1. In your cPanel/Hosting Dashboard, click **File Manager**
2. Navigate to the **public_html** folder (this is your website root)

### Step 3: Delete Old Files (if needed)
- If there are existing index.html or other page files, delete them first

### Step 4: Upload All 5 HTML Files
1. Click **Upload** in File Manager
2. Select all 5 HTML files and upload them
3. Make sure they land directly inside **public_html** (not inside a subfolder)

### Step 5: Verify
- Visit https://harinit.com → should show your new Home page
- Visit https://harinit.com/platform.html → Platform page
- Visit https://harinit.com/services.html → Services page
- etc.

---

## Customise Before Uploading

Open each .html file in any text editor (Notepad, VS Code) and update:

| Placeholder | Replace With |
|-------------|-------------|
| info@harinit.com | Your real email |
| +1 (234) 567-890 | Your real phone |
| Your City, Your Country | Your real address |
| Team member names & bios | Your actual team |
| Stats (150+ clients, etc.) | Your real numbers |
| Service descriptions | Your actual services |

---

## Notes
- All 5 pages share the same navigation — clicking any link works automatically
- The Contact form shows a success message on submit (you'll need a backend/Formspree to receive emails — see below)
- Mobile responsive on all screen sizes

## Making the Contact Form Actually Send Emails

Use **Formspree** (free):
1. Go to formspree.io and create a free account
2. Create a new form and get your form ID
3. In contact.html, find the `<form>` tag and change:
   `<form id="contactForm" onsubmit="handleSubmit(event)">`
   to:
   `<form action="https://formspree.io/f/YOUR_FORM_ID" method="POST">`
4. Remove the `onsubmit` JavaScript — Formspree handles the redirect
