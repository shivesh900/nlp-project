import pandas as pd
import pickle
import logging
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Highly diverse dataset: English, Tamil, Hindi
en_text = [
    "Hello, how are you today?", "What's up bro, how's life?", "This is a great day for NLP.",
    "I am learning machine learning with Python.", "Can you help me with this problem?",
    "The quick brown fox jumps over the lazy dog.", "I love eating pizza and burgers.",
    "Where are you going for vacation?", "Let's go to the park and play cricket.",
    "Artificial intelligence is changing the world.", "I am feeling very happy today.",
    "What is the capital of France?", "The weather is so nice, let's go outside.",
    "I have a lot of work to finish by evening.", "Sharing is caring, they say.",
    "Don't worry, be happy!", "Failure is the stepping stone to success.",
    "Honesty is the best policy.", "Practice makes perfect.", "Knowledge is power.",
    "Hey man, did you see the game last night?", "I'm so tired, I need some coffee.",
    "Believe in yourself and you can achieve anything.", "Dream big and work hard.",
    "Life is what happens when you're busy making other plans.", "Stay hungry, stay foolish.",
    "The only way to do great work is to love what you do.", "Focus on the positive, forget the negative.",
    "Be kind to everyone you meet.", "Every cloud has a silver lining.",
    "Actions speak louder than words.", "Better late than never.", "A journey of a thousand miles begins with a single step.",
    "An apple a day keeps the doctor away.", "Birds of a feather flock together.", "Easy come, easy go.",
    "Money doesn't grow on trees.", "No pain, no gain.", "There's no place like home.",
    "What's the matter with you?", "Are you okay?", "Is everything alright?", "Do you know what I mean?",
    "Exactly, that's what I'm talking about!", "I'm not sure about that.", "I completely agree with you.",
    "That's a very good point.", "I'll think about it.", "Let me know what you decide.",
    "Check this out, it's awesome!", "You're killing it!", "No way, that's unbelievable.",
    "Can we meet tomorrow morning?", "How's your family doing?", "What's the latest news?",
    "I'm looking forward to our next meeting.", "Everything will be fine, trust me.",
    "Take care of yourself.", "See you soon!", "Have a wonderful day ahead.",
    "It's a pleasure to meet you.", "How can I improve my skills?"
]

ta_text = [
    "வணக்கம், நீங்கள் எப்படி இருக்கிறீர்கள்?", "எப்படி இருக்கீங்க நண்பா?", "நலம் இன்று மிகவும் நன்றாக இருக்கிறது.",
    "நான் பைதான் மூலம் இயந்திர கற்றல் கற்கிறேன்.", "எனக்கு இந்த பிரச்சனையில் உதவ முடியுமா?",
    "வேகமான பழுப்பு நிற நரி சோம்பேறி நாயின் மேல் குதிக்கிறது.", "எனக்கு பீட்சா மற்றும் பர்கர் சாப்பிட பிடிக்கும்.",
    "நீங்கள் விடுமுறைக்கு எங்கே போகிறீர்கள்?", "பூங்காவிற்குச் சென்று கிரிக்கெட் விளையாடுவோம்.",
    "செயற்கை நுண்ணறிவு உலகை மாற்றிக் கொண்டிருக்கிறது.", "இன்று நான் மிகவும் மகிழ்ச்சியாக உணர்கிறேன்.",
    "பிரான்சின் தலைநகரம் எது?", "வானிலை மிகவும் நன்றாக இருக்கிறது, வெளியே போவோம்.",
    "மாலைக்குள் முடிக்க எனக்கு நிறைய வேலை இருக்கிறது.", "பகிர்ந்து கொள்வது அக்கறை காட்டுவது என்கிறார்கள்.",
    "கவலைப்படாதே, மகிழ்ச்சியாக இரு!", "தோல்வி வெற்றிக்கு ஒரு படிக்கட்டு.", "நேர்மையே சிறந்த கொள்கை.",
    "பயிற்சி முழுமை அளிக்கும்.", "அறிவே ஆற்றல்.", "ஏய் நண்பா, நேற்று இரவு ஆட்டத்தைப் பார்த்தாயா?",
    "நான் மிகவும் சோர்வாக இருக்கிறேன், எனக்கு கொஞ்சம் காபி வேண்டும்.",
    "உங்களை நம்புங்கள், உங்களால் எதையும் சாதிக்க முடியும்.", "பெரிதாக கனவு காணுங்கள் மற்றும் கடினமாக உழைக்கவும்.",
    "நீங்கள் மற்ற திட்டங்களை வகுப்பதில் பிஸியாக இருக்கும்போது வாழ்க்கை நடக்கிறது.", "பசியுடன் இருங்கள், முட்டாள்தனமாக இருங்கள்.",
    "சிறந்த வேலையைச் செய்வதற்கான ஒரே வழி, நீங்கள் செய்வதை நேசிப்பதாகும்.",
    "நேர்மறையில் கவனம் செலுத்துங்கள், எதிர்மறையை மறந்து விடுங்கள்.", "நீங்கள் சந்திக்கும் அனைவரிடமும் அன்பாக இருங்கள்.",
    "ஒவ்வொரு மேகத்திற்கும் ஒரு வெள்ளி கோடு உள்ளது.", "செயல்கள் வார்த்தைகளை விட சத்தமாக பேசுகின்றன.",
    "தாமதமானாலும் பரவாயில்லை.", "ஆயிரம் மைல் பயணம் ஒரு சிறிய அடியில் தொடங்குகிறது.",
    "தினமும் ஒரு ஆப்பிள் மருத்துவரை விலக்கி வைக்கும்.", "ஒரே மாதிரியான பறவைகள் ஒன்றாகச் சேரும்.",
    "எளிதில் வருவது எளிதில் செல்லும்.", "நேர்மை சிறந்த கொள்கை.", "பணம் மரத்தில் வளருவதில்லை.",
    "வலி இல்லை என்றால் பலன் இல்லை.", "நீங்கள் எதை உபதேசிக்கிறீர்களோ அதையே கடைப்பிடியுங்கள்.",
    "முன்கூட்டியே வருபவர் பலன் பெறுவார்.", "வீட்டைப் போல இடமில்லை.", "உனக்கு என்ன ஆச்சு?",
    "நீங்கள் நலமாக இருக்கிறீர்களா?", "எல்லாம் சரியாக இருக்கிறதா?", "நான் சொல்வது உனக்கு புரிகிறதா?",
    "சரியாகச் சொன்னாய், அதையே தான் நானும் சொல்கிறேன்!", "எனக்கு அதில் உறுதியாக தெரியவில்லை.",
    "நான் உன்னுடன் முழுமையாக உடன்படுகிறேன்.", "அது ஒரு நல்ல கருத்து.", "நான் அதை பற்றி யோசிப்பேன்.",
    "நீங்கள் என்ன முடிவு செய்கிறீர்கள் என்று எனக்குத் தெரியப்படுத்துங்கள்.",
    "இதை பாருங்கள், இது அருமையாக இருக்கிறது!", "நீங்கள் அசத்துகிறீர்கள்!", "முடியவே முடியாது, அது நம்பமுடியாதது.",
    "நாளை காலை நாம் சந்திக்கலாமா?", " உங்கள் குடும்பம் எப்படி இருக்கிறது?", "சமீபத்திய செய்திகள் என்ன?",
    "எங்கள் அடுத்த சந்திப்பை நான் எதிர்பார்த்துக் காத்திருக்கிறேன்.", "எல்லாம் சரியாகிவிடும், என்னை நம்புங்கள்.",
    "உங்களை கவனித்துக்கொள்ளுங்கள்.", "விரைவில் சந்திப்போம்!", "இனிய நாள் அமையட்டும்.",
    "உங்களை சந்தித்ததில் மகிழ்ச்சி.", "எனது திறமைகளை நான் எவ்வாறு மேம்படுத்துவது?"
]

hi_text = [
    "नमस्ते, आप आज कैसे हैं?", "क्या चल रहा है भाई, जीवन कैसा है?", "एनएलपी के लिए यह एक शानदार दिन है।",
    "मैं पायथन के साथ मशीन लर्निंग सीख रहा हूँ।", "क्या आप इस समस्या में मेरी मदद कर सकते हैं?",
    "तेज़ भूरी लोमड़ी आलसी कुत्ते के ऊपर से कूद गई।", "मुझे पिज्जा और बर्गर खाना बहुत पसंद है।",
    "आप छुट्टियों के लिए कहाँ जा रहे हैं?", "चलो पार्क चलते हैं और क्रिकेट खेलते हैं।",
    "आर्टिफिशियल इंटेलिजेंस दुनिया को बदल रहा है।", "आज मैं बहुत खुश महसूस कर रहा हूँ।",
    "फ्रांस की राजधानी क्या है?", "मौसम बहुत अच्छा है, चलो बाहर चलते हैं।",
    "मेरे पास शाम तक खत्म करने के लिए बहुत सारा काम है।", "साझा करना देखभाल करना है, वे कहते हैं।",
    "चिंता मत करो, खुश रहो!", "असफलता सफलता की सीढ़ी है।", "ईमानदारी सबसे अच्छी नीति है।",
    "अभ्यास परिपूर्ण बनाता है।", "ज्ञान ही शक्ति है।", "अरे यार, क्या तुमने कल रात का मैच देखा?",
    "मैं बहुत थक गया हूँ, मुझे कुछ कॉफी चाहिए।", "अपने आप पर विश्वास रखें और आप कुछ भी हासिल कर सकते हैं।",
    "बड़े सपने देखें और कड़ी मेहनत करें।", "जब आप अन्य योजनाएँ बनाने में व्यस्त होते हैं तो जीवन घटित होता है।",
    "भूखे रहो, मूर्ख रहो।", "शानदार काम करने का एकमात्र तरीका यह है कि आप जो करते हैं उसे पसंद करें।",
    "सकारात्मक पर ध्यान दें, नकारात्मक को भूल जाएं।", "आप जिससे भी मिलें उसके प्रति दयालु रहें।",
    "हर बादल में एक आशा की किरण होती है।", "शब्दों से ज़्यादा काम बोलते हैं।", "देर आए दुरुस्त आए।",
    "हजार मील की यात्रा एक कदम से शुरू होती है।", "रोज एक सेब डॉक्टर को दूर रखता है।",
    "एक जैसे लोग एक साथ रहते हैं।", "आसानी से मिला हुआ आसानी से चला जाता है।", "ईमानदारी सबसे अच्छी नीति है।",
    "पैसा पेड़ों पर नहीं उगता।", "बिना कष्ट के फल नहीं मिलता।", "जो उपदेश देते हैं वही करें।",
    "जल्दी आने वाले को फायदा मिलता है।", "घर जैसा कोई स्थान नहीं है।", "तुम्हें क्या हुआ है?", "क्या तुम ठीक हो?",
    "क्या सब कुछ ठीक है?", "क्या तुम समझ रहे हो कि मेरा क्या मतलब है?",
    "बिल्कुल, मैं भी यही कह रहा हूँ!", "मुझे इसके बारे में यकीन नहीं है।", "मैं पूरी तरह से आपसे सहमत हूँ।",
    "यह एक बहुत अच्छा बिंदु है।", "मैं इसके बारे में सोचूँगा।", "मुझे बताएं कि आप क्या निर्णय लेते हैं।",
    "इसे देखो, यह बहुत बढ़िया है!", "तुम बहुत अच्छा कर रहे हो!", "नहीं यार, यह अविश्वसनीय है।",
    "क्या हम कल सुबह मिल सकते हैं?", "आपका परिवार कैसा है?", "ताज़ा ख़बरें क्या हैं?",
    "मैं हमारी अगली मुलाकात का इंतज़ार कर रहा हूँ।", "सब कुछ ठीक हो जाएगा, मुझ पर विश्वास करो।",
    "अपना ख्याल रखें।", "जल्द ही फिर मिलेंगे!", " आपका दिन मंगलमय हो।",
    "आपसे मिलकर खुशी हुई।", "मैं अपने कौशल में सुधार कैसे कर सकता हूँ?"
]

# Ensure precise matching of labels to text
data = {
    "text": en_text + ta_text + hi_text,
    "language": ["English"] * len(en_text) + ["Tamil"] * len(ta_text) + ["Hindi"] * len(hi_text)
}

df = pd.DataFrame(data)

# Character-level TF-IDF (n-grams 1 to 3)
vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(1, 3))

# Logistic Regression Model with balanced weights
model = LogisticRegression(class_weight='balanced', max_iter=1000)

# Training
logger.info(f"Training robust model on {len(df)} samples...")
X = vectorizer.fit_transform(df['text'])
y = df['language']
model.fit(X, y)

# Save the model and vectorizer
logger.info("Saving resources...")
with open('model.pkl', 'wb') as model_file:
    pickle.dump(model, model_file)

with open('vectorizer.pkl', 'wb') as vec_file:
    pickle.dump(vectorizer, vec_file)

logger.info("Training process completed successfully.")
