# AI Destekli Tıbbi Anamnez Uygulaması / AI-Assisted Medical Anamnesis Application

Bu uygulama, hekimlerin ve tıp öğrencilerinin hasta anamnez (öykü) alma sürecini kolaylaştırmak ve geliştirmek için tasarlanmış bir yapay zeka destekli araçtır.

## 🇹🇷 Türkçe

### 📋 Genel Bakış

AI Destekli Tıbbi Anamnez Uygulaması, tıp öğrencileri ve hekimler için tasarlanmış, anamnez alma sürecini interaktif ve dijital hale getiren bir araçtır. Uygulama, çeşitli yapay zeka destekli özellikleriyle etkili ve kapsamlı anamnez alınmasına yardımcı olur.

### ✨ Özellikler

- **İki Dil Desteği**: Türkçe ve İngilizce arayüz seçenekleri
- **Yapay Zeka Destekli Soru Önerileri**: Hasta öyküsüne göre akıllı takip soruları önerileri
- **İlaç Bilgisi Analizi**: Girilen ilaçların etken maddeleri ve grupları hakkında otomatik bilgi sunumu
- **Ön Tanı Önerileri**: Semptom ve öyküye dayalı olası tanı önerileri
- **Tetkik ve Muayene Önerileri**: Kapsamlı fizik muayene odakları ve uygun tetkik önerileri
- **Kapsamlı Sistem Sorgulaması**: Tüm sistemlerin detaylı sorgulanması için yapılandırılmış form
- **Anamnez Rehberi**: Etkili anamnez alma teknikleri ve TUS için püf noktaları
- **Metin Olarak Dışa Aktarma**: Alınan anamnezin kolayca metin dosyası olarak kaydedilmesi

### 🚀 Başlangıç

#### Gereksinimler

- Python 3.7 veya daha yeni bir sürüm
- Streamlit
- OpenAI API anahtarı

#### Kurulum

1. Repository'yi klonlayın:
   ```
   git clone [repository-url]
   cd ai-assisted-medical-anamnesis
   ```

2. Gerekli paketleri yükleyin:
   ```
   pip install -r requirements.txt
   ```

3. Uygulamayı başlatın:
   ```
   streamlit run app.py
   ```

4. Web tarayıcınızda şu adrese gidin: `http://localhost:8501`

### 🔑 API Anahtarı

Bu uygulama, OpenAI API'sini kullanır. Uygulamayı kullanmak için bir OpenAI API anahtarına ihtiyacınız olacaktır. API anahtarınızı [OpenAI API sayfasından](https://platform.openai.com/api-keys) edinebilirsiniz.

### 💡 Nasıl Kullanılır?

1. Sol menüden API anahtarınızı ve kullanmak istediğiniz modeli (GPT-3.5, GPT-4 vb.) girin.
2. Hasta bilgilerini ve şikayetini girin.
3. Hasta öyküsünü girin ve "Soru Önerileri Al" butonuna tıklayarak akıllı takip soruları alın.
4. Hastanın kullandığı ilaçları girin ve "İlaç Bilgilerini Al" butonuna tıklayarak detaylı ilaç bilgilerini görüntüleyin.
5. "Ön Tanı Önerileri Al" butonuna tıklayarak muhtemel tanıları görüntüleyin.
6. "Tetkik ve Muayene Önerileri Al" butonuna tıklayarak önerilen tetkik ve fizik muayene odaklarını alın.
7. Sistem Sorgulaması sekmesinden detaylı sistem sorgulaması yapın.
8. Anamnezi metin dosyası olarak dışa aktarın.

### 🎓 TUS Adayları İçin

Uygulama içinde, TUS sınavında başarılı olmak için gerekli anamnez alma püf noktaları ve tekniklerini içeren bir rehber bulunmaktadır. Bu rehber, sınavda hasta öyküsü ile ilgili sorularda size yardımcı olacaktır.

---

## 🇬🇧 English

### 📋 Overview

The AI-Assisted Medical Anamnesis Application is a tool designed for medical students and physicians, transforming the process of taking patient histories into an interactive and digital experience. The application assists in effective and comprehensive history-taking with various AI-powered features.

### ✨ Features

- **Bilingual Support**: Interface options in both Turkish and English
- **AI-Powered Question Suggestions**: Intelligent follow-up questions based on patient history
- **Medication Information Analysis**: Automatic information about active ingredients and groups of entered medications
- **Diagnostic Suggestions**: Possible diagnoses based on symptoms and history
- **Test and Examination Recommendations**: Comprehensive physical examination focuses and appropriate test suggestions
- **Complete Systems Review**: Structured form for detailed inquiry of all body systems
- **Anamnesis Guide**: Effective history-taking techniques and tips for medical exams
- **Text Export**: Easy saving of the collected anamnesis as a text file

### 🚀 Getting Started

#### Requirements

- Python 3.7 or newer
- Streamlit
- OpenAI API key

#### Installation

1. Clone the repository:
   ```
   git clone [repository-url]
   cd ai-assisted-medical-anamnesis
   ```

2. Install required packages:
   ```
   pip install -r requirements.txt
   ```

3. Start the application:
   ```
   streamlit run app.py
   ```

4. Go to `http://localhost:8501` in your web browser

### 🔑 API Key

This application uses the OpenAI API. You will need an OpenAI API key to use the application. You can obtain your API key from the [OpenAI API page](https://platform.openai.com/api-keys).

### 💡 How to Use?

1. Enter your API key and the model you want to use (GPT-3.5, GPT-4, etc.) in the left menu.
2. Enter patient information and chief complaint.
3. Enter patient history and click the "Get Question Suggestions" button to receive intelligent follow-up questions.
4. Enter the patient's medications and click "Get Medication Info" to view detailed medication information.
5. Click "Get Diagnostic Suggestions" to view possible diagnoses.
6. Click "Get Test Recommendations" to receive recommended tests and physical examination focuses.
7. Use the Systems Review tab for detailed system inquiries.
8. Export the anamnesis as a text file.

### 🎓 For Medical Exam Candidates

The application includes a guide with tips and techniques for taking medical histories that are essential for success in medical exams. This guide will help you with questions related to patient history in exams.
