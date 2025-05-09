from IssueHandling import *
from telegram import Update, Bot
from main import *
import VacationHandler

async def HandleMainMenu(update: Update , context: ContextTypes.DEFAULT_TYPE):
    await Send_Response(update , "Hello")
    user_message = await ExtractUserMessage(update , context)
    Prompt = f"""
        Analyze this message for me :
        {user_message}
        if it's a user who has a problem or issue to fix, Respont Only with one word : "Issue",
        else if the user needs to take a day off, Respont Only with one word : "Vacation",
        else if the user needs to get the results, Respont Only with one word : "Results",
        else :
            generate a response based on the fact that you are a telegram bot assistant who can provide the services as mentioned 
    """
    bot_response = await DEEPSEEK_API_CALL(Prompt)

    if bot_response == "Issue":
        await DetectingSoftwareHandler(update , context)


    elif bot_response == "Vacation":
        await VacationHandler.HandleVacationDays(update , context)
    
    
    elif bot_response == "Results":
        await Send_Response(update , "You're requesting results, this service isn't available yet")
    
    else:
        await Send_Response(update , bot_response)
