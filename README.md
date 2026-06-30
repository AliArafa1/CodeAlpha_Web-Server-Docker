# Web Server using Docker

A production-grade multi-container web application built with Docker.
Stack: **Flask** (Python web app) + **Nginx** (reverse proxy) + **Docker Compose** (orchestration).

---

## Project Structure

```
Web Server using Docker/
├── app/
│   ├── app.py              # Flask application
│   └── requirements.txt    # Python dependencies
├── nginx/
│   └── nginx.conf          # Nginx reverse proxy config
├── Dockerfile              # Multi-stage container build
├── docker-compose.yml      # Service orchestration
├── .dockerignore           # Build context exclusions
└── README.md               # This file
```

---

## 1. Docker Containerization Basics

### What is Docker?

Docker packages applications into **containers** — lightweight, portable, isolated environments that include everything needed to run the application (code, runtime, libraries, config).

### Key Concepts

| Concept     | Description                                                       |
|-------------|-------------------------------------------------------------------|
| **Image**   | Read-only template (snapshot) used to create containers           |
| **Container** | Running instance of an image                                    |
| **Dockerfile** | Blueprint for building an image                                |
| **Volume**  | Persistent storage outside the container                          |
| **Network** | Connects containers so they can communicate                      |
| **Registry** | Repository for storing/distributing images (e.g., Docker Hub)   |

### Core Commands

```bash
# --- Images ---
docker images                          # List images
docker pull nginx:alpine               # Download an image
docker build -t myapp:latest .         # Build an image from Dockerfile
docker rmi myapp:latest                # Remove an image

# --- Containers ---
docker run -d -p 8080:80 nginx:alpine  # Run container in detached mode
docker ps                              # List running containers
docker ps -a                           # List all containers (including stopped)
docker stop <container_id>             # Stop a running container
docker start <container_id>            # Start a stopped container
docker restart <container_id>          # Restart a container
docker rm <container_id>               # Remove a stopped container
docker rm -f <container_id>            # Force remove a running container

# --- Inside Containers ---
docker logs <container_id>             # View container logs
docker logs -f <container_id>          # Follow logs in real-time
docker exec -it <container_id> sh      # Open interactive shell inside container
docker inspect <container_id>          # Detailed container metadata

# --- Cleanup ---
docker system prune -a                 # Remove all unused containers, images, networks
docker container prune                 # Remove all stopped containers
docker image prune                     # Remove unused images
```

---

## 2. Deploy & Manage a Web Server Inside Docker

### Build the Images

```bash
# Build the Flask app image
docker build -t webserver-app:latest .

# Pull the Nginx image
docker pull nginx:1.27-alpine
```

### Run Containers Manually

```bash
# Run Flask app container
docker run -d --name flask_app -p 5000:5000 webserver-app:latest

# Run Nginx as reverse proxy
docker run -d --name nginx_proxy -p 80:80 `
  -v ${PWD}/nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro `
  --link flask_app:app nginx:1.27-alpine
```

### Or use Docker Compose (recommended)

```bash
# Build and start all services
docker compose up -d

# Rebuild after code changes
docker compose up -d --build

# Check status
docker compose ps
```

### Verify Deployment

```bash
# Test the web server
curl http://localhost:80
curl http://localhost:80/health
curl http://localhost:80/info

# Or use PowerShell
Invoke-RestMethod -Uri "http://localhost:80"
Invoke-RestMethod -Uri "http://localhost:80/health"
Invoke-RestMethod -Uri "http://localhost:80/echo" -Method POST -Body '{"test":"data"}' -ContentType "application/json"
```

---

## 3. Container Lifecycle & Commands

### Lifecycle States

```
                    docker build
                   +------------+
                   |   Image    |
                   +-----+------+
                         |
                   docker run
                         |
                   +-----v------+
            +------|  Created   |------+
            |      +-----+------+      |
            |            |             |
       docker start   docker start   docker create
            |            |             |
      +-----v------+    |        +-----v------+
      |  Running   |    |        |  Created   |
      +-----+------+    |        +------------+
            |           |
       docker stop      |
            |           |
      +-----v------+    |
      |  Stopped   |<---+
      +-----+------+
            |
       docker rm
            |
      +-----v------+
      |  Removed   |
      +------------+
```

### Practical Examples

```bash
# 1. Create a container without starting it
docker create --name my_container nginx:alpine

# 2. Start it
docker start my_container

# 3. Pause / Unpause (freezes processes)
docker pause my_container
docker unpause my_container

# 4. Stop gracefully (SIGTERM + timeout)
docker stop my_container

# 5. Kill immediately (SIGKILL)
docker kill my_container

# 6. Restart
docker restart my_container

# 7. Remove
docker rm my_container
```

---

## 4. Monitor Container Health & Troubleshoot

### Health Checks

This project uses **Docker HEALTHCHECK**:
- Checks `/health` endpoint every **30 seconds**
- Timeout after **10 seconds**
- **3 retries** before marking unhealthy
- **10-second start period** before checking begins

```bash
# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Inspect health check results
docker inspect --format='{{json .State.Health}}' flask_app
```

### Monitoring Commands

```bash
# Real-time resource usage
docker stats

# Specific container stats
docker stats flask_app nginx_proxy

# View processes running inside container
docker top flask_app

# Live logs
docker logs -f flask_app

# Recent logs with timestamps
docker logs --since 5m flask_app

# Events on the Docker daemon
docker events
```

### Troubleshooting

```bash
# 1. Check container status
docker ps -a

# 2. Check container logs
docker logs flask_app

# 3. Inspect container config & state
docker inspect flask_app

# 4. Exec into container for deep inspection
docker exec -it flask_app sh
# Inside container: ps aux, netstat -tlnp, cat /etc/os-release, etc.

# 5. Check network connectivity
docker exec nginx_proxy sh -c "wget -qO- http://app:5000/health"

# 6. View resource usage history
docker container stats --no-stream flask_app

# 7. Check Docker daemon logs (Windows)
# Event Viewer -> Windows Logs -> Application (search "docker")

# 8. Common issues
#   - Port already in use: Change host port mapping
#   - Container exits immediately: Check logs for errors
#   - "No such image": Run docker build first
#   - Network not found: Check docker-compose.yml or docker network ls
```

---

## 5. Container-Based App Deployment Best Practices

### Dockerfile Best Practices

| Practice                     | How We Apply It                                      |
|------------------------------|------------------------------------------------------|
| **Multi-stage builds**       | Builder stage for deps, final stage is minimal       |
| **Minimal base images**      | `python:3.12-slim` instead of full `python:3.12`     |
| **Non-root user**            | `appuser` with limited permissions                   |
| **Layer caching**            | `requirements.txt` copied & installed before code    |
| **`.dockerignore`**          | Prevents sending unnecessary files to build context  |
| **Explicit `EXPOSE`**        | Documents which ports the container uses             |
| **`HEALTHCHECK`**            | Docker monitors app health automatically             |
| **Fixed versions**           | Pinned `flask==3.1.1` — no surprise upgrades         |

### Docker Compose Best Practices

| Practice                     | How We Apply It                                      |
|------------------------------|------------------------------------------------------|
| **Service dependency order** | `depends_on` with `condition: service_healthy`       |
| **Resource limits**          | CPU & memory limits prevent resource starvation      |
| **Restart policy**           | `unless-stopped` for automatic recovery              |
| **Custom networks**          | Isolated `webnet` network — no `--link` needed       |
| **Read-only volumes**        | Nginx config mounted `:ro` (read-only)               |
| **Health checks**            | Compose-level health checks for orchestration        |
| **Environment variables**    | Config via `environment:` not hardcoded              |

### General Best Practices

```bash
# Tag images meaningfully (not just 'latest')
docker build -t webserver-app:1.0.0 .
docker tag webserver-app:1.0.0 webserver-app:latest

# Use a container registry for versioned deploys
docker tag webserver-app:1.0.0 myrepo/webserver-app:1.0.0
docker push myrepo/webserver-app:1.0.0

# Never store secrets in images — use Docker secrets or env files
# docker secret create db_password ./password.txt

# Scan images for vulnerabilities
docker scout quickview webserver-app:latest

# Always set memory limits in production
# (Already configured in docker-compose.yml)

# Use read-only root filesystem when possible
# (Add `read_only: true` to compose service)

# Log to stdout/stderr — never to files inside the container
# (Gunicorn already logs to stdout with --access-logfile -)

# Keep containers ephemeral — treat them as disposable
```

---

## Quick Start

```bash
# 1. Build and start everything
docker compose up -d --build

# 2. Verify all services are healthy
docker compose ps
curl http://localhost:80
curl http://localhost:80/health

# 3. Scale to multiple app instances
docker compose up -d --scale app=3

# 4. View real-time logs
docker compose logs -f

# 5. Stop everything
docker compose down

# 6. Stop and remove volumes too
docker compose down -v
```

---

## API Endpoints

| Method | Path       | Description                |
|--------|------------|----------------------------|
| GET    | `/`        | Service info               |
| GET    | `/health`  | Health check with uptime   |
| GET    | `/info`    | Container & platform info  |
| POST   | `/echo`    | Echo back JSON payload     |
# CodeAlpha_Web-Server-Docker
