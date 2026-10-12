# PageTurners Frontend

PageTurners is a React/Vite frontend for a Geology student learning and academic competition platform. It connects to the FastAPI/PostgreSQL backend when `VITE_API_BASE_URL` is configured, and uses local sample data when it is not.

## Requirements

- Node.js 20+
- npm 10+

## Installation

```bash
npm install
```

## Development

```bash
npm run dev
```

Open the local URL shown by Vite.

## Connecting to the backend

1. Follow [Backend setup](../Backend/README.md) to configure `.env`, install the Python requirements, and start PostgreSQL. For the provided Docker Compose database, set `DATABASE_URL=postgresql+psycopg://pageturners:pageturners@localhost:5432/pageturners`.
2. Run the migrations, seed the initial course and accounts, and start the API from the `Backend` directory:

   ```powershell
   python -m alembic upgrade head
   python seed.py
   python -m uvicorn app.main:app --reload
   ```

3. In `Frontend/.env`, set `VITE_API_BASE_URL=http://localhost:8000/api/v1`, then start Vite with `npm run dev`. Restart Vite after changing `.env`.

The API uses bearer-token authentication. To add learning content, set both seed passwords in `Backend/.env`, run `python seed.py`, and sign in using the configured `SEED_ADMIN_EMAIL` (default `admin@pageturners.org`) and `SEED_ADMIN_PASSWORD`. The **Manage content** link then appears in the sidebar. Its guided form lets administrators create courses for academic levels, add topics, and add lessons and multiple-choice quiz questions. Students can register normally but cannot manage content. The frontend also uses the API for authentication, course and lesson display, quiz answers, progress, profiles, achievements, and leaderboard data. API errors are displayed in the relevant screen; a failed API request does not silently switch to sample data.

The admin content page also lists existing courses and their topics, lessons, and quiz questions. Administrators can edit courses, topics, lessons, and quiz questions or delete individual items; deleting a course or topic also removes its nested content, and deleting a question removes its attempt history. The app asks for confirmation before each deletion.

Password reset is available from the **Forgot password?** link on the sign-in page. It requires a configured SMTP provider in `Backend/.env` and the database migration (`python -m alembic upgrade head`). Reset links are one-use and expire after 30 minutes.

## Build

```bash
npm run build
```

## Preview production build

```bash
npm run preview
```

## Frontend architecture

```text
src/
├── assets/logo/              # Official supplied light/dark brand assets
├── components/               # Reusable UI by product domain
├── pages/                    # Route-level screens
├── layouts/                  # Application shells
├── context/                  # Authentication and theme state
├── hooks/                    # Reusable React hooks
├── services/                 # FastAPI client and local sample-data adapters
├── utils/                    # Pure helpers
├── data/                     # Editable educational/mock content
├── routes/                   # Router and protected route architecture
├── config/                   # Product configuration
└── styles/                   # Global CSS and design tokens
```

## Content editing locations

### Lesson notes

**PATH:** `src/data/lessons/index.js`

Each lesson includes `id`, `courseId`, `topicId`, `title`, `topic`, `order`, `duration`, `completed`, and `content`. Add or edit lesson objects there; the lesson UI consumes them automatically.

### Quiz questions and answers

**PATH:** `src/data/questions/index.js`

Each question contains:
- `question` — question text
- `options` — answer choices with `id` and `text`
- `correctAnswer` — the option id used after submission
- `explanation` — feedback shown after submission
- `courseId` / `topicId` — academic grouping
- `difficulty` — easy/medium/etc.
- `points` — mock score value
- `type` — question type

The question UI never renders `correctAnswer` before submission.

### Courses

**PATH:** `src/data/courses.js`

Add course code, title, academic level, description, category, progress, question count and related metadata here.

### Achievements

**PATH:** `src/data/achievements.js`

### Learning levels

**PATH:** `src/data/learningLevels.js`

Thresholds are configuration/data, not hardcoded inside the UI.

### Mock students

**PATH:** `src/data/students.js`

### Leaderboard

**PATH:** `src/data/leaderboard.js`

## Theme system

`src/context/ThemeContext.jsx` supports:

- Light
- Dark
- System

The preference is persisted under `pageturners-theme`. The resolved theme is written to `data-theme` on the root HTML element, and CSS variables in `src/styles/tokens.css` control the visual system. Theme-specific logic is therefore centralized rather than scattered across components.

## Logo system

The two supplied logo files are preserved exactly in:

- `src/assets/logo/pageturners-light-logo.png`
- `src/assets/logo/pageturners-dark-logo.png`

`src/components/common/Logo.jsx` automatically selects the appropriate supplied asset from the resolved theme. No manual image swapping is required.

## Brand and color system

The design tokens are derived from the visible brand palette: deep violet/purple for primary interaction, warm gold for the book/star identity, and magenta as a restrained accent. Light and dark surfaces are defined separately so dark mode is not simply an inverted light theme.

## Mock authentication

Use the login page with any non-empty email/password. The default form is prefilled with a demo account. Registration also creates a local mock session. User state is stored in local storage only for this frontend phase.

## Backend integration boundary

The pages call service modules such as:

- `src/services/authService.js`
- `src/services/courseService.js`
- `src/services/lessonService.js`
- `src/services/questionService.js`
- `src/services/leaderboardService.js`
- `src/services/profileService.js`
- `src/services/achievementService.js`

These are the intended replacement points when FastAPI is introduced. The backend, database, JWT authentication and authoritative scoring/ranking are intentionally **not included in Phase 1**.

## Important security note

Mock data and mock authentication are for frontend demonstration only. Do not treat client-side points, rankings, answer validation or local storage as authoritative. Phase 2 must move those responsibilities to the backend.
