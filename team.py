import time
import sys
from datetime import datetime
from agno.agent import Agent
from agno.team.team import Team
from agno.models.openai import OpenAIChat
from tools.get_items import get_items
from tools.get_requirement_details import get_requirement_details
from tools.get_quotations import get_quotations
from evaluate_ai import evaluate_vendors
from database import get_db_connection

requirement_agent = Agent(
    name="Requirement Fetcher",
    role="Fetches procurement terms",
    model=OpenAIChat(id="gpt-4-turbo"),
    #debug_mode = True,
    tools=[get_requirement_details]
)

item_agent = Agent(
    name="Item Fetcher",
    role="Fetches product specifications",
    model=OpenAIChat(id="gpt-4-turbo"),
    #debug_mode = True,
    tools=[get_items]
)

quotation_agent = Agent(
    name="Quotation Fetcher",
    role="Fetches vendor quotations",
    model=OpenAIChat(id="gpt-4-turbo"),
    #debug_mode=True,
    tools=[get_quotations]
)

evaluation_agent = Agent(
    name="Vendor Evaluator",
    role="Evaluates vendor offers",
    model=OpenAIChat(id="gpt-4-turbo"),
    #debug_mode=True,
    tools=[evaluate_vendors]
)

# Define the procurement team with instructions
procurement_team = Team(
    name="Procurement Team",
    mode="coordinate",
    model=OpenAIChat(id="gpt-4-turbo"),
    members=[requirement_agent, item_agent, quotation_agent, evaluation_agent],  # Team members
    instructions=[
        "1. **Requirement Fetching**: First, the **Requirement Fetcher** must fetch the procurement terms from the provided request data. This includes gathering all necessary procurement requirements.",
        "    - **Task for Requirement Fetcher**: Fetch the requirement details using the `get_requirement_details` tool.",
        "    - **Expected output**: A detailed list of the procurement terms that include specifications, quantity, delivery timelines, and any other relevant terms.",
        "2. **Product Specifications**: Once the procurement terms are fetched, the **Item Fetcher** is responsible for gathering the product specifications as per the given requirements.",
        "    - **Task for Item Fetcher**: Use the `get_items` tool to fetch the product specifications.",
        "    - **Expected output**: A detailed specification of the product(s) requested, including quality, material, and size.",
        "3. **Quotation Retrieval**: The **Quotation Fetcher** will retrieve the quotations from vendors who meet the criteria.",
        "    - **Task for Quotation Fetcher**: Use the `get_quotations` tool to retrieve vendor quotations that match the product specifications.",
        "    - **Expected output**: A list of vendor quotations, including price, delivery terms, and vendor information.",
        "4. **Vendor Evaluation**: The **Vendor Evaluator** will evaluate the vendor quotations to ensure they align with the procurement terms and requirements.",
        "    - **Task for Vendor Evaluator**: Use the `evaluate_vendors` tool to evaluate the retrieved vendor quotations.",
        "    - **Before evaluation**: Create evaluation criteria based on the requirement details (price, quality, delivery time, etc.).",
        "    - **Expected output**: A list of accepted/rejected vendors based on the evaluation criteria.",
        "5. **Final Response**: After the vendor evaluation, the team will compile the final response, which will include a list of approved vendors along with their quotations.",
        "    - **Final Output**: A summary of the vendor evaluation and the final vendor list, including their quotations and contact details.",
        "Key Notes:",
        "1. **Task Transfer**: If any task cannot be completed by a given agent, it should be transferred to the appropriate agent. Ensure the task is clearly defined with expected output.",
        "2. **Validation**: After each agent completes its task, validate the output before moving to the next step. If the output is not satisfactory, re-assign the task or request additional information.",
        "3. **Coordination**: Since this is a multi-agent team, ensure that each agent's output is passed to the next agent in the sequence as per the instructions.",
        "4. **Data Flow**: Make sure to properly collect and pass all required data between agents. The Vendor Evaluator needs the req_id, items data, quotations data, and evaluation criteria to function properly."
    ],
    #response_model=dict,  # Define the expected response format
    show_tool_calls=True,  # Optionally enable to see the tool calls
    markdown=True,  # Enable markdown formatting for responses
    #debug_mode=True,  # Enable debug mode for debugging purposes
    show_members_responses=True,  # Show responses from all members
)

# Track processed requirements
processed_requirements = set()

def fetch_new_requirements():
    conn = get_db_connection()
    cursor = conn.cursor()

    while True:
        print("Checking for new requirements...")

        # Fetch new requirements based on DATE_CREATED
        cursor.execute("""
            SELECT REQ_ID, QUOTATION_FREEZ_TIME, DATE_CREATED 
            FROM requirementdetails
            WHERE DATE_CREATED >= DATEADD(SECOND, -10, GETDATE())
        """)
        new_requirements = cursor.fetchall()

        for req in new_requirements:
            req_id, freeze_time, date_created = req.REQ_ID, req.QUOTATION_FREEZ_TIME, req.DATE_CREATED

            # Process only new requirements
            if req_id not in processed_requirements:
                print(f"New Requirement Detected: {req_id}")

                # Notify all vendors
                notify_vendors(req_id)

                # Wait until freeze time is over
                current_time = datetime.now()
                time_diff = (freeze_time - current_time).total_seconds()
                print(time_diff)

                if time_diff > 0:
                    print(f" Waiting {time_diff} seconds until freeze time is over for REQ_ID: {req_id}")
                    for remaining in range(int(time_diff), 0, -1):
                        sys.stdout.write(f"\r Time remaining: {remaining} seconds ")  # Overwrite the line
                        sys.stdout.flush()
                        time.sleep(1)

                    print("\n Freeze time over. Proceeding with the procurement process.")

                # Start the procurement process
                print(f"Triggering Procurement Process for REQ_ID: {req_id}")
                start_procurement(req_id)

                # Mark the requirement as processed
                processed_requirements.add(req_id)

        time.sleep(10)  # Check for new requirements every 10 seconds

# Function to notify vendors
def notify_vendors(req_id):
    print(f"Notifying all vendors for Requirement {req_id}")

# Function to start procurement process
def start_procurement(req_id):
    procurement_team.print_response(
    f"Please analyze procurement requirement #{req_id} and provide vendor recommendations."
)

# Start monitoring requirements
if __name__ == "__main__":
    fetch_new_requirements()