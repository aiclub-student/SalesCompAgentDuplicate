# src/ticket_agent.py

from langchain_core.messages import SystemMessage, HumanMessage
from src.create_llm_message import create_llm_message
from src.send_email import send_email
from pydantic import BaseModel

# When TicketAgent object is created, it's initialized with a model. 
# The main entry point is the ticket_agent method. You can see workflow.add_node for ticket_agent node in graph.py

# Define Pydantic models for structured output
class TicketResponse(BaseModel):
    response: str
    createTicket: bool 

class TicketEmail(BaseModel):
    response: str
    htmlEmail: str
    
class TicketAgent:
    
    def __init__(self, model):
        """
        Initialize the TicketAgent with a ChatOpenAI model.
        
        :param model: An instance of the ChatOpenAI model used for generating responses.
        """
        self.model = model

    def generate_ticket_response(self, state: dict) -> str:
        """
        Generate a response for ticket-related queries using the ChatOpenAI model. 
        
        :param user_query: The original query from the user.
        :return: A string, including response (string) and createTicket (bool) generated by the language model. Please
        note that the 'response' goes to the user in the chat interaction.
        
        """
        user_query = state.get('initialMessage', '')

        # Define the prompt to generate a response for the user
        ticket_prompt = f"""
        You are a Sales Compensation Support Assistant. Your role is to collect necessary information and decide if a support 
        ticket needs to be created or not.

        USER QUERY: "{user_query}"

        REQUIRED INFORMATION:
        - Full Name
        - Email Address (must be valid email format)
        - Issue Description

        INSTRUCTIONS:
        1. Check conversation history to confirm if ticket has already been created:
           - If a ticket has already been created for this issue, set createTicket=False and politely ask if they need anything else
        
        2. Parse user information:
           - Extract Full Name (if provided)
           - Extract and validate Email Address (if provided)
           - Extract Issue Description from query
        
        3. Determine next action:
           IF all required information is present:
           - Set createTicket=True
           - Format response: "Thank you [First Name], I've created a support ticket for the Sales Compensation team. They will contact you at [email]. Is there anything else I can help you with?"
           
           IF information is missing:
           - Set createTicket=False
           - Format response: "To help you better, I need your [missing information]. This will allow me to create a support ticket for our Sales Compensation team."

        OUTPUT REQUIREMENTS:
        - response: Your message to the user
        - createTicket: Boolean (True only if all required information is present and no ticket exists)

        Remember: Only create new tickets when you have ALL required information and no existing ticket.
       
        """
       
        # Create a well-formatted message for LLM by passing the retrieved information above to create_llm_messages
        llm_messages = create_llm_message(ticket_prompt)

        # Invoke the model with the well-formatted prompt, including SystemMessage, HumanMessage, and AIMessage
        llm_response = self.model.with_structured_output(TicketResponse).invoke(llm_messages)
        
        # Extract the content attribute from the llm_response object 
        full_response = llm_response
        
        return full_response

    def generate_ticket_email(self, state: dict) -> str:
        """
        Generate an email as a well-formatted html using the ChatOpenAI model.
        
        :param user_query: The original query from the user.
        :return: A string response generated by the language model.
        
        """

        # Define the prompt to generate email for the support team
        ticket_email_prompt = f"""
        You are creating a support ticket email for the Sales Compensation team. You have realized that you are not able to solve user's concern. 
        
        Create a well-formatted HTML email as a well-formatted html that can be sent directly to the Sales Comp Support team.
        1. User Details: 
           - User's Full name
           - User's Email address
        3. Issue description

        Format Requirements:
        - Use proper HTML tags (<p>, <br>, etc.)
        - Make important information visually stand out
        - Use "Sales Comp Agent" as your signature at the end of email
        - Keep it professional and concise

        Please provide the email content in the field "htmlEmail".

        """
        # Create a well-formatted message for LLM by passing the retrieved information above to create_llm_messages
        llm_messages = create_llm_message(ticket_email_prompt)

        # Invoke the model with the well-formatted prompt, including SystemMessage, HumanMessage, and AIMessage
        llm_response = self.model.with_structured_output(TicketEmail).invoke(llm_messages)
        
        # Extract the content attribute from the llm_response object 
        ticket_email_response = llm_response.htmlEmail
        return ticket_email_response

    def ticket_agent(self, state: dict) -> dict:
        """
        Handle ticket-related queries by generating a response using the ChatOpenAI model.
        
        :param state: A dictionary containing the state of the current conversation, including the user's initial message.
        :return: A dictionary with the updated state, including the response and the node category.
        """
        # Generate a response based on the user's initial message
        full_response = self.generate_ticket_response(state)

        if full_response.createTicket:
            # Generate an email that can be sent to ServiceNow ticketing system
            ticket_email_response = self.generate_ticket_email(state)

            # Send the generated ticket response as an email to the support team
            send_email(from_email='malihajburney@gmail.com', 
                            to_email='i_jahangir@hotmail.com', 
                        subject='New Ticket from SalesCompAgent', 
                        html_content=ticket_email_response)
            
        # Return the updated state with the generated response and the category set to 'ticket'.
        return {
            "lnode": "ticket_agent", 
            "responseToUser": full_response.response,
            "category": "ticket"
        }