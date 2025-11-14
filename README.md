# 🛒 Treeyaa WhatsApp AI Chatbot

Treeyaa is an AI-powered WhatsApp chatbot that can do grocery ordering.  
Customers can order groceries using **text or voice**
Bot responds like a friendly store salesperson.

---

## Features
 
- **Voice ordering** powered by speech-to-text  
- **Natural text conversations** with AI  
- **Real-time stock checking** (presence & availability)   
- Converses like a store salesperson  
- Outputs every response in **structured JSON**
- Uses tool calling to interact with the store’s stock DB  

---

## 🧠 Tech Stack

### **Backend**
- **Python**
- **FastAPI**

### **AI Models**
- **Speech-to-Text (STT):** Sarvam AI  
- **Text-to-Text (LLM):** Gemini 2.5 Flash  

### **Database**
- **MariaDB** (for product stock, pricing, categories, user conversations etc.)

---

## 🤖 Prompting Strategy

Used multiple prompt engineering approaches:

### **1. Chain-of-thought prompting**
### **2. Few-shot prompting** 
### **3. Tool Calling for Stock Search**
- AI triggers a “stock search tool”  
- Queries the store's database for:
  - item match  
  - availability  
  - selling price  
  - unit & category  
  - quantity validation  
### **4. JSON-formatted Responses**
Every response from the AI is structured as JSON:
- detected items  
- matched SKUs  
- missing items  
- stock availability  
- total price calculations  
- conversation intent flags  
- error handling  

---

## 📌 Example Use Cases

- “Send me 1 kg of rice and 2 oil.”  
- “I need snacks for kids.”  
- Voice message: “Half kg thanga samba rice.”  
- “Do you have multigrain noodles?”  
- “Add poongar rice 2 kg to my order.”  

---
