from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
import json
import google.generativeai as genai
from .models import Conversation
from django.conf import settings


# Create your views here.

def home(request):
    user = request.user
    return render(request, "home.html", {'user': user})


def logout_view(request):
    logout(request)
    return redirect('/')

@csrf_exempt
def chat(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            question = data.get('question')
            
            if not question:
                return JsonResponse({'error': 'Question is required'}, status=400)
            
            # Configure Gemini
            genai.configure(api_key=settings.GOOGLE_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            # Enhanced context and persona for the AI
            prompt = f"""You are LawBot, an intelligent AI assistant specializing in legal matters and constitutional law. 
Format your responses using the following markdown-style conventions:

• Use **bold** for important terms and concepts
• Use *italics* for emphasis or examples
• Use bullet points (•) for lists
• Add line breaks between sections for readability

When explaining legal concepts:
• Start with a clear definition
• Break down complex ideas into simple terms
• Use examples when helpful
• Organize information into clear sections

Question to answer:
{question}

Remember to maintain a professional yet approachable tone and format the response for easy reading."""
            
            try:
                response = model.generate_content(prompt)
                
                # Save the conversation
                Conversation.objects.create(
                    question=question,
                    answer=response.text
                )
                
                return JsonResponse({
                    'answer': response.text
                })
            except Exception as e:
                print(f"Gemini API Error: {str(e)}")
                return JsonResponse({
                    'error': 'AI service temporarily unavailable'
                }, status=503)
                
        except json.JSONDecodeError:
            return JsonResponse({
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({
                'error': 'Internal server error'
            }, status=500)

    return JsonResponse({'error': 'Invalid request method'}, status=400)