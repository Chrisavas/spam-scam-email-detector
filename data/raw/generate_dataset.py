"""
generate_dataset.py — Δημιουργία synthetic dataset για scam/legit email classification.

Συνδυάζει 4 κατηγορίες scam (Nigerian prince, lottery, romance, investment/crypto)
+ legit/ham emails (επαγγελματικά, προσωπικά, newsletters, κλπ).

Βασισμένο σε γνωστά, δημόσια καταγεγραμμένα patterns scam emails
(τύποι κειμένου ευρέως τεκμηριωμένοι σε security research / FTC / Action Fraud),
όχι αντιγραφή συγκεκριμένου πραγματικού email.
"""

import pandas as pd
import random

random.seed(42)

# ─────────────────────────────────────────────────────────
# SCAM EMAILS — 4 κατηγορίες, πολλαπλές παραλλαγές η καθεμία
# ─────────────────────────────────────────────────────────

nigerian_prince_templates = [
    "Dear Beloved Friend, I am Prince {name} from {country}. My late father left me ${amount} million dollars that I need to transfer out of the country urgently. I need your assistance and bank account to complete this transfer. You will receive 30% of the total sum. This is 100% legitimate and confidential. Please reply with your full name, address and bank details so we can proceed immediately. God bless you, Prince {name}.",
    "Greetings, I am Barrister {name}, lawyer to the late Mr. {country} businessman who died without a will. He left behind ${amount} million dollars in a bank account. I am contacting you because you share the same last name and could be declared next of kin. We can split the funds 50/50 if you assist me. Kindly respond urgently with your personal information.",
    "URGENT BUSINESS PROPOSAL!!! I am Mrs. {name}, widow of the former oil minister of {country}. I have ${amount} MILLION dollars trapped in a bank account due to political instability. I need a trustworthy partner to help me move this money abroad. You will be rewarded with 40% commission. Please keep this STRICTLY CONFIDENTIAL and reply with your bank account number.",
    "Dear Sir/Madam, This letter might come to you as a surprise. I am {name}, an account officer at a bank in {country}. One of our customers died with his family in a plane crash leaving a deposit of ${amount} million dollars unclaimed. I want you to stand as next of kin so we can claim and share this money. Reply urgently for more details.",
]

lottery_templates = [
    "CONGRATULATIONS!!! Your email address has WON ${amount},000 in the International Online Lottery Promotion! To claim your prize, kindly send us your full name, address, phone number and a copy of your ID. Processing fee of $200 is required to release your winnings. Reply IMMEDIATELY as this offer expires in 48 hours!",
    "Dear Winner, We are pleased to inform you that your email was selected as one of the lucky winners in our {amount} Million Dollar Sweepstakes Draw. This is a Microsoft promotional lottery. To claim your prize you must contact our claims agent and provide your personal details and a small administrative fee.",
    "WINNING NOTIFICATION: Your number has been selected to receive a cash prize of ${amount},000.00 USD from the National Lottery Board. Kindly fill out the attached claim form with your bank information so we can transfer your winnings without delay. Congratulations once again!",
    "ATTENTION: This is to inform you that you have won the sum of ${amount},000 GBP in the UK National Lottery International Draw. You were randomly selected through our computer ballot system. Send your details and a verification fee of 150 GBP to claim your prize today!",
]

romance_templates = [
    "My Dearest, I hope this message finds you well. I am a lonely {age} year old widow living alone since my husband passed. I found your profile and felt an instant connection. I would love to get to know you better. I am currently stuck abroad for a business trip and need a little help with my hotel bill, just $300, I will pay you back when I return. You are my only hope.",
    "Hello my love, It has been wonderful talking to you these past weeks. I feel like we have a real connection. Unfortunately I have an emergency, my daughter is sick and I cannot access my funds here in {country}. Could you send $500 through Western Union? I promise to pay you back as soon as I land. I trust you completely, my dear.",
    "My darling, I think about you every day since we started talking. I am a soldier currently deployed and I need help shipping my personal belongings home, it requires a customs fee of $450. Please help me, you are the love of my life and I cannot wait to finally meet you in person.",
]

investment_templates = [
    "Hello Investor, I am reaching out with an exclusive opportunity to DOUBLE YOUR MONEY in just 7 days through our guaranteed crypto trading platform. Our AI algorithm has a 100% success rate. Minimum investment is just $200. Send your Bitcoin wallet details now before this offer closes. Limited spots available!",
    "URGENT INVESTMENT ALERT: Our trading bot generated 500% returns last month for our investors. Join now and start earning passive income immediately! Send your initial deposit via cryptocurrency to begin. Guaranteed profits, zero risk, act fast before the price increases!",
    "Dear Future Millionaire, I am a financial advisor managing a private investment fund with guaranteed returns of 30% monthly. This is a once in a lifetime opportunity reserved for select clients. Wire transfer your investment today and start seeing profits within 48 hours!",
]

names = ["Adebayo", "Johnson", "Williams", "Okafor", "Mbeki", "Hassan", "Ibrahim", "Garcia",
         "Chukwu", "Mensah", "Diallo", "Osei", "Abara", "Khalid", "Suleiman", "Kamau"]
countries = ["Nigeria", "South Africa", "Ghana", "Kenya", "Ivory Coast", "Sierra Leone",
             "Senegal", "Burkina Faso", "Togo", "Benin"]
amounts = ["15", "25", "45", "8", "12", "30", "18", "60", "22", "38", "50", "9", "17", "33"]
ages = ["52", "58", "47", "61", "55", "49", "63", "57"]


def fill_template(template):
    return template.format(
        name=random.choice(names),
        country=random.choice(countries),
        amount=random.choice(amounts),
        age=random.choice(ages),
    )


# ─────────────────────────────────────────────────────────
# LEGIT EMAILS — επαγγελματικά, προσωπικά, newsletters
# ─────────────────────────────────────────────────────────

legit_templates = [
    "Hi {name}, Just confirming our meeting tomorrow at {time}. Let me know if you need to reschedule. Best regards, {sender}",
    "Hello team, Attached is the quarterly report for Q{q}. Please review before Friday's meeting and send any feedback. Thanks, {sender}",
    "Dear {name}, Thank you for your order #{order}. Your package has shipped and should arrive within 3-5 business days. You can track it using the link in your account. Best, Customer Support",
    "Hi {name}, Reminder that your subscription renews on the 1st of next month. No action needed unless you wish to make changes to your plan. Thanks for being a valued customer.",
    "Hey, are we still on for dinner on Saturday? Let me know what time works for you. Looking forward to catching up! - {sender}",
    "Dear Valued Customer, Your monthly statement is now available in your online banking portal. If you have any questions about your transactions, please contact customer service during business hours.",
    "Hi {name}, I wanted to follow up on the proposal I sent last week. Do you have any questions or feedback? Happy to schedule a call if that's easier. Best, {sender}",
    "Hello, this is a reminder that your appointment with Dr. {sender} is scheduled for {time} on Thursday. Please arrive 15 minutes early to complete paperwork. Call us if you need to reschedule.",
    "Hi {name}, Welcome to our newsletter! Here are this week's top stories and updates from the community. Click below to read more and manage your subscription preferences.",
    "Dear {name}, Your application has been received and is currently under review. We will contact you within 5-7 business days with an update. Thank you for your patience.",
    "Hi team, Just a heads up that the server maintenance is scheduled for this weekend between 2-4 AM. Expect brief downtime. Let me know if you have concerns. Thanks, {sender}",
    "Hello {name}, Thanks for reaching out. I checked with the team and we can definitely accommodate your request. I'll send over the updated contract by end of day. Best, {sender}",
    "Hi, just wanted to say thanks again for your help moving last weekend! Let's grab coffee soon to catch up properly. Talk soon, {sender}",
    "Dear Resident, This is a reminder that the building's water will be shut off briefly tomorrow morning for scheduled maintenance between 9-11 AM. We apologize for any inconvenience.",
    "Hi {name}, Your flight confirmation: Departure {time} from Gate 22. Please arrive at the airport at least 2 hours before departure. Safe travels!",
    "Hi {name}, I've attached the meeting notes from today's call. Let me know if I missed anything important. Thanks for joining on short notice! Best, {sender}",
    "Dear {name}, Your library books are due in 3 days. You can renew them online or visit any branch. Thank you for using our library services.",
    "Hi, can you send me the updated spreadsheet when you get a chance? No rush, just want to review it before the standup tomorrow. Thanks! {sender}",
    "Dear {name}, Thank you for attending our webinar last week. As promised, here are the slides and recording link. Let us know if you have questions.",
    "Hi team, Quick reminder that timesheets are due by end of day Friday. Please submit through the portal as usual. Thanks for your cooperation, {sender}",
    "Hello {name}, Your gym membership renewal is coming up next month. Log in to your account to update payment details or manage your plan.",
    "Hi {name}, Happy birthday! Hope you have a wonderful day. Let's celebrate properly this weekend if you're free. Talk soon, {sender}",
    "Dear Parent, This is a reminder that the school will be closed on Monday for the public holiday. Classes resume as normal on Tuesday. Thank you.",
    "Hi {name}, I reviewed the draft you sent and left some comments in the document. Overall looks great, just a few small tweaks needed. Best, {sender}",
]

sender_names = ["John", "Sarah", "Michael", "Emma", "David", "Anna", "Chris", "Maria"]
recipient_names = ["John", "Sarah", "Michael", "Emma", "David", "Anna", "Chris", "Maria", "team"]
times = ["10:00 AM", "2:30 PM", "9:00 AM", "4:00 PM", "11:15 AM", "3:00 PM"]


def fill_legit(template):
    return template.format(
        name=random.choice(recipient_names),
        sender=random.choice(sender_names),
        time=random.choice(times),
        q=random.choice(["1", "2", "3", "4"]),
        order=random.randint(10000, 99999),
    )


# ─────────────────────────────────────────────────────────
# Δημιουργία dataset με πολλαπλασιασμό παραλλαγών
# ─────────────────────────────────────────────────────────

rows = []

# Scam emails (label = 1) — κάθε template παράγει πολλές παραλλαγές
all_scam_templates = (
    nigerian_prince_templates * 18
    + lottery_templates * 18
    + romance_templates * 20
    + investment_templates * 20
)
for t in all_scam_templates:
    rows.append({"text": fill_template(t), "label": 1})

# Legit emails (label = 0)
all_legit_templates = legit_templates * 18
for t in all_legit_templates:
    rows.append({"text": fill_legit(t), "label": 0})

df = pd.DataFrame(rows)
df = df.drop_duplicates(subset="text").reset_index(drop=True)
df = df.sample(frac=1, random_state=42).reset_index(drop=True)  # shuffle

print(f"Σύνολο emails: {len(df)}")
print(f"Scam (1): {(df['label']==1).sum()}")
print(f"Legit (0): {(df['label']==0).sum()}")

df.to_csv("/home/claude/dataset/emails.csv", index=False)
print("\n✓ Αποθηκεύτηκε: emails.csv")
