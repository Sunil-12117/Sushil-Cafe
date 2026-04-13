# Sushil Cafe — Backend Setup Guide

## Folder Structure
```
sushil-cafe/
  ├── app.py
  ├── requirements.txt
  ├── Procfile
  └── README.md
```

---

## Step 1 — MongoDB Atlas Setup (Free)

1. https://mongodb.com/atlas pe jaao
2. Free account banao
3. "Create a Cluster" → Free M0 select karo
4. Username + Password set karo (yaad rakhna)
5. "Network Access" → "Add IP Address" → "Allow Access from Anywhere"
6. "Connect" → "Drivers" → Connection string copy karo
   Example: `mongodb+srv://sushil:password@cluster0.xxxxx.mongodb.net/`

---

## Step 2 — Render pe Deploy karo (Free)

1. https://github.com pe jaao — new repository banao "sushil-cafe-backend"
2. Apni saari files upload karo (app.py, requirements.txt, Procfile)
3. https://render.com pe jaao — free account banao
4. "New Web Service" → GitHub repo connect karo
5. Settings:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `gunicorn app:app`
6. "Environment Variables" mein yeh add karo:
   - `MONGO_URI` = apni MongoDB connection string
   - `ADMIN_USERNAME` = admin
   - `ADMIN_PASSWORD` = apna password
7. "Deploy" karo!

Render aapko ek URL dega jaise:
`https://sushil-cafe-backend.onrender.com`

---

## Step 3 — Frontend mein Backend URL daalo

`index.html` aur `Admin.html` mein yeh line dhundho:
```javascript
const API = 'http://localhost:5000';
```
Aur replace karo:
```javascript
const API = 'https://sushil-cafe-backend.onrender.com';
```

---

## Local Testing (Optional)

```bash
pip install -r requirements.txt
python app.py
```
Server chalega: http://localhost:5000

---

## API Endpoints

| Method | URL | Kaam |
|--------|-----|------|
| POST | /api/login | Admin login |
| GET | /api/menu | Menu dekhna |
| POST | /api/menu | Dish add karna |
| DELETE | /api/menu/:id | Dish delete karna |
| GET | /api/reservations | Reservations dekhna |
| POST | /api/reservations | Reservation submit karna |
| PUT | /api/reservations/:id | Status update karna |
| GET | /api/feedback | Feedback dekhna |
| POST | /api/feedback | Feedback submit karna |
| GET | /api/orders | Orders dekhna |
| POST | /api/orders | Order place karna |
| PUT | /api/orders/:id | Order status update |
| GET | /api/stats | Dashboard stats |
