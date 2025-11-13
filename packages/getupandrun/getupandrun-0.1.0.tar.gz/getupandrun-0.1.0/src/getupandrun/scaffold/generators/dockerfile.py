"""Dockerfile generator for scaffolding."""

from typing import Any


class DockerfileGenerator:
    """Generator for Dockerfile content."""

    @staticmethod
    def generate(service: dict[str, Any], framework: str, service_type: str = "") -> str:
        """
        Generate Dockerfile content for service.

        Args:
            service: Service configuration
            framework: Framework name
            service_type: Type of service (frontend, backend, etc.)

        Returns:
            Dockerfile content
        """
        framework_lower = framework.lower()
        service_type_lower = service_type.lower()

        # React frontend
        if "react" in framework_lower and service_type_lower == "frontend":
            return """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "start"]
"""

        # Vue frontend
        elif "vue" in framework_lower and service_type_lower == "frontend":
            return """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
"""

        # Angular frontend
        elif "angular" in framework_lower and service_type_lower == "frontend":
            return """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 4200

CMD ["npm", "start"]
"""

        # Next.js frontend
        elif "nextjs" in framework_lower or "next.js" in framework_lower or "next" in framework_lower:
            return """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
"""

        # Nuxt.js frontend
        elif "nuxtjs" in framework_lower or "nuxt.js" in framework_lower or "nuxt" in framework_lower:
            return """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
"""

        # NestJS backend
        elif "nestjs" in framework_lower or "nest.js" in framework_lower or "nest" in framework_lower:
            return """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 3000

CMD ["npm", "run", "start:dev"]
"""

        # Node.js backend (Express, etc.)
        elif "node" in framework_lower and service_type_lower == "backend":
            return """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 8000

CMD ["npm", "start"]
"""

        # Fallback: Node.js without clear service type (default to backend port)
        elif "node" in framework_lower and service_type_lower != "frontend":
            return """FROM node:20-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .

EXPOSE 8000

CMD ["npm", "start"]
"""

        elif "python" in framework_lower or "fastapi" in framework_lower or "django" in framework_lower or "flask" in framework_lower:
            return """FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["python", "app.py"]
"""

        elif "postgres" in framework_lower or "postgresql" in framework_lower:
            return """FROM postgres:15-alpine

ENV POSTGRES_DB=${POSTGRES_DB:-app}
ENV POSTGRES_USER=${POSTGRES_USER:-user}
ENV POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-password}

VOLUME ["/var/lib/postgresql/data"]

EXPOSE 5432
"""

        elif "mysql" in framework_lower:
            return """FROM mysql:8.0

ENV MYSQL_DATABASE=${MYSQL_DATABASE:-app}
ENV MYSQL_USER=${MYSQL_USER:-user}
ENV MYSQL_PASSWORD=${MYSQL_PASSWORD:-password}
ENV MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD:-rootpassword}

VOLUME ["/var/lib/mysql"]

EXPOSE 3306
"""

        elif "redis" in framework_lower:
            return """FROM redis:7-alpine

EXPOSE 6379

CMD ["redis-server"]
"""

        elif "mongodb" in framework_lower or "mongo" in framework_lower:
            return """FROM mongo:7.0

ENV MONGO_INITDB_DATABASE=${MONGO_INITDB_DATABASE:-app}
ENV MONGO_INITDB_ROOT_USERNAME=${MONGO_INITDB_ROOT_USERNAME:-admin}
ENV MONGO_INITDB_ROOT_PASSWORD=${MONGO_INITDB_ROOT_PASSWORD:-password}

VOLUME ["/data/db"]

EXPOSE 27017

CMD ["mongod"]
"""

        elif "memcached" in framework_lower:
            return """FROM memcached:1.6-alpine

EXPOSE 11211

CMD ["memcached"]
"""

        elif "rabbitmq" in framework_lower:
            return """FROM rabbitmq:3.12-management-alpine

ENV RABBITMQ_DEFAULT_USER=${RABBITMQ_DEFAULT_USER:-admin}
ENV RABBITMQ_DEFAULT_PASS=${RABBITMQ_DEFAULT_PASS:-password}

EXPOSE 5672 15672

CMD ["rabbitmq-server"]
"""

        elif "kafka" in framework_lower:
            return """FROM apache/kafka:latest

ENV KAFKA_BROKER_ID=1
ENV KAFKA_ZOOKEEPER_CONNECT=zookeeper:2181
ENV KAFKA_ADVERTISED_LISTENERS=PLAINTEXT://kafka:9092
ENV KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR=1

EXPOSE 9092

CMD ["kafka-server-start.sh"]
"""

        else:
            return f"""FROM alpine:latest

WORKDIR /app

# Add your service setup here

CMD ["sh"]
"""

