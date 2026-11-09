import os
import requests
import telebot
import time

# GitHub secrets se keys uthana
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    welcome_text = (
        "👋 Welcome! Main ek AI Video Generator Bot hu.\n\n"
        "Mujhe koi bhi prompt do (jaise: 'A realistic cinematic shot of a futuristic city at sunset, 4k') "
        "aur main aapko video banakar dunga!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def generate_video(message):
    prompt = message.text
    
    # User ko waiting message bhejna
    msg = bot.reply_to(message, f"⏳ Aapka prompt receive ho gaya hai:\n'{prompt}'\n\nVideo generate ho raha hai, isme 1-2 minute lag sakte hain. Kripya wait karein...")
    
    # OpenRouter API setup
    url = "https://openrouter.ai/api/v1/videos"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
        # API Payload (Prompt bhejna)
    payload = {
        "prompt": prompt,
        "model": "luma/dream-machine" 
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        
        # API se video URL nikalna (JSON response ke hisaab se)
        # Note: OpenRouter ki API response me video url aam taur par 'url' ya 'video_url' key me hota hai.
        video_url = data.get("video_url") or data.get("url")
        
        if not video_url and "choices" in data:
            # Agar text jaisa response aaye jisme link ho
            video_url = data["choices"][0]["message"]["content"]

        if video_url and "http" in video_url:
            bot.send_video(message.chat.id, video_url, caption=f"🎥 **Prompt:** {prompt}", parse_mode="Markdown")
            bot.delete_message(message.chat.id, msg.message_id) # Waiting message delete karna
        else:
            bot.edit_message_text(f"❌ Video generate nahi ho paya. API Response samajh nahi aaya:\n{data}", chat_id=message.chat.id, message_id=msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error aagaya: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)

if __name__ == "__main__":
    print("Bot is running...")
    # Bot ko lagatar chalane ke liye
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
