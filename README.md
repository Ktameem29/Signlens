# SignLens — Luxury Street Sign Detection & Translation
### Java Spring Boot Edition

A production-grade street sign OCR and translation system built with **Java 17 + Spring Boot 3**, featuring a luxury gold-and-obsidian UI.

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | Java 17, Spring Boot 3.2, Maven |
| **API** | RESTful JSON endpoints |
| **AI Vision** | Claude AI (OCR + Translation) |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Fonts** | Cormorant Garamond, Playfair Display, Montserrat |
| **Theme** | Luxury Gold & Obsidian |

---

## Supported Languages

Kannada · Telugu · Tamil · Marathi · Malayalam · Hindi · English · French · Spanish · Arabic

---

## Project Structure

```
signlens-java/
├── src/
│   └── main/
│       ├── java/com/signlens/
│       │   ├── SignLensApplication.java      ← Main entry point
│       │   ├── controller/
│       │   │   └── SignLensController.java   ← REST API endpoints
│       │   ├── service/
│       │   │   └── AIVisionService.java      ← AI OCR + Translation
│       │   └── model/
│       │       ├── OcrResponse.java          ← Response model
│       │       └── TranslateRequest.java     ← Request model
│       └── resources/
│           ├── application.properties        ← Config
│           └── static/
│               └── index.html                ← Luxury frontend
├── pom.xml                                   ← Maven dependencies
└── README.md
```

---

## Quick Start

### Prerequisites
- Java 17+
- Maven 3.8+

### 1. Set your API key
```bash
export ANTHROPIC_API_KEY=your_api_key_here
```

### 2. Build and run
```bash
mvn spring-boot:run
```

### 3. Open browser
```
http://localhost:8080
```

---

## API Endpoints

### GET /api/health
```json
{ "status": "ok", "service": "SignLens API v2.0", "java": "17.0.x" }
```

### GET /api/languages
Returns list of all 10 supported languages.

### POST /api/process-image
Upload image + language code, get OCR + translation.

**Request:** `multipart/form-data`
- `file` — image file (JPG/PNG/WEBP)
- `language` — BCP-47 code (e.g. `kn`, `te`, `ta`)

**Response:**
```json
{
  "detected_text": "NO PARKING",
  "translated_text": "ನಿಲ್ಲುಗಡೆ ಇಲ್ಲ",
  "confidence": 92.5,
  "target_language": "kn",
  "status": "success"
}
```

---

## Design

The frontend uses a **luxury editorial aesthetic**:
- **Colors:** Obsidian black `#080A0F` with 24-karat gold `#C9A84C` accents
- **Typography:** Cormorant Garamond (display) · Playfair Display (headings) · Montserrat (body)
- **UI:** Roman numeral panel headers · Corner bracket viewfinder · Gold confidence bar · Language chip selector

*SignLens v2.0 · Java Edition*
