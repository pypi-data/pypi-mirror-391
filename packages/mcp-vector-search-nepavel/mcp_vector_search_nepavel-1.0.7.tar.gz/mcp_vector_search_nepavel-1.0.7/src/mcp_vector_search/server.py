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
    
    # Конфигурация из env (поддержка старой и новой переменной)
    server_url = os.environ.get('MCP_SERVER_URL') or os.environ.get('MCP_RENDER_URL')
    openrouter_key = os.environ.get('OPENROUTER_KEY')
    supabase_url = os.environ.get('SUPABASE_URL')
    supabase_key = os.environ.get('SUPABASE_KEY')
    
    try:
        # Headers для облачного API
        headers = {
            'Content-Type': 'application/json',
            'X-OpenRouter-Key': openrouter_key,
            'X-Supabase-URL': supabase_url,
            'X-Supabase-Key': supabase_key
        }
        
        # Маршрутизация
        if method == 'initialize':
            result = {
                "protocolVersion": "2024-11-05",
                "serverInfo": {
                    "name": "mcp-vector-search",
                    "version": "1.0.7"
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
                    f'{server_url}/search',
                    json=tool_params,
                    headers=headers,
                    timeout=600
                )
            elif tool_name == 'index':
                # Читаем файлы если пришли пути
                files = tool_params.get('files', [])
                if files and isinstance(files[0], str):
                    # Преобразуем относительные пути в абсолютные
                    absolute_files = []
                    for file_path in files:
                        if not os.path.isabs(file_path):
                            # Относительный путь - делаем абсолютным от CWD
                            absolute_path = os.path.abspath(file_path)
                            sys.stderr.write(f"Converted: {file_path} -> {absolute_path}\n")
                            sys.stderr.flush()
                            absolute_files.append(absolute_path)
                        else:
                            # Уже абсолютный
                            absolute_files.append(file_path)
                    
                    # Читаем файлы с абсолютными путями
                    files_with_content = []
                    for file_path in absolute_files:
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            files_with_content.append({
                                "path": file_path,
                                "content": content,
                                "file_type": file_path.split('.')[-1] if '.' in file_path else 'text'
                            })
                        except Exception as e:
                            sys.stderr.write(f"Error reading {file_path}: {e}\n")
                            sys.stderr.flush()
                            continue
                    tool_params['files'] = files_with_content
                
                response = requests.post(
                    f'{server_url}/index',
                    json=tool_params,
                    headers=headers,
                    timeout=600
                )
            elif tool_name == 'list_projects':
                response = requests.get(
                    f'{server_url}/projects',
                    headers=headers,
                    timeout=30
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
    # Отправляем приветствие при старте
    sys.stderr.write("MCP Vector Search server starting...\n")
    sys.stderr.flush()
    
    try:
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
            except Exception as e:
                sys.stderr.write(f"Error: {e}\n")
                sys.stderr.flush()
    except KeyboardInterrupt:
        sys.stderr.write("MCP server stopped\n")
        sys.stderr.flush()

if __name__ == "__main__":
    main()
