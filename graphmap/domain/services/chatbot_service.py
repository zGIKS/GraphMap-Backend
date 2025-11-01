"""
Servicio de chatbot usando DeepSeek para responder preguntas sobre el grafo
"""
import json
from typing import Dict, Optional
from openai import OpenAI
from config import settings
from graphmap.domain.services.graph_service import GraphService
from graphmap.domain.services.city_service import CityService


class ChatbotService:
    """Servicio para IA"""

    def __init__(self):
        self.client = OpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=settings.DEEPSEEK_BASE_URL)
        self.graph_service = GraphService()
        self.city_service = CityService()

    def _execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        if tool_name == "get_graph_summary":
            return self.graph_service.get_graph_summary()

        elif tool_name == "get_cities":
            cities = self.city_service.load_cities_from_excel()
            return {
                "total": len(cities),
                "cities": [{"id": c.id, "name": c.city, "country": c.country} for c in cities]
            }

        elif tool_name == "get_city_details":
            city_name = arguments.get("city_name", "")
            cities = self.city_service.load_cities_from_excel()
            for c in cities:
                if c.city.lower() == city_name.lower() and c.country.lower() == "united states":
                    return {"id": c.id, "city": c.city, "country": c.country, "lat": c.lat, "lng": c.lng}
            return {"error": "City not found in United States"}

        return {"error": "Unknown tool"}

    def chat(self, user_message: str, conversation_history: Optional[list] = None) -> Dict:
        graph_context = self.graph_service.get_graph_summary()
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "get_graph_summary",
                    "description": "Obtiene la cantidad de ciudades y conexiones",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_cities",
                    "description": "Lista las ciudades disponibles",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_city_details",
                    "description": "Obtiene detalles de una ciudad específica por nombre",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {"type": "string", "description": "Nombre de la ciudad"}
                        },
                        "required": ["city_name"]
                    }
                }
            }
        ]

        messages = conversation_history or []
        if not messages:
            system_msg = f"""Eres Graphito, un asistente que responde preguntas sobre las ciudades, la cantidad de ciudades y conexiones del grafo, y detalles de ciudades específicas.
Grafo: {graph_context['num_nodes']} ciudades, {graph_context['num_edges']} conexiones.
Responde en español de forma clara. Saluda diciendo 'Hazle preguntas a Graphito' al inicio de la conversación.
Responde en formato Markdown."""
            messages.append({"role": "system", "content": system_msg})

        messages.append({"role": "user", "content": user_message})

        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            temperature=0.7,
            max_tokens=300
        )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append({
                "role": "assistant",
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {"name": tc.function.name, "arguments": tc.function.arguments}
                    } for tc in assistant_message.tool_calls
                ]
            })

            for tool_call in assistant_message.tool_calls:
                args = json.loads(tool_call.function.arguments)
                result = self._execute_tool(tool_call.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result)
                })

            final_response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7,
                max_tokens=300
            )

            final_msg = final_response.choices[0].message
            messages.append({"role": "assistant", "content": final_msg.content or ""})

            return {
                "response": final_msg.content,
                "conversation_history": messages,
                "tool_used": True
            }

        messages.append({"role": "assistant", "content": assistant_message.content or ""})
        return {
            "response": assistant_message.content,
            "conversation_history": messages,
            "tool_used": False
        }
