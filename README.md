# SignLens

A real-time street sign detection and translation web application.

## Features

- Upload or capture street sign images via webcam
- Automatic text extraction from signs
- Translation into 10 languages
- Clean responsive UI

## Supported Languages

- Kannada
- Telugu
- Tamil
- Marathi
- Malayalam
- Hindi
- English
- French
- Spanish
- Arabic

## Tech Stack

- **Backend:** Java 17, Spring Boot 3.2, Maven
- **Frontend:** HTML, CSS, JavaScript
- **AI:** Vision API for OCR and translation

## Getting Started

### Prerequisites
- Java 17+
- Maven 3.8+

### Run locally

```bash
export ANTHROPIC_API_KEY=your_api_key
mvn spring-boot:run
```

Open `http://localhost:8080` in your browser.

## API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| GET | `/api/languages` | List supported languages |
| POST | `/api/process-image` | Upload image for OCR + translation |

## Project Structure

```
src/
└── main/
    ├── java/com/signlens/
    │   ├── SignLensApplication.java
    │   ├── controller/SignLensController.java
    │   ├── service/AIVisionService.java
    │   └── model/
    └── resources/
        ├── application.properties
        └── static/index.html
```

## License

MIT
