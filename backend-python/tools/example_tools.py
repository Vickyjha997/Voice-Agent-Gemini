"""Example function calling tools"""
from datetime import datetime
from tools.tool_registry import ToolRegistry, ToolDefinition

tool_registry = ToolRegistry()


# Example 1: SQL Query Tool
async def execute_sql_query_handler(args: dict):
    """Execute SQL query handler"""
    query = args.get('query')
    database = args.get('database', 'main')
    
    # TODO: Replace with actual database connection
    # Example: result = await db.query(query)
    
    # Simulated response
    return {
        'success': True,
        'database': database,
        'query': query,
        'rows': [
            {'id': 1, 'name': 'Example', 'value': 100},
            {'id': 2, 'name': 'Sample', 'value': 200},
        ],
        'rowCount': 2,
        'message': 'Query executed successfully (simulated)',
    }


tool_registry.register(ToolDefinition(
    name='execute_sql_query',
    description='Execute a SQL query on a database. Use this for data retrieval and analytics.',
    parameters={
        'type': 'object',
        'properties': {
            'query': {
                'type': 'string',
                'description': 'The SQL query to execute',
            },
            'database': {
                'type': 'string',
                'description': 'The database name (optional, defaults to main)',
            },
        },
        'required': ['query'],
    },
    handler=execute_sql_query_handler
))


# Example 2: Analytics Tool
async def get_analytics_handler(args: dict):
    """Get analytics handler"""
    metric = args.get('metric')
    start_date = args.get('startDate')
    end_date = args.get('endDate')
    
    # TODO: Replace with actual analytics API call
    # Example: data = await analytics_api.get_metric(metric, start_date, end_date)
    
    # Simulated response
    return {
        'metric': metric,
        'period': {'start': start_date, 'end': end_date},
        'value': 12345,
        'trend': '+12.5%',
        'dataPoints': [
            {'date': start_date, 'value': 10000},
            {'date': end_date, 'value': 12345},
        ],
        'message': 'Analytics retrieved successfully (simulated)',
    }


tool_registry.register(ToolDefinition(
    name='get_analytics',
    description='Retrieve analytics data for a given time period and metric.',
    parameters={
        'type': 'object',
        'properties': {
            'metric': {
                'type': 'string',
                'description': 'The metric to retrieve (e.g., "users", "revenue", "conversions")',
            },
            'startDate': {
                'type': 'string',
                'description': 'Start date in ISO format (YYYY-MM-DD)',
            },
            'endDate': {
                'type': 'string',
                'description': 'End date in ISO format (YYYY-MM-DD)',
            },
        },
        'required': ['metric', 'startDate', 'endDate'],
    },
    handler=get_analytics_handler
))


# Example 3: Knowledge Base Search
async def search_knowledge_base_handler(args: dict):
    """Search knowledge base handler"""
    query = args.get('query')
    max_results = args.get('maxResults', 5)
    
    # TODO: Replace with actual RAG/vector search
    # Example: results = await vector_db.search(query, max_results)
    
    # Simulated response
    return {
        'query': query,
        'results': [
            {
                'title': 'Example Document 1',
                'content': f'Relevant information about {query}',
                'relevance': 0.95,
            },
            {
                'title': 'Example Document 2',
                'content': f'Additional context for {query}',
                'relevance': 0.87,
            },
        ],
        'totalResults': 2,
        'message': 'Knowledge base search completed (simulated)',
    }


tool_registry.register(ToolDefinition(
    name='search_knowledge_base',
    description='Search the knowledge base for relevant information on a topic.',
    parameters={
        'type': 'object',
        'properties': {
            'query': {
                'type': 'string',
                'description': 'The search query',
            },
            'maxResults': {
                'type': 'number',
                'description': 'Maximum number of results to return (default: 5)',
            },
        },
        'required': ['query'],
    },
    handler=search_knowledge_base_handler
))


# Example 4: External API Call
async def call_external_api_handler(args: dict):
    """Call external API handler"""
    url = args.get('url')
    method = args.get('method', 'GET')
    body = args.get('body')
    
    # TODO: Replace with actual API call
    # Example: response = await httpx.request(method, url, json=body)
    
    # Simulated response
    return {
        'url': url,
        'method': method,
        'status': 200,
        'data': {
            'message': 'API call successful (simulated)',
            'timestamp': datetime.now().isoformat(),
        },
    }


tool_registry.register(ToolDefinition(
    name='call_external_api',
    description='Make a call to an external API endpoint.',
    parameters={
        'type': 'object',
        'properties': {
            'url': {
                'type': 'string',
                'description': 'The API endpoint URL',
            },
            'method': {
                'type': 'string',
                'description': 'HTTP method (GET, POST, PUT, DELETE)',
            },
            'body': {
                'type': 'object',
                'description': 'Request body (for POST/PUT)',
            },
        },
        'required': ['url', 'method'],
    },
    handler=call_external_api_handler
))


# Example 5: Weather API (Real implementation example)
async def get_weather_handler(args: dict):
    """Get weather handler"""
    location = args.get('location')
    units = args.get('units', 'celsius')
    
    # Example: Real API integration
    # api_key = os.getenv('WEATHER_API_KEY')
    # async with httpx.AsyncClient() as client:
    #     response = await client.get(
    #         f'https://api.weather.com/v1/current',
    #         params={'location': location, 'units': units, 'key': api_key}
    #     )
    #     return response.json()
    
    # Simulated response
    return {
        'location': location,
        'temperature': 22 if units == 'celsius' else 72,
        'condition': 'Partly Cloudy',
        'humidity': 65,
        'windSpeed': 15,
        'units': units,
        'message': 'Weather data retrieved (simulated)',
    }


tool_registry.register(ToolDefinition(
    name='get_weather',
    description='Get current weather information for a location.',
    parameters={
        'type': 'object',
        'properties': {
            'location': {
                'type': 'string',
                'description': 'City name or coordinates',
            },
            'units': {
                'type': 'string',
                'description': 'Temperature units: celsius or fahrenheit',
            },
        },
        'required': ['location'],
    },
    handler=get_weather_handler
))

