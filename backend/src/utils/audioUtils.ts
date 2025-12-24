/**
 * Audio utility functions for backend processing
 */

/**
 * Converts a base64 string to a Uint8Array.
 */
export function decodeBase64(base64: string): Uint8Array {
  const binaryString = Buffer.from(base64, 'base64').toString('binary');
  const len = binaryString.length;
  const bytes = new Uint8Array(len);
  for (let i = 0; i < len; i++) {
    bytes[i] = binaryString.charCodeAt(i);
  }
  return bytes;
}

/**
 * Converts a Uint8Array to base64 string.
 */
export function encodeBase64(bytes: Uint8Array): string {
  return Buffer.from(bytes).toString('base64');
}

/**
 * Validates audio data format
 */
export function validateAudioData(data: any): boolean {
  if (!data || typeof data !== 'object') return false;
  if (!data.data || typeof data.data !== 'string') return false;
  if (!data.mimeType || !data.mimeType.includes('audio')) return false;
  return true;
}

