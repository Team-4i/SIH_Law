import os
import django
import random
import requests
import json
import time

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SIH.settings')
django.setup()

from snake_ladder.models import Cell

PERPLEXITY_API_KEY = "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"
API_URL = "https://api.perplexity.ai/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
    "Content-Type": "application/json"
}

# Content formats
FORMATS = [
    "Quick Fact: {content}",
    "Constitutional Point: {content}",
    "Key Principle: {content}",
    "Important Note: {content}"
]

def get_perplexity_response(prompt):
    data = {
        "model": "mixtral-8x7b-instruct",
        "messages": [{
            "role": "system",
            "content": "You are a constitutional law expert. Provide brief, accurate information about Parts 5 and 6 of the Indian Constitution."
        }, {
            "role": "user",
            "content": prompt
        }],
        "max_tokens": 100
    }
    
    try:
        response = requests.post(API_URL, headers=HEADERS, json=data)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        print(f"API Error: {e}")
        return None

def generate_cell_content():
    prompts = [
        "Give me a brief fact about the Union Judiciary from Part 5 of the Indian Constitution.",
        "Share a key point about High Courts from Part 6 of the Indian Constitution.",
        "Explain a concept about the Supreme Court's jurisdiction.",
        "Tell me about the appointment of judges in state courts.",
        "Describe a power of the Supreme Court.",
    ]
    
    prompt = random.choice(prompts)
    content = get_perplexity_response(prompt)
    
    if content:
        format_template = random.choice(FORMATS)
        return format_template.format(content=content)
    return None

def populate_cells():
    # Clear existing cells
    Cell.objects.all().delete()
    
    # Generate list of all cell numbers
    all_cells = list(range(1, 101))
    
    # Select random cells for snakes and ladders
    special_cells = random.sample(all_cells, 18)
    normal_cells = [x for x in all_cells if x not in special_cells]
    
    # Create normal cells with content
    for number in normal_cells:
        content = generate_cell_content()
        if content:
            Cell.objects.create(
                number=number,
                content=content,
                cell_type='NORMAL'
            )
        time.sleep(1)  # Rate limiting
    
    # Create snake and ladder cells
    snake_cells = special_cells[:9]
    ladder_cells = special_cells[9:]
    
    for number in snake_cells:
        destination = random.choice([x for x in normal_cells if x < number])
        Cell.objects.create(
            number=number,
            content="Answer the question correctly to avoid the snake!",
            cell_type='SNAKE',
            destination=destination
        )
    
    for number in ladder_cells:
        destination = random.choice([x for x in normal_cells if x > number])
        Cell.objects.create(
            number=number,
            content="Answer the question correctly to climb the ladder!",
            cell_type='LADDER',
            destination=destination
        )

if __name__ == "__main__":
    print("Starting cell population...")
    populate_cells()
    print("Cell population completed!") 