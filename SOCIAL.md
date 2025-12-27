# 📣 Social Media Announcement Kit
**Release Date:** December 2025
**Version:** 2.1 "The Isolated Learning Update"

---

## 🐦 Twitter / X Thread

**Post 1 (Hook):**
🚀 Massive update to the Argentquest Development Suite!
We've just dropped v2.1, focusing on **Isolated Learning** and **Zero-Friction Setup**.
Run a complete 22-container AI & DevOps stack locally for free.
No cloud bills. No mess on your host machine.
👇 What's new? #FastAPI #Docker #DevOps #SelfHosted

**Post 2 (The VM):**
🐧 **New Kubuntu 24.04 VM Guide**
We now officially recommend running the stack in a dedicated VirtualBox VM.
- Keeps your main OS clean ✨
- True "Production-like" Linux environment 🏭
- Safe sandbox to learn system admin skills 🛡️
Full guide included!

**Post 3 (Automation):**
🤖 **Automated Setup Scripts**
Gone are the manual steps.
- **Windows:** PowerShell script creates the VM for you.
- **Linux:** Bash script installs Docker, VS Code, Python 3.13, and sets up the repo.
- **Nginx:** Python script auto-configures all 14 proxy hosts. 🪄

**Post 4 (Docs):**
📚 **Docs Overhaul**
We've rewritten *everything*.
- `PORT_GUIDE.md`: No more port conflicts.
- `DEBUG_SETUP.md`: Modernized for 2025.
- `FAQ.md`: Now with LAN access & troubleshooting guides.
Clear, concise, and accurate.

**Post 5 (CTA):**
Ready to build your own AI cloud?
Clone the repo and start the scripts.
🔗 [Link to Repository]
Build locally. Learn globally. 🌍
#OpenSource #Python #AI

---

## 💼 LinkedIn Post

**Headline: Building a Production-Grade AI Platform on Your Laptop (Without the Cloud Bill)**

I'm excited to announce major updates to the **Argentquest Development Suite (v2.1)**. 🚀

This project has always been about bringing enterprise-grade architecture—FastAPI microservices, vector databases, object storage, and AI agents—down to a local environment that anyone can run.

**What's new in this release?**

🐧 **The "Isolated Learning" Strategy**
We've shifted our primary deployment model to a **Kubuntu 24.04 Virtual Machine**. This isn't just about running code; it's about providing a safe, isolated sandbox where developers can master Linux system administration, networking, and Docker security without risking their personal machine configuration.

⚡ **Hyper-Automation**
We've removed the friction from setup.
*   **Infrastructure**: PowerShell/Bash scripts to provision the VM and install Docker/VSCode automatically.
*   **Networking**: A Python automation script that detects running containers and instantly configures Nginx Proxy Manager with SSL.

📚 **Documentation as a Product**
We treated our docs like code—refactoring them for accuracy. Whether you're debugging a port conflict or setting up bridged LAN access, there is now a verified guide for it.

**Why this matters:**
Cloud skills are best learned by *doing*. By self-hosting this stack (Postgres, MongoDB, Redis, MinIO, n8n, etc.), you gain the architectural intuition that certifications simply can't teach.

Check it out on GitHub: [Link]

#DevOps #FastAPI #Docker #SelfHosted #SystemArchitecture #Linux #Learning

---

## 🤖 Reddit Post (r/selfhosted / r/docker)

**Title:** [Update] Run a 22-Container AI/DevOps Stack Locally (FastAPI, PGVector, Mongo, MinIO) - Now with Automated VM Setup!

Hey everyone,

I've posted about the **Argentquest Development Suite** before—a localized "cloud in a box" that replaces $300/mo of Azure services with local Docker containers.

We just pushed **v2.1**, which is a massive quality-of-life update.

### What is it?
A single Docker Compose stack giving you:
*   **Dual FastAPI** (Dev + Prod)
*   **Databases:** PostgreSQL 16 (w/ pgvector), MongoDB 8, Redis
*   **Storage:** MinIO (S3 compatible)
*   **Tools:** Portainer, pgAdmin, VS Code Server, Jupyter, n8n, MCP Inspector
*   **Monitoring:** Beszel & Heimdall Dashboard

### What's New?

**1. The "Isolated Learning" VM Approach**
We realized that polluting your host machine with dev tools sucks. We now provide a streamlined guide (and scripts!) to run everything in a **Kubuntu 24.04 Virtual Machine**.
*   **Benefits:** Matches production Ubuntu servers exactly. If you break it, just trash the VM and re-run the script.
*   **Networking:** We nailed the Bridged Networking setup so you can access the stack from any device on your LAN (great for testing on mobile).

**2. Automated Everything**
*   **VM Creation:** One script to spin up the VM (Windows/Linux).
*   **Environment Setup:** One script to install Docker, Python 3.13, and VS Code inside the VM.
*   **Nginx Proxy:** A Python script that talks to the NPM API and auto-configures all your subdomains (`api.pocmaster...`, `portainer...`, etc.). No more manual clicking!

**3. Validated Docs**
We spent the last week verifying every single markdown file. If the doc says "Port 8086", the container is actually listening on 8086.

**Repository:** [Link to GitHub]

Feedback welcome! We're trying to make this the ultimate "Learn Backend Architecture" starter kit.

---

## 💬 Discord / Community Announcement

**@everyone 🚨 Big Update: v2.1 "Isolated Learning" is Live!**

We've just merged a major overhaul to the documentation and setup process.

**Highlights:**
*   🆕 **VirtualBox Guide:** Complete walkthrough for setting up Kubuntu 24.04 with Bridged Networking.
*   🔌 **LAN Access:** Updated FAQ on how to connect to your stack from your laptop/phone on the same WiFi.
*   ⚡ **Zero-Touch Setup:** New scripts handle everything from creating the VM to configuring Nginx proxies.
*   🧹 **Cleanup:** Fixed all port confusions in `PORT_GUIDE.md` and modernized `DEBUG_SETUP.md`.

**Action Items:**
1.  User `git pull` to get the latest scripts and docs.
2.  Check out `VirtualBox.md` if you want to migrate to a clean VM setup.
3.  Run `python scripts/npm-simple-setup.py` if your proxy hosts are acting up.

Happy coding! 🐧
