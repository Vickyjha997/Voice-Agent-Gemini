import { FunctionResult } from '../types';

/**
 * Tool Registry - Register all available function calling tools
 */

export interface ToolDefinition {
  name: string;
  description: string;
  parameters: {
    type: 'object';
    properties: Record<string, {
      type: string;
      description: string;
      required?: boolean;
    }>;
    required?: string[];
  };
  handler: (args: Record<string, any>) => Promise<any>;
}

class ToolRegistry {
  private tools: Map<string, ToolDefinition> = new Map();

  register(tool: ToolDefinition) {
    this.tools.set(tool.name, tool);
  }

  get(name: string): ToolDefinition | undefined {
    return this.tools.get(name);
  }

  getAll(): ToolDefinition[] {
    return Array.from(this.tools.values());
  }

  async execute(name: string, args: Record<string, any>): Promise<FunctionResult> {
    const tool = this.tools.get(name);
    if (!tool) {
      return {
        callId: '', // Will be set by caller
        result: null,
        error: `Tool ${name} not found`,
      };
    }

    try {
      const result = await tool.handler(args);
      return {
        callId: '', // Will be set by caller
        result,
      };
    } catch (error: any) {
      return {
        callId: '', // Will be set by caller
        result: null,
        error: error.message || 'Unknown error',
      };
    }
  }

  getGeminiToolsFormat() {
    return this.getAll().map(tool => ({
      name: tool.name,
      description: tool.description,
      parameters: tool.parameters,
    }));
  }
}

export const toolRegistry = new ToolRegistry();

