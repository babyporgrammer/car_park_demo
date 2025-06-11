# 🚗 Car Park Availability Finder API

A FastAPI-based REST API to find real-time parking availability from NSW Transport's open data.

---

## ✅ Features

- 🔍 `GET /carparks/nearby`: Find nearby car parks by location & radius
- 📊 `GET /carparks/{facility_id}`: View real-time occupancy and status
- 🔐 Requires custom `X-API-Key` header (you define valid keys)
- ⚡ Cached TfNSW data with `diskcache` (live data, refreshed every 30s)
- 🌐 Uses `httpx` for async HTTP requests
- 🔁 Rate-limit and async-ready
- ✅ Auto-generated Swagger UI & schema
- 🧪 Full unit tests using `pytest + httpx`

---

## 🛠️ Setup

1. **python >=3.10**
   Ensure you have Python 3.10 or higher installed.

2. **Clone repo & install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Create `.env` file**
   ```env
   VALID_API_KEYS=cxy
   ```

4. **Run locally**
   ```bash
   uvicorn main:app --reload
   ```

---

## 🚀 Usage

### 🔑 All requests require:
```http
TFNSW_API_KEY：your_tfnws_api_key
X-API-Key: cxy
```

### 🔍 Find Nearby Carparks
```http
GET /carparks/nearby?lat=-33.7&lng=150.9&radius_km=5
```

### 📊 Get Carpark Detail
```http
GET /carparks/26
```

### 🧪 Run Tests
```bash
pytest tests/
```

---

## 📘 OpenAPI/Swagger

- Swagger UI: http://localhost:8000/docs
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## 🧠 Assumptions

- API key security is handled via `X-API-Key` (not OAuth)
- TfNSW data is cached for 30s to balance freshness & performance
- "Almost Full" threshold is 10% (adjustable in code)
- No paging / fuzzy search for facility name; purely ID based
- Lat/lng distance uses Haversine approximation