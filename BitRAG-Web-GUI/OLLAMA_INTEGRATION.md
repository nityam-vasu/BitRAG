# Ollama Integration Documentation

## Overview

This document covers all Ollama integration points in the Comic Crafter application. Ollama is used for **local LLM inference** to generate comic scripts, with a fallback to OpenRouter's cloud API.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      FRONTEND (React)                        │
├─────────────────────────────────────────────────────────────┤
│  Step2Script.tsx ───────► llmService.ts ◄────── SettingsPage │
│         │                        │                    │      │
│         │                        │                    │      │
│         └────────────────────────┴────────────────────┘      │
│                              │                               │
│                              │ HTTP (fetch)                   │
│                              ▼                               │
└──────────────────────────────┼───────────────────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  OLLAMA LOCAL SERVER  │
                    │  localhost:11434      │
                    │  Model: gemma:2b      │
                    └──────────────────────┘
                               │
                    ┌──────────┴──────────┐
                    │  OPENROUTER CLOUD   │
                    │  (Fallback API)     │
                    └─────────────────────┘
```

---

## Environment Variables

| Variable | Default Value | Description |
|----------|---------------|-------------|
| `VITE_OLLAMA_ENDPOINT` | `http://localhost:11434` | Ollama server URL |
| `VITE_OLLAMA_MODEL` | `gemma:2b` | Default Ollama model |
| `VITE_OPENROUTER_API_KEY` | (empty) | OpenRouter API key |
| `VITE_OPENROUTER_MODEL` | `google/gemma-2-9b-it` | OpenRouter fallback model |

---

## 1. Main LLM Service (`client/services/llmService.ts`)

### Configuration Constants

```typescript
// Configuration for the APIs
const DEFAULT_OLLAMA_ENDPOINT = import.meta.env.VITE_OLLAMA_ENDPOINT || 'http://localhost:11434';
const DEFAULT_OPENROUTER_API_KEY = import.meta.env.VITE_OPENROUTER_API_KEY || '';
const DEFAULT_OPENROUTER_MODEL = import.meta.env.VITE_OPENROUTER_MODEL || 'google/gemma-2-9b-it';
const DEFAULT_GEMMA_MODEL = import.meta.env.VITE_OLLAMA_MODEL || 'gemma:2b'; // Default to gemma 2b
```

### Ollama Response Interface

```typescript
interface OllamaResponse {
  model: string;
  created_at: string;
  response: string;
  done: boolean;
}
```

### Service Class with Getters/Setters

```typescript
class LLMService {
  private ollamaEndpoint: string;
  private openRouterApiKey: string;
  private openRouterModel: string;
  private gemmaModel: string;

  constructor() {
    this.ollamaEndpoint = DEFAULT_OLLAMA_ENDPOINT;
    this.openRouterApiKey = DEFAULT_OPENROUTER_API_KEY;
    this.openRouterModel = DEFAULT_OPENROUTER_MODEL;
    this.gemmaModel = DEFAULT_GEMMA_MODEL;
  }

  // Getters and setters
  getOllamaEndpoint(): string { return this.ollamaEndpoint; }
  setOllamaEndpoint(endpoint: string): void { this.ollamaEndpoint = endpoint; }
  getGemmaModel(): string { return this.gemmaModel; }
  setGemmaModel(model: string): void { this.gemmaModel = model; }
}
```

### Check Ollama Availability (GET /api/tags)

```typescript
/**
 * Check if Ollama is available
 */
async isOllamaAvailable(): Promise<boolean> {
  try {
    const response = await fetch(`${this.ollamaEndpoint}/api/tags`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });
    
    return response.ok;
  } catch (error) {
    console.warn('Ollama not available:', error);
    return false;
  }
}
```

### Generate with Ollama (POST /api/generate)

```typescript
/**
 * Generate comic script using Ollama
 */
async generateWithOllama(request: GenerationRequest): Promise<ComicPage[]> {
  try {
    const prompt = this.buildPrompt(request);
    
    const response = await fetch(`${this.ollamaEndpoint}/api/generate`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        model: this.gemmaModel,
        prompt: prompt,
        stream: false,
        options: {
          temperature: 0.7,
          top_p: 0.9,
          num_predict: 2000,
        }
      }),
    });

    if (!response.ok) {
      throw new Error(`Ollama API error: ${response.status} ${response.statusText}`);
    }

    const data: OllamaResponse = await response.json();
    
    if (!data.response) {
      throw new Error('No response from Ollama');
    }

    return this.parseResponse(data.response);
  } catch (error) {
    console.error('Error generating with Ollama:', error);
    throw error;
  }
}
```

### Main Orchestrator (Fallback Logic)

```typescript
/**
 * Main method that uses Ollama if available, otherwise OpenRouter
 */
async generateComicScript(request: GenerationRequest): Promise<GenerationResult> {
  // First, check if Ollama is available
  const isOllamaAvailable = await this.isOllamaAvailable();
  
  if (isOllamaAvailable) {
    console.log('Using Ollama for comic script generation');
    const pages = await this.generateWithOllama(request);
    return {
      pages,
      usedService: 'ollama',
      modelUsed: this.gemmaModel
    };
  } else {
    console.log('Ollama not available, using OpenRouter for comic script generation');
    const pages = await this.generateWithOpenRouter(request);
    return {
      pages,
      usedService: 'openrouter',
      modelUsed: this.openRouterModel
    };
  }
}

// Create a singleton instance
const llmService = new LLMService();

export { llmService, LLMService };
```

### Build Prompt Method

```typescript
/**
 * Build a detailed prompt for comic script generation
 */
private buildPrompt(request: GenerationRequest): string {
  return `Generate a detailed comic script for "${request.title}".

Description: ${request.description}
Art Style: ${request.style}
Number of Pages: ${request.pageCount}

Follow this exact JSON format with no other text:
{
  "pages": [
    {
      "pageNumber": 1,
      "scenes": [
        {
          "id": "string",
          "prompt": "detailed visual description for image generation in ${request.style} style",
          "narrator": "narrative text for this panel",
          "dialogue": [
            {
              "id": "string",
              "character": "character name",
              "line": "dialogue line"
            }
          ]
        }
      ]
    }
  ]
}

Generate ${request.pageCount} pages with 2-4 scenes each. Make the visual descriptions vivid and appropriate for ${request.style} style. Include diverse character descriptions and interesting dialogue. Each scene should advance the story logically.`;
}
```

### Parse Response Method

```typescript
/**
 * Parse the LLM response into ComicPage objects
 */
private parseResponse(response: string): ComicPage[] {
  try {
    // Clean the response to extract JSON
    const jsonStart = response.indexOf('{');
    const jsonEnd = response.lastIndexOf('}') + 1;
    const jsonString = response.substring(jsonStart, jsonEnd);
    
    // If response doesn't contain JSON structure, create mock data
    if (jsonStart === -1 || jsonEnd === 0) {
      console.warn('LLM response did not contain valid JSON, using mock data');
      return this.generateMockScript();
    }
    
    const parsed = JSON.parse(jsonString);
    
    // Validate structure
    if (parsed.pages) {
      return parsed.pages;
    } else if (Array.isArray(parsed)) {
      return parsed;
    } else {
      console.warn('Unexpected response structure, using mock data');
      return this.generateMockScript();
    }
  } catch (error) {
    console.error('Error parsing LLM response:', error);
    console.error('Response content:', response);
    
    // If we can't parse the response, return mock data as a fallback
    return this.generateMockScript();
  }
}
```

---

## 2. Settings Page (`client/components/SettingsPage.tsx`)

### Default Settings State

```typescript
const [settings, setSettings] = useState<Settings>({
  ollamaEndpoint: 'http://localhost:11434',
  ollamaModel: 'gemma:2b',
  openRouterApiKey: '',
  openRouterModel: 'google/gemma-2-9b-it'
});
```

### Check Ollama Connection

```typescript
// Check Ollama connection
const checkOllamaConnection = async () => {
  setIsCheckingOllama(true);
  setOllamaStatus(null);
  
  try {
    // Test the connection directly
    const response = await fetch(`${settings.ollamaEndpoint}/api/tags`);
    
    if (response.ok) {
      const data = await response.json();
      const models = data.models?.map((m: any) => m.name) || [];
      
      setAvailableOllamaModels(models);
      setOllamaStatus({ 
        connected: true, 
        message: `Connected to Ollama. ${models.length} models available.` 
      });
    } else {
      setAvailableOllamaModels([]);
      setOllamaStatus({ 
        connected: false, 
        message: `Cannot connect to Ollama: ${response.status} ${response.statusText}` 
      });
    }
  } catch (error) {
    setAvailableOllamaModels([]);
    setOllamaStatus({ 
      connected: false, 
      message: `Error connecting to Ollama: ${(error as Error).message}` 
    });
  } finally {
    setIsCheckingOllama(false);
  }
};
```

### Download/Pull Model (POST /api/pull)

```typescript
// Handle model download
const downloadOllamaModel = async (modelName: string) => {
  try {
    const response = await fetch(`${settings.ollamaEndpoint}/api/pull`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        name: modelName
      })
    });
    
    if (!response.ok) {
      throw new Error(`Failed to download model: ${response.status} ${response.statusText}`);
    }
    
    // For now, just show success - in a real implementation you'd want to stream the progress
    setSaveMessage({ type: 'success', text: `Started downloading model: ${modelName}` });
    
    // Refresh available models after a delay
    setTimeout(checkOllamaConnection, 2000);
  } catch (error) {
    setSaveMessage({ type: 'error', text: `Error downloading model: ${(error as Error).message}` });
  }
};
```

### Model Download Buttons

```typescript
// Model Download Section
<div className="border-t border-gray-100 pt-4">
  <h3 className="font-medium text-gray-800 mb-2">Download New Models</h3>
  <div className="flex flex-wrap gap-2">
    {['gemma:2b', 'gemma:7b', 'llama3', 'mistral', 'phi3'].map(model => (
      <button
        key={model}
        onClick={() => downloadOllamaModel(model)}
        disabled={isCheckingOllama}
        className="flex items-center gap-2 px-3 py-1.5 text-sm bg-gray-100 text-gray-700 hover:bg-gray-200 rounded-lg transition disabled:opacity-50"
      >
        <Download className="w-4 h-4" />
        {model}
      </button>
    ))}
  </div>
  <p className="text-xs text-gray-500 mt-2">
    Click to download Ollama models. Download progress will appear in your Ollama terminal.
  </p>
</div>
```

---

## 3. Step 2 Script Component (`client/components/Step2Script.tsx`)

### Track Which Service Was Used

```typescript
const [llmServiceUsed, setLlmServiceUsed] = useState<'ollama' | 'openrouter' | null>(null);
const [modelUsed, setModelUsed] = useState<string | null>(null);
```

### Load Settings and Generate Script

```typescript
// Load settings from localStorage to ensure latest configuration is used
const savedSettings = localStorage.getItem('komamaker-settings');
if (savedSettings) {
  try {
    const parsedSettings = JSON.parse(savedSettings) as Settings;
    // Update the LLM service with current settings
    llmService.setOllamaEndpoint(parsedSettings.ollamaEndpoint);
    llmService.setOpenRouterApiKey(parsedSettings.openRouterApiKey);
    llmService.setOpenRouterModel(parsedSettings.openRouterModel);
    llmService.setGemmaModel(parsedSettings.ollamaModel);
  } catch (parseError) {
    console.error('Error parsing saved settings:', parseError);
  }
}

// Generate script
const result = await llmService.generateComicScript({
  title: project.title,
  description: project.description,
  style: project.style,
  pageCount: project.pageCount
});
setProject(prev => ({ ...prev, pages: result.pages }));
setLlmServiceUsed(result.usedService);
setModelUsed(result.modelUsed);
```

### Display Service Indicator

```typescript
{llmServiceUsed && (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-full bg-indigo-100 text-indigo-700 text-xs font-medium">
        {llmServiceUsed === 'ollama' ? <Cpu className="w-3 h-3" /> : <Globe className="w-3 h-3" />}
        {llmServiceUsed === 'ollama' ? 'Local Ollama' : 'OpenRouter Cloud'} ({modelUsed})
    </div>
)}

{llmServiceUsed && (
    <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg text-sm">
        <p className="font-medium text-blue-800">
            {llmServiceUsed === 'ollama' 
              ? '🔒 Using your local Ollama instance for story generation' 
              : '☁️ Using OpenRouter cloud service for story generation'}
        </p>
        <p className="text-blue-600 mt-1">
            Model: <span className="font-mono">{modelUsed}</span>
        </p>
    </div>
)}
```

---

## 4. Ollama Setup Utility (`utils/ollama_setup.py`)

### Install Ollama

```python
def install_ollama():
    """
    Install Ollama in Google Colab environment.
    This function installs lshw first (required for Ollama) then installs Ollama.
    """
    print("Installing lshw (required for Ollama)...")
    result = subprocess.run(['apt-get', 'update'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error updating apt: {result.stderr}")
        return False
        
    result = subprocess.run(['apt-get', 'install', '-y', 'lshw'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error installing lshw: {result.stderr}")
        return False

    print("Installing Ollama...")
    result = subprocess.run(['curl', '-fsSL', 'https://ollama.ai/install.sh'], 
                            capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        print(f"Error downloading Ollama installer: {result.stderr}")
        return False

    # Execute the installer
    install_result = subprocess.run('curl -fsSL https://ollama.ai/install.sh | sh', 
                                    capture_output=True, text=True, shell=True)
    if install_result.returncode != 0:
        print(f"Error installing Ollama: {install_result.stderr}")
        return False

    print("Ollama installation completed successfully!")
    return True
```

### Start Ollama Server (nohup)

```python
def start_ollama_server_nohup():
    """
    Start the Ollama server in the background using nohup for better persistence.
    Returns True if successful.
    """
    print("Starting Ollama server in background with nohup...")
    
    # Use nohup to ensure the process continues running even if the session disconnects
    result = subprocess.run(['nohup', 'ollama', 'serve', '>', 'ollama.log', '2>&1', '&'], 
                            shell=True, capture_output=True, text=True)
    
    # Alternative approach that's more reliable in Colab
    import os
    os.system("nohup ollama serve > ollama.log 2>&1 &")
    
    # Wait for the server to start
    time.sleep(5)
    print("Ollama server started with nohup!")
    print("Check status with: !cat ollama.log")
    
    return True
```

### Start Ollama Server (subprocess)

```python
def start_ollama_server():
    """
    Start the Ollama server in the background using subprocess.
    Returns the subprocess object so it can be managed.
    """
    print("Starting Ollama server in background...")
    # Using preexec_fn=os.setsid to create a new process group
    ollama_process = subprocess.Popen(['ollama', 'serve'], 
                                      stdout=subprocess.DEVNULL, 
                                      stderr=subprocess.DEVNULL,
                                      preexec_fn=os.setsid)
    
    # Wait for the server to start
    time.sleep(5)
    print("Ollama server started!")
    
    return ollama_process
```

### Pull Model

```python
def pull_model_background(model_name):
    """
    Pull a model in the background.
    """
    print(f"Pulling model: {model_name}")
    result = subprocess.run(['ollama', 'pull', model_name], 
                            capture_output=True, text=True)
    if result.returncode == 0:
        print(f"Successfully pulled model: {model_name}")
    else:
        print(f"Error pulling model {model_name}: {result.stderr}")
```

### Complete Setup

```python
def setup_ollama_with_models(model_list=['llama3', 'mistral'], use_nohup=True):
    """
    Complete Ollama setup: install, start server, and pull models.
    """
    # Install Ollama
    if not install_ollama():
        print("Failed to install Ollama, aborting setup.")
        return None

    # Start Ollama server
    if use_nohup:
        success = start_ollama_server_nohup()
        if not success:
            print("Failed to start Ollama with nohup, trying subprocess method...")
            ollama_process = start_ollama_server()
        else:
            print("Ollama server running with nohup!")
            return "nohup"  # Indicate that it's running via nohup
    else:
        ollama_process = start_ollama_server()
    
    # Pull models in background
    if use_nohup:
        pull_models_nohup(model_list)
    else:
        pull_models_background(model_list)
    
    print("Ollama setup complete with all models!")
    return ollama_process if not use_nohup else "nohup"
```

---

## 5. Type Definitions (`client/types.ts`)

```typescript
export interface Settings {
  ollamaEndpoint: string;
  ollamaModel: string;
  openRouterApiKey: string;
  openRouterModel: string;
}
```

---

## Ollama API Endpoints Used

| Endpoint | Method | Purpose | File |
|----------|--------|---------|------|
| `/api/tags` | GET | Check availability + list models | `llmService.ts`, `SettingsPage.tsx` |
| `/api/generate` | POST | Generate comic script text | `llmService.ts` |
| `/api/pull` | POST | Download/pull models | `SettingsPage.tsx` |

### API Request/Response Examples

#### GET /api/tags (List Models)
**Request:**
```http
GET http://localhost:11434/api/tags
Content-Type: application/json
```

**Response:**
```json
{
  "models": [
    { "name": "gemma:2b", "size": 1600000000 },
    { "name": "llama3", "size": 4700000000 }
  ]
}
```

#### POST /api/generate (Generate Text)
**Request:**
```http
POST http://localhost:11434/api/generate
Content-Type: application/json

{
  "model": "gemma:2b",
  "prompt": "Your prompt here...",
  "stream": false,
  "options": {
    "temperature": 0.7,
    "top_p": 0.9,
    "num_predict": 2000
  }
}
```

**Response:**
```json
{
  "model": "gemma:2b",
  "created_at": "2024-01-15T10:30:00Z",
  "response": "Generated text...",
  "done": true
}
```

#### POST /api/pull (Download Model)
**Request:**
```http
POST http://localhost:11434/api/pull
Content-Type: application/json

{
  "name": "gemma:2b"
}
```

---

## Flow Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                         GENERATE COMIC SCRIPT                           │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  1. Load settings from        │
                    │     localStorage               │
                    └───────────────────────────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │  2. Check if Ollama is        │
                    │     available (GET /api/tags) │
                    └───────────────────────────────┘
                                    │
                    ├────────────────┴────────────────┐
                    │                              │
                    ▼                              ▼
         ┌──────────────────┐          ┌──────────────────┐
         │   OLLAMA IS       │          │  OLLAMA NOT      │
         │   AVAILABLE       │          │  AVAILABLE       │
         └──────────────────┘          └──────────────────┘
                    │                              │
                    ▼                              ▼
    ┌──────────────────────────┐      ┌──────────────────────────┐
    │  POST /api/generate      │      │  Use OpenRouter API      │
    │  with gemma:2b model     │      │  as fallback             │
    └──────────────────────────┘      └──────────────────────────┘
                    │                              │
                    └──────────────────┬───────────┘
                                         │
                                         ▼
                    ┌──────────────────────────────────┐
                    │  3. Parse JSON response into    │
                    │     ComicPage[] objects          │
                    └──────────────────────────────────┘
                                         │
                                         ▼
                    ┌──────────────────────────────────┐
                    │  4. Return GenerationResult      │
                    │     { pages, usedService,        │
                    │       modelUsed }               │
                    └──────────────────────────────────┘
```

---

## File Summary

| File | Purpose |
|------|---------|
| `client/services/llmService.ts` | Main service for LLM calls, Ollama integration, fallback logic |
| `client/components/SettingsPage.tsx` | UI for configuring Ollama endpoint/model, testing connection, downloading models |
| `client/components/Step2Script.tsx` | UI for script generation, displays which LLM service was used |
| `client/types.ts` | TypeScript interfaces for Settings |
| `utils/ollama_setup.py` | Python utility for installing/running Ollama in Google Colab |
