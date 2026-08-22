# Nexus AI

A Python-based personal AI voice assistant developed independently by a first-year Computer Science and Engineering student.

Nexus is designed to provide voice-based interaction with an AI system while also performing useful tasks on a local macOS system. The project combines speech recognition, AI APIs, text-to-speech, web search, application control, and a modular skill-based architecture.

The project was developed individually from scratch as a practical exploration of Python, artificial intelligence, automation, API integration, and software engineering.

---

## Overview

Nexus allows users to interact with a computer using natural voice commands.

The assistant can process spoken input, determine the type of request, route the request to the appropriate skill, and provide a spoken response.

The architecture is designed to be modular so that new capabilities can be added without restructuring the entire application.

---

## Key Features

- Voice-based interaction
- Speech-to-text processing
- AI-powered conversational responses
- Text-to-speech output
- Web search
- Application launching and control
- System information retrieval
- File-related operations
- Spotify integration
- Browser integration
- Modular skill system
- Skill-based command routing
- Global activation shortcut
- Graceful shutdown and interruption handling
- Environment-variable based API configuration

---

## Architecture

```text
User Voice
    |
    v
Speech Recognition
    |
    v
Nexus Controller
    |
    v
Skill Router
    |
    +-------------------+
    |         |         |
    v         v         v
 System    Browser   Spotify
  Skills     Skills    Skills
    |         |         |
    +---------+---------+
              |
              v
          AI Backend
              |
              v
        Response Generation
              |
              v
         Text-to-Speech
              |
              v
          User Response
