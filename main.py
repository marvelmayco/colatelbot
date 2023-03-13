import openai
from decouple import config
import telebot
import os


apiKey = config("API_KEY")
token = config("TOKEN")

openai.api_key = apiKey
bot = telebot.TeleBot(token)


@bot.message_handler(commands =  ["start", "help"])
def enviar (message):
    bot.reply_to (message, """
   Hello! Ask what you want.

   By: Ricardo Otero
   http://techislife.es/
    """)
    


@bot.message_handler(commands=[""])

@bot.message_handler(func=lambda message:True)
def run(message):
        
    question= message.text
    mess = message.chat.id
    model_engine = "text-davinci-003"
    prompt = question
    # Generate a response
    completion = openai.Completion.create(
    engine=model_engine,
    prompt=question,
    max_tokens=500,
    n=1,
    stop=None,
    temperature=0.5,
        )
    
    response = completion.choices[0].text
    return bot.send_message(mess, response)

bot.infinity_polling()
