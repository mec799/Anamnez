import streamlit as st
import requests
import json
import time
import re
import os
import base64
from io import BytesIO

# Set page configuration
st.set_page_config(
    page_title="AI Destekli Tıbbi Anamnez",
    page_icon="🏥",
    layout="wide"
)

# Define OpenAI API parameters
API_URL = "https://api.openai.com/v1/chat/completions"

def get_openai_response(prompt, model="gpt-3.5-turbo", max_tokens=500, temperature=0.3):
    """Get response from OpenAI API"""
    
    # Kullanıcının API anahtarını kullan
    api_key = st.session_state.get('api_key', '')
    if not api_key:
        return "API anahtarı girilmemiş. Lütfen yan menüden OpenAI API anahtarınızı girin."
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": temperature,
        "max_tokens": max_tokens
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data)
        response.raise_for_status()
        
        # API kullanım sayacını artır
        st.session_state.api_call_count += 1
        
        return response.json()["choices"][0]["message"]["content"]
            
    except Exception as e:
        if "401" in str(e):
            return "API anahtarı geçersiz. Lütfen doğru API anahtarını girin."
        elif "429" in str(e):
            return "API istek limiti aşıldı. Lütfen daha sonra tekrar deneyin."
        else:
            return f"API hatası: {str(e)}"

def get_question_suggestions(patient_history, model="gpt-3.5-turbo"):
    """AI'den soru önerileri al"""
    
    prompt = f"""
    Bir uzman hekim olarak, hastanın şu ana kadar anlatılan öyküsünü analiz edin ve takip soruları önerin:
    
    HASTA ÖYKÜSÜ:
    {patient_history}
    
    Bu bilgilere dayanarak, kapsamlı bir anamnez tamamlamak için sorulması gereken 3-5 önemli takip sorusu önerin.
    Yanıtınızı yalnızca soruları içeren bir JSON dizesi olarak biçimlendirin.
    Örneğin: ["Soru 1", "Soru 2", "Soru 3"]
    """
    
    response_text = get_openai_response(prompt, model=model)
    
    # Try to extract JSON format if possible
    try:
        # Look for brackets that might contain JSON
        json_match = re.search(r'\[.*\]', response_text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        else:
            # Fallback to parsing the whole response
            return json.loads(response_text)
        
    except json.JSONDecodeError:
        # If not proper JSON, try to split by newlines or numbers
        if "1." in response_text and "2." in response_text:
            questions = []
            for line in response_text.split("\n"):
                if re.match(r'^\d+\.', line.strip()):
                    questions.append(re.sub(r'^\d+\.\s*', '', line.strip()))
            return questions[:5]  # Limit to 5 questions
        return [response_text]  # API hatası mesajını döndür

def get_medication_info(medications, model="gpt-3.5-turbo"):
    """İlaç bilgilerini al"""
    if not medications.strip():
        return "İlaç bilgisi girilmedi."
    
    prompt = f"""
    Aşağıdaki ilaçların etken maddelerini ve hangi gruba ait olduğunu liste halinde yaz.
    İlaçlar: {medications}
    
    Yanıtını aşağıdaki formatta hazırla:
    İlaç Adı - Etken Madde - İlaç Grubu
    
    Örneğin:
    Lasix - Furosemid - Diüretik
    Norvasc - Amlodipin - Kalsiyum Kanal Blokörü
    """
    
    return get_openai_response(prompt, model=model)

def get_preliminary_diagnosis(patient_history, chief_complaint, model="gpt-3.5-turbo"):
    """Hastanın şikayetleri ve öyküsüne göre ön tanı önerileri"""
    if not patient_history.strip() and not chief_complaint.strip():
        return ""
    
    prompt = f"""
    Bir hekim olarak, aşağıdaki hasta şikayeti ve öyküsünü analiz et ve olası ön tanıları liste halinde sırala.
    
    ŞİKAYET:
    {chief_complaint}
    
    ÖYKÜ:
    {patient_history}
    
    Yanıtını kısa bir liste olarak ver (5 tanıyı geçme). Sadece tanıları yaz, açıklama yapma.
    """
    
    return get_openai_response(prompt, model=model, temperature=0.1)

def get_recommended_tests(patient_history, chief_complaint, preliminary_diagnosis, model="gpt-3.5-turbo"):
    """Önerilen tetkikler ve muayeneler"""
    if not patient_history.strip() and not chief_complaint.strip():
        return ""
    
    prompt = f"""
    Bir hekim olarak, aşağıdaki hasta bilgilerine dayanarak önerilen tetkikleri ve fizik muayene odaklarını belirt.
    
    ŞİKAYET:
    {chief_complaint}
    
    ÖYKÜ:
    {patient_history}
    
    ÖN TANI:
    {preliminary_diagnosis}
    
    Yanıtını iki bölüm halinde ver:
    1. Önerilen Tetkikler: (liste halinde)
    2. Fizik Muayene Odakları: (liste halinde)
    
    Her listede 3-6 madde olsun, gereğinden fazla uzatma.
    """
    
    return get_openai_response(prompt, model=model)

def create_text_file(form_data):
    """Anamnez bilgilerini metin dosyası olarak oluştur"""
    # Metin içeriğini oluştur
    content = f"""
HASTA ANAMNEZ FORMU
===================

HASTA BİLGİLERİ
--------------
Ad Soyad: {form_data.get('name', '')}
Yaş: {form_data.get('age', '')}
Cinsiyet: {form_data.get('gender', '')}
Boy (cm): {form_data.get('height', '')}
Kilo (kg): {form_data.get('weight', '')}
Meslek: {form_data.get('profession', '')}

ŞİKAYET
-------
{form_data.get('chief_complaint', '')}

HASTA ÖYKÜSÜ
-----------
{form_data.get('patient_history', '')}

KULLANDIĞI İLAÇLAR
----------------
{form_data.get('medications', '')}

İLAÇ BİLGİLERİ
------------
{form_data.get('medication_info', '')}

VİTAL BULGULAR
------------
Ateş (°C): {form_data.get('temp', '')}
Nabız (/dk): {form_data.get('pulse', '')}
Kan Basıncı (mmHg): {form_data.get('bp_sys', '')}/{form_data.get('bp_dia', '')}

FİZİK MUAYENE
-----------
Baş-Boyun: 
{form_data.get('head_neck', '')}

Göğüs: 
{form_data.get('chest', '')}

Karın: 
{form_data.get('abdomen', '')}

Ekstremiteler: 
{form_data.get('extremities', '')}

ÖN TANI
------
{form_data.get('diagnosis', '')}

ÖNERILEN TETKİKLER
----------------
{form_data.get('recommended_tests', '')}

NOTLAR VE PLANLAR
---------------
{form_data.get('notes', '')}
    """
    
    return content

def init_new_patient():
    """Yeni hasta için tüm formu sıfırla"""
    st.session_state.form_data = {
        'name': '',
        'age': 0,
        'gender': 'Seçiniz',
        'height': 0,
        'weight': 0,
        'profession': '',
        'chief_complaint': '',
        'patient_history': '',
        'medications': '',
        'medication_info': '',
        'temp': 36.5,
        'pulse': 0,
        'bp_sys': 120,
        'bp_dia': 80,
        'head_neck': '',
        'chest': '',
        'abdomen': '',
        'extremities': '',
        'diagnosis': '',
        'diagnosis_suggestions': '',
        'recommended_tests': '',
        'notes': ''
    }

def main():
    st.title("AI Destekli Tıbbi Anamnez Aracı")
    
    # API kullanım sayacını başlat
    if 'api_call_count' not in st.session_state:
        st.session_state.api_call_count = 0
    
    # AI model selection ve API ayarları
    st.sidebar.header("AI Model ve API Ayarları")
    
    # API anahtarı girişi
    api_key = st.sidebar.text_input("OpenAI API Anahtarınız", 
                                   type="password", 
                                   help="OpenAI API anahtarınızı girin (sk- ile başlamalıdır)")
    
    if api_key:
        st.session_state.api_key = api_key
    
    # Model seçimi
    model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    default_model = "gpt-3.5-turbo"
    
    selected_model = st.sidebar.selectbox(
        "Model Seçimi",
        model_options,
        index=model_options.index(default_model) if default_model in model_options else 0
    )
    
    # API kullanım istatistikleri
    st.sidebar.markdown(f"**API Kullanımı:** {st.session_state.api_call_count} istek")
    
    st.sidebar.markdown("---")
    
    # API kullanımı hakkında bilgi
    st.sidebar.markdown("""
    ### API Kullanımı Hakkında
    - Bu uygulama OpenAI API'sini kullanır
    - Kendi API anahtarınızı kullanmanız gerekir
    - Her AI istek için bir API çağrısı yapılır
    - OpenAI API ücretlendirmesi modele göre değişir:
      - GPT-3.5-turbo: En ekonomik seçenek
      - GPT-4/GPT-4-turbo: Daha pahalı ama daha yetenekli
    
    API anahtarını [OpenAI API sayfasından](https://platform.openai.com/api-keys) alabilirsiniz.
    """)
    
    # Tabs for different sections of the application
    tab1, tab2, tab3 = st.tabs(["Hasta Anamnezi", "Sistem Sorgulaması", "Referans"])

    with tab1:
        # Yeni hasta butonu - üst barda sabit kalsın
        if st.button("🆕 Yeni Hasta", type="primary", help="Tüm formu temizleyip yeni hasta için hazırlar"):
            init_new_patient()
            st.success("Form yeni hasta için hazırlandı!")
        
        # Initialize form data in session state if not exists
        if 'form_data' not in st.session_state:
            init_new_patient()
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader("Hasta Bilgileri")
            
            # Patient basic info
            with st.expander("Hasta Detayları", expanded=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.session_state.form_data['name'] = st.text_input("Ad Soyad", value=st.session_state.form_data['name'])
                    st.session_state.form_data['age'] = st.number_input("Yaş", min_value=0, max_value=120, value=st.session_state.form_data['age'])
                    st.session_state.form_data['gender'] = st.selectbox("Cinsiyet", ["Seçiniz", "Erkek", "Kadın"], index=["Seçiniz", "Erkek", "Kadın"].index(st.session_state.form_data['gender']))
                with col_b:
                    st.session_state.form_data['height'] = st.number_input("Boy (cm)", min_value=0, max_value=250, value=st.session_state.form_data['height'])
                    st.session_state.form_data['weight'] = st.number_input("Kilo (kg)", min_value=0, max_value=500, value=st.session_state.form_data['weight'])
                    st.session_state.form_data['profession'] = st.text_input("Meslek", value=st.session_state.form_data['profession'])
            
            # Chief complaint and patient history
            st.session_state.form_data['chief_complaint'] = st.text_area("Hastanın Şikayeti", value=st.session_state.form_data['chief_complaint'], height=100)
            
            # Patient history
            st.subheader("Hasta Öyküsü")
            st.session_state.form_data['patient_history'] = st.text_area("Hasta öyküsünü giriniz", value=st.session_state.form_data['patient_history'], height=250)
            
            # Medications with AI support
            st.subheader("Kullandığı İlaçlar")
            st.session_state.form_data['medications'] = st.text_area("İlaçları giriniz (virgülle ayırın)", value=st.session_state.form_data['medications'], height=100)
            
            if st.button("İlaç Bilgilerini Al"):
                with st.spinner("İlaç bilgileri alınıyor..."):
                    st.session_state.form_data['medication_info'] = get_medication_info(st.session_state.form_data['medications'], model=selected_model)
            
            if st.session_state.form_data['medication_info']:
                st.markdown("### İlaç Bilgileri:")
                st.text(st.session_state.form_data['medication_info'])
            
            # Physical examination section
            st.subheader("Fizik Muayene")
            
            with st.expander("Vital Bulgular", expanded=True):
                col_c, col_d, col_e = st.columns(3)
                with col_c:
                    st.session_state.form_data['temp'] = st.number_input("Ateş (°C)", min_value=30.0, max_value=45.0, value=st.session_state.form_data['temp'], step=0.1, format="%.1f")
                with col_d:
                    st.session_state.form_data['pulse'] = st.number_input("Nabız (/dk)", min_value=0, max_value=250, value=st.session_state.form_data['pulse'])
                with col_e:
                    st.session_state.form_data['bp_sys'] = st.number_input("Kan Basıncı - Sistolik", min_value=0, max_value=300, value=st.session_state.form_data['bp_sys'])
                    st.session_state.form_data['bp_dia'] = st.number_input("Kan Basıncı - Diastolik", min_value=0, max_value=200, value=st.session_state.form_data['bp_dia'])
            
            with st.expander("Fizik Muayene Detayları"):
                st.session_state.form_data['head_neck'] = st.text_area("Baş-Boyun", value=st.session_state.form_data['head_neck'], height=100)
                st.session_state.form_data['chest'] = st.text_area("Göğüs", value=st.session_state.form_data['chest'], height=100)
                st.session_state.form_data['abdomen'] = st.text_area("Karın", value=st.session_state.form_data['abdomen'], height=100)
                st.session_state.form_data['extremities'] = st.text_area("Ekstremiteler", value=st.session_state.form_data['extremities'], height=100)
            
            # Get test recommendations
            if st.button("Tetkik ve Muayene Önerileri Al"):
                with st.spinner("Öneriler alınıyor..."):
                    st.session_state.form_data['recommended_tests'] = get_recommended_tests(
                        st.session_state.form_data['patient_history'],
                        st.session_state.form_data['chief_complaint'],
                        st.session_state.form_data['diagnosis_suggestions'],
                        model=selected_model
                    )
            
            if st.session_state.form_data['recommended_tests']:
                st.markdown("### Önerilen Tetkik ve Muayeneler:")
                st.text(st.session_state.form_data['recommended_tests'])
            
            # Preliminary diagnosis and notes with AI suggestions
            st.subheader("Tanı ve Notlar")
            
            # Get diagnosis suggestions
            if st.button("Ön Tanı Önerileri Al"):
                with st.spinner("Tanı önerileri alınıyor..."):
                    st.session_state.form_data['diagnosis_suggestions'] = get_preliminary_diagnosis(
                        st.session_state.form_data['patient_history'],
                        st.session_state.form_data['chief_complaint'],
                        model=selected_model
                    )
            
            if st.session_state.form_data['diagnosis_suggestions']:
                st.markdown("### Olası Tanılar:")
                st.text(st.session_state.form_data['diagnosis_suggestions'])
            
            st.session_state.form_data['diagnosis'] = st.text_area("Ön Tanı", 
                                                                  value=st.session_state.form_data['diagnosis'], 
                                                                  height=100,
                                                                  placeholder=st.session_state.form_data['diagnosis_suggestions'])
            
            st.session_state.form_data['notes'] = st.text_area("Notlar ve Planlar", value=st.session_state.form_data['notes'], height=100)
            
            # Export Text button
            if st.button("Anamnezi Metin Olarak İndir", type="primary"):
                text_content = create_text_file(st.session_state.form_data)
                
                # Metin içeriğini doğrudan indirilecek şekilde hazırla
                b64 = base64.b64encode(text_content.encode('utf-8')).decode()
                download_name = f"hasta_anamnez_{st.session_state.form_data['name'].strip().replace(' ', '_')}.txt" if st.session_state.form_data['name'].strip() else "hasta_anamnez.txt"
                href = f'<a href="data:file/txt;base64,{b64}" download="{download_name}">Anamnezi İndir</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success("Anamnez dosyası başarıyla oluşturuldu!")
            
        with col2:
            st.subheader("AI Önerileri")
            
            # API anahtarı kontrol et
            if not st.session_state.get('api_key', ''):
                st.warning("OpenAI API anahtarınızı sol menüden girin.")
            
            # Button to get question suggestions
            if st.button("Soru Önerileri Al"):
                if not st.session_state.get('api_key', ''):
                    st.error("API anahtarı gereklidir.")
                elif not st.session_state.form_data['patient_history'].strip():
                    st.warning("Lütfen önce hasta öyküsünü girin.")
                else:
                    with st.spinner("Soru önerileri alınıyor..."):
                        suggestions = get_question_suggestions(st.session_state.form_data['patient_history'], model=selected_model)
                    
                    if isinstance(suggestions, list) and len(suggestions) > 0:
                        st.markdown("### Sorulması Önerilen Sorular:")
                        for i, suggestion in enumerate(suggestions, 1):
                            st.info(f"{i}. {suggestion}")
                    else:
                        st.error("Öneriler alınamadı. Lütfen API anahtarınızı kontrol edin.")
            
            # Reference section for common symptoms
            with st.expander("Semptom Rehberi", expanded=False):
                st.markdown("""
                ### Sık Görülen Semptomlar için Sorular
                
                **Baş ağrısı:**
                - Ağrının lokalizasyonu?
                - Ağrının karakteri (zonklayıcı, baskı hissi)?
                - Ne zaman başladı ve ne kadar sürüyor?
                - Eşlik eden bulantı, kusma, ışık/ses hassasiyeti?
                - Tetikleyici faktörler?
                
                **Göğüs ağrısı:**
                - Ağrının karakteri (baskı, sıkışma, batma)?
                - Eforla ilişkisi?
                - Nefes alıp vermeyle ilişkisi?
                - Yayılımı (sol kol, çene, sırt)?
                - Eşlik eden semptomlar (nefes darlığı, terleme)?
                
                **Karın ağrısı:**
                - Ağrının lokalizasyonu ve yayılımı?
                - Ağrının karakteri (kramp, yanma, keskin)?
                - Yemekle ilişkisi?
                - Eşlik eden bulantı, kusma, ishal veya kabızlık?
                - Ağrıyı azaltan veya arttıran faktörler?
                """)

    with tab2:
        st.subheader("Sistemlerin Sorgulanması")
        
        col_sys1, col_sys2 = st.columns(2)
        
        with col_sys1:
            with st.expander("Kardiyovasküler Sistem", expanded=False):
                st.multiselect(
                    "Semptomlar",
                    ["Göğüs ağrısı", "Çarpıntı", "Nefes darlığı", "Ortopne", "Paroksismal nokturnal dispne", "Ayak bileği ödemi", "Senkop", "Siyanoz"],
                    key="cv_symptoms"
                )
                st.text_area("Notlar", key="cv_notes")
                
            with st.expander("Solunum Sistemi", expanded=False):
                st.multiselect(
                    "Semptomlar",
                    ["Öksürük", "Balgam", "Hemoptizi", "Nefes darlığı", "Hırıltılı solunum", "Göğüs ağrısı", "Gece terlemesi"],
                    key="resp_symptoms"
                )
                st.text_area("Notlar", key="resp_notes")
                
            with st.expander("Gastrointestinal Sistem", expanded=False):
                st.multiselect(
                    "Semptomlar",
                    ["Karın ağrısı", "Bulantı", "Kusma", "İshal", "Kabızlık", "Rektal kanama", "Melena", "Sarılık", "Dispepsi", "Disfaji", "İştahsızlık", "Kilo kaybı"],
                    key="gi_symptoms"
                )
                st.text_area("Notlar", key="gi_notes")
            
            with st.expander("Genitoüriner Sistem", expanded=False):
                st.multiselect(
                    "Semptomlar",
                    ["Disüri", "Sık idrara çıkma", "Noktüri", "Hematüri", "İdrar inkontinansı", "Menstrüasyon düzensizlikleri", "Disparoni"],
                    key="gu_symptoms"
                )
                st.text_area("Notlar", key="gu_notes")
        
        with col_sys2:
            with st.expander("Nörolojik Sistem", expanded=False):
                st.multiselect(
                    "Semptomlar",
                    ["Baş ağrısı", "Baş dönmesi", "Senkop", "Konvülziyon", "Parestezi", "Güçsüzlük", "Paralizi", "Tremor", "Hafıza kaybı", "Konuşma bozukluğu"],
                    key="neuro_symptoms"
                )
                st.text_area("Notlar", key="neuro_notes")
            
            with st.expander("Kas-İskelet Sistemi", expanded=False):
                st.multiselect(
                    "Semptomlar",
                    ["Eklem ağrısı", "Kas ağrısı", "Şişlik", "Kızarıklık", "Sertlik", "Hareket kısıtlılığı", "Deformite"],
                    key="musculo_symptoms"
                )
                st.text_area("Notlar", key="musculo_notes")
            
            with st.expander("Endokrin Sistem", expanded=False):
                st.multiselect(
                    "Semptomlar",
                    ["Poliüri", "Polidipsi", "Polifaji", "Kilo kaybı/artışı", "Sıcak/soğuk intoleransı", "Hirsutizm", "Alopesi", "Cilt değişiklikleri"],
                    key="endo_symptoms"
                )
                st.text_area("Notlar", key="endo_notes")
                
            with st.expander("Psikiyatrik Değerlendirme", expanded=False):
                st.multiselect(
                    "Semptomlar",
                    ["Depresif duygudurum", "Anksiyete", "Uykusuzluk", "İştahsızlık", "Panik ataklar", "Fobiler", "Obsesyonlar", "Sanrılar", "Varsanılar"],
                    key="psych_symptoms"
                )
                st.text_area("Notlar", key="psych_notes")

    with tab3:
        st.subheader("Anamnez Alma Rehberi")
        st.markdown("""
        ### Etkili Anamnez Alma İpuçları
        
        1. **Açık uçlu sorularla başlayın:** "Bugün sizi buraya getiren şikayetlerinizi anlatır mısınız?" gibi.
        
        2. **Semptomları detaylandırın:**
           - **Lokalizasyon:** "Ağrı tam olarak nerede?"
           - **Kalite:** "Ağrıyı nasıl tarif edersiniz? (keskin, künt, yanıcı vb.)"
           - **Şiddet:** "1-10 arası bir skalada ağrınızın şiddeti nedir?"
           - **Zamanlama:** "Ne zaman başladı? Ne kadar sürüyor? Ne sıklıkta oluyor?"
           - **Arttıran/Azaltan faktörler:** "Ağrıyı ne artırıyor veya azaltıyor?"
           - **İlişkili semptomlar:** "Başka semptomlarınız var mı?"
        
        3. **Hastayı yönlendirmekten kaçının:** "Ağrınız zonklayıcı mı?" yerine "Ağrınızı nasıl tarif edersiniz?"
        
        4. **Önceki tedavileri sorun:** "Bu şikayet için daha önce herhangi bir tedavi aldınız mı?"
        
        5. **Aile ve sosyal öyküyü ihmal etmeyin:** Aile hastalık öyküsü, mesleki maruziyetler, alışkanlıklar.
        
        6. **Aktif dinleme yapın:** Göz teması kurun, hastayı dikkatle dinleyin ve uygun zamanlarda özetleyin.
        
        7. **Kırmızı bayrakları kaçırmayın:** Ciddi hastalıkları düşündüren semptomları fark etmek önemlidir.
        
        ### TUS için Anamnez Alma Püf Noktaları
        
        - Her sistem sorgulamasını eksiksiz yapın
        - Temel şikayetin olası ayırıcı tanılarını aklınızda tutun
        - Özel hasta grupları için özel sorular (pediatrik, geriatrik, gebe hastalar)
        - Uygun terminoloji kullanımına dikkat edin
        - Acil müdahale gerektiren durumları tanıyın
        """)

if __name__ == "__main__":
    main()