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
        
        # Select random cells for snakes and ladders
        special_cells = random.sample(all_cells, 18)
        normal_cells = [x for x in all_cells if x not in special_cells]
        
        self.stdout.write('Creating normal cells...')
        for number in normal_cells:
            content = self.generate_cell_content()
            Cell.objects.create(
                number=number,
                content=content,
                cell_type='NORMAL'
            )
            self.stdout.write(f'Created cell {number}')
            time.sleep(1)  # Rate limiting
        
        self.stdout.write('Creating snake and ladder cells...')
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
            self.stdout.write(f'Created snake at cell {number}')
        
        for number in ladder_cells:
            destination = random.choice([x for x in normal_cells if x > number])
            Cell.objects.create(
                number=number,
                content="Answer the question correctly to climb the ladder!",
                cell_type='LADDER',
                destination=destination
            )
            self.stdout.write(f'Created ladder at cell {number}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated cells')) 