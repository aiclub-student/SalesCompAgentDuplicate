DAILY PROGRESS LOG:

1/3/2025:
- Plan: I think I need to continue to refine the prompt. I think it could be a great differentiator to take time and do thorough testing myself rather than using some Eval tool. It is the human element and going through the prompt refinement myself that would make this AI agent better than others. 

1/2/2025:
- Used Cursor (Claude) to refine the prompt construction for Ticket Agent. My goal was to make it more structured so that the output is more predictable. I learned that if you structure the prompt such that the instructions are less verbose, more specific and concise, it's better for LLM. I also learned that when you want LLM to do some logic checks it is better to say, "Set createTicket=False" instead to verbalizing the logic.

12/31/2024:
- Tested Ticket Agent. Fine tuned the prompt so that it doesn't repeat the ticket generation.

12/30/2024:
- Updated the logic for book_appointment.py. It was not accurately pulling the available slots. Instead it was showing all timeslots as available. Used Cursor to update the logic. The issue was with time zone.
- Updated license to MIT license.

12/28/2024:
- Created test_contest_agent.py to do Eval on contest_agent.py specifically. Haven't checked it yet.

12/23/2024:
- Tested Policy Agent, Commission Agent, and Contest Agent
- Contest Agent has a kink. After booking an appointment, it doesn't end the conversation. Even when the user wants to end conversation it keeps sending the meeting invite.

12/2/2024:
- Updated contestrules.txt, requesting full name and email address instead of simply asking the user to confirm if they have read the rules.
- Tried logic change to ask for full name and email address in the code but it didn't work.

11/30/2024:
- Integrated appointment booking into contest agent.
- Added functions to get available slots and send confirmation message once the user picks a slot.
- We have not completed sending the meeting invite yet.

11/28/2024:
- Created a book_appointment.py and test.py and added client_secret.json. I got help from Cursor and appointment booking is working correctly.

11/17/2024:
- Commission agent started having formatting issue again. I have no idea why it keeps popping up even when though I had fixed it a week ago.
- I ended up removing the following sub-bullets from my commission_prompt, step 5 "Provide Result and Explanation":
    - Please provide the response without using LaTex.
    - Format any calculations and equations in simple plain text or markdown
    - Do not use LaTex for formatting

11/16/2024:
- Created the initial file bookappt.py
- Completed basic Google Calendar integration to get 10 upcoming events and create a dummy event (hard coded)
- Ran using "streamlit run src/bookappt.py", working well
- The only issue is that Access token expires in 3600 sec. You will be required to refresh the access token and put the new token in secrets.toml
- This is the URL for oauthplayground: https://developers.google.com/oauthplayground/?code=4/0AeanS0auqT_S6ohMIHXcBb6oHRh1lXEZIy68E4sCZneBEjdXk6NbeLzCIKvonsUxHJxh0A&scope=https://www.googleapis.com/auth/calendar.events


11/7/2024:
- Updated the prompt for commission agent. Working well with no formatting issues.
- The current prompt calculates the commission using BCR and does not take into account current quota attainment
- If the user provides that additional input then it performs the calculations correctly
- This is something I need to think about whether I'd like the assistant to ask for this information or just clarify that these calculations do not take into account any acceleration.

11/6/2024:
- Fixed the formatting issue for commission agent responses. This required a tricky solution because chat history was not formatting correctly.

11/2/2024:
- Finalized the code for contest_agent. The agent workflow is working well.

11/1/24: 
- I updated the prompt for "plan_explainer_agent.py". 
- Updated the Apachee license info.
- Added feedback_collector_agent to graph.py

10/31/24: 
- I worked on "feedback_collector_agent.py". 
- I've updated the code in this file. 
- I also worked on writing a detailed prompt. I used ChatGPT to refine my prompt. I think I should try to optimize all prompts for other sub-agents as well. However, I think I should do that carefully and do some sort of A/B testing to optimize the prompts.