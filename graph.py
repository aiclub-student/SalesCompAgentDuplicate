from langchain_openai import ChatOpenAI
from typing import TypedDict, Annotated, List, Dict
from langgraph.graph import StateGraph, END
import sqlite3
from langgraph.checkpoint.sqlite import SqliteSaver
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.messages import AnyMessage, SystemMessage, HumanMessage, AIMessage, ChatMessage

# Define the structure of the agent state using TypedDict
class AgentState(TypedDict):
    agent: str
    initialMessage: str
    responseToUser: str
    lnode: str
    category: str

# Define the structure for category classification
class Category(BaseModel):
    category: str

class PolicyResponse(BaseModel):
    policy: str
    response: str

class CommissionResponse(BaseModel):
    commission: str
    calculation: str
    response: str

# Define valid categories
VALID_CATEGORIES = ["policy", "commission", "contest", "ticket", "clarify"]

# Define the salesCompAgent class
class salesCompAgent():
    def __init__(self, api_key):
        # Initialize the model with the given API key
        self.model = ChatOpenAI(model="gpt-4o-mini", temperature=0, api_key=api_key)

        # Build the state graph
        builder = StateGraph(AgentState)
        builder.add_node("classifier", self.initial_classifier)
        builder.add_node("policy", self.policy_agent)
        builder.add_node("commission", self.commission_agent)
        builder.add_node("contest", self.contest_agent)
        builder.add_node("ticket", self.ticket_agent)
        builder.add_node("clarify", self.clarify_agent)

        # Set the entry point and add conditional edges
        builder.set_entry_point("classifier")
        builder.add_conditional_edges("classifier", self.main_router)

        # Define end points for each node
        builder.add_edge("policy", END)
        builder.add_edge("commission", END)
        builder.add_edge("contest", END)
        builder.add_edge("ticket", END)
        builder.add_edge("clarify", END)

        # Set up in-memory SQLite database for state saving
        memory = SqliteSaver(conn=sqlite3.connect(":memory:", check_same_thread=False))
        self.graph = builder.compile(checkpointer=memory)

    # Initial classifier function to categorize user messages
    def initial_classifier(self, state: AgentState):
        print("initial classifier")
        classifier_prompt = f"""
        You are an expert at customer service in sales operations. Please classify the customer
        requests as follows:
        1) If the request is a question about sales policies, category is 'policy'
        2) If the request is a question about user's commissions, category is 'commission'
        3) If the request is a question about contests, category is 'contest'
        4) If the request is a question about tickets, category is 'ticket'
        5) Otherwise ask the user to clarify, category is 'clarify'
        """

        # Invoke the model with the classifier prompt
        llm_response = self.model.with_structured_output(Category).invoke([
            SystemMessage(content=classifier_prompt),
            HumanMessage(content=state['initialMessage']),
        ])

        category = llm_response.category
        print(f"category is {category}")
        
        # Return the updated state with the category
        return{
            "lnode": "initial_classifier", 
            "responseToUser": "Classifier successful",
            "category": category
        }
    
     # Main router function to direct to the appropriate agent based on the category
    def main_router(self, state: AgentState):
        my_category = state['category']
        if my_category in VALID_CATEGORIES:
            return my_category
        else:
            print(f"unknown category: {my_category}")
            return END

    # Defining Policy Agent function
    def policy_agent(self, state: AgentState):
        POLICY_PROMPT = f"""
        You are a Sales Compensation Policy expert. You understand four policies related
        sales compensation. Based on user's query, you would decide which policy to use. 
        The polices are:
        1) Minimum commission guarantee
        2) Air cover bonus
        3) Windfall activation
        4) Leave of absence

        Please provide user response as well as the policy used to decide.      
        """
        print("policy agent")

        # Invoke the model with the policy agent prompt
        llm_response = self.model.with_structured_output(PolicyResponse).invoke([
            SystemMessage(content=POLICY_PROMPT),
            HumanMessage(content=state['initialMessage']),
        ])

        policy = llm_response.policy
        response = llm_response.response
        print(f"Policy is: {policy}, Response is: {response}")
        
        # Return the updated state with the category
        return{
            "lnode": "initial_classifier", 
            "responseToUser": f"{response} \n\n Source: {policy}",
            "category": policy
        }

    # Defining Commission Agent function
    def commission_agent(self, state: AgentState):
        COMMISSION_PROMPT = f"""
        You are a Sales Commissions expert. Users will ask you about what their commission
        will be for a particular deal. You can assume their on-target incentive to be $100000
        and their annual quota to be $2000000. Also note that Commission is equal to on-target
        incentive divided by annual quota. 
        
        Please provide user commission as well as explain how you computed it.      
        """
        print("commission agent")

        # Invoke the model with the commission agent prompt
        llm_response = self.model.with_structured_output(CommissionResponse).invoke([
            SystemMessage(content=COMMISSION_PROMPT),
            HumanMessage(content=state['initialMessage']),
        ])

        commission = llm_response.commission
        calculation = llm_response.calculation
        response = llm_response.response
        print(f"Commission is {commission}, Calculation is {calculation}, Response is {response}")
        
        # Return the updated state with the category
        return{
            "lnode": "initial_classifier", 
            "responseToUser": f"{response} \n\n Source: {calculation}.\n Commission: {commission}",
            "category": calculation
        }
        
        print("commission agent")

    # Placeholder function for the contest agent
    def contest_agent(self, state: AgentState):
        print("contest agent")

    # Placeholder function for the ticket agent
    def ticket_agent(self, state: AgentState):
        print("ticket agent")

    # Placeholder function for the clarify agent
    def clarify_agent(self, state: AgentState):
        print("clarify agent")