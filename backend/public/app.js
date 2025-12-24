// Configuration
let backendUrl = 'http://localhost:3001';
let wsUrl = 'ws://localhost:3002';
let sessionId = null;
let ws = null;
let isConnected = false;

// Audio setup
let audioContext = null;
let outputAudioContext = null;
let processor = null;
let inputSource = null;
let outputNode = null;
let inputAnalyser = null;
let outputAnalyser = null;
let nextStartTime = 0;
let audioSources = new Set();
const INPUT_SAMPLE_RATE = 16000;
const OUTPUT_SAMPLE_RATE = 24000;
const BUFFER_SIZE = 4096;

// DOM elements
const connectBtn = document.getElementById('connectBtn');
const disconnectBtn = document.getElementById('disconnectBtn');
const statusIndicator = document.getElementById('statusIndicator');
const statusText = document.getElementById('statusText');
const errorBox = document.getElementById('errorBox');
const infoBox = document.getElementById('infoBox');
const transcriptionBox = document.getElementById('transcriptionBox');
const inputVolume = document.getElementById('inputVolume');
const outputVolume = document.getElementById('outputVolume');
const backendUrlInput = document.getElementById('backendUrl');
const wsUrlInput = document.getElementById('wsUrl');

// Update URLs from inputs
backendUrlInput.addEventListener('change', (e) => {
    backendUrl = e.target.value;
});

wsUrlInput.addEventListener('change', (e) => {
    wsUrl = e.target.value;
});

// Connect button
connectBtn.addEventListener('click', async () => {
    try {
        await connect();
    } catch (error) {
        showError('Connection failed: ' + error.message);
        updateStatus('ERROR', 'Connection failed');
    }
});

// Disconnect button
disconnectBtn.addEventListener('click', async () => {
    await disconnect();
});

// Connect function
async function connect() {
    if (isConnected) return;

    updateStatus('CONNECTING', 'Connecting...');
    connectBtn.disabled = true;
    hideError();

    try {
        // 1. Create session
        const response = await fetch(`${backendUrl}/api/sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
        });

        if (!response.ok) {
            throw new Error(`Failed to create session: ${response.statusText}`);
        }

        const data = await response.json();
        sessionId = data.sessionId;
        addTranscription('system', `Session created: ${sessionId.substring(0, 8)}...`);

        // 2. Setup audio contexts
        audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: INPUT_SAMPLE_RATE,
        });
        outputAudioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: OUTPUT_SAMPLE_RATE,
        });

        // 3. Setup input audio
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        inputSource = audioContext.createMediaStreamSource(stream);
        inputAnalyser = audioContext.createAnalyser();
        processor = audioContext.createScriptProcessor(BUFFER_SIZE, 1, 1);

        inputSource.connect(inputAnalyser);
        inputAnalyser.connect(processor);
        processor.connect(audioContext.destination);

        // 4. Setup output audio
        outputNode = outputAudioContext.createGain();
        outputAnalyser = outputAudioContext.createAnalyser();
        outputNode.connect(outputAnalyser);
        outputAnalyser.connect(outputAudioContext.destination);

        // 5. Connect WebSocket
        ws = new WebSocket(`${wsUrl}?sessionId=${sessionId}`);

        ws.onopen = () => {
            addTranscription('system', 'WebSocket connected');
            // #region agent log
            fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:109',message:'WebSocket onopen fired',data:{sessionId},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            // #endregion
            // Send connect message
            ws.send(JSON.stringify({
                type: 'connect',
                sessionId: sessionId,
            }));
            updateStatus('CONNECTING', 'Connecting to Gemini...');
        };

        ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            handleMessage(message);
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            showError('WebSocket error occurred');
            updateStatus('ERROR', 'WebSocket error');
        };

        ws.onclose = () => {
            addTranscription('system', 'WebSocket disconnected');
            updateStatus('DISCONNECTED', 'Disconnected');
            cleanup();
        };

        // 6. Start audio processing
        // #region agent log
        fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:137',message:'setupAudioProcessing called',data:{sessionId,isConnected},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
        // #endregion
        setupAudioProcessing();
        startVolumeMonitoring();

    } catch (error) {
        console.error('Connection error:', error);
        showError(error.message);
        updateStatus('ERROR', 'Connection failed');
        cleanup();
        throw error;
    }
}

// Setup audio processing
function setupAudioProcessing() {
    if (!processor) return;

    processor.onaudioprocess = (e) => {
        if (!ws || ws.readyState !== WebSocket.OPEN || !sessionId) return;
        // #region agent log
        if (!isConnected) {
            fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:153',message:'audio data ready but not connected',data:{sessionId,isConnected,wsReadyState:ws?.readyState},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
            return;
        }
        // #endregion

        const inputData = e.inputBuffer.getChannelData(0);
        const pcmBlob = createPcmBlob(inputData);

        ws.send(JSON.stringify({
            type: 'audio',
            data: pcmBlob,
            sessionId: sessionId,
        }));
    };
}

// Handle WebSocket messages
function handleMessage(message) {
    switch (message.type) {
        case 'status':
            const status = message.data.status;
            if (status === 'CONNECTED') {
                // #region agent log
                fetch('http://127.0.0.1:7245/ingest/15e3bf2d-33c4-432b-b85e-7b4628f43030',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({location:'app.js:168',message:'CONNECTED status received',data:{sessionId,previousIsConnected:isConnected},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'C'})}).catch(()=>{});
                // #endregion
                updateStatus('CONNECTED', 'Connected');
                isConnected = true;
                connectBtn.disabled = true;
                disconnectBtn.disabled = false;
                infoBox.textContent = 'Connected! Start speaking...';
            } else if (status === 'ERROR') {
                updateStatus('ERROR', 'Error');
                showError('Connection error');
            } else if (status === 'DISCONNECTED') {
                updateStatus('DISCONNECTED', 'Disconnected');
                isConnected = false;
            }
            break;

        case 'audio':
            if (message.data.interrupt) {
                stopAllAudio();
                nextStartTime = outputAudioContext?.currentTime || 0;
            } else if (message.data.audio && outputAudioContext && outputNode) {
                playAudio(message.data.audio);
            }
            break;

        case 'transcription':
            addTranscription(
                message.data.isUser ? 'user' : 'assistant',
                message.data.text,
                message.data.isFinal
            );
            break;

        case 'error':
            showError(message.data.message || 'Unknown error');
            break;

        case 'pong':
            // Keepalive response
            break;
    }
}

// Play audio from server
async function playAudio(base64Audio) {
    if (!outputAudioContext || !outputNode) return;

    try {
        // Decode base64
        const binaryString = atob(base64Audio);
        const len = binaryString.length;
        const bytes = new Uint8Array(len);
        for (let i = 0; i < len; i++) {
            bytes[i] = binaryString.charCodeAt(i);
        }

        // Convert PCM to AudioBuffer
        const dataInt16 = new Int16Array(bytes.buffer);
        const frameCount = dataInt16.length;
        const buffer = outputAudioContext.createBuffer(1, frameCount, OUTPUT_SAMPLE_RATE);
        const channelData = buffer.getChannelData(0);

        for (let i = 0; i < frameCount; i++) {
            channelData[i] = dataInt16[i] / 32768.0;
        }

        // Schedule playback
        nextStartTime = Math.max(nextStartTime, outputAudioContext.currentTime);
        const source = outputAudioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(outputNode);
        source.start(nextStartTime);

        nextStartTime += buffer.duration;
        audioSources.add(source);

        source.onended = () => {
            audioSources.delete(source);
        };
    } catch (error) {
        console.error('Error playing audio:', error);
    }
}

// Stop all audio
function stopAllAudio() {
    audioSources.forEach(source => {
        try { source.stop(); } catch (e) {}
    });
    audioSources.clear();
}

// Create PCM blob from Float32Array
function createPcmBlob(data) {
    const l = data.length;
    const int16 = new Int16Array(l);
    for (let i = 0; i < l; i++) {
        const sample = Math.max(-1, Math.min(1, data[i]));
        int16[i] = sample < 0 ? sample * 32768 : sample * 32767;
    }

    // Convert to base64
    let binary = '';
    const bytes = new Uint8Array(int16.buffer);
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    const base64 = btoa(binary);

    return {
        data: base64,
        mimeType: 'audio/pcm;rate=16000',
    };
}

// Volume monitoring
function startVolumeMonitoring() {
    setInterval(() => {
        let inputVol = 0;
        let outputVol = 0;

        if (inputAnalyser) {
            const dataArray = new Uint8Array(inputAnalyser.frequencyBinCount);
            inputAnalyser.getByteFrequencyData(dataArray);
            const sum = dataArray.reduce((a, b) => a + b, 0);
            inputVol = sum / dataArray.length / 255;
        }

        if (outputAnalyser) {
            const dataArray = new Uint8Array(outputAnalyser.frequencyBinCount);
            outputAnalyser.getByteFrequencyData(dataArray);
            const sum = dataArray.reduce((a, b) => a + b, 0);
            outputVol = sum / dataArray.length / 255;
        }

        inputVolume.style.width = (inputVol * 100) + '%';
        outputVolume.style.width = (outputVol * 100) + '%';
    }, 50);
}

// Disconnect
async function disconnect() {
    if (ws && sessionId) {
        ws.send(JSON.stringify({
            type: 'disconnect',
            sessionId: sessionId,
        }));
        ws.close();
    }
    cleanup();
}

// Cleanup
function cleanup() {
    isConnected = false;
    connectBtn.disabled = false;
    disconnectBtn.disabled = true;

    if (processor) {
        processor.disconnect();
        processor.onaudioprocess = null;
        processor = null;
    }

    if (inputSource) {
        inputSource.disconnect();
        inputSource = null;
    }

    if (audioContext) {
        audioContext.close();
        audioContext = null;
    }

    if (outputAudioContext) {
        outputAudioContext.close();
        outputAudioContext = null;
    }

    stopAllAudio();
    ws = null;
    sessionId = null;
}

// Update status
function updateStatus(status, text) {
    statusText.textContent = text;
    statusIndicator.className = 'status-indicator';
    
    if (status === 'CONNECTED') {
        statusIndicator.classList.add('connected');
    } else if (status === 'CONNECTING') {
        statusIndicator.classList.add('connecting');
    }
}

// Add transcription
function addTranscription(type, text, isFinal = false) {
    if (!text && !isFinal) return;

    const item = document.createElement('div');
    item.className = `transcription-item ${type}`;
    
    const label = document.createElement('div');
    label.className = 'transcription-label';
    label.textContent = type === 'user' ? 'You' : type === 'assistant' ? 'Assistant' : 'System';
    
    const content = document.createElement('div');
    content.textContent = text || (isFinal ? '[Turn complete]' : '');
    
    item.appendChild(label);
    item.appendChild(content);
    transcriptionBox.appendChild(item);
    
    // Auto-scroll
    transcriptionBox.scrollTop = transcriptionBox.scrollHeight;

    // If final, add separator
    if (isFinal && type !== 'system') {
        const separator = document.createElement('div');
        separator.style.height = '8px';
        transcriptionBox.appendChild(separator);
    }
}

// Show error
function showError(message) {
    errorBox.textContent = message;
    errorBox.classList.add('show');
    setTimeout(() => {
        errorBox.classList.remove('show');
    }, 5000);
}

// Hide error
function hideError() {
    errorBox.classList.remove('show');
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    disconnect();
});

