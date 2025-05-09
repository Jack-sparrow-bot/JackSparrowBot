from Escalating import *
from MainMenuHandling import *
from main import *


available_softwares = [
    "squaretalk" ,"st", "vpn", "forticlient", "outline" , "helpdesk" , "backoffice", "bo" , "hd"
]

async def CheckingSoftware(update : Update , context : ContextTypes.DEFAULT_TYPE):  
        user_message = await ExtractUserMessage(update , context)
        prompt = f""" 
            Analyze this message for me:
            {user_message}
            This message is from a user who said he has a specific issue with some software and he provided the software in his message
            Analyze the message and respond only with one word, which is the software name
        """
        Response = str(await DEEPSEEK_API_CALL(prompt))
        if Response.lower() in available_softwares:
            context.user_data["state"] = GettingInfo
            context.user_data["software"] = Response.lower()
            await Send_Response(update , "provide me with a screenshot please")
        else:
            Response = f"""
                Sorry, I can't help you to solve this issue
                I can help you solve issues with :
                Your VPN , SquareTalk, HelpDesck , BackOffice
                Your process is cancelled, what else can I help you with ?
            """
            Send_Response(update , Response)
            context.user_data["state"] = STATE_MAIN



async def DetectingSoftwareHandler(update : Update , context : ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    Prompt = f"""
            Analyze this message for me:
            {user_message}
            This message is from a user who said he has a specific issue with some software, but didn't specify which one
            You previously asked him to provide you with the software
            Now I need you to analyze this message and respond based on these rules:
            If this message contain the software with the problem, respond only with one word "Detected"
            else If the user refuse to provide you with the software name or he wants to cancell the process, respond with only one word "Cancelled"
            else If the message is an out of context message, (EX: Thank you , how are you ..... anything casual message), then generate a normal response and send it to user, in the end of the response, ask him to provide you with the sofware name
            else if this message doesn't contain the software with the problem, respond only with one word "NotDetected"
            else respond with only one word "NotUnderstandable"
        """
    Bot_Response = await DEEPSEEK_API_CALL(Prompt)

    if Bot_Response == "Detected":
        await CheckingSoftware(update , context)
    elif Bot_Response == "Cancelled":
        await Cancel_Process(Update , context)
    elif Bot_Response == "NotUnderstandable":
        await Send_Response(update, "Your message isn't clear, what software are you having issue with exactly ?")
    elif Bot_Response == "NotDetected":
        await Send_Response(update , "Provide me with the software with the issue please")
        context.user_data["state"] = DetectingSoftware
    else:
        await Send_Response(update , Bot_Response)


async def GettingInfoHandler(update : Update, context : ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        photo_caption = update.message.caption
        if not photo_caption:
            await Send_Response(update, "Your Issue has been escalated, thank you")
            Escalate_Issue(update)
            context.user_data["state"] = STATE_MAIN

    else:
        user_message = update.message.text
        Prompt = f"""
            Analyze this message for me :
            {user_message}
            This is a message for a user who is facing an issue, I previously asked him to provide me with a screenshot for the issue, but instead he sent me a message
            I want you to analyze it and respond as I tell you to,
            If the user wants to cancel the process, or is refusing to provide a screenshot, respond with one word "Cancelled"
            else If the message contains a description of the issue, respont with one word "Description"
            else If the message is an out of context message, (EX: Thank you , how are you ..... anything casual message), then generate a normal response and send it to user, in the end of the response, ask him to provide you with the screenshot
            else respond with only one word "NotUnderstandable"
            """
        Bot_Response = await DEEPSEEK_API_CALL(Prompt)
        if Bot_Response == "Cancelled":
            await Cancel_Process(update, context)
        elif Bot_Response == "Description":
            Response =  "Thank you for providing me with the descripion, can you provide me with a screenshot please"
            await Send_Response(update, Response)
            if "Description" not in context.user_data:
                context.user_data["Description"] = user_message + '\n'
            else:
                context.user_data["Description"] += user_message + '\n'
        elif Bot_Response == "NotUnderstandable":
            Response = "I don't understand, Can you provide me with a screenshot please ?"
            await Send_Response(update , Response)
        else:
            await Send_Response(update , Bot_Response)