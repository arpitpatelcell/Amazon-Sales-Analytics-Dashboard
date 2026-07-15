# Dockerfile — containerize the dashboard so it runs identically anywhere
# (your laptop, a classmate's laptop, or any cloud provider).
#
# Build:  docker build -t amazon-dashboard .
# Run:    docker run -p 8501:8501 amazon-dashboard

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (separate layer = faster rebuilds when only code changes)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the project
COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

ENTRYPOINT ["streamlit", "run", "dashboard/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
