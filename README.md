# 🛒 About

- WhatsApp chatbot that orders grocery items.  
- Customers can order groceries using **text or voice**

---

## Technical Flow
 
1. Chat history of user - fetched from MariaDB.
2. SarvamAI - converts user voice into text.
3. user query = (chat history + user text)
4. Gemini(text) - responds to user query.
    -> Calls a tool to get stock database.
    -> Finds whether requested grocery items exists and have sufficent stock in database.
    -> If insufficient stock, clarifies with the user telling existing stock details.
    -> Finally creates an order response.
5. (user text + gemini response) - Added to chat history(MariaDB).
6. Stock is reduced in stock database(MariaDB).

- All AI responses are **JSON**

---

## 🧠 Tech Stack

### **Backend**
- **Python**
- **FastAPI**

### **AI Models**
- **Speech-to-Text (STT):** Sarvam AI  
- **Text-to-Text (LLM):** Gemini 2.5 Flash  

### **Database**
- **MariaDB**

---

## 🤖 Prompting Strategy

See prompt.py

---
