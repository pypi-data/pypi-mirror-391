#!/usr/bin/env python3
"""
MCP сервер для облачного векторного поиска
"""
import os
import sys
import json
import requests
from typing import Any, Dict

def send_response(response: Dict[str, Any]):
    """Отправить ответ в stdout"""
    print(json.dumps(response), flush=True)

def handle_request(request: Dict[str, Any]):
    """Обработать MCP запрос"""
    method = request.get('method')
    params = request.get('params', {})
    request_id = request.get('id')
    
    # Конфигурация из env
    render_url = os.environ.get('MCP_RENDER_URL')
    openrouter_key = os.environ.get('OPENROUTER_KEY')
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    try:
        # Headers для Render API
        headers = {
            'Content-Type': 'application/json',
            'X-OpenRouter-Key': openrouter_key,
            'X-Supabase-URL': supabase_url,
            'X-Supabase-Key': supabase_key
        }
        
        # Маршрутизация
        if method == 'initialize':
            result = {
                "protocolVersion": "0.1.0",
                "serverInfo": {
                    "name": "mcp-vector-search",
                    "version": "1.0.0"
                },
                "capabilities": {
                    "tools": {}
                }
            }
        elif method == 'tools/list':
            result = {
                "tools": [
                    {
                        "name": "search",
                        "description": "Search code in vector database",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {"type": "string"},
                                "project_filter": {"type": "string"},
                                "max_results": {"type": "number"}
                            },
                            "required": ["query"]
                        }
                    },
                    {
                        "name": "index",
                        "description": "Index project files",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "project_name": {"type": "string"},
                                "files": {"type": "array"}
                            },
                            "required": ["project_name", "files"]
                        }
                    },
                    {
                        "name": "list_projects",
                        "description": "List all indexed projects",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        elif method == 'tools/call':
            tool_name = params.get('name')
            tool_params = params.get('arguments', {})
            
            if tool_name == 'search':
                response = requests.post(
                    f'{render_url}/search',
                    json=tool_params,
                    headers=headers,
                    timeout=120
                )
            elif tool_name == 'index':
                response = requests.post(
                    f'{render_url}/index',
                    json=tool_params,
                    headers=headers,
                    timeout=120
                )
            elif tool_name == 'list_projects':
                response = requests.get(
                    f'{render_url}/projects',
                    headers=headers,
                    timeout=120
                )
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
            
            response.raise_for_status()
            result = {"content": [{"type": "text", "text": json.dumps(response.json())}]}
        else:
            raise ValueError(f"Unknown method: {method}")
        
        send_response({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        })
        
    except Exception as e:
        send_response({
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": str(e)
            }
        })

def main():
    """Основной цикл MCP сервера"""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        
        try:
            request = json.loads(line)
            handle_request(request)
        except json.JSONDecodeError as e:
            send_response({
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": f"Parse error: {e}"
                }
            })

if __name__ == "__main__":
    main()
