from django.core.management.base import BaseCommand
import random
import time
import google.generativeai as genai
from snake_ladder.models import Cell

class Command(BaseCommand):
    help = 'Populates cells with educational content about Parts 5 and 6 of the Constitution'

    GOOGLE_API_KEY = 'AIzaSyA8GHU0QhwXkgCXEBYnost56YOPmsd2pPs'

    # Configure Gemini
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    # Predefined prompts for content generation
    PROMPTS = [
        "Give me a brief fact about the Union Judiciary from Part 5 of the Indian Constitution (max 20 words).",
        "Share a key point about High Courts from Part 6 of the Indian Constitution (max 20 words).",
        "Tell me about a power of the Supreme Court (max 20 words).",
        "Explain a concept about state judiciary from Part 6 (max 20 words).",
        "Share an important point about judicial appointments (max 20 words)."
    ]

    FORMATS = [
        "Quick Fact: {content}",
        "Constitutional Point: {content}",
        "Key Principle: {content}",
        "Important Note: {content}"
    ]

    def generate_cell_content(self):
        try:
            prompt = random.choice(self.PROMPTS)
            response = self.model.generate_content(prompt)
            content = response.text.strip().split('.')[0] + '.'  # Take first sentence and add period
            format_template = random.choice(self.FORMATS)
            return format_template.format(content=content)
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'API Error: {str(e)}'))
            # Fallback content if API fails
            return "Constitutional Point: The judiciary is an independent pillar of Indian democracy."

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing cells...')
        Cell.objects.all().delete()

        # Generate list of all cell numbers
        all_cells = list(range(1, 101))
        
        # Divide board into 5 sections for even distribution
        sections = [
            range(1, 21),    # Section 1
            range(21, 41),   # Section 2
            range(41, 61),   # Section 3
            range(61, 81),   # Section 4
            range(81, 101)   # Section 5
        ]
        
        special_cells = []
        # Select snakes and ladders from each section
        for section in sections:
            section_cells = list(section)
            # 2 snakes and 2 ladders per section
            section_special = random.sample(section_cells, 4)
            special_cells.extend(section_special)
        
        normal_cells = [x for x in all_cells if x not in special_cells]
        
        # Create normal cells
        for number in normal_cells:
            content = self.generate_cell_content()
            Cell.objects.create(
                number=number,
                content=content,
                cell_type='NORMAL'
            )
            self.stdout.write(f'Created cell {number}')
            time.sleep(1)
        
        # Create snakes and ladders evenly distributed
        snake_cells = special_cells[:10]  # First half for snakes
        ladder_cells = special_cells[10:]  # Second half for ladders
        
        for number in snake_cells:
            # Find destination in lower section
            possible_destinations = [x for x in normal_cells if x < number and abs(number - x) <= 20]
            destination = random.choice(possible_destinations) if possible_destinations else number - 10
            Cell.objects.create(
                number=number,
                content="Answer the question correctly to avoid the snake!",
                cell_type='SNAKE',
                destination=destination
            )
        
        for number in ladder_cells:
            # Find destination in higher section
            possible_destinations = [x for x in normal_cells if x > number and abs(x - number) <= 20]
            destination = random.choice(possible_destinations) if possible_destinations else number + 10
            Cell.objects.create(
                number=number,
                content="Answer the question correctly to climb the ladder!",
                cell_type='LADDER',
                destination=destination
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully populated cells')) 