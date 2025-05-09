from main import *
from datetime import datetime

AvailaleDaysForOption = {
    1 : 20,
    2 : 20,
    3 : 20,
    4 : 20
}
PaidVacation , UnpaidVacation , SickLeave , FamilyReasons = 1 , 2 , 3 , 4
async def NumberOfDays(Start_Date : str, End_Date : str):
    
    Start_Date_Obj = datetime.strptime(Start_Date, "%d/%m/%Y")
    End_Date_Obj = datetime.strptime(End_Date, "%d/%m/%Y")
    Formatted_Start_date = Start_Date_Obj.strftime("%Y-%m-%d")
    Formatted_End_date = End_Date_Obj.strftime("%Y-%m-%d")
    start_date = datetime.strptime(Formatted_Start_date, "%Y-%m-%d")
    end_date = datetime.strptime(Formatted_End_date, "%Y-%m-%d")
    return (end_date - start_date).days

async def HandleVacationDays(update : Update, context: ContextTypes.DEFAULT_TYPE):
    
    user_message = await ExtractUserMessage(update , context)
    prompt = f"""
        Analyze this message for me:
        {user_message}
        this is a message for a user who needs to request a vacation
        assuming that today's date is {date_str}
        analyze this message and check if the user provided the start and end date of the vacation 
        if the user provided the date , respond with this format : DD/MM/YYYY To DD/MM/YYYY where the first one is the start date, and the second one is the end date
        else if the user seems like he wants to cancel the process, or doesn't want to provide the date, respond with one word "Cancelled"
        else if the message is a regular message, in this case:
        {
            "Respond only with one word : NotDetected" if context.user_data["state"] == STATE_MAIN else
            "Generate a response based on the fact that you are a telgram bot assistant and you want to know the date of this user's vacation, and ask from the user to provide you with the date of the vacation"
        }
    """
    Bot_Response = await DEEPSEEK_API_CALL(prompt)
    if Bot_Response == "Cancelled":
        await Cancel_Process(update , context)
    elif Bot_Response[2] == '/':
        Start_Date = Bot_Response[0:10]
        End_Date = Bot_Response[14:]
        
        context.user_data["VacationDate"]["StartDate"] = Start_Date
        context.user_data["VatationDate"]["EndDate"] = End_Date
        context.user_data["VacationDate"]["NumberOfDays"] = NumberOfDays(Start_Date , End_Date)
        
        if not "VacationPurpose" in context.user_data:
            context.user_data["state"] = GettingVacationPurpose
            await ShowAvailableOptions(update)
        else :
            Option = context.user_data["VacationPurpose"]
            if AvailaleDaysForOption[Option] >= context.user_data["VacationDate"]["NumberOfDays"]:
                await Send_Response("Okey , Your Request has been escalated")
                context.user_data["state"] = STATE_MAIN
                del context.user_data["VacationPurpose"]
                del context.user_data["VacationDate"]
            else:                
                await Send_Response(update , "You don't have enough left days for this vacation , Your process is cancelled ?")
                context.user_data["state"] = STATE_MAIN
                del context.user_data["VacationDate"]
                del context.user_data["VacationPurpose"]
    elif Bot_Response == "NotDetected":
        context.user_data["state"] = GettingVacationPurpose
        await ShowAvailableOptions(update)
    else:
        Send_Response(update , Bot_Response)
        


async def ShowAvailableOptions(update : Update):
    await Send_Response("""
        What's the purpose of your Vacation ?
        1.Paid Vacation (20 Days Left)
        2.Unpaid Vacation (20 Days Left)
        3.Sick Leave (20 Days Left)
        4.Family Reasons (20 Days Left)
        0 To cancel the process
    """
    )



async def ChooseVacationOption(update : Update, context : ContextTypes.DEFAULT_TYPE):
    user_message = ExtractUserMessage(update , context)
    prompt = f"""
        Analyze this message for me:
        {user_message}
        This is a message for a user who I asked him this question before :
            What's the purpose of your Vacation ?
            1.Paid Vacation (20 Days Left)
            2.Unpaid Vacation (20 Days Left)
            3.Sick Leave (20 Days Left)
            4.Family Reasons (20 Days Left)
            0 To cancel the process
        I want you to analyze this message and respond with the number of the option
        for example :
            user message : I want a Paid Vacation Please
            your response : "1"
        another example:
            user message : The Third option
            you response : "3"
        if the user want to cancel the process or he refuses to pick the option or he sends 0 simply
        Respond with "0" only
        if the user picked a number or an option out of range, Respond with one word "OutOfRange"
        if the user says something out of context and has nothing to do with these options, Generate a response to be sent to the user directly, and tell him to pick an option
    """
    Bot_Response = await DEEPSEEK_API_CALL(prompt)
    OK = 0
    if Bot_Response == "0":
        await Cancel_Process(update , context)
    elif Bot_Response == "1":
        context.user_data["VacationPurpose"] = PaidVacation , OK = 1
    elif Bot_Response == "2":
        context.user_data["VacationPurpose"] = UnpaidVacation , OK = 1
    elif Bot_Response == "3":
        context.user_data["VacationPurpose"] = SickLeave , OK = 1
    elif Bot_Response == "4":
        context.user_data["VacationPurpose"] = FamilyReasons , OK = 1
    elif Bot_Response == "OutofRange":
        Send_Response(update , "Choose a valid option please")
    else:
        Send_Response(update, Bot_Response)
    if OK :
        if "VacationDate" in context.user_data:
            if AvailaleDaysForOption[context.user_data["VacationPurpose"]] >= context.user_data["VacationDate"]["NumberOfDays"]:
                Send_Response(update , "You're request has been escalated")
                context.user_data["state"] = STATE_MAIN
                del context.user_data["VacationDate"]
                del context.user_data["VacationPurpose"]
                
            else:
                Send_Response(update , "You don't have enough left days for this vacation , Your process is cancelled ?")
                context.user_data["state"] = STATE_MAIN
                del context.user_data["VacationDate"]
                del context.user_data["VacationPurpose"]
        else:
            Response = "Ok , what's the date of your vacation ?"
            Send_Response(update , Response)
            context.user_data["state"] = GettingVacationDays 
    
    