# VR-LMS Backend (Django + DRF + Channels)

A **Learning Management System (LMS) backend** built with **Django**, **Django REST Framework (DRF)**, and **Django Channels**, designed to power **VR classrooms on DPVR headsets**.  
It enables teachers to create and control lessons, synchronize playback across devices, and monitor student engagement in real time.  

---

## Features & Highlights

- **Multi-tenancy & Organization Support**  
  Manage multiple institutions (schools, organizations) in one platform.  

- **User & Device Binding**  
  Teachers and students log in using **nickname + 4-digit PIN**.  
  Devices (DPVR headsets) are bound by unique device IDs and linked to user accounts.  

- **Course / Class / Lesson Management**  
  Admin interface to create courses, modules, lessons, and schedule sessions.  
  Pre-installed VR lesson APKs can be triggered remotely.  

- **Real-Time Orchestration**  
  Teachers can push playback commands (play, pause, stop) to connected VR devices via WebSockets.  

- **Interaction Tracking & Monitoring**  
  Student devices send interaction events (gaze, clicks, actions) back to the backend.  
  Teacher dashboards can monitor what each student sees in real time.  

- **APIs**  
  REST endpoints (DRF) for resources like users, lessons, sessions, analytics.  
  WebSocket endpoints (Channels) for real-time synchronization.  

- **Admin / Staff Panel**  
  Django Admin for managing organizations, users, classes, lessons, device registrations, etc.  

---

## 🔌 API & WebSocket Endpoints

### Authentication
- `POST /api/login/` — Login using **nickname + 4-digit PIN**

### Classes & Lessons
- `GET  /api/classes/` — List available classes
- `POST /api/session/addLesson/` — Add a lesson to a session

### Session Control
- `POST /api/session/create/` — Create a new session
- `POST /api/session/start/` — Start a session (teacher command)
- `POST /api/session/pause/` — Pause the current session
- `POST /api/session/stop/` — Stop the current session

### Progress & Results
- `GET  /api/results/` — Retrieve student progress/results

### Real-Time Communication
- `WS /websocket/` — WebSocket endpoint for real-time sync (teacher ↔ students)
- `GET /index/` — Demo/test view (basic index page)


## Typical Workflow

Admin/Teacher sets up organizations, classes, lessons via Django Admin.

Students log in with nickname + PIN on DPVR devices (bound to device IDs).

Teacher starts a session, devices connect via WebSockets.

Teacher pushes playback commands to sync lessons across devices.

Students’ interactions (gaze, clicks) are logged and monitored live.

## User Roles
### Student

Logs in with nickname + PIN (and optionally tied to a DPVR device ID).

Can join sessions started by a teacher.

Receives lesson playback commands (play, pause, stop) from the teacher.

Can interact inside VR lessons (gaze, clicks, object selection, quizzes).

Has access to their own progress and results.

Cannot create or manage classes/lessons.

### Teacher

Logs in with nickname + PIN.

Can create classes, lessons, and sessions.

Has control over lesson playback across devices:

Start, pause, stop VR lessons for the whole class.

Add lessons to an existing session.

Can monitor student devices in real-time (viewport, interactions).

Can view results and analytics for their students.

Cannot manage system-wide settings (e.g., add new organizations).

### Admin

Full access through the Django Admin panel.

Manages organizations/schools.

Creates and manages users (teachers & students).

Manages devices (DPVR bindings, registration).

Configures global settings (roles, permissions, content policies).

Can see all courses, lessons, sessions, and results across the system.
