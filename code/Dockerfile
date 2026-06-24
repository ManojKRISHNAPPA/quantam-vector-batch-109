FROM python:3.12-slim

WORKDIR /app

#SYSTEM DEPEDENCIES REQUIRED FOR PDF PRROCESSING
RUN apt-get update && apt-get  install -y \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*


COPY requirement.txt .

RUN pip install --no-cache-dir -r requirement.txt 

COPY . .

ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]