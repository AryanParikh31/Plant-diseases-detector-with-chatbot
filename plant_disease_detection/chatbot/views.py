import os
from django.http import HttpResponse
import requests
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .models import ChatMessage  

# ✅ Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# ✅ Ensure API key is loaded
if GEMINI_API_KEY is None:
    raise ValueError("GEMINI_API_KEY is not set! Check your .env file.")

# ✅ Allowed words in English, Hindi, and Gujarati
ALLOWED_CATEGORIES = {
    "plant": [
        "plant", "पौधा", "વૃક્ષ", "पेड़", "झाड़ी", "लता", "बेल", "वनस्पति", "औषधीय पौधा", "फूल", "છોડ", "પાન"
    ],
    
    "plant disease": [
        "plant disease", "पौधों की बीमारी", "છોડની બિમારી", "फसल रोग", "जीवाणु रोग", "કૃમિનાશક રોગ", "વાયરસ રોગ",
        "Powdery Mildew", "डाउनी मिल्ड्यू", "પાવડરી મિલ્ડ્યુ",
        "Rust Disease", "रस्ट रोग", "રસ્ટ રોગ",
        "Blight", "झुलसा रोग", "છોડનો સુકો રોગ",
        "Wilt Disease", "मुरझाने की बीमारी", "મોલ પછડાટ રોગ",
        "Leaf Spot", "पत्तों के धब्बे", "પાનના ધબ્બા",
        "Root Rot", "जड़ सड़न", "મૂળ નાશ",
        "Anthracnose", "एन्थ्रेक्नोज़", "એન્થ્રાક્નોઝ",
        "Damping Off", "डैम्पिंग ऑफ", "ડેમ્પિંગ ઑફ",
        "Bacterial Wilt", "जीवाणु विल्ट", "બેક્ટેરિયલ વિલ્ટ",
        "Canker", "कैंकर रोग", "કૅન્કર રોગ",
        "Mosaic Virus", "मोज़ेक वायरस", "મોઝેક વાયરસ"
    ],
    
    "soil": [
        "soil", "मिट्टी", "માટી", "भूमि", "उर्वर मृदा", "रेतीली मिट्टी", "મકરજ", "સરસવ",
        "Sandy Soil", "बलुई मिट्टी", "વાળવાળી માટી",
        "Clay Soil", "चिकनी मिट्टी", "ચીકણી માટી",
        "Loamy Soil", "दोमट मिट्टी", "લૂમી માટી",
        "Silty Soil", "गाद वाली मिट्टी", "ગાદવાળી માટી",
        "Peaty Soil", "पीट मिट्टी", "પીટ માટી",
        "Chalky Soil", "चूना मिट्टी", "ચૂનાધારી માટી",
        "Saline Soil", "लवणीय मिट्टी", "લવણીય માટી",
        "Alluvial Soil", "जलोढ़ मिट्टी", "જલોધીય માટી",
        "Black Soil", "काली मिट्टी", "કાળી માટી",
        "Red Soil", "लाल मिट्टी", "લાલ માટી",
        "Laterite Soil", "लेटराइट मिट्टी", "લેટરાઈટ માટી"
    ],
    
    "pesticides": [
        "pesticides", "कीटनाशक", "કીડનાશક", "रासायनिक कीटनाशक", "જંતુનાશક દવા", "જીવાણુનાશક", "फसल संरक्षक",
        "Insecticide", "कीटनाशक", "જંતુનાશક",
        "Herbicide", "शाकनाशी", "શાકનાશક",
        "Fungicide", "फफूंदनाशी", "ફૂગનાશક",
        "Bactericide", "जीवाणुनाशी", "બેક્ટેરિસાઈડ",
        "Rodenticide", "कृंतकनाशी", "રોડેન્ટિસાઈડ",
        "Nematicide", "नेमाटोडनाशी", "નેમેટિસાઈડ",
        "Acaricide", "माइटनाशी", "માઈટનાશક",
        "Biopesticide", "जैविक कीटनाशक", "જૈવિક જીવાણુનાશક",
        "Pyrethrin", "पाइरेथ्रिन", "પાયરેથ્રિન",
        "Carbamate", "कार्बामेट", "કાર્બામેટ",
        "Organophosphate", "ऑर्गेनोफॉस्फेट", "ઓર્ગેનોફોસ્ફેટ",
        "Chlorpyrifos", "क्लोरपाइरीफोस", "ક્લોરપાયરિફોસ"
    ],
    
    "fertilizer": [
        "fertilizer", "उर्वरक", "ખાતર", "जैविक उर्वरक", "રાસાયનિક ખાતર", "કોમ્પોસ્ટ", "હરિત ખાતર",
        "Nitrogen Fertilizer", "नाइट्रोजन उर्वरक", "નાઈટ્રોજન ખાતર",
        "Phosphorus Fertilizer", "फॉस्फोरस उर्वरक", "ફોસ્ફરસ ખાતર",
        "Potassium Fertilizer", "पोटेशियम उर्वरक", "પોટેશિયમ ખાતર",
        "Organic Fertilizer", "जैविक उर्वरक", "જૈવિક ખાતર",
        "Compost", "खाद", "કોમ્પોસ્ટ",
        "Manure", "गोबर खाद", "ખેતર ખાતર",
        "Urea", "यूरिया", "યુરિયા",
        "DAP", "डीएपी", "ડી.એ.પી.",
        "Superphosphate", "सुपरफॉस्फेट", "સુપરફોસ્ફેટ",
        "NPK Fertilizer", "एनपीके उर्वरक", "એનપીક fertilizers",
        "Ammonium Sulfate", "अमोनियम सल्फेट", "એમોનિયમ સલ્ફેટ",
        "Calcium Nitrate", "कैल्शियम नाइट्रेट", "કૅલ્શિયમ નાઈટ્રેટ"
    ],
    
    "solution": [
        "solution", "समाधान", "ઉકેલ", "इलाज", "उपचार", "પ્રતિસાધન", "સલાહ", "વિકલ્પ", "ફાયદાકારક ઉપાય",
        "Preventive Measures", "निवारक उपाय", "પહેલા પગલાં",
        "Chemical Treatment", "रासायनिक उपचार", "રાસાયણિક ઉપચાર",
        "Biological Control", "जैविक नियंत्रण", "જૈવિક નિયંત્રણ",
        "Integrated Pest Management", "समेकित कीट प्रबंधन", "સંયોજનિત જીવાણુ વ્યવસ્થાપન",
        "Soil Testing", "मिट्टी परीक्षण", "માટી પરીક્ષણ",
        "Water Management", "जल प्रबंधन", "પાણી વ્યવસ્થાપન"
    ]
}

# ✅ Greetings
GREETINGS = {
    "en": ["hi", "hello"],
    "hi": ["नमस्ते", "नमस्कार"],
    "gu": ["હેલો", "હાય"]
}

GREETING_RESPONSES = {
    "en": "Hi, how can I assist you?",
    "hi": "नमस्ते, मैं आपकी कैसे सहायता कर सकता हूँ?",
    "gu": "નમસ્તે, હું તમને કેવી રીતે મદદ કરી શકું?"
}

# ✅ Expanded Predefined Questions and Answers in Multiple Languages
PREDEFINED_QUESTIONS = {
    "who are you": {
        "en": "I am an AI-powered chatbot designed to assist with plant-related questions.",
        "hi": "मैं एक एआई-पावर्ड चैटबॉट हूँ जो पौधों से संबंधित प्रश्नों में आपकी सहायता करने के लिए बना हूँ।",
        "gu": "હું એઆઈ-શક્તિસભર ચેટબોટ છું જે છોડ સંબંધિત પ્રશ્નો માટે તમારી મદદ માટે તૈયાર છું."
    },
    "how are you": {
        "en": "I am just a chatbot, but I am always ready to assist you!",
        "hi": "मैं सिर्फ एक चैटबॉट हूँ, लेकिन मैं हमेशा आपकी सहायता के लिए तैयार हूँ!",
        "gu": "હું ફક્ત એક ચેટબોટ છું, પણ હું હંમેશા તમારી મદદ માટે તૈયાર છું!"
    },
    "what can you do": {
        "en": "I can help you with questions about plants, plant diseases, soil, pesticides, and fertilizers.",
        "hi": "मैं आपको पौधों, पौधों की बीमारियों, मिट्टी, कीटनाशकों और उर्वरकों से संबंधित प्रश्नों में मदद कर सकता हूँ।",
        "gu": "હું તમને છોડ, છોડની બીમારીઓ, માટી, કીડનાશકો અને ખાતર વિશે પૂછેલા પ્રશ્નોમાં મદદ કરી શકું છું."
    },
    "how to take care of plants": {
        "en": "Water them regularly, provide sunlight, and use good soil and fertilizers.",
        "hi": "पौधों की देखभाल के लिए नियमित रूप से पानी दें, धूप दें, और अच्छी मिट्टी व उर्वरक का उपयोग करें।",
        "gu": "છોડની સંભાળ માટે, નિયમિત પાણી આપો, રોશની આપો અને સારી માટી અને ખાતર વાપરો."
    },
    "best fertilizer for plants": {
        "en": "Compost and balanced NPK fertilizers (Nitrogen, Phosphorus, Potassium) are the best.",
        "hi": "खाद और संतुलित NPK उर्वरक (नाइट्रोजन, फॉस्फोरस, पोटैशियम) सबसे अच्छे हैं।",
        "gu": "સજીવ ખાતર અને સંતુલિત NPK ખાતર (નાઈટ્રોજન, ફોસ્ફરસ, પોટેશિયમ) શ્રેષ્ઠ છે."
    },
    "how often should I water plants": {
        "en": "Most plants need water every 2-3 days, but some need daily watering.",
        "hi": "अधिकांश पौधों को हर 2-3 दिन में पानी चाहिए, लेकिन कुछ को रोज़ चाहिए।",
        "gu": "મોટાભાગના છોડને 2-3 દિવસમાં પાણી જોઈએ, પણ કેટલાકને દરરોજ જોઈએ."
    },
    "why are my plant leaves turning yellow": {
        "en": "This may be due to overwatering, underwatering, or nutrient deficiency.",
        "hi": "यह अधिक पानी, कम पानी या पोषक तत्वों की कमी के कारण हो सकता है।",
        "gu": "આ વધારે પાણી, ઓછું પાણી અથવા પોષક તત્વોની ઉણપને કારણે થઈ શકે છે."
    },
    "how can I prevent plant diseases": {
        "en": "Use healthy soil, water properly, and prevent pests and fungal infections.",
        "hi": "अच्छी मिट्टी का उपयोग करें, सही पानी दें और कीटों व फफूंद से बचाव करें।",
        "gu": "સારી માટી વાપરો, યોગ્ય રીતે પાણી આપો અને જીવાત અને ફૂગના સંક્રમણથી બચો."
    },
    "which plants need less water": {
        "en": "Cacti, succulents, and snake plants need very little water.",
        "hi": "कैक्टस, रसीले पौधे और स्नेक प्लांट को बहुत कम पानी की जरूरत होती है।",
        "gu": "કેક્ટસ, સુકુલેન્ટ અને સ્નેક પ્લાન્ટને ઓછી પાણીની જરૂર હોય છે."
    },
    "which plants grow indoors": {
        "en": "Snake plant, money plant, and peace lily grow well indoors.",
        "hi": "स्नेक प्लांट, मनी प्लांट और पीस लिली घर के अंदर अच्छी तरह उगते हैं।",
        "gu": "સ્નેક પ્લાન્ટ, મની પ્લાન્ટ અને પીસ લિલી અંદર સારી રીતે ઉગે છે."
    },
    "why is my plant not growing": {
        "en": "Lack of sunlight, poor soil, or improper watering may be the cause.",
        "hi": "धूप की कमी, खराब मिट्टी या गलत पानी देने से यह हो सकता है।",
        "gu": "સૂર્યપ્રકાશની ઉણપ, ખરાબ માટી અથવા ખોટી રીતે પાણી આપવાથી આમ થઈ શકે છે."
    },
    "which plants purify air": {
        "en": "Aloe vera, spider plant, and peace lily are great air purifiers.",
        "hi": "एलोवेरा, स्पाइडर प्लांट और पीस लिली बेहतरीन वायु शोधक हैं।",
        "gu": "એલોવેરા, સ્પાઇડર પ્લાન્ટ અને પીસ લિલી શ્રેષ્ઠ હવા શુદ્ધિકર્તા છે."
    },
    "why is my plant drooping": {
        "en": "Drooping plants may need more water, better soil, or less sunlight.",
        "hi": "गिरते हुए पौधों को अधिक पानी, बेहतर मिट्टी या कम धूप की जरूरत हो सकती है।",
        "gu": "વાંકડિયાતા છોડને વધારે પાણી, સારી માટી અથવા ઓછી રોશનીની જરૂર પડી શકે છે."
    }
}

def detect_language(message):
    """Detect the language of the message based on greetings and predefined questions."""
    message = message.lower()
    
    for lang, words in GREETINGS.items():
        if any(word in message for word in words):
            return lang  # Return detected language
    
    return "en"  # Default to English if no match is found

def is_greeting(message):
    """Check if the message is a greeting in any supported language."""
    message = message.lower()
    return any(word in message for words in GREETINGS.values() for word in words)

def is_predefined_question(message):
    """Check if the message is a predefined question."""
    message = message.lower()
    return any(question in message for question in PREDEFINED_QUESTIONS.keys())

def get_predefined_answer(message, language):
    """Return the predefined answer in the detected language."""
    for question, answers in PREDEFINED_QUESTIONS.items():
        if question in message:
            return answers.get(language, answers["en"])  # Default to English if language not found
    return None

def is_question_valid(question):
    """Check if the question contains allowed words in English, Hindi, or Gujarati."""
    question = question.lower()
    for category in ALLOWED_CATEGORIES.values():
        for word in category:
            if word in question:
                return True
    return False

def get_gemini_response(question, language):
    """Fetch a response from Gemini API in the detected language."""
    url = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro-002:generateContent"
    headers = {"Content-Type": "application/json"}
    params = {"key": GEMINI_API_KEY}

    structured_prompt = f"Provide a detailed response in {language} for the question: {question}"

    data = {
        "contents": [{"parts": [{"text": structured_prompt}]}]
    }

    try:
        response = requests.post(url, headers=headers, params=params, json=data)
        response_json = response.json()

        if "candidates" in response_json:
            return response_json["candidates"][0]["content"]["parts"][0]["text"]
        elif "error" in response_json:
            return f"Error: {response_json['error']['message']}"
        else:
            return "I'm sorry, I couldn't process that."

    except requests.exceptions.RequestException as e:
        return f"Error connecting to AI service: {e}"

@csrf_exempt
def chat_page(request):
    """Handle user input and render chat interface."""
    chat_history = ChatMessage.objects.all().order_by("timestamp")

    if request.method == "POST":
        user_message = request.POST.get("message", "").strip().lower()
        detected_language = detect_language(user_message)

        if is_greeting(user_message):
            bot_response = GREETING_RESPONSES[detected_language]
        elif is_predefined_question(user_message):
            bot_response = get_predefined_answer(user_message, detected_language)
        elif not is_question_valid(user_message):
            responses = {
                "en": "I can only answer questions related to plants, plant diseases, pesticides, soil, and fertilizers.",
                "hi": "मैं केवल पौधों, पौधों की बीमारियों, कीटनाशकों, मिट्टी और उर्वरकों से संबंधित प्रश्नों का उत्तर दे सकता हूँ।",
                "gu": "હું ફક્ત છોડ, છોડની બીમારીઓ, કીડનાશકો, માટી અને ખાતર વિશેના પ્રશ્નોના જવાબ આપી શકું."
            }
            bot_response = responses[detected_language]
        else:
            bot_response = get_gemini_response(user_message, detected_language)

        ChatMessage.objects.create(user_message=user_message, bot_response=bot_response)
        return HttpResponse(bot_response)

    return render(request, "chat.html", {"chat_history": chat_history})
