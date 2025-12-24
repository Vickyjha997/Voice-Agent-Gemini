# Function Calling in Gemini Live Voice Chat - Complete Guide

## 📚 Table of Contents
1. [What is Function Calling?](#what-is-function-calling)
2. [How It Works in This Codebase](#how-it-works-in-this-codebase)
3. [The Complete Flow](#the-complete-flow)
4. [Understanding the Code Structure](#understanding-the-code-structure)
5. [How to Read and Understand the Code](#how-to-read-and-understand-the-code)

---

## What is Function Calling?

**Function Calling** (also called "Tool Use" or "Function Calling") allows the AI model (Gemini) to:
- **Decide** when it needs to call external functions/tools
- **Request** specific functions with appropriate parameters
- **Receive** results from those functions
- **Use** the results to generate a more informed response

Think of it like giving the AI "hands" to interact with the real world - databases, APIs, calculators, etc.

---

## How It Works in This Codebase

### 1. **Tool Registration** (`backend/src/tools/exampleTools.ts`)

Tools are **registered** when the server starts. Each tool has:
- **Name**: Unique identifier (e.g., `get_weather`)
- **Description**: What the tool does (Gemini uses this to decide when to call it)
- **Parameters**: Schema defining what inputs the tool needs (JSON Schema format)
- **Handler**: The actual function that executes when called

**Example:**
```typescript
toolRegistry.register({
  name: 'get_weather',
  description: 'Get current weather information for a location.',
  parameters: {
    type: 'object',
    properties: {
      location: { type: 'string', description: 'City name or coordinates' },
      units: { type: 'string', description: 'Temperature units: celsius or fahrenheit' }
    },
    required: ['location']
  },
  handler: async (args) => {
    // This function runs when Gemini calls get_weather
    const { location, units = 'celsius' } = args;
    return { location, temperature: 22, condition: 'Partly Cloudy' };
  }
});
```

### 2. **Tool Registry** (`backend/src/tools/toolRegistry.ts`)

The `ToolRegistry` class:
- **Stores** all registered tools in a Map
- **Converts** tools to Gemini's format (`getGeminiToolsFormat()`)
- **Executes** tools when requested (`execute()`)

### 3. **Connection Setup** (`backend/src/services/geminiProxy.ts` - Line 30-45)

When connecting to Gemini, tools are **passed in the config**:

```typescript
const tools = toolRegistry.getGeminiToolsFormat(); // Convert to Gemini format

const geminiSession = await this.ai.live.connect({
  model: this.MODEL_NAME,
  config: {
    // ... other config ...
    tools: tools.length > 0 ? tools : undefined, // ← Tools passed here!
  }
});
```

This tells Gemini: *"Here are the functions you can call"*

### 4. **Function Call Interception** (`backend/src/services/geminiProxy.ts` - Line 54-59)

When Gemini sends a message, it's intercepted **BEFORE** being sent to the client:

```typescript
onmessage: async (message: LiveServerMessage) => {
  // Handle function calls BEFORE passing message to client
  await this.handleFunctionCalls(message, sessionId, onMessage);
  
  // Pass the message to client
  onMessage(message);
}
```

### 5. **Function Call Processing** (`backend/src/services/geminiProxy.ts` - Line 80-149)

The `handleFunctionCalls` method:

**Step 1: Extract Function Calls**
```typescript
const functionCalls = message.serverContent?.modelTurn?.parts?.filter(
  (part: any) => part.functionCall
);
```

**Step 2: Execute Each Function**
```typescript
for (const part of functionCalls) {
  const functionCall = part.functionCall;
  const toolName = functionCall.name;  // e.g., "get_weather"
  const args = functionCall.args;      // e.g., { location: "New York" }
  
  // Execute the function
  const result = await toolRegistry.execute(toolName, args);
}
```

**Step 3: Send Results Back to Gemini**
```typescript
await session.geminiSession.send({
  serverContent: {
    modelTurn: {
      parts: [{
        functionResponse: {
          name: toolName,
          response: result.error ? { error: result.error } : result.result
        }
      }]
    }
  }
});
```

---

## The Complete Flow

Here's what happens when a user asks: *"What's the weather in New York?"*

```
┌─────────────┐
│   USER      │
│  (Voice)    │
└──────┬──────┘
       │ "What's the weather in New York?"
       ▼
┌─────────────────────────────────────┐
│  WebSocket Handler                  │
│  Receives audio, sends to Gemini    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Gemini Live API                    │
│  - Transcribes audio                │
│  - Understands intent               │
│  - Decides to call get_weather       │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Message with Function Call         │
│  {                                  │
│    functionCall: {                  │
│      name: "get_weather",           │
│      args: { location: "New York" }│
│    }                                │
│  }                                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  handleFunctionCalls()              │
│  - Extracts function call           │
│  - Executes toolRegistry.execute()  │
│  - Gets weather data                │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Tool Handler Executes              │
│  Returns: {                          │
│    location: "New York",             │
│    temperature: 22,                  │
│    condition: "Partly Cloudy"        │
│  }                                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Send Function Result to Gemini     │
│  {                                  │
│    functionResponse: {              │
│      name: "get_weather",           │
│      response: { ...weather data }  │
│    }                                │
│  }                                  │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Gemini Receives Result             │
│  - Uses weather data                │
│  - Generates voice response         │
│  "The weather in New York is..."    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│  Response Sent to Client            │
│  (Audio + Transcription)            │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────┐
│   USER      │
│  Hears AI   │
└─────────────┘
```

---

## Understanding the Code Structure

### Key Files and Their Roles:

1. **`backend/src/tools/toolRegistry.ts`**
   - **Purpose**: Central registry for all tools
   - **Key Methods**:
     - `register()`: Add a new tool
     - `getGeminiToolsFormat()`: Convert tools to Gemini's expected format
     - `execute()`: Run a tool with given arguments

2. **`backend/src/tools/exampleTools.ts`**
   - **Purpose**: Define and register example tools
   - **When to read**: When you want to add new tools or understand tool structure

3. **`backend/src/services/geminiProxy.ts`**
   - **Purpose**: Manages connection to Gemini API
   - **Key Methods**:
     - `connectSession()`: Sets up connection with tools (line 30-45)
     - `handleFunctionCalls()`: Processes function calls (line 80-149)
     - `sendAudio()`: Sends audio to Gemini

4. **`backend/src/services/websocketHandler.ts`**
   - **Purpose**: Handles WebSocket communication with clients
   - **Key Method**: `handleGeminiMessage()` - Processes messages from Gemini

5. **`backend/src/types.ts`**
   - **Purpose**: TypeScript type definitions
   - **Key Types**: `FunctionCall`, `FunctionResult`, `ToolDefinition`

---

## How to Read and Understand the Code

### Reading Order (Recommended):

1. **Start with `toolRegistry.ts`** (Simple, foundational)
   - Understand how tools are stored and executed
   - Look at `getGeminiToolsFormat()` - this is what Gemini sees

2. **Read `exampleTools.ts`** (See real examples)
   - Pick one tool (e.g., `get_weather`)
   - Understand the structure: name, description, parameters, handler

3. **Read `geminiProxy.ts` - `connectSession()` method** (Lines 19-78)
   - See how tools are passed to Gemini (line 30, 45)
   - Understand the callback structure

4. **Read `geminiProxy.ts` - `handleFunctionCalls()` method** (Lines 80-149)
   - **This is the heart of function calling!**
   - Line 86-88: How function calls are extracted
   - Line 100-112: How functions are executed
   - Line 117-144: How results are sent back

5. **Read `websocketHandler.ts` - `handleGeminiMessage()`** (Lines 176-238)
   - See how messages flow from Gemini to client
   - Note: Function calls are handled BEFORE this (in `handleFunctionCalls`)

### Key Concepts to Understand:

#### 1. **Message Structure**
Gemini messages have this structure:
```typescript
{
  serverContent: {
    modelTurn: {
      parts: [
        { functionCall: { name: "...", args: {...} } },  // ← Function call
        { inlineData: { data: "..." } },                  // ← Audio data
        { text: "..." }                                   // ← Text
      ]
    }
  }
}
```

#### 2. **Tool Format for Gemini**
Tools must be in this format:
```typescript
{
  name: "get_weather",
  description: "Get weather...",
  parameters: {
    type: "object",
    properties: {
      location: { type: "string", description: "..." }
    },
    required: ["location"]
  }
}
```

#### 3. **Function Response Format**
Results must be sent back as:
```typescript
{
  serverContent: {
    modelTurn: {
      parts: [{
        functionResponse: {
          name: "get_weather",
          response: { ...result data... }
        }
      }]
    }
  }
}
```

---

## Important Notes

1. **Function calls happen BEFORE the final response**
   - Gemini sends function call → You execute → Send result → Gemini generates response

2. **Tools are registered at server startup**
   - See `backend/src/index.ts` line 12: `import './tools/exampleTools'`

3. **Multiple function calls can happen in one message**
   - The code loops through all function calls (line 100)

4. **Error handling**
   - If a tool fails, the error is sent back to Gemini (line 128)
   - Gemini can then handle the error in its response

5. **Tool descriptions are critical**
   - Gemini uses descriptions to decide when to call tools
   - Make descriptions clear and specific!

---

## Next Steps

1. **Read the code** in the order suggested above
2. **Add a simple tool** to understand the process
3. **Test function calling** using the test script (see `backend/test-function-calling.js`)
4. **Check console logs** - function calls are logged (line 108 in geminiProxy.ts)

