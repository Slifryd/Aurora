from datetime import datetime
import os
import subprocess
import sys
import time
import asyncio
# Mettre à jour
subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])

# Liste des librairies à installer
modules_to_install = [
    'discord.py',
    'json',
]


for module in modules_to_install:
    try:
        __import__(module)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", module])
#debut du code
import json
def lire_config_json(fichier):
    with open(fichier, 'r') as f:
        return json.load(f)

config = lire_config_json('config.json')
#---------------------------------------------------


#---------------------------------------------------
import discord
from discord import app_commands
from discord.ext import commands

# Initialisation du bot avec les intents
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# Événement pour synchroniser les slash commands







def save_discord_id(user_id, data, folder="data"):

    if not os.path.exists(folder):
        os.makedirs(folder)
    # Créer un fichier avec l'ID de l'utilisateur comme nom
    file_name = f"{folder}/{user_id}.json"

    # Ouvrir le fichier et y écrire les données
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Fichier {file_name} créé avec succès.")
def new_discord_id(user_id, user_name, coin, worktime=0):
    data = {
        "id": user_id,
        "name": user_name,
        "coin": coin,
        "joined_at": datetime.now().strftime("%Y-%m-%d"),  # Date actuelle
        "work": worktime,

    }
    if os.path.isfile(f"data/{user_id}.json") == False:
        save_discord_id(user_id, data)
def lire_json(user_id, user_name,folder="data"):
    file_path = f"{folder}/{user_id}.json"
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        print(f"Le fichier {file_path} n'existe pas.")
        new_discord_id(user_id, user_name, 0)
        lire_json(user_id, user_name)
        return None

# Fonction pour écrire dans le fichier JSON
def ecrire_json(user_id, data, folder="data"):
    file_path = f"{folder}/{user_id}.json"
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)
    print(f"Fichier {file_path} mis à jour avec succès.")

def modifier_json(user_id, element, valeur, user_name,folder="data"):
    data = lire_json(user_id, user_name,folder)
    if data:
        data[element] = valeur  # Modifier la valeur
        ecrire_json(user_id, data, folder)  # Enregistrer les modifications
    else:
        print(f"Impossible de modifier le fichier, {user_id}.json est introuvable.")


def lecture(element, user_id, user_name):
    file_path = f"data/{user_id}.json"
    if os.path.exists(file_path):
        with open(f"data/{user_id}.json", "r") as f:
            data = json.load(f)
            return(data.get(element))
    else:
        new_discord_id(user_id, user_name, 0)

@bot.event
async def on_ready():
    # Synchronise les commandes slash avec Discord
    await bot.tree.sync()
    print(f"Bot ON : {bot.user}")

# Exemple de commande slash simple
@bot.tree.command(name="helloo", description="Dis bonjour à l'utilisateur")
async def hello(interaction: discord.Interaction):
    user_id, user_name, coin= interaction.user.id, interaction.user.name, 0
    if os.path.isfile(f"data/{user_id}.json") == False:
        new_discord_id(interaction.user.id, interaction.user.name, 0)
    else:
        print("Id déjà enregisté")
    await interaction.response.send_message(f"Bonjour, {interaction.user} !")

# Exemple de commande slash avec des arguments
@bot.tree.command(name="add", description="Additionne deux nombres")
async def add(interaction: discord.Interaction, nombre1: int, nombre2: int):
    resultat = nombre1 + nombre2
    await interaction.response.send_message(f"Le résultat de {nombre1} + {nombre2} est {resultat}")

@bot.tree.command(name="coin", description="Permet de connaître son nombre de pièces")
async def coin(interaction: discord):
    user_id=interaction.user.id
    coin=lecture("coin", user_id)
    await interaction.response.send_message(f"Tu possèdes {coin} pièce(s)")

user_sessions = {}

# Commande pour démarrer une session de travail
@bot.tree.command(name="work", description="Commence une session de travail")
async def work(interaction: discord.Interaction):
    last = 0
    user_id = interaction.user.id
    if user_id in user_sessions and user_sessions[user_id]["active"]:
        await interaction.response.send_message("Tu as déjà une session de travail en cours.")
        return

    user_sessions[user_id] = {"start_time": time.time(), "active": True}
    await interaction.response.send_message("Session de travail commencée !")

    # Démarrer le timer en arrière-plan
    while user_sessions[user_id]["active"]:
        elapsed_time = int(time.time() - user_sessions[user_id]["start_time"])
        minutes, seconds = divmod(elapsed_time, 60)
        hours, minutes = divmod(minutes, 60)
        timer = f'{hours:02d}:{minutes:02d}:{seconds:02d}'
        print(f"Utilisateur {interaction.user.name} - Temps écoulé : {timer}", end="\r")
        await asyncio.sleep(30)
        last +=30# Attend 30 secondes avant d'afficher à nouveau le temps écoulé
        if last == last+60:
            await interaction.response.send_message("Es-tu toujours en train de travaillé ?")



# Commande pour arrêter une session de travail
@bot.tree.command(name="stop_work", description="Arrête la session de travail")
async def stop_work(interaction: discord.Interaction):
    user_id, user_name = interaction.user.id, interaction.user.name
    if user_id not in user_sessions or not user_sessions[user_id]["active"]:
        await interaction.response.send_message("Aucune session de travail en cours.")
        return

    elapsed_time = int(time.time() - user_sessions[user_id]["start_time"])
    minutes, seconds = divmod(elapsed_time, 60)
    hours, minutes = divmod(minutes, 60)
    timer = f'{hours:02d}:{minutes:02d}:{seconds:02d}'

    user_sessions[user_id]["active"] = False  # Arrêter la session
    gain = round(hours+minutes/60, 3)
    modifier_json(user_id, "coin", gain, user_name)
    await interaction.response.send_message(f"Session de travail terminée. Temps total : {timer}. Félicitations : {interaction.user.mention} tu viens de gagner {gain} pièce(s)")

# Démarrage du bot avec le token
bot.run(config.get("token"))
