# Replace Lyrics

A local-first web application that lets you replace lyrics in songs while preserving the original melody.

## Current Status

**PHASE 1 & 2 COMPLETE** - MVP foundation with mock processing

### What's Implemented

**Backend (FastAPI):**
- POST `/api/v1/generate` - Accepts song file and lyrics, creates processing job
- GET `/api/v1/jobs/{jobId}` - Returns job status and progress
- GET `/api/v1/jobs/{jobId}/audio` - Returns generated audio (placeholder)
- Mock job processing with realistic progress stages
- In-memory job storage
- CORS enabled for frontend communication

**Frontend (HTML/JS - temporary):**
- Song upload (MP3/WAV) with drag-and-drop
- Lyrics input with character count
- Audio preview for uploaded song
- Generate button (enabled when song + lyrics ready)
- Processing screen with real-time progress polling
- Result screen with audio player and download
- Tab switching between Original/Generated audio
- Error handling and user feedback

**Note:** The frontend is currently a simple HTML/JS implementation because Node.js/npm is not installed on this system. Once Node.js is installed, this will be replaced with a full Next.js + TypeScript + Tailwind CSS application.

## Project Structure

```
replace-lyrics/
├── frontend/
│   └── index.html          # Temporary HTML/JS frontend
├── backend/
│   ├── app/
│   │   ├── main.py         # FastAPI application
│   │   ├── api/
│   │   │   ├── generate.py # Generate endpoint
│   │   │   └── jobs.py     # Job status endpoints
│   │   ├── models/
│   │   │   └── job.py      # Pydantic models
│   │   ├── jobs/
│   │   │   └── job_manager.py # In-memory job storage
│   │   └── services/
│   │       └── mock_processor.py # Mock processing pipeline
│   ├── data/
│   │   └── jobs/           # Job data storage (for future use)
│   ├── requirements.txt    # Python dependencies
│   └── venv/               # Python virtual environment
└── README.md
```

## How to Run

### Backend

1. Navigate to the backend directory:
```bash
cd /Users/3597267/CascadeProjects/replace-lyrics/backend
```

2. Activate the virtual environment:
```bash
source venv/bin/activate
```

3. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

### Frontend

Open `frontend/index.html` in a web browser:
```bash
open /Users/3597267/CascadeProjects/replace-lyrics/frontend/index.html
```

## Testing the End-to-End Flow

1. Open the frontend in your browser
2. Upload an MP3 or WAV file (drag-and-drop or click to select)
3. Preview the original song using the audio player
4. Type or paste new lyrics in the textarea
5. Click "Generate Song"
6. Watch the processing progress through all stages:
   - Uploading song
   - Separating vocals
   - Analyzing melody
   - Aligning lyrics
   - Generating vocals
   - Mixing audio
   - Finalizing MP3
7. When complete, play the result and download the MP3
8. Switch between Original and Generated tabs to compare

## Current Limitations

- **No actual audio processing** - Uses mock processing that simulates the pipeline
- **No real stem separation** - Placeholder service
- **No melody analysis** - Placeholder service
- **No lyrics alignment** - Placeholder service
- **No singing synthesis** - Placeholder service (uses original audio as result)
- **No audio mixing** - Placeholder service
- **In-memory job storage** - Jobs are lost on server restart
- **No file persistence** - Uploaded files are not saved
- **HTML/JS frontend** - Temporary solution until Node.js is installed

## Next Steps (PHASE 3+)

### PHASE 3: FFmpeg Integration
- Install and configure FFmpeg
- Implement real audio validation
- Convert uploaded audio to consistent format

### PHASE 4: Stem Separation
- Research and integrate open-source stem separation (e.g., Spleeter, Demucs)
- Separate vocals from instrumental
- Test independently

### PHASE 5: Melody Analysis
- Extract pitch/F0 from vocals
- Analyze timing and tempo
- Create internal note representation

### PHASE 6: Lyrics Alignment
- Implement syllable detection
- Map lyrics to melody notes
- Add validation for lyrics that don't fit

### PHASE 7: Singing Synthesis
- Research open-source singing synthesis (e.g., DiffSinger, OpenSinger)
- Integrate real model (not TTS)
- Generate vocals with new lyrics

### PHASE 8: Audio Mixing
- Use FFmpeg to mix vocals with instrumental
- Handle volume balancing and normalization
- Generate final MP3

### PHASE 9: Frontend Migration
- Install Node.js
- Migrate to Next.js + TypeScript + Tailwind CSS
- Improve UI/UX

## Technology Stack

**Backend:**
- Python 3.12
- FastAPI 0.109.0
- Uvicorn 0.27.0
- Pydantic 2.5.3

**Frontend (temporary):**
- HTML5
- Vanilla JavaScript
- CSS3

**Frontend (planned):**
- Next.js
- React
- TypeScript
- Tailwind CSS

## API Endpoints

### POST /api/v1/generate
Upload song and lyrics to start generation.

**Request:** multipart/form-data
- `song`: MP3 or WAV file
- `lyrics`: Text string

**Response:**
```json
{
  "jobId": "uuid",
  "status": "QUEUED"
}
```

### GET /api/v1/jobs/{jobId}
Get job status and progress.

**Response:**
```json
{
  "jobId": "uuid",
  "status": "PROCESSING",
  "stage": "GENERATING_VOCALS",
  "progress": 70
}
```

**Status values:** QUEUED, PROCESSING, COMPLETED, FAILED

**Stage values:** UPLOAD_COMPLETE, SEPARATING_VOCALS, ANALYZING_MELODY, ALIGNING_LYRICS, GENERATING_VOCALS, MIXING, FINALIZING, COMPLETED

### GET /api/v1/jobs/{jobId}/audio
Download the generated MP3 (placeholder in current version).

## Development Notes

- The application is designed with service interfaces to allow easy replacement of ML models
- Mock services are used to enable end-to-end testing before integrating real models
- The job system is designed to be replaceable with a real queue (Redis, etc.)
- All audio processing happens on the backend, not in the browser
- The application does not clone or impersonate original singer voices
