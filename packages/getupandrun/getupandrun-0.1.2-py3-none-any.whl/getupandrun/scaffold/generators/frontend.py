"""Frontend service file generators."""

from pathlib import Path
from typing import Any


class FrontendGenerator:
    """Generator for frontend service files."""

    @staticmethod
    def generate(service_dir: Path, service: dict[str, Any], framework: str) -> None:
        """
        Generate frontend service files.

        Args:
            service_dir: Service directory
            service: Service configuration
            framework: Framework name
        """
        framework_lower = framework.lower()

        if "react" in framework_lower:
            (service_dir / "src").mkdir(exist_ok=True)
            (service_dir / "public").mkdir(exist_ok=True)

            package_json = """{
  "name": "frontend",
  "version": "1.0.0",
  "scripts": {
    "start": "react-scripts start",
    "build": "react-scripts build",
    "test": "react-scripts test"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-scripts": "5.0.1"
  }
}
"""
            (service_dir / "package.json").write_text(package_json)

            app_js = """import React from 'react';

function App() {
  return (
    <div className="App">
      <header className="App-header">
        <h1>Welcome to GetUpAndRun</h1>
        <p>Your React app is ready!</p>
      </header>
    </div>
  );
}

export default App;
"""
            (service_dir / "src" / "App.js").write_text(app_js)

            index_js = """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""
            (service_dir / "src" / "index.js").write_text(index_js)

            index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>React App</title>
</head>
<body>
  <div id="root"></div>
</body>
</html>
"""
            (service_dir / "public" / "index.html").write_text(index_html)

        elif "vue" in framework_lower:
            (service_dir / "src").mkdir(exist_ok=True)
            (service_dir / "public").mkdir(exist_ok=True)

            package_json = """{
  "name": "frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "vue": "^3.3.4"
  },
  "devDependencies": {
    "@vitejs/plugin-vue": "^4.4.0",
    "vite": "^4.5.0"
  }
}
"""
            (service_dir / "package.json").write_text(package_json)

            # Vite config
            vite_config = """import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 3000
  }
})
"""
            (service_dir / "vite.config.js").write_text(vite_config)

            # App.vue
            app_vue = """<template>
  <div id="app">
    <header>
      <h1>Welcome to GetUpAndRun</h1>
      <p>Your Vue app is ready!</p>
    </header>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}
</style>
"""
            (service_dir / "src" / "App.vue").write_text(app_vue)

            # main.js
            main_js = """import { createApp } from 'vue'
import App from './App.vue'

createApp(App).mount('#app')
"""
            (service_dir / "src" / "main.js").write_text(main_js)

            # index.html
            index_html = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Vue App</title>
</head>
<body>
  <div id="app"></div>
  <script type="module" src="/src/main.js"></script>
</body>
</html>
"""
            (service_dir / "index.html").write_text(index_html)

        elif "angular" in framework_lower:
            # Angular uses Angular CLI, so we'll create a basic structure
            (service_dir / "src" / "app").mkdir(parents=True, exist_ok=True)
            (service_dir / "src" / "assets").mkdir(parents=True, exist_ok=True)

            package_json = """{
  "name": "frontend",
  "version": "1.0.0",
  "scripts": {
    "start": "ng serve --host 0.0.0.0 --port 4200",
    "build": "ng build",
    "test": "ng test"
  },
  "dependencies": {
    "@angular/animations": "^17.0.0",
    "@angular/common": "^17.0.0",
    "@angular/compiler": "^17.0.0",
    "@angular/core": "^17.0.0",
    "@angular/forms": "^17.0.0",
    "@angular/platform-browser": "^17.0.0",
    "@angular/platform-browser-dynamic": "^17.0.0",
    "@angular/router": "^17.0.0",
    "rxjs": "^7.8.0",
    "tslib": "^2.6.0",
    "zone.js": "^0.14.0"
  },
  "devDependencies": {
    "@angular-devkit/build-angular": "^17.0.0",
    "@angular/cli": "^17.0.0",
    "@angular/compiler-cli": "^17.0.0",
    "typescript": "~5.2.0"
  }
}
"""
            (service_dir / "package.json").write_text(package_json)

            # angular.json (simplified)
            angular_json = """{
  "projects": {
    "frontend": {
      "architect": {
        "build": {
          "builder": "@angular-devkit/build-angular:browser",
          "options": {
            "outputPath": "dist/frontend",
            "index": "src/index.html",
            "main": "src/main.ts",
            "polyfills": ["zone.js"]
          }
        },
        "serve": {
          "builder": "@angular-devkit/build-angular:dev-server",
          "options": {
            "port": 4200
          }
        }
      }
    }
  }
}
"""
            (service_dir / "angular.json").write_text(angular_json)

            # app.component.ts
            app_component_ts = """import { Component } from '@angular/core';

@Component({
  selector: 'app-root',
  template: `
    <header>
      <h1>Welcome to GetUpAndRun</h1>
      <p>Your Angular app is ready!</p>
    </header>
  `,
  styles: [`
    header {
      text-align: center;
      padding: 20px;
    }
  `]
})
export class AppComponent {
  title = 'frontend';
}
"""
            (service_dir / "src" / "app" / "app.component.ts").write_text(app_component_ts)

            # app.module.ts
            app_module_ts = """import { NgModule } from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { AppComponent } from './app.component';

@NgModule({
  declarations: [AppComponent],
  imports: [BrowserModule],
  providers: [],
  bootstrap: [AppComponent]
})
export class AppModule { }
"""
            (service_dir / "src" / "app" / "app.module.ts").write_text(app_module_ts)

            # main.ts
            main_ts = """import { platformBrowserDynamic } from '@angular/platform-browser-dynamic';
import { AppModule } from './app/app.module';

platformBrowserDynamic().bootstrapModule(AppModule)
  .catch(err => console.error(err));
"""
            (service_dir / "src" / "main.ts").write_text(main_ts)

            # index.html
            index_html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Angular App</title>
  <base href="/">
  <meta name="viewport" content="width=device-width, initial-scale=1">
</head>
<body>
  <app-root></app-root>
</body>
</html>
"""
            (service_dir / "src" / "index.html").write_text(index_html)

            # tsconfig.json
            tsconfig_json = """{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ES2020",
    "lib": ["ES2020", "dom"],
    "moduleResolution": "node",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true
  }
}
"""
            (service_dir / "tsconfig.json").write_text(tsconfig_json)

        elif "nextjs" in framework_lower or "next.js" in framework_lower or "next" in framework_lower:
            (service_dir / "src" / "app").mkdir(parents=True, exist_ok=True)
            (service_dir / "public").mkdir(exist_ok=True)

            package_json = """{
  "name": "frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "next dev",
    "build": "next build",
    "start": "next start"
  },
  "dependencies": {
    "next": "^14.0.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  }
}
"""
            (service_dir / "package.json").write_text(package_json)

            # next.config.js
            next_config = """/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
}

module.exports = nextConfig
"""
            (service_dir / "next.config.js").write_text(next_config)

            # app/page.js (App Router)
            page_js = """export default function Home() {
  return (
    <main>
      <header>
        <h1>Welcome to GetUpAndRun</h1>
        <p>Your Next.js app is ready!</p>
      </header>
    </main>
  )
}
"""
            (service_dir / "src" / "app" / "page.js").write_text(page_js)

            # app/layout.js
            layout_js = """export const metadata = {
  title: 'Next.js App',
  description: 'Generated by GetUpAndRun',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
"""
            (service_dir / "src" / "app" / "layout.js").write_text(layout_js)

        elif "nuxtjs" in framework_lower or "nuxt.js" in framework_lower or "nuxt" in framework_lower:
            (service_dir / "pages").mkdir(exist_ok=True)
            (service_dir / "components").mkdir(exist_ok=True)
            (service_dir / "public").mkdir(exist_ok=True)

            package_json = """{
  "name": "frontend",
  "version": "1.0.0",
  "scripts": {
    "dev": "nuxt dev",
    "build": "nuxt build",
    "start": "nuxt start"
  },
  "dependencies": {
    "nuxt": "^3.8.0",
    "vue": "^3.3.4"
  }
}
"""
            (service_dir / "package.json").write_text(package_json)

            # nuxt.config.ts
            nuxt_config = """// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  devServer: {
    host: '0.0.0.0',
    port: 3000
  }
})
"""
            (service_dir / "nuxt.config.ts").write_text(nuxt_config)

            # pages/index.vue
            index_vue = """<template>
  <div>
    <header>
      <h1>Welcome to GetUpAndRun</h1>
      <p>Your Nuxt.js app is ready!</p>
    </header>
  </div>
</template>

<script setup>
// Page logic here
</script>

<style scoped>
header {
  text-align: center;
  padding: 20px;
}
</style>
"""
            (service_dir / "pages" / "index.vue").write_text(index_vue)

            # app.vue
            app_vue = """<template>
  <NuxtPage />
</template>
"""
            (service_dir / "app.vue").write_text(app_vue)

