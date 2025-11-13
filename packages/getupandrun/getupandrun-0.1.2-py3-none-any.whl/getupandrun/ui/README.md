# GetUpAndRun Web UI

A simple, demo-friendly web interface for GetUpAndRun that allows users to create development environments without using the command line.

## Features

- **Template Selection**: Choose from predefined templates for common stacks
- **Custom Prompts**: Describe your project in natural language
- **Settings Management**: Configure base directory for project creation
- **Project Creation**: Create projects locally or download as ZIP (for Vercel)

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- GetUpAndRun CLI installed (`pip install getupandrun`)
- OpenAI API key set in environment variable

### Installation

1. Install dependencies:
```bash
npm install
```

2. Set up environment variables:
```bash
cp .env.example .env.local
# Edit .env.local and add your OPENAI_API_KEY
```

3. Start the development server:
```bash
npm run dev
```

Or use the CLI command:
```bash
getupandrun ui
```

The UI will be available at `http://localhost:3000`.

## Project Structure

```
ui/
├── app/
│   ├── api/              # API routes
│   │   ├── create/       # Project creation endpoint
│   │   ├── settings/     # Settings management endpoint
│   │   └── templates/    # Templates listing endpoint
│   ├── settings/          # Settings page
│   ├── layout.tsx        # Root layout
│   └── page.tsx          # Main page
├── components/           # React components
│   ├── TemplateCard.tsx
│   ├── TemplateGrid.tsx
│   ├── PromptInput.tsx
│   ├── ProjectForm.tsx
│   └── ProgressSpinner.tsx
├── lib/                  # Utility functions
│   └── settings.ts       # Settings management
└── public/               # Static assets
```

## Development

### Running Locally

```bash
npm run dev
```

### Building for Production

```bash
npm run build
npm start
```

### Linting

```bash
npm run lint
```

## Deployment

### Vercel

The UI is configured for Vercel deployment with automatic deployments on push to `main`.

#### Quick Setup:

1. **Connect Repository**: 
   - Go to [vercel.com](https://vercel.com) → Add New Project
   - Import your Git repository (GitHub/GitLab/Bitbucket)
   - Vercel will automatically set up deployments on push to `main`

2. **Set Root Directory**: 
   - **CRITICAL**: In Project Settings → General → Root Directory, set to `ui/`
   - This tells Vercel where your Next.js app is located

3. **Environment Variables**: 
   - Go to Project Settings → Environment Variables
   - Add `OPENAI_API_KEY`: Your OpenAI API key (required, mark as sensitive)
   - Optional: `PYTHON_PATH` (defaults to `python3`)
   - Optional: `GETUPANDRUN_CLI_PATH` (defaults to `python3 -m getupandrun.cli.main`)

4. **Deploy**: 
   - Click "Deploy" for the first deployment
   - Future pushes to `main` will automatically trigger deployments
   - Preview deployments are created for other branches and PRs

**📖 For detailed deployment instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)**

#### Important Notes:

- **⚠️ Vercel Limitation**: Vercel's Node.js serverless functions **do not have Python available at runtime**. Project creation **will not work on Vercel**.
  
  **Recommended Solution: Deploy to Railway**
  - Railway supports both Node.js and Python in the same deployment
  - See [RAILWAY_DEPLOYMENT.md](../RAILWAY_DEPLOYMENT.md) for full instructions
  - Railway auto-detects and installs both Node.js and Python
  - Project creation works out of the box on Railway

- **Project Creation**: 
  - On Railway/Render: Projects are created and downloaded as ZIP files
  - Locally: Projects are created directly in the filesystem

- **Alternative Platforms**: 
  - **Railway** (recommended): Supports both Node.js and Python ✅
  - **Render**: Supports both Node.js and Python ✅
  - **Fly.io**: Supports both Node.js and Python ✅
  - **Vercel**: Node.js only, Python not available ❌

### Local Deployment

When running locally, projects are created directly in the filesystem at the configured base directory.

## Configuration

### Settings

Users can configure the base directory for project creation via the Settings page (`/settings`). Settings are stored in `~/.getupandrun/ui-config.json`.

### Environment Variables

- `OPENAI_API_KEY`: Required for GPT integration
- `GETUPANDRUN_CLI_PATH`: Optional, full path to getupandrun CLI (defaults to `python3 -m getupandrun.cli.main`)
- `PYTHON_PATH`: Optional, path to Python executable (defaults to `python3`)

## API Routes

### POST /api/create

Creates a new project.

**Request Body:**
```json
{
  "templateKey": "react-node-postgres", // Optional
  "prompt": "React frontend with Node.js backend", // Optional (if no templateKey)
  "projectName": "my-project",
  "baseDirectory": "~/getupandrun-projects/"
}
```

**Response (Local):**
```json
{
  "success": true,
  "projectPath": "/path/to/project"
}
```

**Response (Vercel):**
Returns a ZIP file download.

### GET /api/settings

Gets current settings.

**Response:**
```json
{
  "baseDirectory": "~/getupandrun-projects/"
}
```

### POST /api/settings

Saves settings.

**Request Body:**
```json
{
  "baseDirectory": "~/getupandrun-projects/"
}
```

### GET /api/templates

Gets list of available templates.

**Response:**
```json
[
  {
    "key": "react-node-postgres",
    "name": "React + Node.js + Postgres",
    "description": "Full-stack web application..."
  }
]
```

## Technologies

- **Next.js 16**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Archiver**: ZIP file generation (for Vercel)

## License

MIT
