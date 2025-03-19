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
    page_title="AI Destekli Tıbbi Anamnez / AI-Assisted Medical Anamnesis",
    page_icon="🏥",
    layout="wide"
)

# Translations dictionary
translations = {
    "tr": {
        "page_title": "AI Destekli Tıbbi Anamnez",
        "language_selector": "Dil Seçimi",
        "language_tr": "Türkçe",
        "language_en": "İngilizce",
        "api_settings": "AI Model ve API Ayarları",
        "api_key_label": "OpenAI API Anahtarınız",
        "api_key_help": "OpenAI API anahtarınızı girin (sk- ile başlamalıdır)",
        "model_selection": "Model Seçimi",
        "api_usage": "API Kullanımı",
        "api_usage_count": "istek",
        "api_usage_info": "Uygulama Kullanım Rehberi",
        "api_usage_details": [
            "**Yapay Zeka Ne Zaman Devreye Girer?**",
            "1. **Soru Önerileri:** Hasta öyküsünün bir kısmını girdikten sonra \"Soru Önerileri Al\" butonuna tıklayarak hastaya sorulabilecek akıllı takip soruları alabilirsiniz.",
            "2. **İlaç Bilgileri:** Hastanın kullandığı ilaçları girip \"İlaç Bilgilerini Al\" butonuna tıklayarak, ilaçların etken maddeleri ve grupları hakkında detaylı bilgi edinebilirsiniz.",
            "3. **Ön Tanılar:** Hasta şikayeti ve öyküsünü girdikten sonra \"Ön Tanı Önerileri Al\" butonuyla muhtemel tanılar hakkında fikir alabilirsiniz.",
            "4. **Tetkik Önerileri:** \"Tetkik ve Muayene Önerileri Al\" butonu ile vaka için uygun olabilecek tetkik ve fizik muayene odakları önerilerini görüntüleyebilirsiniz."
        ],
        "api_key_link": "**Not:** Bu uygulama için bir OpenAI API anahtarı gereklidir. [OpenAI API sayfasından](https://platform.openai.com/api-keys) edinebilirsiniz.",
        "tab_patient": "Hasta Anamnezi",
        "tab_system": "Sistem Sorgulaması",
        "tab_reference": "Referans",
        "new_patient": "🆕 Yeni Hasta",
        "new_patient_help": "Tüm formu temizleyip yeni hasta için hazırlar",
        "new_patient_success": "Form yeni hasta için hazırlandı!",
        "patient_info": "Hasta Bilgileri",
        "patient_details": "Hasta Detayları",
        "fullname": "Ad Soyad",
        "age": "Yaş",
        "gender": "Cinsiyet",
        "gender_select": "Seçiniz",
        "gender_male": "Erkek",
        "gender_female": "Kadın",
        "height": "Boy (cm)",
        "weight": "Kilo (kg)",
        "profession": "Meslek",
        "chief_complaint": "Hastanın Şikayeti",
        "patient_history": "Hasta Öyküsü",
        "patient_history_input": "Hasta öyküsünü giriniz",
        "medications": "Kullandığı İlaçlar",
        "medications_input": "İlaçları giriniz (virgülle ayırın)",
        "get_medication_info": "İlaç Bilgilerini Al",
        "medication_info_loading": "İlaç bilgileri alınıyor...",
        "medication_info_title": "İlaç Bilgileri:",
        "physical_exam": "Fizik Muayene",
        "vital_signs": "Vital Bulgular",
        "temperature": "Ateş (°C)",
        "pulse": "Nabız (/dk)",
        "blood_pressure": "Kan Basıncı",
        "blood_pressure_sys": "Kan Basıncı - Sistolik",
        "blood_pressure_dia": "Kan Basıncı - Diastolik",
        "physical_exam_details": "Fizik Muayene Detayları",
        "head_neck": "Baş-Boyun",
        "chest": "Göğüs",
        "abdomen": "Karın",
        "extremities": "Ekstremiteler",
        "get_test_recommendations": "Tetkik ve Muayene Önerileri Al",
        "test_recommendations_loading": "Öneriler alınıyor...",
        "test_recommendations_title": "Önerilen Tetkik ve Muayeneler:",
        "diagnosis_notes": "Tanı ve Notlar",
        "get_diagnosis": "Ön Tanı Önerileri Al",
        "diagnosis_loading": "Tanı önerileri alınıyor...",
        "diagnosis_title": "Olası Tanılar:",
        "preliminary_diagnosis": "Ön Tanı",
        "notes_plans": "Notlar ve Planlar",
        "export_text": "Anamnezi Metin Olarak İndir",
        "export_success": "Anamnez dosyası başarıyla oluşturuldu!",
        "download_text": "Anamnezi İndir",
        "ai_suggestions": "AI Önerileri",
        "api_key_warning": "OpenAI API anahtarınızı sol menüden girin.",
        "get_question_suggestions": "Soru Önerileri Al",
        "api_key_required": "API anahtarı gereklidir.",
        "history_required": "Lütfen önce hasta öyküsünü girin.",
        "question_suggestions_loading": "Soru önerileri alınıyor...",
        "suggested_questions": "Sorulması Önerilen Sorular:",
        "suggestions_failed": "Öneriler alınamadı. Lütfen API anahtarınızı kontrol edin.",
        "symptom_guide": "Semptom Rehberi",
        "common_symptoms": "Sık Görülen Semptomlar için Sorular",
        "headache": "Baş ağrısı:",
        "headache_questions": [
            "Ağrının lokalizasyonu?",
            "Ağrının karakteri (zonklayıcı, baskı hissi)?",
            "Ne zaman başladı ve ne kadar sürüyor?",
            "Eşlik eden bulantı, kusma, ışık/ses hassasiyeti?",
            "Tetikleyici faktörler?"
        ],
        "chest_pain": "Göğüs ağrısı:",
        "chest_pain_questions": [
            "Ağrının karakteri (baskı, sıkışma, batma)?",
            "Eforla ilişkisi?",
            "Nefes alıp vermeyle ilişkisi?",
            "Yayılımı (sol kol, çene, sırt)?",
            "Eşlik eden semptomlar (nefes darlığı, terleme)?"
        ],
        "abdominal_pain": "Karın ağrısı:",
        "abdominal_pain_questions": [
            "Ağrının lokalizasyonu ve yayılımı?",
            "Ağrının karakteri (kramp, yanma, keskin)?",
            "Yemekle ilişkisi?",
            "Eşlik eden bulantı, kusma, ishal veya kabızlık?",
            "Ağrıyı azaltan veya arttıran faktörler?"
        ],
        "systems_review": "Sistemlerin Sorgulanması",
        "cv_system": "Kardiyovasküler Sistem",
        "respiratory_system": "Solunum Sistemi",
        "gi_system": "Gastrointestinal Sistem",
        "gu_system": "Genitoüriner Sistem",
        "neuro_system": "Nörolojik Sistem",
        "musculoskeletal_system": "Kas-İskelet Sistemi",
        "endocrine_system": "Endokrin Sistem",
        "psychiatric_assessment": "Psikiyatrik Değerlendirme",
        "symptoms": "Semptomlar",
        "notes": "Notlar",
        "anamnesis_guide": "Anamnez Alma Rehberi",
        "anamnesis_tips": "Etkili Anamnez Alma İpuçları",
        "anamnesis_tips_content": [
            "1. **Açık uçlu sorularla başlayın:** \"Bugün sizi buraya getiren şikayetlerinizi anlatır mısınız?\" gibi.",
            "2. **Semptomları detaylandırın:**",
            "   - **Lokalizasyon:** \"Ağrı tam olarak nerede?\"",
            "   - **Kalite:** \"Ağrıyı nasıl tarif edersiniz? (keskin, künt, yanıcı vb.)\"",
            "   - **Şiddet:** \"1-10 arası bir skalada ağrınızın şiddeti nedir?\"",
            "   - **Zamanlama:** \"Ne zaman başladı? Ne kadar sürüyor? Ne sıklıkta oluyor?\"",
            "   - **Arttıran/Azaltan faktörler:** \"Ağrıyı ne artırıyor veya azaltıyor?\"",
            "   - **İlişkili semptomlar:** \"Başka semptomlarınız var mı?\"",
            "3. **Hastayı yönlendirmekten kaçının:** \"Ağrınız zonklayıcı mı?\" yerine \"Ağrınızı nasıl tarif edersiniz?\"",
            "4. **Önceki tedavileri sorun:** \"Bu şikayet için daha önce herhangi bir tedavi aldınız mı?\"",
            "5. **Aile ve sosyal öyküyü ihmal etmeyin:** Aile hastalık öyküsü, mesleki maruziyetler, alışkanlıklar.",
            "6. **Aktif dinleme yapın:** Göz teması kurun, hastayı dikkatle dinleyin ve uygun zamanlarda özetleyin.",
            "7. **Kırmızı bayrakları kaçırmayın:** Ciddi hastalıkları düşündüren semptomları fark etmek önemlidir."
        ],
        "tus_tips": "TUS için Anamnez Alma Püf Noktaları",
        "tus_tips_content": [
            "- Her sistem sorgulamasını eksiksiz yapın",
            "- Temel şikayetin olası ayırıcı tanılarını aklınızda tutun",
            "- Özel hasta grupları için özel sorular (pediatrik, geriatrik, gebe hastalar)",
            "- Uygun terminoloji kullanımına dikkat edin",
            "- Acil müdahale gerektiren durumları tanıyın"
        ],
        # CV Symptoms
        "cv_symptom_list": ["Göğüs ağrısı", "Çarpıntı", "Nefes darlığı", "Ortopne", "Paroksismal nokturnal dispne", "Ayak bileği ödemi", "Senkop", "Siyanoz"],
        # Respiratory Symptoms
        "resp_symptom_list": ["Öksürük", "Balgam", "Hemoptizi", "Nefes darlığı", "Hırıltılı solunum", "Göğüs ağrısı", "Gece terlemesi"],
        # GI Symptoms
        "gi_symptom_list": ["Karın ağrısı", "Bulantı", "Kusma", "İshal", "Kabızlık", "Rektal kanama", "Melena", "Sarılık", "Dispepsi", "Disfaji", "İştahsızlık", "Kilo kaybı"],
        # GU Symptoms
        "gu_symptom_list": ["Disüri", "Sık idrara çıkma", "Noktüri", "Hematüri", "İdrar inkontinansı", "Menstrüasyon düzensizlikleri", "Disparoni"],
        # Neuro Symptoms
        "neuro_symptom_list": ["Baş ağrısı", "Baş dönmesi", "Senkop", "Konvülziyon", "Parestezi", "Güçsüzlük", "Paralizi", "Tremor", "Hafıza kaybı", "Konuşma bozukluğu"],
        # Musculoskeletal Symptoms
        "musculo_symptom_list": ["Eklem ağrısı", "Kas ağrısı", "Şişlik", "Kızarıklık", "Sertlik", "Hareket kısıtlılığı", "Deformite"],
        # Endocrine Symptoms
        "endo_symptom_list": ["Poliüri", "Polidipsi", "Polifaji", "Kilo kaybı/artışı", "Sıcak/soğuk intoleransı", "Hirsutizm", "Alopesi", "Cilt değişiklikleri"],
        # Psychiatric Symptoms
        "psych_symptom_list": ["Depresif duygudurum", "Anksiyete", "Uykusuzluk", "İştahsızlık", "Panik ataklar", "Fobiler", "Obsesyonlar", "Sanrılar", "Varsanılar"],
    },
    "en": {
        "page_title": "AI-Assisted Medical Anamnesis",
        "language_selector": "Language Selection",
        "language_tr": "Turkish",
        "language_en": "English",
        "api_settings": "AI Model and API Settings",
        "api_key_label": "Your OpenAI API Key",
        "api_key_help": "Enter your OpenAI API key (starts with sk-)",
        "model_selection": "Model Selection",
        "api_usage": "API Usage",
        "api_usage_count": "requests",
        "api_usage_info": "Application Usage Guide",
        "api_usage_details": [
            "**When Does AI Assist You?**",
            "1. **Question Suggestions:** After entering part of the patient history, click the \"Get Question Suggestions\" button to receive intelligent follow-up questions tailored to your patient.",
            "2. **Medication Information:** Enter the patient's medications and click \"Get Medication Info\" to obtain detailed information about active ingredients and drug classifications.",
            "3. **Preliminary Diagnoses:** After entering the patient's complaint and history, click \"Get Diagnostic Suggestions\" to receive possible diagnoses to consider.",
            "4. **Test Recommendations:** Use the \"Get Test Recommendations\" button to view appropriate tests and physical examination focuses for the case."
        ],
        "api_key_link": "**Note:** This application requires an OpenAI API key. You can obtain one from the [OpenAI API page](https://platform.openai.com/api-keys).",
        "tab_patient": "Patient Anamnesis",
        "tab_system": "Systems Review",
        "tab_reference": "Reference",
        "new_patient": "🆕 New Patient",
        "new_patient_help": "Clears the form and prepares it for a new patient",
        "new_patient_success": "Form prepared for a new patient!",
        "patient_info": "Patient Information",
        "patient_details": "Patient Details",
        "fullname": "Full Name",
        "age": "Age",
        "gender": "Gender",
        "gender_select": "Select",
        "gender_male": "Male",
        "gender_female": "Female",
        "height": "Height (cm)",
        "weight": "Weight (kg)",
        "profession": "Occupation",
        "chief_complaint": "Chief Complaint",
        "patient_history": "Patient History",
        "patient_history_input": "Enter patient history",
        "medications": "Current Medications",
        "medications_input": "Enter medications (separate with commas)",
        "get_medication_info": "Get Medication Info",
        "medication_info_loading": "Getting medication information...",
        "medication_info_title": "Medication Information:",
        "physical_exam": "Physical Examination",
        "vital_signs": "Vital Signs",
        "temperature": "Temperature (°C)",
        "pulse": "Pulse (bpm)",
        "blood_pressure": "Blood Pressure",
        "blood_pressure_sys": "Blood Pressure - Systolic",
        "blood_pressure_dia": "Blood Pressure - Diastolic",
        "physical_exam_details": "Physical Examination Details",
        "head_neck": "Head & Neck",
        "chest": "Chest",
        "abdomen": "Abdomen",
        "extremities": "Extremities",
        "get_test_recommendations": "Get Test Recommendations",
        "test_recommendations_loading": "Getting recommendations...",
        "test_recommendations_title": "Recommended Tests and Examinations:",
        "diagnosis_notes": "Diagnosis and Notes",
        "get_diagnosis": "Get Diagnostic Suggestions",
        "diagnosis_loading": "Getting diagnostic suggestions...",
        "diagnosis_title": "Possible Diagnoses:",
        "preliminary_diagnosis": "Preliminary Diagnosis",
        "notes_plans": "Notes and Plans",
        "export_text": "Download Anamnesis as Text",
        "export_success": "Anamnesis file successfully created!",
        "download_text": "Download Anamnesis",
        "ai_suggestions": "AI Suggestions",
        "api_key_warning": "Please enter your OpenAI API key in the left menu.",
        "get_question_suggestions": "Get Question Suggestions",
        "api_key_required": "API key is required.",
        "history_required": "Please enter patient history first.",
        "question_suggestions_loading": "Getting question suggestions...",
        "suggested_questions": "Suggested Questions:",
        "suggestions_failed": "Failed to get suggestions. Please check your API key.",
        "symptom_guide": "Symptom Guide",
        "common_symptoms": "Questions for Common Symptoms",
        "headache": "Headache:",
        "headache_questions": [
            "Location of the pain?",
            "Character of the pain (throbbing, pressure)?",
            "When did it start and how long does it last?",
            "Associated nausea, vomiting, sensitivity to light/sound?",
            "Triggering factors?"
        ],
        "chest_pain": "Chest pain:",
        "chest_pain_questions": [
            "Character of the pain (pressure, tightness, stabbing)?",
            "Relation to exertion?",
            "Relation to breathing?",
            "Radiation (left arm, jaw, back)?",
            "Associated symptoms (shortness of breath, sweating)?"
        ],
        "abdominal_pain": "Abdominal pain:",
        "abdominal_pain_questions": [
            "Location and radiation of the pain?",
            "Character of the pain (cramping, burning, sharp)?",
            "Relation to meals?",
            "Associated nausea, vomiting, diarrhea, or constipation?",
            "Factors that alleviate or exacerbate the pain?"
        ],
        "systems_review": "Systems Review",
        "cv_system": "Cardiovascular System",
        "respiratory_system": "Respiratory System",
        "gi_system": "Gastrointestinal System",
        "gu_system": "Genitourinary System",
        "neuro_system": "Neurological System",
        "musculoskeletal_system": "Musculoskeletal System",
        "endocrine_system": "Endocrine System",
        "psychiatric_assessment": "Psychiatric Assessment",
        "symptoms": "Symptoms",
        "notes": "Notes",
        "anamnesis_guide": "Anamnesis Guide",
        "anamnesis_tips": "Effective History Taking Tips",
        "anamnesis_tips_content": [
            "1. **Start with open-ended questions:** Like \"What brought you here today?\"",
            "2. **Detail the symptoms:**",
            "   - **Location:** \"Where exactly is the pain?\"",
            "   - **Quality:** \"How would you describe the pain? (sharp, dull, burning, etc.)\"",
            "   - **Severity:** \"On a scale of 1-10, how severe is your pain?\"",
            "   - **Timing:** \"When did it start? How long does it last? How often does it occur?\"",
            "   - **Aggravating/Alleviating factors:** \"What makes the pain better or worse?\"",
            "   - **Associated symptoms:** \"Do you have any other symptoms?\"",
            "3. **Avoid leading the patient:** Ask \"How would you describe your pain?\" instead of \"Is your pain throbbing?\"",
            "4. **Ask about previous treatments:** \"Have you had any treatment for this complaint before?\"",
            "5. **Don't neglect family and social history:** Family disease history, occupational exposures, habits.",
            "6. **Practice active listening:** Maintain eye contact, listen attentively, and summarize at appropriate times.",
            "7. **Don't miss red flags:** It's important to recognize symptoms that suggest serious illness."
        ],
        "tus_tips": "Medical Exam History Taking Tips",
        "tus_tips_content": [
            "- Complete each system review thoroughly",
            "- Keep possible differential diagnoses in mind for the chief complaint",
            "- Special questions for special patient groups (pediatric, geriatric, pregnant patients)",
            "- Pay attention to appropriate terminology use",
            "- Recognize conditions requiring emergency intervention"
        ],
        # CV Symptoms
        "cv_symptom_list": ["Chest pain", "Palpitations", "Shortness of breath", "Orthopnea", "Paroxysmal nocturnal dyspnea", "Ankle edema", "Syncope", "Cyanosis"],
        # Respiratory Symptoms
        "resp_symptom_list": ["Cough", "Sputum", "Hemoptysis", "Dyspnea", "Wheezing", "Chest pain", "Night sweats"],
        # GI Symptoms
        "gi_symptom_list": ["Abdominal pain", "Nausea", "Vomiting", "Diarrhea", "Constipation", "Rectal bleeding", "Melena", "Jaundice", "Dyspepsia", "Dysphagia", "Loss of appetite", "Weight loss"],
        # GU Symptoms
        "gu_symptom_list": ["Dysuria", "Frequency", "Nocturia", "Hematuria", "Urinary incontinence", "Menstrual irregularities", "Dyspareunia"],
        # Neuro Symptoms
        "neuro_symptom_list": ["Headache", "Dizziness", "Syncope", "Seizures", "Paresthesia", "Weakness", "Paralysis", "Tremor", "Memory loss", "Speech disorders"],
        # Musculoskeletal Symptoms
        "musculo_symptom_list": ["Joint pain", "Muscle pain", "Swelling", "Redness", "Stiffness", "Limited motion", "Deformity"],
        # Endocrine Symptoms
        "endo_symptom_list": ["Polyuria", "Polydipsia", "Polyphagia", "Weight loss/gain", "Heat/cold intolerance", "Hirsutism", "Alopecia", "Skin changes"],
        # Psychiatric Symptoms
        "psych_symptom_list": ["Depressed mood", "Anxiety", "Insomnia", "Loss of appetite", "Panic attacks", "Phobias", "Obsessions", "Delusions", "Hallucinations"],
    }
}

# Define OpenAI API parameters
API_URL = "https://api.openai.com/v1/chat/completions"

def get_openai_response(prompt, model="gpt-3.5-turbo", max_tokens=500, temperature=0.3, language="tr"):
    """Get response from OpenAI API"""
    
    # Get the user's API key
    api_key = st.session_state.get('api_key', '')
    if not api_key:
        return translations[language]["api_key_required"]
    
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
        
        # Increment API usage counter
        st.session_state.api_call_count += 1
        
        return response.json()["choices"][0]["message"]["content"]
            
    except Exception as e:
        if "401" in str(e):
            return "Invalid API key. Please enter a valid API key."
        elif "429" in str(e):
            return "API rate limit exceeded. Please try again later."
        else:
            return f"API error: {str(e)}"

def get_question_suggestions(patient_history, model="gpt-3.5-turbo", language="tr"):
    """Get question suggestions from AI"""
    
    prompts = {
        "tr": f"""
        Bir uzman hekim olarak, hastanın şu ana kadar anlatılan öyküsünü analiz edin ve takip soruları önerin:
        
        HASTA ÖYKÜSÜ:
        {patient_history}
        
        Bu bilgilere dayanarak, kapsamlı bir anamnez tamamlamak için sorulması gereken 3-5 önemli takip sorusu önerin.
        Yanıtınızı yalnızca soruları içeren bir JSON dizesi olarak biçimlendirin.
        Örneğin: ["Soru 1", "Soru 2", "Soru 3"]
        """,
        "en": f"""
        As a medical expert, analyze the patient's history provided so far and suggest follow-up questions:
        
        PATIENT HISTORY:
        {patient_history}
        
        Based on this information, suggest 3-5 important follow-up questions to complete a comprehensive anamnesis.
        Format your response as a JSON array containing only the questions.
        For example: ["Question 1", "Question 2", "Question 3"]
        """
    }
    
    response_text = get_openai_response(prompts[language], model=model, language=language)
    
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
        return [response_text]  # Return API error message

def get_medication_info(medications, model="gpt-3.5-turbo", language="tr"):
    """Get medication information"""
    if not medications.strip():
        return translations[language]["medications_input"]
    
    prompts = {
        "tr": f"""
        Aşağıdaki ilaçların etken maddelerini ve hangi gruba ait olduğunu liste halinde yaz.
        İlaçlar: {medications}
        
        Yanıtını aşağıdaki formatta hazırla:
        İlaç Adı - Etken Madde - İlaç Grubu
        
        Örneğin:
        Lasix - Furosemid - Diüretik
        Norvasc - Amlodipin - Kalsiyum Kanal Blokörü
        """,
        "en": f"""
        List the active ingredients and drug groups for the following medications.
        Medications: {medications}
        
        Prepare your response in the following format:
        Medication Name - Active Ingredient - Drug Group
        
        For example:
        Lasix - Furosemide - Diuretic
        Norvasc - Amlodipine - Calcium Channel Blocker
        """
    }
    
    return get_openai_response(prompts[language], model=model, language=language)

def get_preliminary_diagnosis(patient_history, chief_complaint, model="gpt-3.5-turbo", language="tr"):
    """Get preliminary diagnosis suggestions based on patient complaints and history"""
    if not patient_history.strip() and not chief_complaint.strip():
        return ""
    
    prompts = {
        "tr": f"""
        Bir hekim olarak, aşağıdaki hasta şikayeti ve öyküsünü analiz et ve olası ön tanıları liste halinde sırala.
        
        ŞİKAYET:
        {chief_complaint}
        
        ÖYKÜ:
        {patient_history}
        
        Yanıtını kısa bir liste olarak ver (5 tanıyı geçme). Sadece tanıları yaz, açıklama yapma.
        """,
        "en": f"""
        As a physician, analyze the following patient complaint and history and list possible preliminary diagnoses.
        
        COMPLAINT:
        {chief_complaint}
        
        HISTORY:
        {patient_history}
        
        Give your answer as a short list (no more than 5 diagnoses). Just list the diagnoses, don't provide explanations.
        """
    }
    
    return get_openai_response(prompts[language], model=model, temperature=0.1, language=language)

def get_recommended_tests(patient_history, chief_complaint, preliminary_diagnosis, model="gpt-3.5-turbo", language="tr"):
    """Get recommended tests and examinations"""
    if not patient_history.strip() and not chief_complaint.strip():
        return ""
    
    prompts = {
        "tr": f"""
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
        """,
        "en": f"""
        As a physician, specify the recommended tests and physical examination focuses based on the following patient information.
        
        COMPLAINT:
        {chief_complaint}
        
        HISTORY:
        {patient_history}
        
        PRELIMINARY DIAGNOSIS:
        {preliminary_diagnosis}
        
        Give your answer in two sections:
        1. Recommended Tests: (as a list)
        2. Physical Examination Focuses: (as a list)
        
        Each list should contain 3-6 items, keep it concise.
        """
    }
    
    return get_openai_response(prompts[language], model=model, language=language)

def create_text_file(form_data, language="tr"):
    """Create anamnesis information as text file"""
    # Create text content
    content = ""
    if language == "tr":
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
    else:
        content = f"""
PATIENT ANAMNESIS FORM
======================

PATIENT INFORMATION
-----------------
Full Name: {form_data.get('name', '')}
Age: {form_data.get('age', '')}
Gender: {form_data.get('gender', '')}
Height (cm): {form_data.get('height', '')}
Weight (kg): {form_data.get('weight', '')}
Occupation: {form_data.get('profession', '')}

CHIEF COMPLAINT
-------------
{form_data.get('chief_complaint', '')}

PATIENT HISTORY
-------------
{form_data.get('patient_history', '')}

CURRENT MEDICATIONS
----------------
{form_data.get('medications', '')}

MEDICATION INFORMATION
-------------------
{form_data.get('medication_info', '')}

VITAL SIGNS
---------
Temperature (°C): {form_data.get('temp', '')}
Pulse (bpm): {form_data.get('pulse', '')}
Blood Pressure (mmHg): {form_data.get('bp_sys', '')}/{form_data.get('bp_dia', '')}

PHYSICAL EXAMINATION
-----------------
Head & Neck: 
{form_data.get('head_neck', '')}

Chest: 
{form_data.get('chest', '')}

Abdomen: 
{form_data.get('abdomen', '')}

Extremities: 
{form_data.get('extremities', '')}

PRELIMINARY DIAGNOSIS
------------------
{form_data.get('diagnosis', '')}

RECOMMENDED TESTS
--------------
{form_data.get('recommended_tests', '')}

NOTES AND PLANS
------------
{form_data.get('notes', '')}
"""
    
    return content

def init_new_patient():
    """Initialize all form fields for a new patient"""
    st.session_state.form_data = {
        'name': '',
        'age': 0,
        'gender': 'Seçiniz' if st.session_state.language == 'tr' else 'Select',
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
    # Initialize language
    if 'language' not in st.session_state:
        st.session_state.language = 'tr'
    
    # Initialize API usage counter
    if 'api_call_count' not in st.session_state:
        st.session_state.api_call_count = 0
    
    # Translation shortcut function
    def t(key):
        return translations[st.session_state.language].get(key, key)
    
    # Set page title based on language
    st.title(t("page_title"))
    
    # Sidebar for settings
    st.sidebar.header(t("language_selector"))
    
    # Language selector
    selected_language = st.sidebar.radio(
        "",
        options=["tr", "en"],
        format_func=lambda x: t("language_tr") if x == "tr" else t("language_en"),
        index=0 if st.session_state.language == "tr" else 1
    )
    
    # Update language if changed
    if selected_language != st.session_state.language:
        st.session_state.language = selected_language
        st.rerun()
    
    # AI model and API settings
    st.sidebar.header(t("api_settings"))
    
    # API key input
    api_key = st.sidebar.text_input(
        t("api_key_label"), 
        type="password", 
        help=t("api_key_help")
    )
    
    if api_key:
        st.session_state.api_key = api_key
    
    # Model selection
    model_options = ["gpt-3.5-turbo", "gpt-4", "gpt-4-turbo"]
    default_model = "gpt-3.5-turbo"
    
    selected_model = st.sidebar.selectbox(
        t("model_selection"),
        model_options,
        index=model_options.index(default_model) if default_model in model_options else 0
    )
    
    # API usage statistics
    st.sidebar.markdown(f"**{t('api_usage')}:** {st.session_state.api_call_count} {t('api_usage_count')}")
    
    st.sidebar.markdown("---")
    
    # API usage information
    st.sidebar.markdown(f"### {t('api_usage_info')}")
    for detail in t("api_usage_details"):
        st.sidebar.markdown(f"- {detail}")
    
    st.sidebar.markdown(t("api_key_link"))
    
    # Tabs for different sections of the application
    tab1, tab2, tab3 = st.tabs([t("tab_patient"), t("tab_system"), t("tab_reference")])

    with tab1:
        # New patient button - fixed at the top
        if st.button(t("new_patient"), type="primary", help=t("new_patient_help")):
            init_new_patient()
            st.success(t("new_patient_success"))
        
        # Initialize form data in session state if not exists
        if 'form_data' not in st.session_state:
            init_new_patient()
        
        col1, col2 = st.columns([3, 2])
        
        with col1:
            st.subheader(t("patient_info"))
            
            # Patient basic info
            with st.expander(t("patient_details"), expanded=True):
                col_a, col_b = st.columns(2)
                with col_a:
                    st.session_state.form_data['name'] = st.text_input(t("fullname"), value=st.session_state.form_data['name'])
                    st.session_state.form_data['age'] = st.number_input(t("age"), min_value=0, max_value=120, value=st.session_state.form_data['age'])
                    gender_options = [t("gender_select"), t("gender_male"), t("gender_female")]
                    gender_index = 0
                    if st.session_state.form_data['gender'] in gender_options:
                        gender_index = gender_options.index(st.session_state.form_data['gender'])
                    elif st.session_state.form_data['gender'] == "Seçiniz":
                        gender_index = 0
                    elif st.session_state.form_data['gender'] == "Erkek":
                        gender_index = 1
                    elif st.session_state.form_data['gender'] == "Kadın":
                        gender_index = 2
                    elif st.session_state.form_data['gender'] == "Select":
                        gender_index = 0
                    elif st.session_state.form_data['gender'] == "Male":
                        gender_index = 1
                    elif st.session_state.form_data['gender'] == "Female":
                        gender_index = 2
                    
                    st.session_state.form_data['gender'] = st.selectbox(t("gender"), gender_options, index=gender_index)
                with col_b:
                    st.session_state.form_data['height'] = st.number_input(t("height"), min_value=0, max_value=250, value=st.session_state.form_data['height'])
                    st.session_state.form_data['weight'] = st.number_input(t("weight"), min_value=0, max_value=500, value=st.session_state.form_data['weight'])
                    st.session_state.form_data['profession'] = st.text_input(t("profession"), value=st.session_state.form_data['profession'])
            
            # Chief complaint and patient history
            st.session_state.form_data['chief_complaint'] = st.text_area(t("chief_complaint"), value=st.session_state.form_data['chief_complaint'], height=100)
            
            # Patient history
            st.subheader(t("patient_history"))
            st.session_state.form_data['patient_history'] = st.text_area(t("patient_history_input"), value=st.session_state.form_data['patient_history'], height=250)
            
            # Medications with AI support
            st.subheader(t("medications"))
            st.session_state.form_data['medications'] = st.text_area(t("medications_input"), value=st.session_state.form_data['medications'], height=100)
            
            if st.button(t("get_medication_info")):
                with st.spinner(t("medication_info_loading")):
                    st.session_state.form_data['medication_info'] = get_medication_info(
                        st.session_state.form_data['medications'], 
                        model=selected_model,
                        language=st.session_state.language
                    )
            
            if st.session_state.form_data['medication_info']:
                st.markdown(f"### {t('medication_info_title')}")
                st.text(st.session_state.form_data['medication_info'])
            
            # Physical examination section
            st.subheader(t("physical_exam"))
            
            with st.expander(t("vital_signs"), expanded=True):
                col_c, col_d, col_e = st.columns(3)
                with col_c:
                    st.session_state.form_data['temp'] = st.number_input(t("temperature"), min_value=30.0, max_value=45.0, value=st.session_state.form_data['temp'], step=0.1, format="%.1f")
                with col_d:
                    st.session_state.form_data['pulse'] = st.number_input(t("pulse"), min_value=0, max_value=250, value=st.session_state.form_data['pulse'])
                with col_e:
                    st.session_state.form_data['bp_sys'] = st.number_input(t("blood_pressure_sys"), min_value=0, max_value=300, value=st.session_state.form_data['bp_sys'])
                    st.session_state.form_data['bp_dia'] = st.number_input(t("blood_pressure_dia"), min_value=0, max_value=200, value=st.session_state.form_data['bp_dia'])
            
            with st.expander(t("physical_exam_details")):
                st.session_state.form_data['head_neck'] = st.text_area(t("head_neck"), value=st.session_state.form_data['head_neck'], height=100)
                st.session_state.form_data['chest'] = st.text_area(t("chest"), value=st.session_state.form_data['chest'], height=100)
                st.session_state.form_data['abdomen'] = st.text_area(t("abdomen"), value=st.session_state.form_data['abdomen'], height=100)
                st.session_state.form_data['extremities'] = st.text_area(t("extremities"), value=st.session_state.form_data['extremities'], height=100)
            
            # Get test recommendations
            if st.button(t("get_test_recommendations")):
                with st.spinner(t("test_recommendations_loading")):
                    st.session_state.form_data['recommended_tests'] = get_recommended_tests(
                        st.session_state.form_data['patient_history'],
                        st.session_state.form_data['chief_complaint'],
                        st.session_state.form_data['diagnosis_suggestions'],
                        model=selected_model,
                        language=st.session_state.language
                    )
            
            if st.session_state.form_data['recommended_tests']:
                st.markdown(f"### {t('test_recommendations_title')}")
                st.text(st.session_state.form_data['recommended_tests'])
            
            # Preliminary diagnosis and notes with AI suggestions
            st.subheader(t("diagnosis_notes"))
            
            # Get diagnosis suggestions
            if st.button(t("get_diagnosis")):
                with st.spinner(t("diagnosis_loading")):
                    st.session_state.form_data['diagnosis_suggestions'] = get_preliminary_diagnosis(
                        st.session_state.form_data['patient_history'],
                        st.session_state.form_data['chief_complaint'],
                        model=selected_model,
                        language=st.session_state.language
                    )
            
            if st.session_state.form_data['diagnosis_suggestions']:
                st.markdown(f"### {t('diagnosis_title')}")
                st.text(st.session_state.form_data['diagnosis_suggestions'])
            
            st.session_state.form_data['diagnosis'] = st.text_area(
                t("preliminary_diagnosis"), 
                value=st.session_state.form_data['diagnosis'], 
                height=100,
                placeholder=st.session_state.form_data['diagnosis_suggestions']
            )
            
            st.session_state.form_data['notes'] = st.text_area(t("notes_plans"), value=st.session_state.form_data['notes'], height=100)
            
            # Export Text button
            if st.button(t("export_text"), type="primary"):
                text_content = create_text_file(st.session_state.form_data, language=st.session_state.language)
                
                # Prepare text content for direct download
                b64 = base64.b64encode(text_content.encode('utf-8')).decode()
                download_prefix = "hasta_anamnez" if st.session_state.language == "tr" else "patient_anamnesis"
                download_name = f"{download_prefix}_{st.session_state.form_data['name'].strip().replace(' ', '_')}.txt" if st.session_state.form_data['name'].strip() else f"{download_prefix}.txt"
                href = f'<a href="data:file/txt;base64,{b64}" download="{download_name}">{t("download_text")}</a>'
                st.markdown(href, unsafe_allow_html=True)
                st.success(t("export_success"))
            
        with col2:
            st.subheader(t("ai_suggestions"))
            
            # Add explanatory text about AI suggestions
            if st.session_state.language == "tr":
                st.markdown("""
                💡 **Nasıl Kullanılır:** Hasta öyküsünün bir kısmını girdikten sonra, 
                "Soru Önerileri Al" butonuna tıklayarak bu hastaya özel sorulması 
                gereken ek soruları öğrenebilirsiniz. Bu, önemli detayları 
                atlamanızı önleyecek ve daha kapsamlı bir anamnez almanıza yardımcı olacaktır.
                """)
            else:
                st.markdown("""
                💡 **How to Use:** After entering part of the patient history, 
                you can click on the "Get Question Suggestions" button to receive 
                tailored follow-up questions specific to this patient. This will help 
                you avoid missing important details and collect a more comprehensive history.
                """)
            
            # Check API key
            if not st.session_state.get('api_key', ''):
                st.warning(t("api_key_warning"))
            
            # Button to get question suggestions
            if st.button(t("get_question_suggestions")):
                if not st.session_state.get('api_key', ''):
                    st.error(t("api_key_required"))
                elif not st.session_state.form_data['patient_history'].strip():
                    st.warning(t("history_required"))
                else:
                    with st.spinner(t("question_suggestions_loading")):
                        suggestions = get_question_suggestions(
                            st.session_state.form_data['patient_history'], 
                            model=selected_model,
                            language=st.session_state.language
                        )
                    
                    if isinstance(suggestions, list) and len(suggestions) > 0:
                        st.markdown(f"### {t('suggested_questions')}")
                        for i, suggestion in enumerate(suggestions, 1):
                            st.info(f"{i}. {suggestion}")
                    else:
                        st.error(t("suggestions_failed"))
            
            # Reference section for common symptoms
            with st.expander(t("symptom_guide"), expanded=False):
                st.markdown(f"### {t('common_symptoms')}")
                
                st.markdown(f"**{t('headache')}**")
                for q in t("headache_questions"):
                    st.markdown(f"- {q}")
                
                st.markdown(f"**{t('chest_pain')}**")
                for q in t("chest_pain_questions"):
                    st.markdown(f"- {q}")
                
                st.markdown(f"**{t('abdominal_pain')}**")
                for q in t("abdominal_pain_questions"):
                    st.markdown(f"- {q}")

    with tab2:
        st.subheader(t("systems_review"))
        
        col_sys1, col_sys2 = st.columns(2)
        
        with col_sys1:
            with st.expander(t("cv_system"), expanded=False):
                st.multiselect(
                    t("symptoms"),
                    t("cv_symptom_list"),
                    key="cv_symptoms"
                )
                st.text_area(t("notes"), key="cv_notes")
                
            with st.expander(t("respiratory_system"), expanded=False):
                st.multiselect(
                    t("symptoms"),
                    t("resp_symptom_list"),
                    key="resp_symptoms"
                )
                st.text_area(t("notes"), key="resp_notes")
                
            with st.expander(t("gi_system"), expanded=False):
                st.multiselect(
                    t("symptoms"),
                    t("gi_symptom_list"),
                    key="gi_symptoms"
                )
                st.text_area(t("notes"), key="gi_notes")
            
            with st.expander(t("gu_system"), expanded=False):
                st.multiselect(
                    t("symptoms"),
                    t("gu_symptom_list"),
                    key="gu_symptoms"
                )
                st.text_area(t("notes"), key="gu_notes")
        
        with col_sys2:
            with st.expander(t("neuro_system"), expanded=False):
                st.multiselect(
                    t("symptoms"),
                    t("neuro_symptom_list"),
                    key="neuro_symptoms"
                )
                st.text_area(t("notes"), key="neuro_notes")
            
            with st.expander(t("musculoskeletal_system"), expanded=False):
                st.multiselect(
                    t("symptoms"),
                    t("musculo_symptom_list"),
                    key="musculo_symptoms"
                )
                st.text_area(t("notes"), key="musculo_notes")
            
            with st.expander(t("endocrine_system"), expanded=False):
                st.multiselect(
                    t("symptoms"),
                    t("endo_symptom_list"),
                    key="endo_symptoms"
                )
                st.text_area(t("notes"), key="endo_notes")
                
            with st.expander(t("psychiatric_assessment"), expanded=False):
                st.multiselect(
                    t("symptoms"),
                    t("psych_symptom_list"),
                    key="psych_symptoms"
                )
                st.text_area(t("notes"), key="psych_notes")

    with tab3:
        st.subheader(t("anamnesis_guide"))
        st.markdown(f"### {t('anamnesis_tips')}")
        
        for tip in t("anamnesis_tips_content"):
            st.markdown(tip)
        
        st.markdown(f"### {t('tus_tips')}")
        for tip in t("tus_tips_content"):
            st.markdown(tip)

if __name__ == "__main__":
    main()
