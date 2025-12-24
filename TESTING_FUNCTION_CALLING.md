# Testing Function Calling - Quick Guide

## 🧪 Quick Test Methods

### Method 1: Automated Test Script (Recommended)

Run the automated test script:

```bash
# Make sure backend is running first (in one terminal)
cd backend
npm run dev

# In another terminal, run the test (from backend directory)
cd backend
node test-function-calling.js
```

The script will:
- ✅ Check if tools are registered
- ✅ Create a session
- ✅ Connect via WebSocket
- ✅ Monitor for function calls

### Method 2: Manual Testing via Frontend

1. **Start the backend server:**
   ```bash
   cd backend
   npm run dev
   ```

2. **Open the frontend:**
   - Navigate to `http://localhost:3001` (or the port your backend uses)
   - Or use the frontend client example

3. **Connect and test:**
   - Click "Connect" to establish WebSocket connection
   - Speak or type a request that should trigger a function call
   - Examples:
     - "What's the weather in New York?"
     - "Get analytics for users from 2024-01-01 to 2024-01-31"
     - "Search the knowledge base for information about TypeScript"
     - "Execute a SQL query to get all users"

4. **Check the backend console:**
   - Look for logs like: `[Function Call] get_weather { location: 'New York' }`
   - This confirms function calling is working!

### Method 3: Direct API Testing

#### Step 1: Check Available Tools
```bash
curl http://localhost:3001/api/tools
```

Expected response:
```json
{
  "tools": [
    {
      "name": "get_weather",
      "description": "Get current weather information for a location.",
      "parameters": { ... }
    },
    ...
  ]
}
```

#### Step 2: Create a Session
```bash
curl -X POST http://localhost:3001/api/sessions \
  -H "Content-Type: application/json" \
  -d '{"userId": "test-user"}'
```

Response:
```json
{
  "sessionId": "abc-123-def",
  "createdAt": "2024-01-01T00:00:00.000Z"
}
```

#### Step 3: Connect via WebSocket
Use a WebSocket client (like `wscat` or a browser console):

```bash
# Install wscat if needed
npm install -g wscat

# Connect
wscat -c "ws://localhost:3002?sessionId=YOUR_SESSION_ID"
```

Then send:
```json
{"type": "connect", "sessionId": "YOUR_SESSION_ID"}
```

#### Step 4: Monitor Function Calls
Watch the backend console for `[Function Call]` logs.

---

## 🔍 How to Verify Function Calling is Working

### Signs That Function Calling Works:

1. **Backend Console Logs:**
   ```
   [Function Call] get_weather { location: 'New York' }
   ```
   This appears in `geminiProxy.ts` at line 108.

2. **WebSocket Messages:**
   Check for messages with `type: 'function_call'` or `type: 'function_result'`
   (Note: These might not be sent to client by default - check `websocketHandler.ts`)

3. **Gemini's Response:**
   - If function calling works, Gemini will use the tool results in its response
   - Example: "The weather in New York is 22°C and partly cloudy"

### Signs That Function Calling is NOT Working:

1. **No `[Function Call]` logs in backend console**
   - Gemini might not be calling functions
   - Check tool descriptions (they need to be clear)
   - Check if tools are registered (use `/api/tools` endpoint)

2. **Error messages in console:**
   - `[Function Call] Error sending result for...`
   - Check the error details

3. **Gemini doesn't use tools even when asked:**
   - Tool descriptions might be unclear
   - Tools might not be passed to Gemini correctly
   - Check `geminiProxy.ts` line 45 - tools should be in config

---

## 🐛 Debugging Tips

### 1. Check Tool Registration

```bash
curl http://localhost:3001/api/tools
```

If no tools appear:
- Check `backend/src/index.ts` line 12 - should import `'./tools/exampleTools'`
- Check `backend/src/tools/exampleTools.ts` - tools should be registered

### 2. Check Gemini Connection

Look for these logs in backend console:
```
[Gemini] Session <sessionId> connected
```

If you don't see this:
- Check API key is set: `process.env.GEMINI_API_KEY`
- Check network connectivity

### 3. Check Function Call Extraction

Add debug logs in `geminiProxy.ts`:

```typescript
// In handleFunctionCalls method, after line 88
console.log('[DEBUG] Message parts:', message.serverContent?.modelTurn?.parts);
console.log('[DEBUG] Function calls found:', functionCalls);
```

### 4. Check Function Execution

Add debug logs in `toolRegistry.ts`:

```typescript
// In execute method, before line 48
console.log('[DEBUG] Executing tool:', name, 'with args:', args);
```

### 5. Check Function Result Sending

Add debug logs in `geminiProxy.ts`:

```typescript
// In handleFunctionCalls method, after line 112
console.log('[DEBUG] Sending function result:', {
  name: toolName,
  response: result.error ? { error: result.error } : result.result
});
```

---

## 📝 Test Cases

### Test Case 1: Simple Function Call
**Request:** "What's the weather in London?"
**Expected:**
- Backend log: `[Function Call] get_weather { location: 'London' }`
- Function executes and returns weather data
- Gemini responds with weather information

### Test Case 2: Function with Multiple Parameters
**Request:** "Get analytics for revenue from 2024-01-01 to 2024-12-31"
**Expected:**
- Backend log: `[Function Call] get_analytics { metric: 'revenue', startDate: '2024-01-01', endDate: '2024-12-31' }`
- Function executes with all parameters
- Gemini responds with analytics data

### Test Case 3: Function Call Error Handling
**Request:** "Get weather for invalid_location_xyz"
**Expected:**
- Function executes (even with invalid input)
- Error is handled gracefully
- Gemini explains the error to user

### Test Case 4: Multiple Function Calls
**Request:** "Get weather for New York and also get analytics for users"
**Expected:**
- Multiple function calls in sequence
- Each function executes independently
- Gemini combines results in response

---

## 🎯 Quick Verification Checklist

- [ ] Backend server is running
- [ ] Tools are registered (check `/api/tools`)
- [ ] Session can be created (check `/api/sessions`)
- [ ] WebSocket connection works
- [ ] Gemini connection established (check backend logs)
- [ ] Function calls appear in backend console
- [ ] Function results are sent back to Gemini
- [ ] Gemini uses function results in response

---

## 💡 Pro Tips

1. **Start Simple:**
   - Test with one tool first (`get_weather`)
   - Make sure it works before adding more

2. **Check Tool Descriptions:**
   - Clear descriptions help Gemini decide when to call tools
   - Be specific about when to use each tool

3. **Monitor Backend Logs:**
   - All function calls are logged at line 108 in `geminiProxy.ts`
   - This is your primary debugging tool

4. **Test Error Cases:**
   - What happens if a tool fails?
   - What happens if Gemini calls a non-existent tool?

5. **Use Console Logs:**
   - Add temporary `console.log()` statements to trace the flow
   - Remove them after debugging

---

## 🚀 Next Steps After Testing

Once function calling works:

1. **Add Real Implementations:**
   - Replace simulated responses in `exampleTools.ts`
   - Connect to real APIs, databases, etc.

2. **Add More Tools:**
   - Create tools specific to your use case
   - Register them in `toolRegistry`

3. **Improve Error Handling:**
   - Add better error messages
   - Handle edge cases

4. **Optimize Performance:**
   - Cache results if appropriate
   - Batch multiple calls if possible

