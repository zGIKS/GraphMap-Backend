"""
Servicio de chatbot usando DeepSeek para responder preguntas sobre el grafo
"""
import json
from typing import Dict, Optional
from openai import OpenAI
from config import settings
from graphmap.domain.services.graph_service import GraphService
from graphmap.domain.services.city_service import CityService
from graphmap.domain.services.pathfinding_service import PathfindingService


class ChatbotService:
    """Servicio para chatbot con DeepSeek que responde preguntas sobre el grafo"""

    def __init__(self):
        """Inicializa el servicio de chatbot con DeepSeek"""
        self.client = OpenAI(
            api_key=settings.DEEPSEEK_API_KEY,
            base_url="https://api.deepseek.com"
        )
        self.graph_service = GraphService()
        self.city_service = CityService()

    def _get_graph_context(self) -> Dict:
        """
        Obtiene información del grafo para contexto del chatbot

        Returns:
            Dict con información resumida del grafo
        """
        summary = self.graph_service.get_graph_summary()
        cities = self.city_service.load_cities_from_excel()

        return {
            "total_cities": summary["num_nodes"],
            "total_edges": summary["num_edges"],
            "countries": list(set(city.country for city in cities[:100])),  # Muestra
            "algorithm": "Delaunay triangulation with 500km max distance filter"
        }

    def _execute_tool(self, tool_name: str, arguments: Dict) -> Dict:
        """
        Ejecuta una herramienta (función) solicitada por el chatbot

        Args:
            tool_name: Nombre de la herramienta
            arguments: Argumentos de la herramienta

        Returns:
            Resultado de la ejecución
        """
        if tool_name == "find_shortest_path":
            start_id = arguments.get("start_id")
            goal_id = arguments.get("goal_id")

            graph = self.graph_service.build_city_graph()
            cities = self.city_service.load_cities_from_excel()
            pathfinding = PathfindingService(graph, cities)

            result = pathfinding.a_star(start_id, goal_id)

            if result:
                return {
                    "success": True,
                    "start_city": result["path"][0]["city"],
                    "goal_city": result["path"][-1]["city"],
                    "distance_km": result["distance"],
                    "path_length": result["path_length"],
                    "cities_in_path": [city["city"] for city in result["path"]],
                    "cities_explored": result["cities_explored"]
                }
            else:
                return {"success": False, "error": "No path found"}

        elif tool_name == "get_graph_summary":
            return self.graph_service.get_graph_summary()

        elif tool_name == "search_city":
            query = arguments.get("city_name", "")
            cities = self.city_service.search_cities(query)
            return {
                "found": len(cities),
                "cities": [{"id": c.id, "name": c.city, "country": c.country} for c in cities[:10]]
            }

        return {"error": "Unknown tool"}

    def chat(self, user_message: str, conversation_history: Optional[list] = None) -> Dict:
        """
        Procesa un mensaje del usuario y genera una respuesta usando DeepSeek

        Args:
            user_message: Mensaje del usuario
            conversation_history: Historial de conversación (opcional)

        Returns:
            Dict con la respuesta del chatbot
        """
        # Obtener contexto del grafo
        graph_context = self._get_graph_context()

        # Definir herramientas disponibles para el chatbot
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "find_shortest_path",
                    "description": "Encuentra el camino más corto entre dos ciudades usando A*",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "start_id": {"type": "integer", "description": "ID de la ciudad origen"},
                            "goal_id": {"type": "integer", "description": "ID de la ciudad destino"}
                        },
                        "required": ["start_id", "goal_id"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_graph_summary",
                    "description": "Obtiene resumen del grafo (número de nodos y aristas)",
                    "parameters": {"type": "object", "properties": {}}
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "search_city",
                    "description": "Busca ciudades por nombre",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "city_name": {"type": "string", "description": "Nombre de la ciudad a buscar"}
                        },
                        "required": ["city_name"]
                    }
                }
            }
        ]

        # Preparar mensajes
        messages = conversation_history or []

        # Agregar contexto del sistema
        if not messages:
            system_message = f"""Eres un asistente experto en grafos y algoritmos de búsqueda de caminos.
Estás ayudando a usuarios a entender un grafo de ciudades construido con triangulación de Delaunay.

Contexto del grafo:
- Total de ciudades: {graph_context['total_cities']}
- Total de conexiones: {graph_context['total_edges']}
- Algoritmo usado: {graph_context['algorithm']}
- El algoritmo A* usa heurística Haversine con complejidad O(E log V)

Puedes usar las herramientas disponibles para responder preguntas específicas.
Responde en español de forma clara y concisa."""

            messages.append({"role": "system", "content": system_message})

        # Agregar mensaje del usuario
        messages.append({"role": "user", "content": user_message})

        # Llamar a DeepSeek
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            tools=tools,
            temperature=0.7,
            max_tokens=500
        )

        assistant_message = response.choices[0].message

        # Si el modelo quiere usar una herramienta
        if assistant_message.tool_calls:
            # Convertir a dict para serialización
            messages.append({
                "role": assistant_message.role,
                "content": assistant_message.content or "",
                "tool_calls": [
                    {
                        "id": tc.id,
                        "type": tc.type,
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments
                        }
                    }
                    for tc in assistant_message.tool_calls
                ]
            })

            # Ejecutar cada herramienta solicitada
            for tool_call in assistant_message.tool_calls:
                function_name = tool_call.function.name
                function_args = json.loads(tool_call.function.arguments)

                # Ejecutar la herramienta
                function_result = self._execute_tool(function_name, function_args)

                # Agregar resultado al historial
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(function_result)
                })

            # Llamar de nuevo para obtener la respuesta final
            second_response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )

            final_message = second_response.choices[0].message
            messages.append({
                "role": final_message.role,
                "content": final_message.content or ""
            })

            return {
                "response": final_message.content,
                "conversation_history": messages,
                "tool_used": True
            }

        # Respuesta directa sin herramientas
        messages.append({
            "role": assistant_message.role,
            "content": assistant_message.content or ""
        })

        return {
            "response": assistant_message.content,
            "conversation_history": messages,
            "tool_used": False
        }
