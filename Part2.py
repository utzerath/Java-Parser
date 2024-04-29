import json
import requests
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
from openai import OpenAI
import backend
import askOpenAI
import FunctionalProgrammingTest

# Initialize the OpenAI client
OpenAI.api_key = 'YOUR_API_KEY'  # Replace with your actual API key
client = OpenAI()

def construct_doc_url(full_class_name, method_name):
    base_url = "https://docs.oracle.com/javase/8/docs/api/"
    class_path = full_class_name.replace('.', '/')
    return f"{base_url}{class_path}.html#{method_name}"

def read_ast_from_file(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def parse_java_doc(full_class_name, method_name):
    base_url = "https://docs.oracle.com/javase/8/docs/api/"
    class_path = full_class_name.replace('.', '/')
    url = f"{base_url}{class_path}.html"

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        # Locate the method signature header that includes the method name
        method_header = soup.find(lambda tag: tag.name in ['h2', 'h3', 'h4', 'h5', 'h6'] and method_name in tag.text)

        if method_header:
            # Navigate to the method summary, which is usually within a 'div' or 'p' tag following the method header.
            summary = []
            for sibling in method_header.next_siblings:
                if sibling.name in ['p', 'div']:
                    # Get clean text from the summary element
                    text = ' '.join(sibling.get_text().split())
                    # Add text to summary if it is not empty
                    if text:
                        summary.append(text)
                elif sibling.name in ['h2', 'h3', 'h4', 'h5', 'h6', 'dl']:
                    # Stop if we reach the next method header or detail list
                    break

            # Return formatted summary text
            return ' '.join(summary).strip() if summary else "Summary not found"

        return "Summary not found"

    except RequestException as e:
        print(f"Failed to fetch the page: {url} with error: {e}")
        return "Error fetching JavaDoc"

def classify_function(method_name, method_summary):

    prompt_message = (
        f"What's the best classification for this function {method_name}, "
        f"the method summary is: {method_summary}. Using the function name "
        "and method summary, determine which of the 12 classifiers fits best In the answer just list the classifier and definition and NOTHING ELSE"
        "Here are the classifiers: "
        "String Manipulation: Functions that handle parsing, formatting, converting, or manipulating textual data. "
        "Numerical Calculations: Functions focused on performing mathematical or statistical computations and operations. "
        "Data Access: Functions that manage interactions with databases or other persistent storage systems, such as data querying and manipulation. "
        "File Handling: Functions that perform file input/output operations, including reading, writing, and file system manipulation. "
        "Networking: Functions involved in managing data transmission over networks, handling network protocols, and managing network sessions. "
        "Utility: General-purpose utility functions providing common functionalities used across various parts of an application. "
        "API Interaction: Functions that manage interactions with external APIs, including sending requests and handling responses. "
        "User Interface: Functions that directly affect the user interface, including event handling and dynamic content generation. "
        "Security: Functions ensuring application security, including tasks related to encryption, decryption, and user authentication. "
        "Logging and Monitoring: Functions dedicated to logging and monitoring application activity to aid in debugging and providing operational insights. "
        "Business Logic: Functions implementing core business rules and logic specific to the application's domain requirements. "
        "Configuration and Setup: Functions involved in the initial setup and configuration of the application or its components."
    )

    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": prompt_message}
        ]
    )

    # Assuming the response format you expect is to get the content of the message
    return response.choices[0].message.content


def ask_openai_about_method(method_name):
    completion = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "user", "content": f" Whats the import for this class: {method_name}, pick the best answer possible in your asnwer just ONlY answer with the import for example if the method_name is createStatement() answer with java.sql.Statement and nothing else. If you cant find a solid answer just say NA"}
        ]
    )
    return completion.choices[0].message.content

def traverse_and_collect_info(node, collected_invocations, collected_imports, variable_types, current_class=None):
    if isinstance(node, dict):
        node_type = node.get('type')

        if node_type == 'Import':
            path = node.get('path')
            class_name = path.split('.')[-1]
            collected_imports[class_name] = path

        elif node_type in ['ClassDeclaration', 'InterfaceDeclaration']:
            current_class = node.get('name')

        elif node_type == 'VariableDeclarator':
            var_name = node.get('name')
            type_info = node.get('type')

            if isinstance(type_info, dict) and type_info.get('type') == 'ReferenceType':
                var_type = type_info.get('name')
                variable_types[var_name] = collected_imports.get(var_type, var_type)

        elif node_type == 'MethodInvocation':
            method_name = node.get('member')
            qualifier_info = node.get('qualifier')

            if isinstance(qualifier_info, dict) and 'member' in qualifier_info:
                qualifier_name = qualifier_info.get('member')
                variable_types.get(qualifier_name, qualifier_name)
            elif isinstance(qualifier_info, str):
                variable_types.get(qualifier_info, qualifier_info)

            collected_invocations.setdefault(current_class, []).append(method_name)

        for key, value in node.items():
            if isinstance(value, dict) or isinstance(value, list):
                traverse_and_collect_info(value, collected_invocations, collected_imports, variable_types, current_class)

    elif isinstance(node, list):
        for item in node:
            traverse_and_collect_info(item, collected_invocations, collected_imports, variable_types, current_class)

def main(ast_file_path, urls, descriptions):

    #Clear the DB 
    backend.wipeDB()

    ast = read_ast_from_file(ast_file_path)

    method_invocations = {}
    collected_imports = {}
    variable_types = {}
    traverse_and_collect_info(ast, method_invocations, collected_imports, variable_types)

    i = 0

    keys_list = list(descriptions.keys())
    print("Keys:", keys_list)

    # Create a list of values
    values_list = list(descriptions.values())
    print("Values:", values_list)

    for class_name, methods in method_invocations.items():
        for method_name in methods:
            full_class_name = ask_openai_about_method(method_name)
            if full_class_name != "NA":
                java_doc_url = construct_doc_url(full_class_name, method_name)
                method_summary = parse_java_doc(full_class_name, method_name)
                method_classification = classify_function(method_name , method_summary)
                print(f"Method: {method_name}()")
                print(f"Class/Interface: {full_class_name}")
                print(f"JavaDoc URL: {java_doc_url}")
                print(f"Summary: {method_summary}\n")
                print(f"Method Classification: {method_classification}\n")

                #Insert into Postgre
                ai_response, sim_score = askOpenAI.main(method_name, full_class_name)
                print("Postgre \n")
                backend.insert_into_function_table(method_name,full_class_name)
                backend.insert_into_API_function_specific_table(method_name, full_class_name, method_summary, urls[i], keys_list[i], values_list[i], ai_response, sim_score, method_classification, "No Domain")
                i = i + 1
                print(i)
                print("----------------------------------\n")

            else:
                print(f"Method: {method_name}() - Class or interface not found\n")


if __name__ == '__main__':
    main()
