from django.core.management.base import BaseCommand
import random
import time
import google.generativeai as genai
from snake_ladder.models import Cell

class Command(BaseCommand):
    help = 'Populates cells with educational content'

    GOOGLE_API_KEY = 'AIzaSyA8GHU0QhwXkgCXEBYnost56YOPmsd2pPs'

    # Configure Gemini
    genai.configure(api_key=GOOGLE_API_KEY)
    model = genai.GenerativeModel('gemini-pro')

    def generate_cell_content(self):
        try:
            response = self.model.generate_content(
                "Give me a brief fact about the Indian Constitution (max 20 words)."
            )
            return response.text.strip()
        except Exception as e:
            return "A fact about the Indian Constitution."

    def handle(self, *args, **options):
        self.stdout.write('Clearing existing cells...')
        Cell.objects.all().delete()

        # Generate cells (20% will be snake-ladder cells)
        for number in range(1, 101):
            cell_type = 'SNAKE_LADDER' if random.random() < 0.2 else 'NORMAL'
            content = self.generate_cell_content()
            
            Cell.objects.create(
                number=number,
                content=content,
                cell_type=cell_type
            )
            self.stdout.write(f'Created cell {number}')
            time.sleep(1)  # Rate limiting for API 