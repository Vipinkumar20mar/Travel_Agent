import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
import psycopg
from langchain_core.messages import HumanMessage,BaseMessage,AIMessage,SystemMessage
from langgraph.checkpoint.postgres import PostgresSaver
from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flight
from typing import TypedDict, Annotated
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph,START,END
load_dotenv()
DATABASE_URL=os.getenv("DATABASE_URL")

#LLM

llm=ChatGroq(
    model="llama-3.3-70b-versatile",
    api_key=os.getenv("GROQ_API_KEY"),
    temperature=0.3
)

# state schema class
class TravelState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    user_query: str
    flight_results: str
    hotel_results: str
    itinerary: str
    llm_calls: int


# flight_agent
def flight_agent(state: TravelState):
    query = state["user_query"]
    flight_data =  search_flight(query)
    return {
        "flight_results": flight_data,
        "messages": [
            AIMessage(content=f"Flight results fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }
    
# hotel agent
def hotel_agent(state: TravelState):
    query=f"Best Hotel in {state['user_query']}"
    hotel_data=tavily_search(query)
    return{
        "hotel_results":hotel_data,
        "messages":[
            AIMessage(content=f"hotels results fetched")
        ],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

# # Itinerary Agent
def Itinerary_agent(state: TravelState):
    query=f"""
Create a travel itinerary.
User Query:
{state['user_query']}

Create Flight itinerary.
Flight Results:
{state['flight_results']}

Create Hotel itinerary.
Hotel Results:
{state['hotel_results']}

"""
    response=llm.invoke([

       SystemMessage(
            content="You are an expert travel planner"
        ),
        HumanMessage(content=query)
    ])
    return {
        "itinerary":response.content,
        "messages":[response],
        "llm_calls": state.get("llm_calls", 0) + 1


    }

# Final Response Agent
def final_agent(state: TravelState):

    final_prompt = f"""
    Generate final travel response.

    Flights:
    {state['flight_results']}

    Hotels:
    {state['hotel_results']}

    Itinerary:
    {state['itinerary']}
    """

    response = llm.invoke([
        HumanMessage(content=final_prompt)
    ])

    return {
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1
    }

graph = StateGraph(TravelState)

graph.add_node("flight_agent", flight_agent)
graph.add_node("hotel_agent", hotel_agent)
graph.add_node("Itinerary_agent", Itinerary_agent)
graph.add_node("final_agent", final_agent)

graph.add_edge(START, "flight_agent")
graph.add_edge("flight_agent", "hotel_agent")
graph.add_edge("hotel_agent", "Itinerary_agent")
graph.add_edge("Itinerary_agent", "final_agent")
graph.add_edge("final_agent", END)

# Persistent connection so both CLI and Streamlit can share the compiled app
_conn = psycopg.connect(DATABASE_URL, autocommit=True)
checkpointer = PostgresSaver(_conn)
checkpointer.setup()




app=graph.compile(checkpointer=checkpointer)

if __name__ == "__main__":
    config = {
        "configurable": {
            "thread_id": "user_vipin"
        }
    }
    user_input = input("Enter travel request: ")

    result = app.invoke(
        {
            "messages": [
                HumanMessage(content=user_input)
            ],
            "user_query": user_input,
            "flight_results": "",
            "hotel_results": "",
            "itinerary": "",
            "llm_calls": 0
        },
        config=config
    )

    print("\nFINAL RESPONSE:\n")

    for msg in result["messages"]:
        print(msg.content)


    


