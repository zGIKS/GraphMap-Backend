"""
Servicio de chatbot usando DeepSeek para responder preguntas sobre el grafo
"""
import json
from typing import Dict, Optional
from openai import OpenAI
from config import settings
from graphmap.domain.services.graph_service import GraphService
from graphmap.domain.services.city_service import CityService

CACHED_RESPONSES = {
    "hola": "¡Hola! Hazle preguntas a Graphito. Puedo ayudarte con información sobre ciudades y el grafo.",
    "ayuda": "Puedo responder sobre: cantidad de ciudades/conexiones, buscar ciudad específica por nombre.",
}

class ChatbotService:
    """Servicio para IA"""

    def __init__(self):
        self.client = None
        self.api_key = settings.DEEPSEEK_API_KEY
        self.base_url = settings.DEEPSEEK_BASE_URL
        self.graph_service = GraphService()
        self.city_service = CityService()

    def _get_client(self) -> OpenAI:
        if self.client is not None:
            return self.client
        if not self.api_key:
            raise RuntimeError("Chat service is not configured")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        return self.client

    def _execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        if tool_name == "get_graph_summary":
            return self.graph_service.get_graph_summary()
        elif tool_name == "get_city_details":
            city_name = arguments.get("city_name", "")
            results = self.city_service.search_cities(city_name)
            if results:
                c = results[0]
                return {"id": c.id, "city": c.city, "country": c.country, "lat": c.lat, "lng": c.lng}
            return {"error": "City not found"}
        return {"error": "Unknown tool"}

    def chat(self, user_message: str, conversation_history: Optional[list] = None) -> Dict:
        client = self._get_client()
        msg_lower = user_message.lower().strip()
        if msg_lower in CACHED_RESPONSES:
            return {"response": CACHED_RESPONSES[msg_lower], "conversation_history": [], "tool_used": False}

        messages = conversation_history or []
        if len(messages) > 8:
            messages = [messages[0]] + messages[-7:]

        if not messages:
            ctx = self.graph_service.get_graph_summary()
            system_msg = f"Asistente Graphito. {ctx['num_nodes']} ciudades, {ctx['num_edges']} conexiones. Responde en español y Markdown."
            messages.append({"role": "system", "content": system_msg})

        messages.append({"role": "user", "content": user_message})

        tools = [
            {"type": "function", "function": {"name": "get_graph_summary", "description": "Cantidad de ciudades y conexiones", "parameters": {"type": "object", "properties": {}}}},
            {"type": "function", "function": {"name": "get_city_details", "description": "Detalles de ciudad por nombre", "parameters": {"type": "object", "properties": {"city_name": {"type": "string"}}, "required": ["city_name"]}}}
        ]

        response = client.chat.completions.create(
            model="deepseek-chat", messages=messages, tools=tools, temperature=0.3, max_tokens=200
        )

        assistant_message = response.choices[0].message

        if assistant_message.tool_calls:
            messages.append({
                "role": "assistant", "content": assistant_message.content or "",
                "tool_calls": [{"id": tc.id, "type": tc.type, "function": {"name": tc.function.name, "arguments": tc.function.arguments}} for tc in assistant_message.tool_calls]
            })
            for tool_call in assistant_message.tool_calls:
                result = self._execute_tool(tool_call.function.name, json.loads(tool_call.function.arguments))
                messages.append({"role": "tool", "tool_call_id": tool_call.id, "content": json.dumps(result)})

            final = client.chat.completions.create(model="deepseek-chat", messages=messages, temperature=0.3, max_tokens=200)
            messages.append({"role": "assistant", "content": final.choices[0].message.content or ""})
            return {"response": final.choices[0].message.content, "conversation_history": messages, "tool_used": True}

        messages.append({"role": "assistant", "content": assistant_message.content or ""})
        return {"response": assistant_message.content, "conversation_history": messages, "tool_used": False}
