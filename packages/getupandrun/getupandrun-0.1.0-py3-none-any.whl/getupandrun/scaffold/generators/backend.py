"""Backend service file generators."""

from pathlib import Path
from typing import Any, Optional

from getupandrun.gpt.integration import StackConfig


class BackendGenerator:
    """Generator for backend service files."""

    @staticmethod
    def generate(
        service_dir: Path,
        service: dict[str, Any],
        framework: str,
        config: Optional[StackConfig] = None,
    ) -> None:
        """
        Generate backend service files.

        Args:
            service_dir: Service directory
            service: Service configuration
            framework: Framework name
            config: Optional stack configuration to check for SQLite
        """
        framework_lower = framework.lower()
        service_name = service.get("name", "").lower()
        service_type = service.get("type", "").lower()
        
        # Enhanced Django detection: check framework, service name, and description
        # GPT might return "python" as framework even when user says "Django"
        is_django = (
            "django" in framework_lower or
            "django" in service_name or
            (config and "django" in config.description.lower())
        )

        # Check if SQLite is in the stack (embedded database, not separate service)
        has_sqlite = False
        has_postgres = False
        if config:
            for svc in config.services:
                svc_framework = svc.get("framework", "").lower()
                svc_type = svc.get("type", "").lower()
                if "sqlite" in svc_framework:
                    has_sqlite = True
                if svc_type == "database" and ("postgres" in svc_framework or "postgresql" in svc_framework):
                    has_postgres = True

        # Django backend
        if is_django:
            requirements = "Django==4.2\npsycopg2-binary==2.9.9\n"
            (service_dir / "requirements.txt").write_text(requirements)

            # Create Django project structure
            manage_py = """#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)
"""
            (service_dir / "manage.py").write_text(manage_py)

            # Create project directory
            project_dir = service_dir / "project"
            project_dir.mkdir(exist_ok=True)
            (project_dir / "__init__.py").write_text("")

            # Create settings.py with Postgres configuration
            settings_py = """from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-dev-key-change-in-production')

DEBUG = True

ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB', 'app'),
        'USER': os.environ.get('POSTGRES_USER', 'user'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD', 'password'),
        'HOST': os.environ.get('DB_HOST', 'postgres-database'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
"""
            (project_dir / "settings.py").write_text(settings_py)

            # Create urls.py
            urls_py = """from django.contrib import admin
from django.urls import path
from django.http import JsonResponse

def health(request):
    return JsonResponse({'status': 'healthy', 'framework': 'Django'})

def root(request):
    return JsonResponse({'message': 'Welcome to GetUpAndRun', 'status': 'running', 'framework': 'Django'})

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health', health),
    path('', root),
]
"""
            (project_dir / "urls.py").write_text(urls_py)

            # Create wsgi.py
            wsgi_py = """import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
application = get_wsgi_application()
"""
            (project_dir / "wsgi.py").write_text(wsgi_py)

            # Create asgi.py
            asgi_py = """import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
application = get_asgi_application()
"""
            (project_dir / "asgi.py").write_text(asgi_py)

            # Create app.py for Docker CMD
            app_py = """import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
django.setup()

from django.core.management import execute_from_command_line

if __name__ == '__main__':
    # Run migrations
    execute_from_command_line(['manage.py', 'migrate'])
    # Start development server
    execute_from_command_line(['manage.py', 'runserver', '0.0.0.0:8000'])
"""
            (service_dir / "app.py").write_text(app_py)

        # Flask backend
        elif "flask" in framework_lower:
            requirements = "flask==3.0.0\n"
            if has_sqlite:
                requirements += "sqlalchemy==2.0.23\n"
            (service_dir / "requirements.txt").write_text(requirements)

            if has_sqlite:
                app_py = """from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

@app.route('/')
def root():
    return jsonify({'message': 'Welcome to GetUpAndRun', 'status': 'running', 'database': 'SQLite'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy', 'database': 'SQLite'})

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=8000, debug=True)
"""
            else:
                app_py = """from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/')
def root():
    return jsonify({'message': 'Welcome to GetUpAndRun', 'status': 'running'})

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
"""
            (service_dir / "app.py").write_text(app_py)

        # FastAPI backend
        elif "python" in framework_lower or "fastapi" in framework_lower:
            requirements = "fastapi==0.104.1\nuvicorn==0.24.0\n"
            if has_sqlite:
                requirements += "sqlalchemy==2.0.23\naiosqlite==0.19.0\n"
            (service_dir / "requirements.txt").write_text(requirements)

            if has_sqlite:
                app_py = """from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import os

# SQLite database setup
DATABASE_URL = "sqlite+aiosqlite:///./app.db"
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)
Base = declarative_base()

app = FastAPI()

@app.on_event("startup")
async def startup():
    # Create database tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/")
async def read_root():
    return {"message": "Welcome to GetUpAndRun", "status": "running", "database": "SQLite"}

@app.get("/health")
async def health():
    return {"status": "healthy", "database": "SQLite"}

# Example database model
# class Item(Base):
#     __tablename__ = "items"
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String, index=True)
"""
            else:
                app_py = """from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to GetUpAndRun", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
"""
            (service_dir / "app.py").write_text(app_py)

        elif "nestjs" in framework_lower or "nest.js" in framework_lower or "nest" in framework_lower:
            (service_dir / "src").mkdir(exist_ok=True)

            package_json = """{
  "name": "backend",
  "version": "1.0.0",
  "scripts": {
    "build": "nest build",
    "start": "nest start",
    "start:dev": "nest start --watch",
    "start:prod": "node dist/main"
  },
  "dependencies": {
    "@nestjs/common": "^10.2.0",
    "@nestjs/core": "^10.2.0",
    "@nestjs/platform-express": "^10.2.0",
    "reflect-metadata": "^0.1.13",
    "rxjs": "^7.8.1"
  },
  "devDependencies": {
    "@nestjs/cli": "^10.2.0",
    "@nestjs/schematics": "^10.0.3",
    "@types/node": "^20.9.0",
    "typescript": "^5.2.2"
  }
}
"""
            (service_dir / "package.json").write_text(package_json)

            # tsconfig.json
            tsconfig_json = """{
  "compilerOptions": {
    "module": "commonjs",
    "declaration": true,
    "removeComments": true,
    "emitDecoratorMetadata": true,
    "experimentalDecorators": true,
    "allowSyntheticDefaultImports": true,
    "target": "ES2021",
    "sourceMap": true,
    "outDir": "./dist",
    "baseUrl": "./",
    "incremental": true
  }
}
"""
            (service_dir / "tsconfig.json").write_text(tsconfig_json)

            # nest-cli.json
            nest_cli_json = """{
  "$schema": "https://json.schemastore.org/nest-cli",
  "collection": "@nestjs/schematics",
  "sourceRoot": "src"
}
"""
            (service_dir / "nest-cli.json").write_text(nest_cli_json)

            # src/main.ts
            main_ts = """import { NestFactory } from '@nestjs/core';
import { AppModule } from './app.module';

async function bootstrap() {
  const app = await NestFactory.create(AppModule);
  await app.listen(3000);
  console.log('NestJS application is running on: http://0.0.0.0:3000');
}
bootstrap();
"""
            (service_dir / "src" / "main.ts").write_text(main_ts)

            # src/app.module.ts
            app_module_ts = """import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';

@Module({
  imports: [],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}
"""
            (service_dir / "src" / "app.module.ts").write_text(app_module_ts)

            # src/app.controller.ts
            app_controller_ts = """import { Controller, Get } from '@nestjs/common';
import { AppService } from './app.service';

@Controller()
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getHello(): object {
    return { message: 'Welcome to GetUpAndRun', status: 'running' };
  }

  @Get('health')
  getHealth(): object {
    return { status: 'healthy' };
  }
}
"""
            (service_dir / "src" / "app.controller.ts").write_text(app_controller_ts)

            # src/app.service.ts
            app_service_ts = """import { Injectable } from '@nestjs/common';

@Injectable()
export class AppService {
  getHello(): string {
    return 'Hello World!';
  }
}
"""
            (service_dir / "src" / "app.service.ts").write_text(app_service_ts)

        elif "node" in framework_lower:
            package_json = """{
  "name": "backend",
  "version": "1.0.0",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "express": "^4.18.2"
  }
}
"""
            (service_dir / "package.json").write_text(package_json)

            server_js = """const express = require('express');
const app = express();
const PORT = process.env.PORT || 8000;

app.get('/', (req, res) => {
  res.json({ message: 'Welcome to GetUpAndRun', status: 'running' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.listen(PORT, () => {
  console.log(`Server running on port ${PORT}`);
});
"""
            (service_dir / "server.js").write_text(server_js)

