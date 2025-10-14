import os
import json
from datetime import datetime
import ollama

# Configuration
RESULT_FILE = 'analysis_results.txt'
STATE_FILE = 'processing_state.json'
LOG_FILE = 'debug.log'
MODEL_NAME = 'deepseek-r1:1.5b'  # Model to use with Ollama

def log_error(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, 'a') as f:
        f.write(f"[{timestamp}] {message}\n")

def load_processing_state():
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        log_error(f"State load error: {str(e)}")
        return {}

def save_processing_state(state):
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f)
    except Exception as e:
        log_error(f"State save error: {str(e)}")

def analyze_text(content):
    system_prompt = """You are a data extraction assistant. Analyze the text and respond with JSON containing:
    - "animal" object with fields: type, age, location, contact, drive_link
    - "ngo" object with fields: name, location, type, contact
    Return only valid JSON with no additional formatting or explanation.
    Omit empty fields. Escape special characters."""
    
    try:
        response = ollama.generate(
            model=MODEL_NAME,
            prompt=f"System: {system_prompt}\nUser: {content}",
            format='json',
            options={
                'temperature': 0.1,
                'num_predict': 512
            }
        )
        
        response_text = response['response']
        log_error(f"Raw model response: {response_text}")
        response_text = response_text.strip().replace('json', '').replace('', '')
        
        if not response_text:
            log_error("Empty model response")
            return None
            
        return json.loads(response_text)
        
    except json.JSONDecodeError as e:
        log_error(f"JSON Error: {str(e)} | Content: {content[:50]}... | Response: {response_text[:200]}")
        return None
    except Exception as e:
        log_error(f"General Error: {str(e)} | Content: {content[:50]}...")
        return None

def format_entry(entry_type, data, filename, line_number):
    entry = [
        f"=== {entry_type.upper()} ENTRY ===",
        f"Source File: {filename}",
        f"Line Number: {line_number}"
    ]
    
    fields = {
        'animal': ['type', 'age', 'location', 'contact', 'drive_link'],
        'ngo': ['name', 'location', 'type', 'contact']
    }[entry_type]

    for field in fields:
        if data.get(field):
            entry.append(f"{field.title()}: {data[field]}")
    
    return '\n'.join(entry) + '\n\n'

def process_files():
    open(LOG_FILE, 'w').close()  # Clear previous logs
    state = load_processing_state()
    processed_files = False

    for filename in os.listdir('.'):
        if filename.endswith('.txt') and filename not in [RESULT_FILE, STATE_FILE, LOG_FILE]:
            try:
                with open(filename, 'r') as f:
                    lines = f.readlines()
                
                last_processed = state.get(filename, 0)
                new_lines = lines[last_processed:]
                
                if not new_lines:
                    continue

                with open(RESULT_FILE, 'a') as result_file:
                    for idx, line in enumerate(new_lines, start=last_processed+1):
                        line = line.strip()
                        if not line:
                            continue

                        analysis = analyze_text(line)
                        if not analysis:
                            log_error(f"Skipped line {idx} in {filename}")
                            continue

                        entries = []
                        if analysis.get('animal'):
                            entries.append(format_entry('animal', analysis['animal'], filename, idx))
                        if analysis.get('ngo'):
                            entries.append(format_entry('ngo', analysis['ngo'], filename, idx))
                        
                        if entries:
                            result_file.write('\n'.join(entries) + '\n' + '='*40 + '\n\n')

                state[filename] = last_processed + len(new_lines)
                processed_files = True

            except Exception as e:
                log_error(f"File processing error {filename}: {str(e)}")
                continue

    if processed_files:
        save_processing_state(state)
        print(f"Analysis complete. Check {RESULT_FILE} for results and {LOG_FILE} for any errors")
    else:
        print("No new content to analyze.")

# if __name__ == '__main__':
if not os.path.exists(RESULT_FILE):
    with open(RESULT_FILE, 'w') as f:
        f.write("ANIMAL AND NGO ANALYSIS RESULTS\n\n")
    
try:
    test_response = ollama.generate(
        model=MODEL_NAME,
        prompt="Say 'Ollama test successful'",
        options={'temperature': 0.1}
    )
    print(f"Ollama test response: {test_response['response']}")
    process_files()
except Exception as e:
    print(f"Ollama connection failed: {str(e)}")
    print("Make sure Ollama is running and the model is downloaded.")