import joblib
from pathlib import Path
import string

model = 'sentiment_model.pkl'
vectorizer = 'vectorizer.pkl'

for i in Path.cwd().rglob('yorsent/sentiment_model.pkl'):
    if i:
        model_path = i
    else:
        continue
    
for i in Path.cwd().rglob('yorsent/vectorizer.pkl'):
    if i:
        vectorizer_path = i
    else:
        continue

sentiment_model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

# Yoruba Stopwords List
yoruba_stopwords = set([
    "ni", "ati", "sí", "lori", "gbogbo", "sugbon", "pẹlu", "fún", "nitori", "mo", "a",
    "o", "ó", "wọ́n", "mò", "à", "ò", "ẹ̀", "n", "wọn", "kò", "kọ́", "mi", "wa", "yín", "i", "ẹ́", "é", "á", "ú",
    "u", "ọ́", "ọ", "í", "kì", "kìí", "ín", "in", "án", "an", "un", "ún", "ọ́n", "ọn", "tàbí", "ṣùgbọ́n", "wọ̀nyí", "wọ̀nyẹn", "èyí", "ìyẹn",
    "ní", "tí", "ti", "bí", "tilẹ̀", "jẹ́pé", "nígbà", "nígbàtí", "yóò", "máa", "màá", "ń", "náà", "yìí", "kí", "yẹn", "si"
])

positive_words = [i.lower() for i in ["ayọ̀", "ire", "ìbùkún", "àlàáfíà", "gbèjà", "ìdùnnú", "ìlera", "oríire", "dáadáa", "dada",
                  "ìgbádùn", "àjọyọ̀", "àjọ̀dún", "òmìnira", "ìtẹ̀síwájú", "ìrọ̀rùn", "àǹfààní", "làmìlaaka", "ìlọsíwájú",
                  "ìmọrírì", "àṣeyọrí", "ròkè", "pẹ́ẹ́lí", "pèsè", "ìrètí", "Ayọ̀", "Ire", "Adùn", "Ajé", "Ìmọ́lẹ̀", "Ọrọ̀", "Sùúrù", "Ọ̀rẹ́", "Akínkanjú", "Àṣeyọrí",
                  "Òtítọ́", "Ìrẹ̀lẹ̀", "Ìlera", "Itẹríba", "Ìtẹ́lọ́rùn", "Ìdẹ̀ra", "Fẹ́ràn", "Eré", "Àlìkámà",
                  "Tutù", "Ayọ̀", "Àlàáfíà", "Ìbùkún", "Ìfẹ́", "Àṣeyọrí", "Ìyìn", "Ìlera", "Ìdùnú", "Ọlá",
                  "Iṣégun", "Àánú", "Ọ̀rẹ́", "Ìkànsí", "Ìtẹ́lọ́run", "Àtọ́kànwá", "Ẹ̀bùn", "Ìmọ̀lára rere", "Ìtura",
                  "Ìdárayá", "Ìfaradà", "Ayo", "Nifẹ", "Ire", "Àlàáfíà", "Àṣeyọrí", "Ola", "Ireti", "Ìdùnnú",
                  "Ṣíṣe", "Itelorun", "Ibunkun", "Dára", "Yanilenu", "Laṣiri", "Ìgboyà", "Òtítọ", "Ṣé", "Orire",
                  "Ronú", "Gbọn", "Àlàáfíà", "Ayọ̀", "Ìrètí", "Ìfẹ́", "Àṣeyọrí", "Ìfọkànsí", "Òtítọ́", "Ìgbèkẹ̀lé",
                  "Aláàánú", "Oríire", "Ìwà rere", "Ìlera", "Ìbùkún", "Ìgboyà", "Ọpẹ", "Ìṣẹ́gun", "Ìdùnnú",
                  "ìlósìwájú", "Ìpẹ́lẹ́", "Ìmísí", "Ìdùnnú", "Ìfẹ́", "Àlàáfíà", "Ìrètí", "Ìgboyà", "Àṣeyọrí",
                  "Ìlera", "Oore", "Ọ̀rẹ́", "Ìrànlọ́wọ́", "Ìmọ̀", "Ìgbàgbọ́", "Ìtẹ́lọ́rùn", "Ìwà rere", "Ìyìn",
                  "Ìgbórí", "Ìrísí", "Ìfọ̀rọ̀wọ́pọ̀", "Ìtùnú", "Ìṣọ̀rẹ́", "Ayò/ìdùnú", "Èrín", "Àlàáfía", "Orò",
                  "Ïfé", "Àseyorí", "Ìtélórùn", "Ìbùkún", "Ìgbàgbó", "Ìrépò", "Ôòtó", "Ologbón", "Ìfokàbalè",
                  "Rere/dídára", "Ìlera", "Òtímí", "Ìgboyà", "Ìmólè", "Tutù", "Wùrà", "Rere", "Ayò", "Ìyè",
                  "Rere", "Ìtura", "Èrín", "Ìlera", "Ìmólè", "Òré", "Orò", "Olórò", "Sàn", "Adún", "Ìgbádùn",
                  "Òpò", "Ní", "Rewá", "Omo", "Gbón", "Àdúrà"
]]
negative_words = [i.lower() for i in ["ibi", "kú", "ìpọ́njú", "àìbàlẹ̀-ọkàn", "ogun", "ìbànújẹ́", "ikú", "àìní", "àìsàn", "àìlera",
                  "ọ̀fọ̀", "òfò", "ìfòòró", "burú", "burúkú", "rògbòdìyàn", "wàhálà", "ìdààmú", "ìwọ́de", "ìfẹ̀hónúhàn",
                  "ìfàsẹ́yìn", "àìbìkítà", "ẹkún", "ọ̀wọ́ngógó", "ìpèníjà", "èèṣì", "àìrajaja", "léèmọ̀", "ìjìyà", "ẹ̀wọ̀n", "ìṣekúpa",
                  "Ìbànújẹ́", "Ibi", "Ìkorò", "Òkùtà", "Òkùnkùn", "Òsì", "Ìbínú", "Ọ̀tá", "Ọ̀lẹ", "Àṣetì",
                  "Irọ́", "Ìgbéraga", "Àìsàn", "Àrínfín", "Ojúkòkòrò", "Ìnira", "Kórira", "Ìjà", "Èpò", "Gbóná",
                  "Ìbànújẹ́", "Ìbínú", "Ìfarapa", "Ìkà", "Ọ̀tẹ̀", "Ìbànilẹ́nu", "Ìtànjẹ", "Ìfarapa ọkàn", "Iro",
                  "Òtẹ̀lú", "Ofo", "Ekun", "Ẹ̀sùn", "Èṣù", "Òjòburúkú", "Ikorira", "Ìrètíkúrò", "Ìtẹ̀míjù", "Ìkọlà",
                  "Ìfẹ̀kúfẹ̀", "Ìbànújẹ", "Ainife", "Aburu", "AiÀlàáfíà", "Aialaseyori", "Sulola", "Ainireti",
                  "Edun ọkan", "Aisise", "Ainitelorun", "Ainibunkun", "Aidara", "Aiyanilenu", "Ailasisri", "Ainigboya",
                  "Ailotito", "Aisẹ", "Oriibu", "Sotobi", "Aigbon", "bú", "kú", "rírùn", "ìjà", "òfò", "èbi", "àìsàn",
                  "ìkà", "ewú", "dòdò", "òyì", "gbígbóná", "àánú", "ìpòkú", "òṣì", "rò", "òkùnkùn", "dìgbòlugi",
                  "gbígbẹ", "wúwo", "Ìbànújẹ́", "Ìbẹ̀rù", "Ìbínú", "Ìtìjú", "Ìkórìíra", "Ìpọ́njú", "Ìṣòro",
                  "Ìpalára", "Ìfẹ̀gàn", "Ìwà ipá", "Ìparun", "Ìfẹ̀sùnmọ́ni", "Ìṣubú", "Ìkùnà", "Ìbúgbé", "Ìdààmú",
                  "Ìṣekúṣe", "Ìwà àgàgà", "Ìwà ọ̀dà", "Ìfẹ́kúfẹ̀", "Ìbànújé", "Ekú", "Àilera", "Ìsé", "Ìkórira",
                  "Ìkùnà", "Ìfèkúfè", "Ègún", "Iyèméjì", "Ìyapa", "Ètàn", "Òmùgò", "Ìdàmú", "Búburú", "Àisàn",
                  "Èké", "Ìbèrù", "Òkùnkùn", "Gbóná", "Ide", "Ibi", "Ìbànújé", "Ikú", "Búburú", "Ìnira", "Ekún",
                  "Àisàn", "Òkùnkùn", "Òtá", "Òsì", "Tálákà", "Le", "Ìkorò", "Ìyà", "Àiní", "Bùrewà", "Erú",
                  "Gò", "Èpé", "Ìbànújẹ", "Ìbínú", "Ìkà", "Ẹ̀gàn", "Ìfarapa", "Àníyàn", "Ìjà", "Ìṣekúṣe", "Ẹ̀tàn",
                  "Àṣìṣe", "Ìpẹyà", "Ìtẹ́gùn", "Ìṣòro", "Àbùkù", "Ọràn", "Ìfarapa ọpọlọ", "Ìjìyà", "Ẹ̀jọ́",
                  "Ìdènà", "Ìkúnlẹ̀ abẹ́là", "Alaigbonran", "Ibinu", "Ipa", "Ipalara", "Esu", "Esun", "Asise",
                  "Ofo", "Agan", "Aini", "Ise", "Aisan", "Iberu", "Ibanuje", "Inira", "Ika", "Ojukokoro",
                  "Eke", "Ote", "Iya", "Aburú", "Ìkórira", "Wàhálà", "Ìdèra", "Owú", "Ìbínú", "Ìjayà", "Ìsòro",
                  "Ìkùnà", "Èsan", "Àìmòkan", "Ìlara", "Màjèlé", "Ìpónjú", "Èèwò", "Èpè", "Ètàn", "Èsù",
                  "Ìgbéraga", "Àníyàn", "Ibanuje", "Irora", "Itiju", "Iberu", "Idaamu", "Egan", "Ija", "Kabamo",
                  "Ibinu", "Ika", "ifarapa", "Aiseyori", "Abuku", "Ailera", "Ote", "Ifekufe", "Ikorira", "Aibowo",
                  "Buburu", "Okunkun"
]]
neutral_words = [i.lower() for i in ["wa", "ni", "orukọ", "ṣe", "wọn", "pe", "a", "ti", "lati", "si", "gẹgẹ", "bi", "bá", "lati", "de", "le", "wá",
                 "yi", "yìí", "náà", "lẹ́yìn", "kan", "tí", "o", "a", "kì", "nkan", "lọ", "fi", "ṣe", "kó", "tó", "wọlé"]]



def preprocess_text(text):
    """ Converts text to lowercase, removes punctuation, tokenizes words, and filters out Yoruba stopwords. """
    text = text.lower()
    text = text.translate(str.maketrans('', '', string.punctuation))
    tokens = text.split(' ')
    filtered_tokens = [word for word in tokens if word not in yoruba_stopwords]
    return ' '.join(filtered_tokens) 

def hybrid_predict(text):
    """
    Combines the machine learning model prediction with a keyword-based override.
    """
    processed_text = preprocess_text(text)
    text_vec = vectorizer.transform([processed_text])
    model_prediction = sentiment_model.predict(text_vec)[0]

    tokens = processed_text.split()
    pos_count = sum(1 for word in tokens if word in positive_words)
    neg_count = sum(1 for word in tokens if word in negative_words)

    if pos_count >= 1 and neg_count == 0:
        return 1  # Positive
    elif neg_count >= 1 and pos_count == 0:
        return 0  # Negative
    else:
        # Check for neutrality
        neutral_count = sum(1 for word in tokens if word in neutral_words)
        if neutral_count > pos_count + neg_count:
            return 2 # Neutral
        return model_prediction

def app_pred(stream_sent:str):
    ''' 
    Predict sentiment for a given sentence using the hybrid model, mapping numerical output to sentiment labels.
    
    Args:
        stream_sent (str): The input sentence for sentiment analysis.
        
    Returns:
       str: sentiment label: 'Postive' | 'Negative' | 'Neutral' 
    '''
    if not isinstance(stream_sent, str):
        raise TypeError('Input a string!!!')
    
    prediction = hybrid_predict(stream_sent)
    if prediction == 1:
        sentiment_label = "Positive"
    elif prediction == 0:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral"
    return sentiment_label