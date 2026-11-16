FROM python:3.13-slim

# No generar .pyc y mostrar los logs al instante (sin buffer)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primero solo requirements: si el código cambia pero las dependencias no,
# Docker reutiliza esta capa en caché y el build tarda segundos.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

# Usuario sin privilegios: si alguien explota la app, no es root dentro del contenedor
RUN useradd --create-home appuser
USER appuser

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
