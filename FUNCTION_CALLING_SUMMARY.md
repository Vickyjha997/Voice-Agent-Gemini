# Function Calling - Quick Summary

## 🎯 What You Need to Know

### The Flow (Simple Version)

```
User asks question
    ↓
Gemini decides to call a function
    ↓
Function call intercepted in handleFunctionCalls()
    ↓
Function executed via toolRegistry.execute()
    ↓
Result sent back to Gemini
    ↓
Gemini generates response using the result
    ↓
Response sent to user
```

### Key Files to Read (In Order)

1. **`backend/src/tools/toolRegistry.ts`** - How tools are stored
2. **`backend/src/tools/exampleTools.ts`** - Example tool definitions
3. **`backend/src/services/geminiProxy.ts`** (lines 30-45) - Tools passed to Gemini
4. **`backend/src/services/geminiProxy.ts`** (lines 80-149) - Function call handling ⭐ **MOST IMPORTANT**
5. **`backend/src/services/websocketHandler.ts`** - Message routing

### The Critical Code Section

**`backend/src/services/geminiProxy.ts` - `handleFunctionCalls()` method (lines 80-149)**

This is where the magic happens:
- **Line 86-88**: Extracts function calls from Gemini's message
- **Line 100-112**: Loops through and executes each function
- **Line 117-144**: Sends results back to Gemini

### How to Test

1. **Quick Check**: `curl http://localhost:3001/api/tools` - Should show registered tools
2. **Automated Test**: `cd backend && node test-function-calling.js` - Runs full test suite
3. **Manual Test**: Use frontend, ask Gemini to use a tool, check backend console for `[Function Call]` logs

### What to Look For

✅ **Working**: Backend console shows `[Function Call] get_weather { location: 'New York' }`
❌ **Not Working**: No function call logs, or error messages

---

## 📖 Full Documentation

- **Complete Explanation**: See `FUNCTION_CALLING_EXPLANATION.md`
- **Testing Guide**: See `TESTING_FUNCTION_CALLING.md`
- **Test Script**: Run `cd backend && node test-function-calling.js`

---

## 🔧 Quick Debugging

**Problem**: No function calls happening
- Check: Are tools registered? (`/api/tools` endpoint)
- Check: Are tools passed to Gemini? (line 45 in `geminiProxy.ts`)
- Check: Tool descriptions are clear? (Gemini uses these to decide)

**Problem**: Function calls happen but errors occur
- Check: Backend console for error messages
- Check: Function handler code in `exampleTools.ts`
- Check: Function result format (should match what Gemini expects)

**Problem**: Function calls work but results aren't used
- Check: Function result is sent back correctly (line 117-144 in `geminiProxy.ts`)
- Check: Result format matches expected schema

---

## 💡 Key Concepts

1. **Tools are registered at startup** - See `index.ts` line 12
2. **Tools are passed to Gemini during connection** - See `geminiProxy.ts` line 45
3. **Function calls are intercepted BEFORE response** - See `geminiProxy.ts` line 56
4. **Results must be sent back in specific format** - See `geminiProxy.ts` line 125-130
5. **Tool descriptions are critical** - Gemini uses them to decide when to call tools

---

## 🚀 Next Steps

1. Read `FUNCTION_CALLING_EXPLANATION.md` for deep dive
2. Run `cd backend && node test-function-calling.js` to test
3. Check `TESTING_FUNCTION_CALLING.md` for testing strategies
4. Modify `exampleTools.ts` to add your own tools
5. Replace simulated responses with real API calls

