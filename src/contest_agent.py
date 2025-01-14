# src/contest_agent.py

# Importing required libraries for message handling and data validation
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from src.create_llm_message import create_llm_message
from src.book_appointment import handle_appointment_request, book_appointment
from datetime import datetime
from typing import Optional
from src.send_email import send_email
import markdown2

# Data model for structuring the LLM's response
class ContestDecision(BaseModel):
    nextsteps: str # Stores the next steps or actions for the user
    decision: str  # Stores the decision type ('Info', 'URLform', 'Other')
    timeslot: Optional[datetime] = None
    email: Optional[str]
    name: Optional[str]

# When ContestAgent object is created, it's initialized with a model. 
# The main entry point is the contest_agent method. You can see workflow.add_node for contest_agent node in graph.py

class ContestAgent:
    
    def __init__(self, model):
        """
        Initialize the ContestAgent with a ChatOpenAI model.
        
        :param model: An instance of the ChatOpenAI model used for generating responses.
        """
        self.model = model

    def get_available_slots(self):
        # Calls external function to fetch available appointment slots
        # This connects to a calendar or scheduling system
        available_slots = handle_appointment_request()
        # Returns the list of available time slots
        return available_slots

    def list_available_slots(self, available_slots):
        # Creates a prompt template for the AI to format the available slots
        time_slot_prompt = f"""
         You are an appointment booking scheduler. Present the following slots in a brief, easy-to-read format. Keep 
         the message compact but always maintain a friendly, professional, and helpful tone throughout the interaction.

        Available slots: {available_slots}

        Instructions:
        1. Tell the user that they need to book a consultation with Sales Comp team and you will help them book an appointment 
        2. List the slots in a clean and easy to read format
        3. Keep your message under 100 words
        4. Simply ask "Please choose a time slot."
        """

        # Sends the prompt to the AI model to get a formatted response
        response = self.model.invoke(time_slot_prompt)
        # Returns just the content of the AI's response (the formatted slot list)
        return response.content

    def confirm_appointment(self, selected_slot, user_email):
        # Returns a confirmation message with next steps
        result = book_appointment(selected_slot, user_email)
        return result

    def get_contest_url(self) -> str:
        """
        Read and return the contest form URL from a text file. Make sure contesturl.txt exists in the root directory

        :return: A string containing contest URL.
        """
        with open('contesturl.txt', 'r') as file:
            contest_url = file.read()
        return contest_url

    def generate_contest_response(self) -> str:
        """
        Generate a response for contest-related queries using the ChatOpenAI model.
        
        :param user_query: The original query from the user.
        :return: A string response generated by the language model.
        """
        contest_prompt = f"""
        You are a Sales Commissions expert. Users will ask you about starting a SPIF or sales contest. Maintain a 
        friendly, professional, and helpful tone.

        STEP 1: VALIDATE USER INFO
        1. Ask the user to provide their full name and email address to proceed. Update 'decision' to [askforuserinfo] and 'nextsteps' to politely ask the user for name and email address 
        2. If you HAVE all the information (Full name and Email address), categorize user's query per categories in Step 2.
        3. If you DON'T HAVE all the information (Full name and Email address), politely, ask the user for this information.

        STEP 2: UPDATE 'decision' to [BookAppointment]. 

        STEP 3: If user has provided a preferred slot, UPDATE 'decision' to [ConfirmAppointment]

        STEP 4: If the appointment has been confirmed, UPDATE 'decision' to [AppointmentComplete], and explain the next steps using instructions in Step 5

        STEP 5: EXPLAIN THE NEXT STEPS AS DESCRIBED BELOW IN PLAIN ENGLISH
        a. Tell them that the Sales Comp team representative is looking forward to meeting them
        b. Inform them that the Intake Form has been sent via email. Ask them to complete the Intake Form before the meeting
        c. After the meeting, Sales Comp team will send the proposal to the President of Sales and the CFO for approval
        d. No verbal or written communication should be sent to the field without formal approval is complete
        e. If approved, Sales Comp team will prepare launch documentation in collaboration with the Communications team

        STEP 6: END THE CONVERSATION, update the 'nextstep' by wishing the user goodluck and ask them if there is anything
        else that they need help with.
        
        
        """
        # Create a well-formatted message for LLM by passing the contest_prompt above to create_llm_messages
        llm_messages = create_llm_message(contest_prompt)

        # Invoke the model with the well-formatted prompt, including SystemMessage, HumanMessage, and AIMessage
        llm_response = self.model.with_structured_output(ContestDecision).invoke(llm_messages)
        
        full_response = llm_response
        
        return full_response

    def contest_agent(self, state: dict) -> dict:
        """
        Process user's contest-related questions and return appropriate responses.
        
        :param state: Dictionary containing conversation state and user's message
        :return: Dictionary containing:
            - lnode: Name of the current node ("contest_agent")
            - responseToUser: Contest info, URL, or next steps based on the decision
            - category: Type of response ("contest")
        """
        # Generate a response based on the user's initial message
        # Get AI's decision and recommended next steps
        llm_response = self.generate_contest_response()
        
        # Determine the appropriate response based on the LLM's decision
        # Handle BookAppointment case
        if llm_response.decision == 'BookAppointment':
            available_slots = self.get_available_slots()
            user_response = self.list_available_slots(available_slots)

            return {
                "lnode": "contest_agent", 
                "responseToUser": user_response,
                "category": "contest",
                "name": llm_response.name,
                "email": llm_response.email
            }

        elif llm_response.decision == 'ConfirmAppointment':
            user_response = self.confirm_appointment(llm_response.timeslot, llm_response.email)            
            # Send email with Intake Form URL to the user after confirming that the appointment has been booked
            subject = "Please complete the SPIF/Sales Contest Intake Form"
            html_content = markdown2.markdown(self.get_contest_url())
            send_email('malihajburney@gmail.com', llm_response.email, subject, html_content)

        elif llm_response.decision == 'AppointmentComplete':
            user_response = llm_response.nextsteps

        else:  # Handle 'Other' case by sending AI's recommended next steps
            user_response = llm_response.nextsteps

        # Return the updated state with the generated response and the category set to 'contest'
        return {
            "lnode": "contest_agent", 
            "responseToUser": user_response,
            "category": "contest"
        }
