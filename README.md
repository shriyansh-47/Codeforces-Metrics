# CodeForces Metrics 📊

A **Streamlit-based dashboard** that analyzes and visualizes a Codeforces user's competitive programming profile using real-time data from the **Codeforces API**.

---

## 🚀 Features

- User profile overview (rating, rank, country, organization)
- Rating progression over time
- Contest performance & best rating gain
- Problems solved and skipped analysis
- Index-wise problem distribution (A–Z)
- Interactive charts and clean UI

---

## 🛠️ Tech Stack

- Python
- Streamlit
- Requests
- Pandas
- Codeforces Public API

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/your-username/codeforces-metrics.git
cd codeforces-metrics
```

### 2️⃣ Install Dependencies
```bash
pip install streamlit requests pandas
```

### 3️⃣ Run the Application
```bash
streamlit run app.py
```

The app will be available at:
```
```

---

## 🧪 How It Works

1. Enter a **Codeforces username** in the sidebar.
2. The app fetches data from:
   - user.info
   - user.rating
   - user.status
3. Data is processed and displayed in an interactive dashboard.
4. Charts update dynamically for each user.

---

## 📌 Notes

- Uses public Codeforces APIs
- APIs are rate-limited, avoid excessive refreshes
- Optional caching:
```python
@st.cache_data(ttl=300)
```

## 🧑‍💻 Author

**Shriyansh**  
