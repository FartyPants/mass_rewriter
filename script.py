import gradio as gr
import modules.shared as shared
from modules.extensions import apply_extensions
from modules.text_generation import encode, get_max_prompt_length
from modules.text_generation import generate_reply
from modules.text_generation import generate_reply_wrapper
from modules.text_generation import stop_everything_event
from modules.ui import list_interface_input_elements
from modules.ui import gather_interface_values
from modules.html_generator import generate_basic_html
from modules.ui import create_refresh_button
from pathlib import Path
import re
import json
import time
from collections import Counter
import random
import shutil

from modules import chat

right_symbol = '\U000027A1'
left_symbol = '\U00002B05'
refresh_symbol = '\U0001f504'  # 🔄

RED = "\033[91m"
YELLOW = "\033[93m"
GREEN = "\033[92m"
RESET = "\033[0m"

female_names = ["Mary", "Jane", "Alice", "Emma", "Olivia", "Sophia", "Isabella", "Mia", "Charlotte", "Amelia", "Harper", "Evelyn", "Abigail", "Emily", "Elizabeth", "Sofia", "Ella", "Avery", "Madison", "Scarlett", "Grace", "Chloe", "Victoria", "Hannah", "Natalie", "Zoe", "Layla", "Aria", "Lillian", "Addison", "Eleanor", "Nora", "Hazel", "Riley", "Aubrey", "Zoe", "Penelope", "Aurora", "Aaliyah", "Savannah", "Kennedy", "Nova", "Stella", "Paisley", "Taylor", "Alexa",'Fiona', "Lucy", "Ivy", "Abby", "Poppy", "Eva", "Molly", "Lilly", "Callie", "Zara"]
male_names = ["John", "Michael", "William", "James", "David", "Joseph", "Daniel", "Richard", "Robert", "Charles", "Thomas", "Edward", "George", "Donald", "Mark", "Steven", "Brian", "Jeffrey", "Paul", "Kenneth", "Ronald", "Anthony", "Christopher", "Kevin", "Scott", "Timothy", "Stephen", "Dennis", "Larry", "Gary", "Gregory", "Frank", "Jerry", "Matthew", "Peter", "Raymond", "George", "Harry", "Walter", "Roger", "Eric", "Philip", "Lawrence", "Dale", "Carl", "Bruce", "Alan", "Ronnie","Noah", "Jacob", "Logan", "Asher", "Samuel", "Benjamin", "Henry", "Theodore", "Maximus", "Arthur"]
last_names = ["Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor", "Anderson", "Thomas", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson", "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King", "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "White", "Carter", "Turner", "Nelson", "Parker", "Edwards", "Collins", "Stewart", "Sanchez", "Morris", "Rogers", "Reed"]
british_towns = ["London", "Birmingham", "Manchester", "Liverpool", "Glasgow", "Leeds", "Newcastle", "Sheffield", "Bristol", "Cardiff", "Edinburgh", "Belfast", "Aberdeen", "Brighton", "Cambridge", "Oxford", "York", "Nottingham", "Leicester", "Southampton", "Portsmouth", "Bath", "Canterbury", "Durham", "Exeter", "Inverness", "Stirling", "Swansea", "Plymouth", "Dundee",
                 "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose", "Austin", "Jacksonville", "San Francisco", "Indianapolis", "Fort Worth", "Seattle", "Denver", "El Paso", "Washington", "Boston", "Nashville", "Baltimore", "Oklahoma City", "Portland", "Las Vegas", "Louisville", "Milwaukee", "Albuquerque", "Tucson",]
specific_church_names = [
    "St. Patrick",
    "St. Mary",
    "St. John",
    "St. Michael",
    "St. Peter",
    "St. Paul",
    "St. George",
    "St. Andrew",
    "St. James",
    "St. Thomas",
    "St. Stephen",
    "St. Nicholas",
    "St. Joseph",
    "St. Anthony",
    "St. Theresa",
    "St. Francis",
    "St. Catherine",
    "St. Agnes",
    "St. Matthew",
    "St. Luke",
    "St. Mark",
    "St. Mary Magdalene",
    "St. Augustine",
    "St. Vincent",
    "St. Francis Xavier",
    "St. Dominic",
    "St. Elizabeth",
    "St. Cecilia",
    "St. Lawrence",
    "St. Benedict",
]


paragraphs = []
paragraphs_output = []

current_prev = 0
file_namePARAMJSON = "massrewriter.json"
jsonfile = []
plaintextfile = ''
file_nameJSON = "output.json"
file_nameTXT = "output.txt"

JSON_TYPE = ['Instruction -> LLM -> Instruction, Output -> Output','Instruction -> Instruction, Output -> LLM -> Output']
params = {
        "display_name": "Mass Rewritter",
        "is_tab": True,
        "done":False,
        "pUSER": 'USER:',
        "pBOT": 'ASSISTANT:',
        "instruct":'Rewrite the following text: ',
        "final-save":True,
        "replace_eol": False,
        "limit_short":20,
        "include_short":False,
        "include_long":False,
        "paragraph_split":'\\n\\n\\n',
        "plaintext_delim":'\\n\\n',
        "out_type":'JSON',
        "out_reverse": True,
        "generate": True,
        "skip_short": False,
        "block_size": 850,
        "replace_eol2": True,
        "repeat_times": 1,
        "remove_eol": False,
        "selected_template": 'default',
        "double_gen": False,
        'alt_template': '',
        'max_new_tokens': 480,
        'replace_names': False,
        'names_she': '',
        'names_he': '',
        'names_last': '',
        'names_places1': '',
        'names_places2': '',
        'JSONType': 0,
        'output_filename': 'output',
        'chapter_start': 'CHAPTER',
        'add_errors': False,
        'error_level':3,
}
default_req_params = {
    'max_new_tokens': 200,
    'temperature': 0.7,
    'top_p': 0.1,
    'top_k': 40,
    'repetition_penalty': 1.18,
    'encoder_repetition_penalty': 1.0,
    'suffix': None,
    'stream': False,
    'echo': False,
    'seed': -1,
    'truncation_length': 2048,
    'add_bos_token': True,
    'do_sample': True,
    'typical_p': 1.0,
    'epsilon_cutoff': 0,  # In units of 1e-4
    'eta_cutoff': 0,  # In units of 1e-4
    'tfs': 1.0,
    'top_a': 0.0,
    'min_length': 0,
    'no_repeat_ngram_size': 0,
    'num_beams': 1,
    'penalty_alpha': 0.0,
    'length_penalty': 1,
    'early_stopping': False,
    'mirostat_mode': 0,
    'mirostat_tau': 5,
    'mirostat_eta': 0.1,
    'ban_eos_token': False,
    'skip_special_tokens': True,
    'custom_stopping_strings': '',
}

'''
class ToolButton(gr.Button, gr.components.FormComponent):
    """Small button with single emoji as text, fits inside gradio forms"""

    def __init__(self, **kwargs):
        super().__init__(variant="tool", **kwargs)

    def get_block_name(self):
        return "button"


def create_refresh_button(refresh_component, refresh_method, refreshed_args, elem_class):
    def refresh():
        refresh_method()
        args = refreshed_args() if callable(refreshed_args) else refreshed_args

        for k, v in args.items():
            setattr(refresh_component, k, v)

        return gr.update(**(args or {}))

    refresh_button = ToolButton(value=refresh_symbol, elem_classes=elem_class)
    refresh_button.click(
        fn=refresh,
        inputs=[],
        outputs=[refresh_component]
    )
    return refresh_button
'''
def get_file_path(folder, filename):
    basepath = "extensions/mass_rewritter/"+folder
    #print(f"Basepath: {basepath} and {filename}")
    paths = (x for x in Path(basepath).iterdir() if x.suffix in ('.txt'))
    for path in paths:
        if path.stem.lower() == filename.lower():
            return str(path)
    return ""

def get_file_pathJSON(folder, filename):
    basepath = "extensions/mass_rewritter/"+folder
    #print(f"Basepath: {basepath} and {filename}")
    paths = (x for x in Path(basepath).iterdir() if x.suffix in ('.json'))
    for path in paths:
        if path.stem.lower() == filename.lower():
            return str(path)
    return ""

def get_file_path_noCheck(folder, filename):
    basepath = "extensions/mass_rewritter/"+folder+"/"+filename
   
    return basepath

def read_file_to_string(file_path):
    data = ''
    try:
        with open(file_path, 'r') as file:
            data = file.read()
    except FileNotFoundError:
        data = ''

    return data

# Function to replace names from names_she with random names from female_names
def replace_names_with_replace(text, female_names, names_she):

    if len(names_she)>0:
        for name in names_she:
            if name!='':
                replacement = random.choice(female_names)
                text = text.replace(name, replacement)
    
    return text

def string_to_name_list(input_string):
    # Split the input string by commas and remove leading/trailing spaces
    name_list = [name.strip() for name in input_string.split(',')]
    return name_list


def add_random_grammatical_errors(text, num_iterations=3):
    # Split the text into sentences
    print(f"Adding Errors level {num_iterations}")

    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)

    # List of possible grammatical errors
    errors = [
        lambda x: x,  # No error
        lambda x: x.replace('.', ','),  # Remove comma
        lambda x: x.replace(',', ''),  # Remove comma
        lambda x: x.replace(',', ''),  # Remove comma
        lambda x: x.replace(',', ''),  # Remove comma
        lambda x: x.replace("'", ''),  # Remove single quotes
        lambda x: x.replace(" its", " it's"),  # Replace "its" with "it's"
        lambda x: x.replace(" it's", " its"),  # Replace "its" with "it's"
        lambda x: x.replace("'s", "s"),  # Replace "its" with "it's"
        lambda x: x.replace(" the ", " "),  
        lambda x: x.replace(" a ", " "),
        lambda x: x.replace(" an ", " "),
        lambda x: x.replace(" the ", " a "),
        lambda x: x.replace(" a ", " the "),  
        lambda x: x.replace("The ", "A "),    
        lambda x: x.replace(" you're ", " you are "),  
        lambda x: x.replace(" I'm ", " I am "),  
        #lambda x: re.sub(r'\b(a|an|the)\b', '', x),  # Remove articles (a, an, the)
        #lambda x: re.sub(r'\b(a|an|the)\b', lambda m: 'an' if m.group(1) == 'a' else 'a', x),  # Replace articles with wrong ones
        #lambda x: re.sub(r'\b(a|an|the)\b', lambda m: 'the' if m.group(1) == 'a' else 'a', x),

        lambda x: x.replace(' is', ' are'),  # Replace "is" with "are"
        lambda x: x.replace('I\'m', 'Im'),  
        lambda x: x.replace('hers', 'her\'s'),
        lambda x: x.replace('ours', 'our\'s'), 
        #lambda x: x.replace(' you', ' yu'),  # Replace "you" with "u"
        lambda x: x.replace('there', 'their'),  # Replace "there" with "their"
        lambda x: x.replace('yours', 'your\'s'),  # Replace "your" with "you are"
        lambda x: x.replace(' to', ' too'),  # Replace "to" with "too"
        lambda x: x.replace(' it', ' he'),  # Replace "it" with "he"
        lambda x: x.replace(' your', ' you\'re'),  # Replace "your" with "you're"
        # lambda x: re.sub(r'\b(\w+)\b', lambda m: m.group(1) + ',', x, count=1),  # Add "," to a random word

    ]

    # Apply random errors for a specified number of iterations
    for _ in range(num_iterations):
        for i, sentence in enumerate(sentences):
            random_error = random.choice(errors)
            sentences[i] = random_error(sentence)

    # Join the sentences back into a modified text
    modified_text = ' '.join(sentences)
    return modified_text


# Function to load JSON data safely
# JSON has both paragraphs and paragraphs_output
def load_json_data(file, gr_JSONType):
    global params
    global JSON_TYPE

    global paragraphs
    global paragraphs_output

    jsonNum = 0

    if gr_JSONType in JSON_TYPE:
        jsonNum = JSON_TYPE.index(gr_JSONType)

    params['JSONType'] = jsonNum

    left_key = 'instruction'
    right_key = 'output'
    paragraphs = []
    paragraphs_output = []

    path = get_file_pathJSON('inputs',file)
    try:
        
        with open(path, 'r') as json_file:
            
            json_in_data = json.load(json_file)
            if json_in_data:
                #first_item_keys = list(json_in_data[0].keys())
            # Extract 'input' and 'output' values into the arrays
                if jsonNum ==0:
                    for item in json_in_data:
                        paragraphs.append(item[left_key])
                        paragraphs_output.append(item[right_key])


                    return f"JSON data Items: {len(paragraphs)}, the `{left_key}` will be used as input `(Text [in]`, and the `{right_key}` will be used as `original stand-in Text [in]` written in output JSON"
                elif jsonNum == 1:
                    for item in json_in_data:
                        paragraphs.append(item[right_key])
                        paragraphs_output.append(item[left_key])

                    return f"JSON data Items: {len(paragraphs)}, the `{right_key}` will be used as input `(Text [in]`, and the `{left_key}` will be used as `original stand-in Text [in]` written in input JSON"                    

                #for key in first_item_keys:
                #    print(key)
            else:

                print("JSON data is empty or couldn't be loaded.")
                return "JSON data is empty or couldn't be loaded."

    except FileNotFoundError:
        
        print("Error: JSON file not found.")
        return "JSON file not found."
    except json.JSONDecodeError:
        
        print("Error: JSON file is not valid JSON.")
        return "JSON file is not valid JSON."


def save_template(DYNAMEMORY, para_template_exampletext, DYNAMEMORY_filename):

    templ_fname = DYNAMEMORY_filename

    if DYNAMEMORY_filename=='None' or DYNAMEMORY_filename=='' or DYNAMEMORY_filename == "<write file name here>" or DYNAMEMORY_filename == '<Saved>':
        print("File name can't be None")
        templ_fname = "<write file name here>"
    else:    
        basepath = "extensions/mass_rewritter/Template/"+DYNAMEMORY_filename+".txt"
        save_string_to_file(basepath,DYNAMEMORY)
        templ_fname = '<Saved>'
        if para_template_exampletext.strip() != '':
            basepath2 = "extensions/mass_rewritter/Template/"+DYNAMEMORY_filename+"_examples.txt"
            save_string_to_file(basepath2, para_template_exampletext)

    return templ_fname

def load_Paraphrase_template(file):
    global params
    template = 'Paraphrase the following\n<|context|>'
    template2 = ''

    path = get_file_path('Template',file)
    path2 = get_file_path('Template',f"{file}_examples")
    
    if path:
        print(f"Loading Paraphrase Template: {path}")
        template = read_file_to_string(path)

        params['selected_template'] = file

    if path2:
        print(f"Loading Examples Template: {path2}")
        template2 = read_file_to_string(path2)
 
    return template,template2

def convert_to_string_with_units(length):
    if length < 1024:
        return f"{length:.2f} B"
    elif length < 1024 * 1024:
        return f"{length / 1024:.2f} KB"
    else:
        return f"{length / (1024 * 1024):.2f} MB"
        
def extract_names(inputfile_text_drop):
    path = get_file_path('inputs',inputfile_text_drop)
    try:
        with open(path, 'r', encoding='utf-8') as file:
            input_text = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{path}' does not exist.")
    
    input_text = input_text.replace('\r\n', '\n')
    # Define a regular expression pattern to match names
    name_pattern = r'\b[A-Z][a-z]{2,}\b'

    # Find all the matching names in the input_text
    names = re.findall(name_pattern, input_text)

    print(f"Regex: {len(names)}")
    # Count the occurrences of each name
    name_counts = Counter(names)
   
    print(f"Counter: {len(name_counts)}")

    # Sort the names by their occurrences in descending order
    sorted_names_by_occurrences = sorted(name_counts, key=lambda name: (-name_counts[name], name))

    # Filter out names that have more than one occurrence
    filtered_names = [name for name in sorted_names_by_occurrences if name_counts[name] > 1]

    print(f"Names More than once: {len(filtered_names)}")


    capital_words = [
    "January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday", "Christmas", "Mrs", "Miss",
    "Mister", "Doctor", "Professor", "President", "Senator", "Captain", "General", "Governor", "Mr", "British", "Britain"
    "Doctorate", "Bachelor", "Master", "Reverend", "Father", "Judge", "Justice", "Bishop", "Chancellor", "Dean", "Vicar", "Pope", "Principal", "Sir", "Madam", "Archbishop", "Cardinal", "Pastor", "Rector",
    "Argentina", "Brazil", "Canada", "China", "Egypt", "France", "Germany", "India", "Italy", "Japan", "Kenya", "Mexico", "Nigeria", "Peru", "Russia", "Spain", "Sweden", "United", "States", "Venezuela", "Australia", "New", "Zealand", "South", "Africa", "Southeast", "Asia", "Europe", "North", "Northwest", "Southwest","Belgium",
    "Internet","Congress","Americans","American","Coke","Catholic","Airways","Baptist","German","England","Oriental","Belgian","Scotland","Scotish","Pacific","Atlantic","Hollywood","Pepsi","Turkish","Renaissance",
    "Starbucks","Volkswagen","Tylenol","Greece","Whoa","Pakistan","Honda","America","Pennsylvania","Jamaican","Jamaica","Victorian","Teacher","Testament","Wow","Whenever","However","Fridays","Beatles","Shakespeare","Jesus",
    "Democrat","Capitalism","Chinese","University","Switzerland","Austrian","Court","International","European","Arizona","Journal","Madame","Ooooh","Indian","African","Australian",
    "Organization", "Institution", "Committee", "Association", "Department", "Division", "Corporation", "Institute", "Society", "Agency",
    "Bureau", "Establishment", "Firm", "Group", "Partnership", "Committee", "Division", "Office","Academy","Northern", "Olympic",
    "University", "Hospital", "School", "College", "Factory", "Restaurant", "Hotel", "Library", "Museum", "Park","Monopoly",
    "Theater", "Stadium", "Airport", "Station", "Port", "Bridge", "Highway", "Avenue", "Boulevard", "Street", "Market",
    "Mall", "Store", "Shop", "Supermarket", "Pharmacy", "Clinic", "Laboratory","French","Brussel","Kingdom","Socialist","Disney","Japanese","English","Grandma","Grandpa","Madonna","Florida","California","Beethoven","Miami",
    ]   

    filtered_names = [name for name in filtered_names if name not in capital_words]

    # Remove names that also exist in lowercase in the text
    final_names = [name for name in filtered_names if name.lower() not in input_text]
 
    print(f"After excluding common words: {len(final_names)}")

    formatted_names = ', '.join(final_names)

    return formatted_names


def convert_blocks(inputfile_text_drop,gr_block_size):
    path = get_file_path('inputs',inputfile_text_drop)

    inputfile_text_drop = inputfile_text_drop.replace('.txt','')
    outfile = inputfile_text_drop + f'.blocks{int(gr_block_size)}.txt'

    
    pathOUT = get_file_path_noCheck('inputs',outfile)
    
    print(f"inputfile_text_drop {inputfile_text_drop}, outfile {outfile}, pathOUT {pathOUT}")

    try:
        with open(path, 'r', encoding='utf-8') as file:
            input_text = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{path}' does not exist.")
    
    split_temp = params["paragraph_split"].replace('\\n', '\n')
    chapter_start = params['chapter_start']

    params.update({"block_size": gr_block_size})
    # Replace '\r\n' with '\n'
    input_text = input_text.replace('\r\n', '\n')


    input_text = input_text.replace('\n\n\n', '\n<break>\n')
    # Split the text by '\n' into an array
    text_array = input_text.split('\n')

    # Initialize an empty list to store the final paragraphs
    final_paragraphs = []

    # Initialize a variable to keep track of the current paragraph
    current_paragraph = ""

    # Maximum character limit for each paragraph
    max_paragraph_length = gr_block_size

    # Loop through each paragraph in the text array
    for paragraph in text_array:

        paragraph = paragraph.replace('\n', '')
        # If adding the current paragraph to the current content
        # would exceed the character limit, add it to the final list
        if paragraph != "":

            if chapter_start!='' and paragraph.startswith(chapter_start):
                paragraph = "\n"

            if paragraph == '<break>' :
                current_paragraph =  current_paragraph.strip()    

                if current_paragraph !="":
                    final_paragraphs.append(current_paragraph.strip())
                
                current_paragraph = ""
                paragraph = ""
            
            if len(current_paragraph) + len(paragraph) + 1 > max_paragraph_length:

                current_paragraph =  current_paragraph.strip()    
                if current_paragraph !="":
                    final_paragraphs.append(current_paragraph.strip())
                
                current_paragraph = ""
        
            current_paragraph += paragraph+ "\n"

    # Add the last remaining paragraph to the final list
    current_paragraph =  current_paragraph.strip()         
    if current_paragraph !="":
        final_paragraphs.append(current_paragraph.strip())

    # Join the final paragraphs with '\n' to create the output text
    output_text = split_temp.join(final_paragraphs)

    output_text = output_text.replace('\n', '\r\n')

    outmsg = "Something wrong"
    # Write the output string to another text file
    with open(pathOUT, 'w', encoding='utf-8') as file:
        file.write(output_text)
        outmsg = f"File was saved in {pathOUT}"
    
    
    
    return outmsg    
    
    

# TEXT file has only paragraphs and paragraphs_output = []
def load_file(filep):
    global paragraphs
    global paragraphs_output
    global params
    
    paragraphs = []
    paragraphs_output = []
    path = get_file_path('inputs',filep)

    try:
        with open(path, 'r', encoding='utf-8') as file:
            file_content = file.read()

    except FileNotFoundError:
        raise FileNotFoundError(f"The file '{path}' does not exist.")

    #length = len(file_content)
    #lengthuniy= convert_to_string_with_units(length)
    #print((f"File Loaded: {lengthuniy}"))
    file_content = file_content.replace('\r\n','\n')

    
    split_temp = params["paragraph_split"].replace('\\n', '\n')
    
    #print(f"Split: {split_temp} end")

    paragraphs = file_content.split(split_temp)
    paragraphs = [paragraph.rstrip('\n').lstrip('\n') for paragraph in paragraphs]

    paragraphs = list(filter(lambda x: x.strip(), paragraphs))
    num_paragraphs = len(paragraphs)
    print((f"paragraphs: {num_paragraphs}"))
    infotext = f"Loaded Paragraphs: {num_paragraphs}"

    modelname = f"_{shared.model_name}"
    modelname = modelname.replace('-','_')
    modelname = modelname.replace('_HF','')
    modelname = modelname.replace('_GPTQ','')
    modelname = modelname.replace('_4b','')
    modelname = modelname.replace('_128g','')

    params['output_filename'] = filep+ modelname


    return infotext, params['output_filename']

def format_time(seconds: float):
    if seconds < 120:
        return f"`{seconds:.0f}` seconds"

    minutes = seconds / 60
    if minutes < 120:
        return f"`{minutes:.0f}` minutes"

    hours = minutes / 60
    return f"`{hours:.0f}` hours"

def format_time2(seconds: float):
    if seconds < 120:
        return f"{seconds:.0f} seconds"

    minutes = seconds / 60
    if minutes < 120:
        return f"{minutes:.0f} minutes"

    hours = minutes / 60
    return f"{hours:.0f} hours"

def mainloop(para_template_text,para_template_text2, para_template_exampletext, state):

    global params
    global plaintextfile
    global jsonfile
    global paragraphs_output
    global paragraphs
    global file_nameJSON
    global file_nameTXT


    file_nameJSON =  f"{params['output_filename']}.json"
    file_nameTXT = f"{params['output_filename']}.txt"

    params['alt_template'] = para_template_text2
 
    html = ''

    jsonfile.clear()
    plaintextfile = ''
    params['final-save']=False

    summary_state = state.copy()

    stopping_strings = chat.get_stopping_strings(state)
    print(f"Stopping strings: {stopping_strings}")
    # state['custom_stopping_strings']
    
    summary_state['max_new_tokens'] = int(params['max_new_tokens'])

    #for key, value in default_req_params.items():
    #    summary_state[key] = value  # Update the value in 'summary_state' with the value from 'default_req_params

    short_num = int(params['limit_short'])
    print(f"max_new_tokens override: {summary_state['max_new_tokens']}")
    #print(f"temperature: {summary_state['temperature']}")
    #print(f"top_p: {summary_state['top_p']}")
    #print(f"top_k: {summary_state['top_k']}")
    print(f"Min char: {short_num}")
    print(f"Include Short: {params['include_short']}")
    print(f"Include Long: {params['include_long']}")
    print(f"Skip short: {params['skip_short']}")
    print(f"Replace EOL: {params['replace_eol']}")
    print(f"Replace EOL + EOL: {params['replace_eol2']}") 
    
    print(f"Remove EOL before LLM: {params['remove_eol']}") 
    print(f"Output type: {params['out_type']}")

    print(f"Repeat X times: {params['repeat_times']}")
    print(f"Replace Names  {params['replace_names']}")


    if params['out_type']=='JSON': 
        source_file = Path(file_nameJSON)
        if source_file.is_file():
            backup_file = "output_backup.json"
            shutil.copy2(source_file, backup_file)
    else:       
        source_file = Path(file_nameTXT)
        if source_file.is_file():
            backup_file = "output_backup.txt"
            shutil.copy2(source_file, backup_file)
 
    names_she = []
    names_he = []
    names_last = []
    names_places1 = []
    names_places2 = []


    plain_txt_delim = params['plaintext_delim'].replace('\\n', '\n')    
    
    params["done"] = False

    yield f"Preparing...","","Preparing...", "<h1>Preparing...</h1>"
    
    user = params['pUSER']    
    bot = params['pBOT']
   
    baseprompt = str(para_template_text)

    baseprompt2 = str(para_template_text2)

    pretext_examples = str(para_template_exampletext)

    if baseprompt2.strip() == "":
        baseprompt2 = baseprompt
    
    baseprompt = baseprompt.replace('<|user|>', user)
    baseprompt = baseprompt.replace('<|bot|>', bot)

    baseprompt2 = baseprompt2.replace('<|user|>', user)
    baseprompt2 = baseprompt2.replace('<|bot|>', bot) 

    if pretext_examples.strip() != "":
        pretext_examples = pretext_examples.replace('<|user|>', user)
        pretext_examples = pretext_examples.replace('<|bot|>', bot) 
        baseprompt = pretext_examples + "\n" + baseprompt



    jsonInstr = params['instruct']
    jsoninputs = jsonInstr.split('\n')
    jsoninputs = list(filter(lambda x: x.strip(), jsoninputs))
    num_lines = len(jsoninputs)
    jsonindex = 0

    start_time = time.perf_counter()

    reverse = params['out_reverse']
    i = 0
    k = 0

    num = int(params['repeat_times'])
    if num<1:
        num = 1

    removeEOL_beforeLLM = params['remove_eol']

    jason_inp = False

    if len(paragraphs_output)>0:

        if params['JSONType'] == 0: 
            if reverse:
                print (f"{RED}JSON cross case{RESET} - (loaded JSON) 'instructions' -> Text [in] -> {RED}LLM Text [out] -> JSON 'instructions'{RESET} and {YELLOW}(loaded JSON) 'oputput' -> JSON 'output'{RESET}")
            else:
                print (f"{RED}JSON cross case{RESET} - (loaded JSON) 'instructions' -> Text [in] -> {RED}LLM Text [out] -> JSON 'output'{RESET} and {YELLOW}(loaded JSON) 'oputput' -> JSON 'instructions'{RESET}")
        if params['JSONType'] == 1: 
            if reverse:
                print (f"{RED}JSON cross case{RESET} - (loaded JSON) 'output' -> Text [in] -> {RED}LLM Text [out] -> JSON 'instructions'{RESET} and {YELLOW}(loaded JSON) 'oputput' -> JSON 'output'{RESET}")
            else:
                print (f"{RED}JSON cross case{RESET} - (loaded JSON) 'output' -> Text [in] -> {RED}LLM Text [out] -> JSON 'output'{RESET} and {YELLOW}(loaded JSON) 'input' -> JSON 'input'{RESET}")

        jason_inp = True
    else:
        if reverse:
            print (f"{RED}[LLM Output to JSON Instructions]{RESET} Text [in] -> {RED}LLM Text [out] -> JSON 'instructions'{RESET} and {YELLOW}Text [in] -> JSON 'output'{RESET}")
        else:
            print (f"Text [in] -> {RED}LLM Text [out] -> JSON 'output'{RESET} and {YELLOW}Text [in] -> JSON 'instructions'{RESET}")

    if params['double_gen']:
        print(f"{RED}[double generation]{RESET} The Text[in] will be processed twice in LLM: {RED}Text[in] -> LLM -> LLM -> Text[out]{RESET}")


    b_replaceNames = params['replace_names']
    if b_replaceNames:
        names_she = string_to_name_list(params['names_she'])
        names_he = string_to_name_list(params['names_he'])
        names_last = string_to_name_list(params['names_last'])
        names_places1 = string_to_name_list(params['names_places1'])
        names_places2 = string_to_name_list(params['names_places2']) 
        if jason_inp:
            print(f"{RED}Replace Names is incompatible with JSON Cross {RESET}")
            b_replaceNames = False
            print(f"Replace Names  {b_replaceNames}")


    for epch in range(num):   

        for index, paragraph in enumerate(paragraphs):
        #for paragraph in paragraphs:
            repolacement_out = paragraph

            if jason_inp and index<len(paragraphs_output):
                repolacement_out = paragraphs_output[index]

            jsoninputLN = ''
            if num_lines>0:
                jsoninputLN = jsoninputs[jsonindex]
                jsonindex += 1
                if jsonindex >= num_lines:
                    jsonindex = 0

            if params["done"]==True:
                yield f"Interrupted","Interrupted","Interrupted","<h1>Interrupted</h1>"
                break

            i = i+1
            paragraph = paragraph.rstrip("\n")
            paragraph = paragraph.lstrip("\n")

            if params['replace_eol2']==True:
                paragraph = paragraph.replace('\n\n','\n')
                paragraph = paragraph.replace('\n \n','\n')

            if params['replace_eol']==True:
                paragraph = paragraph.replace('\n',' ')

            paragraph = paragraph.replace('  ',' ')

            if b_replaceNames:
                paragraph = replace_names_with_replace(paragraph,female_names,names_she)
                paragraph = replace_names_with_replace(paragraph,male_names,names_he)
                paragraph = replace_names_with_replace(paragraph,last_names,names_last)
                paragraph = replace_names_with_replace(paragraph,british_towns,names_places1)
                paragraph = replace_names_with_replace(paragraph,specific_church_names,names_places2)


            #hasQuoteIn = False
            #if '"' in paragraph:
            #    hasQuoteIn  = True

            #if paragraph.lower().startswith("chapter"):
            #    continue

            infotext = "Starting"
            html = "<h1>Starting</h1>"

            if paragraph:
                

                time_elapsed = time.perf_counter() - start_time
                if time_elapsed <= 0:
                    timer_info = ""
                    total_time_estimate = 999
                else:
                    its = i / time_elapsed
                    if its > 1:
                        timer_info = f"`{its:.2f}` it/s"
                    else:
                        timer_info = f"`{1.0/its:.2f}` s/it"

                    total_time_estimate = (1.0 / its) * (len(paragraphs)*num)


                print(f"{i}/{len(paragraphs)}")

                infotext = f"Epoch: {(epch+1)}/{num} : Progress: {i}/{len(paragraphs)*num}  {timer_info}, {format_time(time_elapsed)} / {format_time(total_time_estimate)} ... {format_time(total_time_estimate - time_elapsed)} remaining"

                #progress_text = f"<h1>Progress: {i}/{len(paragraphs)*num}</h1>"
                #time_info_text = f"<p>{format_time(time_elapsed)} / {format_time(total_time_estimate)}</p>"

                progress_text = f"<p></p><h1 style='text-align: center;'>{i}/{len(paragraphs)*num}</h1>"
                time_info_text = f"<p style='text-align: center;'>{format_time2(time_elapsed)} / {format_time2(total_time_estimate)}</p>"
                time_info_text2 = f"<p style='text-align: center;'>{format_time2(total_time_estimate - time_elapsed)} remaining</p>"

                html = f"<div style='text-align: center;'>{progress_text}{time_info_text}{time_info_text2}</div>"

                #html = progress_text + time_info_text
                #html = f"Progress: {i}/{len(paragraphs)*num} {format_time(time_elapsed)} / {format_time(total_time_estimate)}"

                if removeEOL_beforeLLM:
                    # just internally replace \n with space
                    prompt = baseprompt.replace('<|context|>', paragraph.replace('\n',' '))   
                else:
                    prompt = baseprompt.replace('<|context|>', paragraph)   

                
                #if params['replace_eol']==False:
                #   paragraph = paragraph.replace('\n','\\n')

                paragrap_length = len(paragraph)
                if paragrap_length>short_num:
                    reply = ''

                    if params['generate']:
                        generator = generate_reply(prompt, summary_state, stopping_strings=stopping_strings, is_chat=False)

                        for a in generator:
                            if isinstance(a, str):
                                reply = a
                            else:
                                reply = a[0]


                        indexUser = reply.find(user)

                        if indexUser != -1:
                            # Extract the part of the string before "### Instruction"
                            reply = reply[:indexUser]

                        indexBot = reply.find(bot)

                        if indexBot != -1:
                            # Extract the part of the string before "### Response"
                            reply = reply[:indexBot]


                        if params['double_gen']:
                            # do it again
                            reply = reply.strip()
                            paragraph_double = reply
                            if removeEOL_beforeLLM:
                                prompt_double = baseprompt2.replace('<|context|>', paragraph_double.replace('\n',' '))   
                            else:
                                prompt_double = baseprompt2.replace('<|context|>', paragraph_double)

                            generator = generate_reply(prompt_double, summary_state, stopping_strings=stopping_strings, is_chat=False)

                            for a in generator:
                                if isinstance(a, str):
                                    reply = a
                                else:
                                    reply = a[0]
        
                            indexBot = reply.find(bot)

                            if indexBot != -1:
                                # Extract the part of the string before "### Response"
                                reply = reply[:indexBot]

                        reply = reply.strip()

                        if params['add_errors'] == True:
                            reply = add_random_grammatical_errors(reply,params['error_level'])

                        reply_length = len(reply)
                    else:
                        reply_length = paragrap_length

                    
                    if reply_length>0:
                        #if ('"' not in reply) and (hasQuoteIn):
                        #    paragraph = paragraph.replace('"','')
                        paragraph_orig  =  paragraph
                        if jason_inp and repolacement_out!='':
                            paragraph_orig  =  repolacement_out
                     
                        if reply_length > paragrap_length*3:
                            print("Too weird reply")
                            if params['include_long']:
                                # copy unchanged
                                reply = paragraph
                                if reverse:
                                    inout = jsoninputLN + reply
                                    jsonfile.append({
                                        "instruction": inout,
                                        "output": paragraph_orig
                                    })
                                else:
                                    inout = jsoninputLN + paragraph_orig
                                    jsonfile.append({
                                        "instruction": inout,
                                        "output": reply
                                    })
    
                                
                                plaintextfile = plaintextfile + reply + plain_txt_delim
                                print(f"LONG -> Copy ")

                        else:
                            skip = False
                            if params['skip_short'] and (reply_length < paragrap_length/3):
                                skip = True

                            if skip==False:        
                                if reverse:
                                    inout = jsoninputLN + reply
                                    
                                    jsonfile.append({
                                        "instruction": inout,
                                        "output": paragraph_orig
                                    })
                                else:
                                    inout = jsoninputLN + paragraph_orig
                                    
                                    jsonfile.append({
                                        "instruction": inout,
                                        "output": reply
                                    })
                            else:
                                print("Skipping as too short answer")

                            plaintextfile = plaintextfile + reply + plain_txt_delim
                            print(f"\033[38;5;8m{reply}\033[0;37;0m\n--------------------")

                        yield paragraph,reply,infotext,html
                else:
                    if params['include_short']:
                        
                        paragraph_orig  =  paragraph
                        if jason_inp and repolacement_out!='':
                            paragraph_orig  =  repolacement_out

                        inout = jsoninputLN + paragraph
                        jsonfile.append({
                            "instruction": inout,
                            "output": paragraph_orig
                        })

                        plaintextfile = plaintextfile + paragraph + plain_txt_delim
                        print(f"SHORT -> Copy")
                
                if params['generate']:           
                    time.sleep(0.1)

                k = k+1
                if k % 10 == 0:
                    if params['out_type']=='JSON': 
                        with open(file_nameJSON, 'w') as file:
                            json.dump(jsonfile, file, indent=4)
                    else:
                        with open(file_nameTXT, "w", encoding="utf-8") as file:
                            file.write(plaintextfile)


                    print("\033[1;32;1mSaving...\033[0;37;0m")
    
    if params['out_type']=='JSON': 
        with open(file_nameJSON, 'w') as file:
            json.dump(jsonfile, file, indent=4)
    else:
        with open(file_nameTXT, "w", encoding="utf-8") as file:
            file.write(plaintextfile)
        
        print("\033[1;32;1mLast Saving in loop\033[0;37;0m")
        params['final-save']=True

    print("FINISHED")
    yield f'Finished',f'Finished', "Finished", "Finished"

def final_save():
   
    file_nameJSON =  f"{params['output_filename']}.json"
    file_nameTXT = f"{params['output_filename']}.txt"

    if len(jsonfile)>0 and params['final-save']==False:
        print("\033[1;32;1mInterrupt Saving...\033[0;37;0m")
        if params['out_type']=='JSON': 
            with open(file_nameJSON, 'w') as file:
                json.dump(jsonfile, file, indent=4)
        else:
            with open(file_nameTXT, "w", encoding="utf-8") as file:
                file.write(plaintextfile)
                     
            params['final-save']=True


    print("Stopped")    
    yield "Interrupted"

def preview_prev():
    global current_prev
    
    if 0 < current_prev < len(paragraphs):
        current_prev = current_prev-1
        item = paragraphs[current_prev]
        return item
    
    return "--BEGIN--"
        
def preview_next():
    global current_prev
    
    if 0 <= current_prev < len(paragraphs)-1:
        current_prev = current_prev+1
        item = paragraphs[current_prev]
        return item
    
    return "--END--"

def save_pickle():
    global params
    try:
        with open(file_namePARAMJSON, 'w') as json_file:
            json.dump(params, json_file,indent=2)
            print(f"Saved: {file_namePARAMJSON}")
    except IOError as e:
        print(f"An error occurred while saving the file: {e}")  
    
def atoi(text):
    return int(text) if text.isdigit() else text.lower()

def natural_keys(text):
    return [atoi(c) for c in re.split(r'(\d+)', text)]
    
def get_available_templates():
    paths = (x for x in Path('extensions/mass_rewritter/Template').iterdir() if x.suffix in ('.txt'))
    return ['None'] + sorted(set((k.stem for k in paths)), key=natural_keys)

def get_available_input():
    paths = (x for x in Path('extensions/mass_rewritter/inputs').iterdir() if x.suffix in ('.txt'))
    return ['None'] + sorted(set((k.stem for k in paths)), key=natural_keys)   

def get_available_input_JSON():
    paths = (x for x in Path('extensions/mass_rewritter/inputs').iterdir() if x.suffix in ('.json'))
    return ['None'] + sorted(set((k.stem for k in paths)), key=natural_keys)   

def save_string_to_file(file_path, string):
    try:
        with open(file_path, 'w') as file:
            file.write(string)
        print("String saved to file successfully.")
    except Exception as e:
        print("Error occurred while saving string to file:", str(e))


def ui():
    global params
    global file_nameJSON
    global file_nameTXT

    try:
        with open(file_namePARAMJSON, 'r') as json_file:
            new_params = json.load(json_file)
            for item in new_params:
                params[item] = new_params[item]
    except FileNotFoundError:
        pass

 
    #input_elements = list_interface_input_elements(chat=False)
    #interface_state = gr.State({k: None for k in input_elements})
    paraphrase_text,example_text = load_Paraphrase_template(params['selected_template'])
     
    params["done"] = False
    with gr.Row():
        with gr.Column():
            with gr.Tab('Text'):
                with gr.Row():
                    #inputfile_text = gr.Textbox(value="path to file", lines=1, label='path to file', interactive=True)
                    inputfile_text_drop  = gr.Dropdown(choices=get_available_input(), label='Input file', value='None', elem_classes=['slim-dropdown'])
                    create_refresh_button(inputfile_text_drop, lambda: None, lambda: {'choices': get_available_input()}, 'refresh-button')
                    with gr.Tab('Load Blockified text'):
                        with gr.Row():
                            with gr.Column():
                                gr_par_split= gr.Textbox(value=params["paragraph_split"], lines=1, label='Block split', interactive=True)
                            text_btn_load = gr.Button('Load', variant='primary', elem_classes="small-button")
                    with gr.Tab('Blockify normal text'):  
                        with gr.Row():
                            gr_block_size = gr.Number(value=params['block_size'],label='Block size (in chars)')
                            gr_par_split_chapter = gr.Textbox(value=params["chapter_start"], lines=1, label='Chapter word', interactive=True)
                            gr_convert_to_Block = gr.Button('Convert to Blocks', variant='primary', elem_classes="small-button") 
                    with gr.Tab('Extract names'):  
                        with gr.Row():
                            gr_extractNames= gr.Textbox(value='', lines=1, label='Names that appear more than once (most used on top)', interactive=True)
                            gr_extractNames_button = gr.Button('Extract Names', variant='primary', elem_classes="small-button")                             
            with gr.Tab('JSON'):
                    with gr.Row():
                        inputfile_text_drop_JSON  = gr.Dropdown(choices=get_available_input_JSON(), label='Input file', elem_classes=['slim-dropdown'], value='None')
                        create_refresh_button(inputfile_text_drop_JSON, lambda: None, lambda: {'choices': get_available_input_JSON()}, 'refresh-button')
                        gr_JSONType = gr.Dropdown(choices=JSON_TYPE, value=JSON_TYPE[0])
                        text_btn_load_JSON = gr.Button('Load JSON', variant='primary', elem_classes="small-button")
     
            with gr.Row():
                infotext = gr.Markdown(value='To process txt file with Blocks, use "Load". To format normal TXT file to Blocks, use "Convert to Blocks"')
 
            with gr.Accordion(label = "Edit Template", open=True):
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            para_templates_drop  = gr.Dropdown(choices=get_available_templates(), label='Template Selector', elem_classes=['slim-dropdown'], value=params['selected_template'])
                            create_refresh_button(para_templates_drop, lambda: None, lambda: {'choices': get_available_templates()}, 'refresh-button')
                        with gr.Tab('Main Template'):    
                            with gr.Row():                            
                                para_template_text = gr.Textbox(value=paraphrase_text, lines=10, interactive=True)
                                gr_htmlDisp = gr.HTML(value='', visible=False)
                        with gr.Tab('Alt Template (for duble-gen)'):    
                            with gr.Row():                            
                                para_template_text2 = gr.Textbox(value=params["alt_template"], lines=10, interactive=True, placeholder='If empty, then Main Template will be used for Double-gen')
                        with gr.Tab('Examples'):    
                            with gr.Row():                            
                                para_template_exampletext = gr.Textbox(value=example_text, lines=10, interactive=True, placeholder='Add some examples in the same instruct format as Main Template to better guide the model')
                        with gr.Tab('Names'): 
                            with gr.Column():
                                names_replace = gr.Checkbox(value=params['replace_names'], label='Randomly Replace names/places')
                                names_she = gr.Textbox(value=params['names_she'], lines=1, interactive=True, label='Female Names')
                                names_he = gr.Textbox(value=params['names_he'], lines=1, interactive=True, label='Male Names')
                                names_last = gr.Textbox(value=params['names_last'], lines=1, interactive=True, label='Last Names')
                                names_places1 = gr.Textbox(value=params['names_places1'], lines=1, interactive=True, label='Towns')
                                names_places2 = gr.Textbox(value=params['names_places2'], lines=1, interactive=True, label='Places/Churches')
                                    
                    with gr.Column():    
                        with gr.Row():    
                            templ_filename = gr.Textbox(value='', lines=1, label='') #params['dyn_templ_sel']
                            templ_btn_save = gr.Button('Save Template', elem_classes="small-button")
                            

                        with gr.Row():
                            with gr.Accordion('Settings', open=False):
                                with gr.Row():
                                    with gr.Column():
                                        gr_generate = gr.Checkbox(value=params['generate'],label='Generate Output: Text [in]-> (LLM) -> LLM Text [out]')
                                        gr_generate2 =gr.Checkbox(value=params['double_gen'],label='Double-gen: Text [in]-> (LLM) -> (LLM) -> LLM Text [out]')
                                        gr_radioReverse = gr.Checkbox(label='REVERSE Training: LLM Text[out] -> instruction, Text[in] -> output',value = params['out_reverse'], interactive=True)     
                                    
                                        gr_rep_EOL = gr.Checkbox(value=params['replace_eol'],label='Replace \\n in Text [in] with space')

                                        gr_add_err = gr.Checkbox(value=params['add_errors'], label='Add grammatical errors')
                                        gr_add_err_level = gr.Slider(value=params['error_level'], label="Error level", minimum=1, maximum=10,step = 1)
                                    
                                        gr_rep_EOL2 = gr.Checkbox(value=params['replace_eol2'],label='Replace \\n\\n with one \\n in Text [in]')
                                        gr_rmove_EOL = gr.Checkbox(value=params['remove_eol'],label='Internally Remove \\n before it goes to LLM, but keep it in Text [in]')
                                        gr_max_new_tokens = gr.Slider(minimum=100, maximum=4096, step=1, label='Max new tokens', value=params['max_new_tokens'])
                                        
                                    with gr.Column():
                                        gr_rep_Include_Long = gr.Checkbox(value=params['include_long'],label='if reply is much longer (3x) than IN: Copy IN -> OUT (otherwise ignore)')
                                        gr_rep_skip_short = gr.Checkbox(value=params['skip_short'],label='if reply is much shorter (3x) than IN then skip')
                                        gr_small_lines = gr.Number(value=params['limit_short'],label='SHORT IN cutoff characters')
                                        gr_rep_Include = gr.Checkbox(value=params['include_short'],label='if IN is SHORT: Copy IN -> OUT (otherwise ignore)')
                                        repeat_times = gr.Number(value=params['repeat_times'],label='Repeat each block n times')
                                
                                save_btn = gr.Button('Save Current Settings')        

                        with gr.Row():
                            preset_type = gr.Dropdown(label="Model Instruct (OLD))", choices=["Custom", "Vicuna", "Alpaca", "Mythologic", "Guanaco", "OpenAssistant","ChatML", "Gemma", "Llama 2 (Chat)", "Mistral/Mixtral", "Zephyr","WizardLM", "Solar", "OpenChat", "Phi-2 Instruct", "Nous Hermes"], value="Custom")
                            text_USR = gr.Textbox(value=params['pUSER'], lines=1, label='Replace <|user|> with')
                            text_BOT = gr.Textbox(value=params['pBOT'], lines=1, label='Replace <|bot|> with')
        
                                
            with gr.Row():
                with gr.Column(): 
                    text_in = gr.Textbox(value='', lines=10, label='Text [in] (in the template as <|context|> keyword):',elem_classes=['textbox', 'add_scrollbar'])
                    with gr.Row():
                        prev_prevbtn = gr.Button('<<')
                        prev_nextbtn = gr.Button('>>')
                        
                text_out = gr.Textbox(value='', lines=10, label='LLM Text [out]:', elem_classes=['textbox', 'add_scrollbar'])
            with gr.Row():    
                with gr.Column():
                    with gr.Row():
                        gr_radio = gr.Radio(choices = ['JSON','Plain TEXT'], value = params['out_type'], label='Output: JSON (Text [in,out]) or TXT (Text [out])')
                        text_instruct = gr.Textbox(value=params['instruct'], lines=1, label='JSON instruct (ALT on separate lines)')
                    
                with gr.Column():
                    with gr.Row():
                        out_filename = gr.Textbox(value=params['output_filename'], lines=1, label='Output filename')   
                        plaintext_instruct = gr.Textbox(value=params['plaintext_delim'], lines=1, label='Plain text paragraph separator')        
                    #text_outFile = gr.Textbox(value=file_nameJSON, lines=1, label='Output file JSON')        
                    #text_outFileTXT = gr.Textbox(value=file_nameTXT, lines=1, label='Output file TXT')

            with gr.Row():
                start_btn = gr.Button('Start', variant='primary')
                cancel_btn = gr.Button('Cancel',variant='stop')
                
            with gr.Row():
                infotext2 = gr.Markdown(value='Ready')


    def update_reloadTempl():
        return gr.Dropdown.update(choices=get_available_templates())
   

    para_templates_drop.change(load_Paraphrase_template,para_templates_drop,[para_template_text,para_template_exampletext]) 

    templ_btn_save.click(save_template,[para_template_text,para_template_exampletext, templ_filename],templ_filename).then(update_reloadTempl,None, para_templates_drop)

    input_paramsA = [para_template_text,para_template_text2, para_template_exampletext, shared.gradio['interface_state']]
    output_paramsA =[text_in, text_out, infotext2, gr_htmlDisp]

    #inputfile_text.change(load_file, inputfile_text,infotext)

    text_btn_load.click(load_file,inputfile_text_drop,[infotext,out_filename])

    text_btn_load_JSON.click(load_json_data,[inputfile_text_drop_JSON,gr_JSONType], infotext)

    def make_html_visible():
        return gr.update(visible = True)
    def make_html_hidden():
        return gr.update(visible = False)

    submit_event_1 = start_btn.click(make_html_visible,None,gr_htmlDisp).then(gather_interface_values, [shared.gradio[k] for k in shared.input_elements], shared.gradio['interface_state']).then(
        mainloop, inputs=input_paramsA, outputs=output_paramsA).then(make_html_hidden,None,gr_htmlDisp)
    
    gr_convert_to_Block.click(convert_blocks,[inputfile_text_drop, gr_block_size],infotext)

    gr_extractNames_button.click(extract_names,[inputfile_text_drop],gr_extractNames)

    def cancel_agent():
        global params
        params["done"] = True

    
    cancel_event = cancel_btn.click(
        cancel_agent,
        None,
        None,
        cancels = submit_event_1
    ).then(final_save,None,infotext2).then(make_html_hidden,None,gr_htmlDisp)


    
    def update_Out(x):
        global file_nameJSON
        file_nameJSON = x
    
   
    def update_OutTXT(x):
        global file_nameTXT
        file_nameTXT = x
    

 
 
    def update_preset(x):
        if x == "Vicuna":
            return 'USER:','ASSISTANT:'
        elif x == "Alpaca":
            return '### Instruction:','### Response:'
        elif x == "Mythologic":
            return '### Instruction:','### Response:'
        elif x == "Guanaco":
            return '### Human:','### Assistant:'
        elif x == "OpenAssistant":
            return '<|prompter|>','<|endoftext|><|assistant|>'
        elif x == "ChatML":
            return '<|im_start|>user','<|im_end|><|im_start|>assistant'
        elif x == "Gemma":
            return '<bos><start_of_turn>user\n','<end_of_turn>\n<start_of_turn>model'
        elif x == "Llama 2 (Chat)":
            return '[INST] ',' [/INST]' # Note: This one's tricky, the [/INST] is the bot's *start* of output
        elif x == "Mistral/Mixtral":
            return '[INST] ',' [/INST]' # Similar to Llama 2
        elif x == "Zephyr":
            return '<|user|>\n','<|assistant|>\n' # Simplified, without the '</s>'
        elif x == "WizardLM":
            return '### Instruction:\n','### Response:\n'
        elif x == "Solar":
            return '### User:\n','### Assistant:\n'
        elif x == "OpenChat":
            return 'GPT4 User: ','GPT4 Assistant: '
        elif x == "Phi-2 Instruct":
            return 'Instruct: ','Output: '
        elif x == "Nous Hermes":
            return '### Human:','### Assistant:'

        return 'USER:','ASSISTANT:'           

    prev_nextbtn.click(preview_next,None,text_in)
    prev_prevbtn.click(preview_prev,None,text_in)

    #gr_temperature.change(lambda x: default_req_params.update({"temperature": x}), gr_temperature, None)
    #gr_max_new_tokens.change(lambda x: default_req_params.update({"max_new_tokens": x}), gr_max_new_tokens, None)
    #gr_top_p.change(lambda x: default_req_params.update({"top_p": x}), gr_top_p, None)
    #gr_top_k.change(lambda x: default_req_params.update({"top_k": x}), gr_top_k, None)

    # activate.change(lambda x: params.update({"activate": x}), activate, None)
    text_USR.change(lambda x: params.update({"pUSER": x}), text_USR, None) 
    text_BOT.change(lambda x: params.update({"pBOT": x}), text_BOT, None) 
    #text_outFile.change(update_Out, text_outFile, None) 
    #text_outFileTXT.change(update_OutTXT, text_outFileTXT, None) 

    out_filename.change(lambda x: params.update({"output_filename": x}), out_filename, None)
    
    text_instruct.change(lambda x: params.update({"instruct": x}), text_instruct, None) 
    preset_type.change(update_preset,preset_type,[text_USR,text_BOT])
    gr_rep_EOL.change(lambda x: params.update({"replace_eol": x}), gr_rep_EOL, None)
    gr_add_err.change(lambda x: params.update({"add_errors": x}), gr_add_err, None)
    gr_add_err_level.change(lambda x: params.update({"error_level": x}), gr_add_err_level, None)

    gr_rmove_EOL.change(lambda x: params.update({"remove_eol": x}), gr_rmove_EOL, None)
    gr_rep_EOL2.change(lambda x: params.update({"replace_eol2": x}), gr_rep_EOL2, None)
    repeat_times.change(lambda x: params.update({"repeat_times": x}), repeat_times, None)
    gr_max_new_tokens.change(lambda x: params.update({"max_new_tokens": x}), gr_max_new_tokens, None)

    gr_small_lines.change(lambda x: params.update({"limit_short": x}), gr_small_lines, None)
    gr_rep_Include.change(lambda x: params.update({"include_short": x}), gr_rep_Include, None)
    gr_rep_Include_Long.change(lambda x: params.update({"include_long": x}), gr_rep_Include_Long, None)
    gr_rep_skip_short.change(lambda x: params.update({"skip_short": x}), gr_rep_skip_short, None)
    gr_par_split.change(lambda x: params.update({"paragraph_split": x}), gr_par_split, None)
    gr_par_split_chapter.change(lambda x: params.update({"chapter_start": x}), gr_par_split_chapter, None)


    gr_radio.change(lambda x: params.update({"out_type": x}), gr_radio, None)
    gr_generate.change(lambda x: params.update({"generate": x}), gr_generate, None)
    gr_generate2.change(lambda x: params.update({"double_gen": x}), gr_generate2, None)
    plaintext_instruct.change(lambda x: params.update({"plaintext_delim": x}), plaintext_instruct, None)

    gr_radioReverse.change(lambda x: params.update({"out_reverse": x}), gr_radioReverse, None)
    save_btn.click(save_pickle,None,None)

    names_replace.change(lambda x: params.update({"replace_names": x}), names_replace, None)

    names_she.change(lambda x: params.update({"names_she": x}), names_she, None) 
    names_he.change(lambda x: params.update({"names_he": x}), names_he, None)
    names_last.change(lambda x: params.update({"names_last": x}), names_last, None)
    names_places1.change(lambda x: params.update({"names_places1": x}), names_places1, None)
    names_places2.change(lambda x: params.update({"names_places2": x}), names_places2, None)

