VoxGuard – Secure Voice-First AI Agent

Powered by Gemini AI + AI/ML API
A Hackathon Submission by Team AI_Genesis

Overview

VoxGuard is a secure voice-controlled AI agent that executes real-world tasks such as booking rides, sending emails, and managing to-do lists — all through natural speech.
It integrates biometric voice authentication, Gemini AI tool-calling, and the AI/ML API for speech processing to deliver a seamless, hands-free assistant experience.

This project is built for the hackathon with a focus on impact, originality, technical integration, and business value.

Key Features
  Voice Biometric Authentication

The system verifies the speaker’s identity using voice (demo mode accepts all users but structure supports real biometrics).

 Speech-to-Action AI Agent

Users speak naturally, and Gemini AI interprets the intent and triggers backend tools.

 Automated Ride Booking (Uber Deep Link)

Command example:

“Book me a ride from home to office.”

The system generates an Uber deep link via request_uber_ride.

 Email Automation

Command example:

“Send an email to John saying I’ll be late.”

Gemini calls the send_email tool with subject & body automatically inferred.

 To-Do Management

Command example:

“Add a task to buy groceries today evening.”

Uses the add_todo tool to store tasks.

 TTS Responses

AI/ML API can convert responses into speech (frontend ready).

 Tech Stack
AI / Cloud Tools

Gemini AI (Google DeepMind)

AI/ML API (STT, TTS, Speaker Embeddings)
