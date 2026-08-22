# Nexus AI

A modular AI voice assistant for macOS/Windows, built entirely with Python.

Nexus is a personal AI assistant designed to understand natural voice commands, provide AI-powered responses, perform system-level tasks, search the web, interact with applications, and continuously communicate with the user through voice.

The project was designed and developed individually by a first-year Bachelor of Technology student specializing in Computer Science and Engineering.

Nexus was created as a practical project to explore artificial intelligence, Python programming, voice interfaces, API integration, automation, modular software architecture, and real-world software development.

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Architecture](#architecture)
- [How Nexus Works](#how-nexus-works)
- [Current Capabilities](#current-capabilities)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Development](#development)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Security](#security)
- [Resources](#resources)
- [Learning Outcomes](#learning-outcomes)
- [Project Goals](#project-goals)
- [Future Development](#future-development)
- [Project Status](#project-status)
- [About the Developer](#about-the-developer)
- [Motivation](#motivation)
- [Acknowledgements](#acknowledgements)
- [License](#license)

---

## Overview

Nexus is a voice-controlled AI assistant designed for macOS.

The system combines speech recognition, artificial intelligence, text-to-speech, web search, application control, file operations, and system information into a single modular application.

Instead of implementing every possible command directly inside the main program, Nexus uses a skill-based architecture.

A central skill router determines which capability should handle a request.

This makes the system easier to understand, maintain, debug, and expand.

The long-term goal of Nexus is to evolve from a basic voice assistant into a more capable personal computing interface.

---

## Key Features

### Voice Interaction

- Voice-based commands
- Speech-to-text processing
- Continuous conversation
- Spoken AI responses
- Natural language interaction

### Artificial Intelligence

- Gemini-powered conversational responses
- AI fallback for requests that do not match a local skill
- Web-grounded AI search
- Natural language understanding

### System Control

- Launch macOS applications
- Open folders
- Retrieve system information
- Check battery information
- Check available storage
- Retrieve RAM information
- Retrieve processor information
- Retrieve system details
- Additional macOS automation capabilities

### Application Integration

- Spotify integration
- Browser integration
- macOS application launching
- Extensible application skill architecture

### Web Capabilities

- Web search
- Current information retrieval
- AI-powered web research
- Search-based responses

### Architecture

- Modular skills
- Central skill router
- Separate controller
- Independent system modules
- Environment-based API configuration

### Developer Experience

- Python virtual environment
- Git version control
- GitHub repository
- `.env` configuration
- `.env.example` template
- Modular project structure

---

## Architecture

```text
                         USER
                           |
                           v
                    Voice Command
                           |
                           v
                 Speech Recognition
                           |
                           v
                  NEXUS CONTROLLER
                           |
                           v
                    SKILL ROUTER
                           |
          +----------------+----------------+
          |                |                |
          v                v                v
      SYSTEM            BROWSER          SPOTIFY
       SKILL             SKILL            SKILL
          |                |                |
          +----------------+----------------+
                           |
                           v
                     SEARCH SKILL
                           |
                           v
                    GEMINI AI CORE
                           |
                           v
                  RESPONSE GENERATION
                           |
                           v
                    TEXT TO SPEECH
                           |
                           v
                    VOICE RESPONSE
                           |
                           v
                         USER
