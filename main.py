from openai import OpenAI
import json
import leaf
import time
import os

# Set your Leaf username & password (get these here: https://withleaf.io/account/quickstart)
leaf_username = os.environ["LEAF_USERNAME"]
leaf_password = os.environ["LEAF_PASSWORD"]

# Set your OpenAI API key
OPENAI_API_KEY = os.environ['OPENAI_API_KEY']

LEAF_ASSISTANT_ID = "asst_6LtS8MoQeQM6oyKOdS3jhfPT"
client = OpenAI()


def submit_message(assistant_id, thread, user_message):
    client.beta.threads.messages.create(
        thread_id=thread.id, role="user", content=user_message
    )
    return client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )


def get_response(thread):
    return client.beta.threads.messages.list(thread_id=thread.id, order="asc")


def create_thread_and_run(user_input):
    thread = client.beta.threads.create()
    run = submit_message(LEAF_ASSISTANT_ID, thread, user_input)
    return thread, run


def pretty_print(messages):
    print()
    print("Response:")
    most_recent_message = sorted(messages, key=lambda msg: msg.created_at, reverse=True)[0]
    print (f"{most_recent_message.content[0].text.value} \n")
    print()


# Waiting in a loop
def wait_on_run(run, thread):
    print(f"# status: {run.status}".ljust(30), end='\r')
    while run.status == "queued" or run.status == "in_progress":
        print(f"# status: {run.status}".ljust(30), end='\r')
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id,
        )
        time.sleep(0.5)
    print(f"# status: {run.status}".ljust(30), end='\r')
    return run


def handle_tool_call(tool_call, leaf_token):
    function_name = tool_call.function.name
    arguments = json.loads(tool_call.function.arguments)
    arguments["token"] = leaf_token

    if function_name == "get_operations":
        response = leaf.get_operations(**arguments)
    elif function_name == "get_fields":
        response = leaf.get_fields(**arguments)
    elif function_name == "get_operation_summary":
        response = leaf.get_operation_summary(**arguments)
    elif function_name == "get_single_field":
        response = leaf.get_single_field(**arguments)
    else:
        raise ValueError(f"Unknown function: {function_name}")

    return response


def handle_tool_calls(thread, run, tool_calls, leaf_token):
    tool_outputs = []
    for tool_call in tool_calls:
        tool_call_response = handle_tool_call(tool_call, leaf_token)
        tool_output = {
            "tool_call_id": tool_call.id,
            "output": json.dumps(tool_call_response),
        }
        tool_outputs.append(tool_output)

    tool_response_run = client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread.id,
        run_id=run.id,
        tool_outputs= tool_outputs
    )

    return tool_response_run

def check_and_handle_actions(run, thread, leaf_token):
    if run.status == "requires_action":
        tool_calls = run.required_action.submit_tool_outputs.tool_calls
        tool_response_run = handle_tool_calls(thread, run, tool_calls, leaf_token)
        tool_response_run = wait_on_run(tool_response_run, thread)
        run = check_and_handle_actions(tool_response_run, thread, leaf_token)
    return (run)


def main():
  thread = client.beta.threads.create()
  leaf_token = leaf.authenticate_with_leaf(leaf_username, leaf_password, remember_me=False)
  while True:
      print()
      user_input =  input("Enter your question: \n")
      run = submit_message(LEAF_ASSISTANT_ID, thread, user_input)
      run = wait_on_run(run, thread)
      run = check_and_handle_actions(run, thread, leaf_token)
  
      pretty_print(get_response(thread))

main()
  



