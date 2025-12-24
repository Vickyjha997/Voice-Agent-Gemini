import { toolRegistry } from './toolRegistry';

/**
 * Example function calling tools
 * These demonstrate how to integrate external APIs, databases, and services
 */

// Example 1: SQL Query Tool
toolRegistry.register({
  name: 'execute_sql_query',
  description: 'Execute a SQL query on a database. Use this for data retrieval and analytics.',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'The SQL query to execute',
      },
      database: {
        type: 'string',
        description: 'The database name (optional, defaults to main)',
      },
    },
    required: ['query'],
  },
  handler: async (args) => {
    const { query, database = 'main' } = args;
    
    // TODO: Replace with actual database connection
    // Example: const result = await db.query(query);
    
    // Simulated response
    return {
      success: true,
      database,
      query,
      rows: [
        { id: 1, name: 'Example', value: 100 },
        { id: 2, name: 'Sample', value: 200 },
      ],
      rowCount: 2,
      message: 'Query executed successfully (simulated)',
    };
  },
});

// Example 2: Analytics Tool
toolRegistry.register({
  name: 'get_analytics',
  description: 'Retrieve analytics data for a given time period and metric.',
  parameters: {
    type: 'object',
    properties: {
      metric: {
        type: 'string',
        description: 'The metric to retrieve (e.g., "users", "revenue", "conversions")',
      },
      startDate: {
        type: 'string',
        description: 'Start date in ISO format (YYYY-MM-DD)',
      },
      endDate: {
        type: 'string',
        description: 'End date in ISO format (YYYY-MM-DD)',
      },
    },
    required: ['metric', 'startDate', 'endDate'],
  },
  handler: async (args) => {
    const { metric, startDate, endDate } = args;
    
    // TODO: Replace with actual analytics API call
    // Example: const data = await analyticsAPI.getMetric(metric, startDate, endDate);
    
    // Simulated response
    return {
      metric,
      period: { start: startDate, end: endDate },
      value: 12345,
      trend: '+12.5%',
      dataPoints: [
        { date: startDate, value: 10000 },
        { date: endDate, value: 12345 },
      ],
      message: 'Analytics retrieved successfully (simulated)',
    };
  },
});

// Example 3: Knowledge Base Search
toolRegistry.register({
  name: 'search_knowledge_base',
  description: 'Search the knowledge base for relevant information on a topic.',
  parameters: {
    type: 'object',
    properties: {
      query: {
        type: 'string',
        description: 'The search query',
      },
      maxResults: {
        type: 'number',
        description: 'Maximum number of results to return (default: 5)',
      },
    },
    required: ['query'],
  },
  handler: async (args) => {
    const { query, maxResults = 5 } = args;
    
    // TODO: Replace with actual RAG/vector search
    // Example: const results = await vectorDB.search(query, maxResults);
    
    // Simulated response
    return {
      query,
      results: [
        {
          title: 'Example Document 1',
          content: `Relevant information about ${query}`,
          relevance: 0.95,
        },
        {
          title: 'Example Document 2',
          content: `Additional context for ${query}`,
          relevance: 0.87,
        },
      ],
      totalResults: 2,
      message: 'Knowledge base search completed (simulated)',
    };
  },
});

// Example 4: External API Call
toolRegistry.register({
  name: 'call_external_api',
  description: 'Make a call to an external API endpoint.',
  parameters: {
    type: 'object',
    properties: {
      url: {
        type: 'string',
        description: 'The API endpoint URL',
      },
      method: {
        type: 'string',
        description: 'HTTP method (GET, POST, PUT, DELETE)',
      },
      body: {
        type: 'object',
        description: 'Request body (for POST/PUT)',
      },
    },
    required: ['url', 'method'],
  },
  handler: async (args) => {
    const { url, method = 'GET', body } = args;
    
    // TODO: Replace with actual API call
    // Example: const response = await fetch(url, { method, body: JSON.stringify(body) });
    
    // Simulated response
    return {
      url,
      method,
      status: 200,
      data: {
        message: 'API call successful (simulated)',
        timestamp: new Date().toISOString(),
      },
    };
  },
});

// Example 5: Weather API (Real implementation example)
toolRegistry.register({
  name: 'get_weather',
  description: 'Get current weather information for a location.',
  parameters: {
    type: 'object',
    properties: {
      location: {
        type: 'string',
        description: 'City name or coordinates',
      },
      units: {
        type: 'string',
        description: 'Temperature units: celsius or fahrenheit',
      },
    },
    required: ['location'],
  },
  handler: async (args) => {
    const { location, units = 'celsius' } = args;
    
    // Example: Real API integration
    // const apiKey = process.env.WEATHER_API_KEY;
    // const response = await fetch(
    //   `https://api.weather.com/v1/current?location=${location}&units=${units}&key=${apiKey}`
    // );
    // const data = await response.json();
    // return data;
    
    // Simulated response
    return {
      location,
      temperature: units === 'celsius' ? 22 : 72,
      condition: 'Partly Cloudy',
      humidity: 65,
      windSpeed: 15,
      units,
      message: 'Weather data retrieved (simulated)',
    };
  },
});

