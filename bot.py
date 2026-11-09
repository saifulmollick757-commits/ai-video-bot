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
        "Mujhe koi bhi prompt do aur main aapko ByteDance Seedance 2.5 se video banakar dunga!"
    )
    bot.reply_to(message, welcome_text)

@bot.message_handler(func=lambda message: True)
def generate_video(message):
    prompt = message.text
    
    msg = bot.reply_to(message, f"⏳ Aapka prompt receive ho gaya hai:\n'{prompt}'\n\nSeedance 2.5 video generate kar raha hai. Kripya thoda wait karein...")
    
    url = "https://openrouter.ai/api/v1/videos"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    
    # API Payload (Seedance 2.5 model set kiya gaya hai)
    payload = {
        "prompt": prompt,
        "model": "bytedance/seedance-2.5" 
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        
        video_url = data.get("video_url") or data.get("url")
        
        if not video_url and "choices" in data:
            video_url = data["choices"][0]["message"]["content"]

        if video_url and "http" in video_url:
            bot.send_video(message.chat.id, video_url, caption=f"🎥 **Prompt:** {prompt}", parse_mode="Markdown")
            bot.delete_message(message.chat.id, msg.message_id)
        else:
            bot.edit_message_text(f"❌ Video generate nahi ho paya. API Response:\n{data}", chat_id=message.chat.id, message_id=msg.message_id)
            
    except Exception as e:
        bot.edit_message_text(f"❌ Error aagaya: {str(e)}", chat_id=message.chat.id, message_id=msg.message_id)

if __name__ == "__main__":
    print("Bot is running with Seedance 2.5...")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)
