import telebot
from telebot import types
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

TOKEN = "8019982514:AAFGVa5iPpp__gmh7ksvS43zrJhmYIy3PMU"
bot = telebot.TeleBot(TOKEN)

ADMIN_ID = 6601944801
admin_mode = {}
admin_data = {}
user_sessions = {}

# ASUKA IS GOOD BUT KAWORU DEFINITELY BETTER
art = r"""⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣠⠤⢲⣦⡀⠀⣠⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣀⣀⣀⣠⠖⠚⠓⠒⠒⠲⠿⣍⣛⣻⣦⣷⢠⣻⣀⠤⠤⣀⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⠔⡿⠓⠲⠬⢥⡤⠤⠤⠤⠤⣤⣀⣀⣈⣻⣿⣿⠓⠉⣀⡤⠔⢶⣻⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⣤⢤⠞⠁⣼⠀⠀⠀⠀⠀⠀⠰⠶⢌⣽⡶⠟⢏⡁⢈⣉⣭⣷⡯⣝⠒⢦⣄⠙⠷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⡾⣵⠿⣳⡟⠉⠉⠿⠀⠀⡀⠀⠀⣀⣀⣢⣾⣿⡚⠓⠒⠒⠒⠻⢿⣟⣧⡀⢠⣢⡻⠙⣄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⡀⢿⣟⣲⢿⣷⢀⣤⣠⣄⣈⢿⣷⣤⣷⣻⡓⠒⠻⠭⢷⡄⠒⠲⢶⣦⣬⣻⣏⢦⡈⢿⣆⠘⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⢖⣩⠷⢎⣙⣿⣿⣼⡼⣿⣟⣽⣻⢯⢿⠞⣌⠙⢳⡕⠀⠙⠲⣶⠤⢄⡠⣄⡈⠛⣿⣿⣧⢳⣌⢻⡆⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠰⠗⠉⢀⣾⠟⠒⡿⣫⡿⡾⢫⢟⡏⠉⢸⡀⠑⢾⡆⢤⣻⣶⣤⣘⣲⣿⣶⡽⠿⣯⠲⣌⣇⢹⣷⣿⣆⠸⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠀⠀⡼⠀⣿⢣⣧⠋⣸⠀⣰⢀⣿⣆⠀⠰⣄⠙⣧⣨⣿⣿⣿⣯⣿⣦⠘⣷⡌⢻⡄⠿⣆⠟⣆⢇⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣀⠀⠀⠀⠀⠀⠀⠀⠀⡇⡼⣹⠈⢣⠆⡇⣰⣻⣼⣿⣽⣷⣦⣹⣿⣟⣯⠉⠘⣿⠏⠃⠀⣷⣽⡿⣾⡹⣷⣹⣧⡈⢺⡀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣠⢾⠟⠉⠀⠀⠀⠀⠀⠀⠀⠀⣷⣱⣽⡀⢸⣆⢳⣿⣇⣷⡿⠖⠿⠷⢦⣙⣆⠩⡗⠀⠀⠀⠀⠀⡯⠿⠳⣟⠻⣽⣄⢧⠈⠳⣷⡀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⣸⡇⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣤⣿⣿⣷⣸⣿⡀⣿⣅⠛⠇⠀⠀⠀⠀⢈⠙⠂⠀⠀⠀⠀⠀⣸⣿⠀⢠⣜⢦⠘⢿⣮⣷⡀⠀⠙⢦⡀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢯⣇⠙⢄⣀⠀⠀⠀⢀⣀⡠⣴⣾⣫⠵⠛⣿⣻⠿⣷⣹⣾⣷⡠⡀⠀⠀⠀⠻⠦⠀⣀⠔⠀⠀⣴⣿⣸⣧⡀⠳⣝⠳⢴⡙⢞⣏⠢⡀⠀⠹⡄⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⢀⣀⣀⣈⣻⣤⣀⠈⠉⠻⠿⢿⣺⣿⡵⣶⢶⣦⠀⠘⣿⢷⣾⢿⣿⡋⢙⣮⣄⡀⠀⠀⠉⠈⠀⠀⢀⢞⣿⣼⣿⣿⣿⣆⡀⠙⢦⣝⣮⠛⢷⡙⢆⠀⣷⠀⠀⠀⠀
⠀⠀⠀⢠⡴⢟⣫⠤⠖⠒⠛⢛⣲⣿⣿⣿⠟⠋⢱⣿⣴⣷⣿⣹⢃⣀⣘⠃⢩⢿⣫⣥⣿⠧⢿⣿⣗⡶⣤⣄⣀⣴⣷⣻⣿⣿⠻⠘⣏⠛⢿⣦⣀⠱⢤⣉⡑⠛⠮⢿⣹⠀⠀⠀⠀
⠀⢠⢖⠵⠊⠁⢀⡤⠖⣲⣿⣿⣟⣻⣿⣋⠀⠀⠈⢿⣿⡿⠟⣵⣿⣿⣿⣷⡏⠈⢿⡿⣷⣤⣼⢿⣿⣿⢶⣯⣭⣵⣾⢿⣿⠿⢦⡀⢹⠀⠈⣏⠉⠉⢻⣶⣯⡑⠦⣄⠈⠳⣄⠀⠀
⠀⠹⠁⠀⠀⣞⢁⡾⢽⣯⣝⣛⣛⣯⣭⣽⣿⣷⣶⣤⣤⣴⣿⣿⣿⣿⣿⣿⡀⣀⣼⣀⠈⠙⠛⠷⣾⡿⢿⡟⣿⠟⠁⣈⣥⡴⠾⠷⢾⡄⠀⣿⠀⠀⠈⢇⠘⣿⣤⣀⠑⢦⡘⢧⠀
⠄⠀⠀⠀⠀⠈⠻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡿⢿⡿⠛⣻⢏⡽⣯⡄⠘⣏⣿⡏⠈⠙⠓⠶⣤⣀⠀⠙⢿⣿⡇⢀⡿⠋⠁⠀⢀⣀⣸⡇⠀⣟⣀⠀⠀⠀⠙⠃⣿⡎⠑⣤⡙⣌⡇
⠀⠀⠀⠀⠀⠀⠀⠙⢿⣿⣿⣿⣿⣿⣿⣿⡥⣖⡯⠖⢋⣡⡞⣼⣿⠀⠀⢹⣿⣷⠀⠀⣀⡀⠀⠉⠻⣦⠀⢿⣿⡿⠁⣠⡶⠟⠋⠉⠹⣆⣸⣿⣿⠀⣀⡤⣤⡀⣿⠇⠀⢸⠳⡜⡇
⠀⠀⠀⠀⠀⠀⠀⠀⣈⣿⣿⣿⣿⣿⣿⣏⢿⣗⠒⠊⠉⢸⠁⡿⡏⠀⢀⣿⡿⣁⠤⢶⣿⣽⡆⠀⠀⠘⢷⡈⠉⣡⠾⠋⠀⠀⣠⣆⢠⣿⣿⣿⡟⢀⣷⠒⢺⣧⡏⠀⠀⢸⠀⢹⣹
⠀⠀⠀⠀⠀⠀⡠⢪⠟⡽⠙⢶⣾⣿⣿⣿⣷⡻⣦⡀⠀⠀⢣⣇⡇⢀⡞⣸⠏⠁⠀⠀⡇⢻⡀⠀⠀⣾⣶⡟⣿⣥⡄⠀⠀⢠⣇⣼⡶⣿⣿⠋⣸⣾⣷⣚⣽⡟⠀⠀⠀⣏⠀⡼⣿
⠀⠀⠀⠀⢀⠎⡴⣣⣾⠟⣡⠞⢹⡿⣿⢿⣿⣿⣿⣷⣄⠀⠈⠻⡹⣼⠀⣿⡄⠀⠀⠀⠉⠻⣷⡀⠀⠙⠿⠇⣿⠿⠇⠀⠀⢠⡿⠋⢇⢹⣟⢷⠫⣿⣟⡿⠋⠀⠀⣠⣾⢞⡜⠁⡿
⠀⠀⠀⠀⡼⡼⣵⠏⡏⣰⠃⠀⢾⡇⠈⠻⣿⣮⡉⠹⣿⣧⣄⡀⠙⣇⠀⠸⣿⣄⡀⠀⠀⠀⠈⢉⣧⡴⠀⠠⡄⣀⡤⠤⠴⠋⠁⠀⠈⢻⣿⣾⣤⡿⠋⠀⠀⠀⣉⣽⠿⠋⠀⣰⠃
⠀⠀⠀⠀⣿⣽⠋⠀⡇⡇⠀⠀⠘⣷⢠⣶⢮⣻⣿⣦⠈⠛⠙⠹⣷⠘⢦⣤⣿⣳⣭⣑⣒⣒⣺⣿⢿⣀⣀⣀⣿⣧⣀⣀⣀⡤⠴⠒⣶⣿⣏⣾⡿⠁⠀⠀⠀⠉⠉⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⢻⡏⠀⠀⢳⣇⠀⠀⠀⠈⠈⣿⣾⣿⣿⣮⣿⣦⠀⠀⢿⣶⡫⣿⣿⣿⣿⣿⡹⣯⣊⠁⠉⠉⠉⠉⢙⣮⣷⣶⡤⣤⣶⣿⣿⣟⣾⢿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠸⣿⣦⡀⠀⠙⠦⠀⠀⢀⣼⠿⣽⣿⣯⣷⣼⡷⢾⣻⣾⣿⠞⢿⢻⡷⠻⣿⣏⡙⢝⣻⡾⡖⠒⣻⣿⣿⣿⣿⣿⣿⣿⣿⣿⣿⡟⣎⠣⣀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠈⠁⠀⠀⠀⠀⣴⣋⣉⣩⣿⣿⢿⣟⣷⣾⣯⡟⢱⡇⠀⠘⣿⠣⡀⣈⣻⣿⣿⣿⣷⣷⣶⣿⣿⣟⠋⡿⣹⣿⣿⣿⣿⢟⣏⠺⠿⠶⠭⠷⠂⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⢰⣿⣿⣿⣿⣿⣿⣿⢹⣮⣾⣿⡿⢋⣶⢸⡇⠀⠀⠈⢷⡑⠈⢻⣟⠛⠛⠿⠋⠙⠓⣭⣿⣹⣵⣿⣿⣿⣿⣿⠈⠻⣷⣄⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⠙⢟⣛⡭⠶⢾⡿⠃⠀⠀⢸⢹⣾⣇⠀⠀⠀⠀⠻⣟⣿⡏⠀⠀⠀⠀⢰⣿⣿⢿⡇⣿⣿⣿⣿⣟⡏⠀⠀⠀⠉⠙⠓⠒⠂⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢠⡟⠀⠀⠀⢰⣿⢸⣿⢿⡀⠀⠀⠀⠀⢸⣿⣣⠀⠀⠀⢠⣿⡟⣷⣾⣿⢿⣿⣿⣿⣿⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢀⣿⠁⠀⠀⠀⠘⡿⡿⢿⣏⣧⠀⠀⠀⢀⣾⣿⠿⠀⢀⣴⣿⣿⢿⡹⡇⣿⠈⣿⣿⡟⣾⠇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⡇⠀⠀⠀⠀⢳⢧⠈⢿⣿⠀⠀⢀⣼⣿⠕⠁⣠⣾⡿⣻⠏⠀⢹⣹⣿⣆⣿⣿⣿⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⣾⣿⣷⠀⠀⠀⠀⠈⣏⢧⠀⢻⣧⠶⣋⠿⠋⣀⣾⣟⣿⠞⠁⠀⠀⠀⢯⣿⣿⣿⣿⣿⡏⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣿⣿⣇⠀⠀⠀⠀⠸⡜⣆⠈⢷⣿⠀⢠⣾⣿⠟⢻⡏⠀⠀⠀⠀⠀⠘⣿⣿⠏⣿⣿⠃⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⡻⣿⣿⣦⡀⠀⠀⠀⢧⠘⣆⠈⢷⠒⠛⢻⡿⠄⠘⣧⠀⠀⠀⠀⠀⢰⣷⣹⠀⠙⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣷⣝⣿⣿⣷⣄⠀⠀⠈⢇⠸⡄⠈⣇⠀⠀⢻⣆⠀⠘⣇⠀⠀⣠⣾⣽⢹⡟⠀⢰⣷⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣾⢻⠙⢿⣿⡇⠀⠀⠈⢧⢳⠀⢸⡀⠀⠀⢻⣆⠀⢻⡄⢠⣿⣯⣽⣓⣧⣤⠾⢹⣿⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢸⣿⣼⡇⠀⠙⣿⠀⠀⠀⠈⢏⢧⠀⣇⠀⠀⠀⢻⣆⠀⢷⠘⣿⣮⡻⣿⠁⠀⢀⣯⣿⡄⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢿⣿⣧⡀⠀⠀⠀⠀⠀⠀⠘⡾⡄⢸⠀⠀⠀⠈⢻⣆⠈⢷⣷⣾⣟⣻⣶⣿⡿⠛⢿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⣿⣿⣿⣦⣀⠀⠀⠀⠀⠀⢳⣇⠘⡆⠀⠀⠀⠀⠻⣶⢺⡏⢹⡟⠀⠉⠁⠀⠀⠀⢩⣍⠙⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠸⣟⣿⣿⣿⣧⠀⢀⣤⣤⡸⣸⠀⡇⠀⠀⠀⠀⠀⠙⣿⣷⢡⣿⣶⣄⠀⠀⣄⠀⣦⣍⠙⢳⡀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⡿⢿⡙⠿⠀⢸⡟⢲⣷⡿⡄⢿⠀⠀⠀⠀⠀⠀⠘⣏⢸⣇⣍⢻⣷⣀⢻⣦⣤⣌⡙⣦⡇⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠹⣯⢷⠀⠀⠸⡇⠀⢿⣧⡇⢸⠀⠀⠀⠀⠀⠀⠀⣼⢸⣿⣯⠀⣿⣿⣷⣝⣿⣻⣿⣼⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⣎⣧⠀⠐⣇⠀⠘⣽⣿⡸⡆⠀⠀⠀⠀⠀⠀⠈⠋⠈⠻⣼⣿⢶⢿⣿⣯⡻⣿⣿⣾⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢻⡼⡆⠀⣿⡀⠀⣿⢿⡇⢷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣿⣾⢧⠈⠙⠿⣮⠟⠉⠙⢦⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠈⢿⢻⢠⣿⡇⠀⠹⣄⢳⣜⡆⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢹⡏⠪⠳⢤⣄⣀⠀⠀⠀⠈⢣⠀⠀⠀⠀⠀⠀⠀⠀⠀
⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠘⣎⣿⡟⡇⠀⠀⠈⢻⣿⣷⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⠀⢳⡄⠀⠀⠀⠙⢧⡀⢀⡄⠈⡇⠀⠀⠀⠀⠀⠀⠀⠀"""

# Google Sheets
scope = ["https://spreadsheets.google.com/feeds","https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("telegram_bot/telegrambotproject-488220-a7fc4e6fa52d.json", scope)
client = gspread.authorize(creds)

users_sheet = client.open_by_key("1T6-e0zrmZKHkJ6v3xv_vq0i7hd3jT6K0Cifd4Svy2Zk").sheet1
teams_sheet = client.open_by_key("12_WiTULAvKVcPXOP4bda7FSR3DUGHVHmM2ZEYme418w").sheet1
checkpoints_sheet = client.open_by_key("1kwTDIUrNnpK6xfyktCBORsoG4RPw4ofdKnhTtz4pTfQ").sheet1
teams = [
    "Команда 1", "Команда 2", "Команда 3", "Команда 4",
    "Команда 5", "Команда 6", "Команда 7", "Команда 8"
]


def is_registered(user_id):
    ids = users_sheet.col_values(1)
    return str(user_id) in ids


def get_all_users():
    ids = users_sheet.col_values(1)
    users = []
    for user_id in ids[1:]:
        if user_id:
            users.append(int(user_id))
    return users


def buttons(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Регистрация"))
    markup.add(types.KeyboardButton("Правила"))
    markup.add(types.KeyboardButton("Персонажи"))
    markup.add(types.KeyboardButton("Статистика"))
    markup.add(types.KeyboardButton("Потратить очки заражения"))

    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Меню (админ): /check, /broadcast, /addpoints",
            reply_markup=markup
        )
    else:
        bot.send_message(
            message.chat.id,
            "Меню:",
            reply_markup=markup
        )


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton("Регистрация"))
    markup.add(types.KeyboardButton("Правила"))
    markup.add(types.KeyboardButton("Персонажи"))
    markup.add(types.KeyboardButton("Статистика"))
    markup.add(types.KeyboardButton("Потратить очки заражения"))

    if message.from_user.id == ADMIN_ID:
        bot.send_message(
            message.chat.id,
            "Привет! Команды админа: /check, /broadcast, /addpoints",
            reply_markup=markup
        )
    else:
        bot.send_message(message.chat.id, "Привет!", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Регистрация")
def registration(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(types.KeyboardButton(team))
    bot.send_message(message.chat.id, "Выбери свою команду:", reply_markup=markup)


characters = {
    "Сергей Королёв": (
        "🚀 <b>Сергей Королёв</b>\n"
        "Главный конструктор. Твоя суперсила — превращать хаос в систему.\n"
        "Пассивка: +1 к воле команды, когда всё горит.\n\n"
    ),
    "Андрей Туполев": (
        "✈️ <b>Андрей Туполев</b>\n"
        "Авиаконструктор. Твоя суперсила — надёжность и расчёт.\n"
        "Пассивка: шанс избежать критической ошибки в проекте.\n\n"
    ),
    "Владимир Шухов": (
        "🧠 <b>Владимир Шухов</b>\n"
        "Инженер-новатор. Твоя суперсила — гениальная простота.\n"
        "Пассивка: находишь решение там, где другие видят тупик.\n\n"
    ),
    "Николай Жуковский": (
        "🌬️ <b>Николай Жуковский</b>\n"
        "Основоположник аэродинамики. Твоя суперсила — теория, которая работает.\n"
        "Пассивка: +точность в расчётах и планировании.\n\n"
    ),
    "Игорь Сикорский": (
        "🚁 <b>Игорь Сикорский</b>\n"
        "Пионер авиации. Твоя суперсила — смелые идеи.\n"
        "Пассивка: ускоряешь прогресс команды, но риск выше.\n\n"
    ),
}


@bot.message_handler(func=lambda message: message.text == "Персонажи")
def characters_listing(message):
    if not characters:
        bot.send_message(message.chat.id, "Персонажи пока не добавлены.")
        buttons(message)
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for name in characters.keys():
        markup.add(types.KeyboardButton(name))
    markup.add(types.KeyboardButton("В меню"))
    bot.send_message(message.chat.id, "Выбери персонажа:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text in list(characters.keys()) + ["В меню"])
def send_character_info(message):
    if message.text == "В меню":
        buttons(message)
        return

    bot.send_message(message.chat.id, characters[message.text], parse_mode="HTML")
    buttons(message)


@bot.message_handler(func=lambda message: message.text in teams)
def choose_team(message):
    user = message.from_user

    if is_registered(user.id):
        bot.send_message(
            message.chat.id,
            "Ты уже зарегистрирован!",
            reply_markup=types.ReplyKeyboardRemove()
        )
        buttons(message)
        return

    try:
        users_sheet.append_row([
            user.id,
            user.username if user.username else "нет",
            user.first_name,
            message.text,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ])
        bot.send_message(
            message.chat.id,
            f"✅ Ты зарегистрирован в {message.text}!",
            reply_markup=types.ReplyKeyboardRemove()
        )
        buttons(message)
    except Exception as e:
        bot.send_message(message.chat.id, "⚠️ Ошибка регистрации, попробуй через 5 секунд")
        print("REGISTRATION ERROR:", e)


RULES_TEXT = (
    "🛠️ <b>Бауманское братство — черновые правила</b>\n\n"
    "1) <b>Мы — одна команда.</b> Не мешаем другим, не спамим, не токсичим.\n"
    "2) <b>Инженерная честь.</b> Не используем баги/дыры для нечестной игры.\n"
    "3) <b>Дисциплина.</b> Админские решения по игре — финальные.\n"
    "4) <b>Братство.</b> Помогаем новичкам и не бросаем своих.\n"
    "5) <b>Чекпоинты.</b> Отмечаемся честно, без повторных отметок.\n"
    "6) <b>Заражение.</b> Тратим очки осознанно; игра заканчивается при 0 жизней.\n\n"
    "⚙️ <i>Это заглушка. Ты потом заменишь на нормальный текст.</i>"
)


@bot.message_handler(func=lambda message: message.text == "Правила")
def send_rules(message):
    bot.send_message(message.chat.id, RULES_TEXT, parse_mode="HTML")
    buttons(message)


@bot.message_handler(commands=['broadcast'])
def broadcast_start(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return
    msg = bot.send_message(message.chat.id, "✉️ Введи сообщение для рассылки:")
    bot.register_next_step_handler(msg, send_broadcast)


def send_broadcast(message):
    if message.from_user.id != ADMIN_ID:
        return

    users = get_all_users()
    text = message.text
    sent = 0
    failed = 0

    for user_id in users:
        try:
            bot.send_message(user_id, text)
            sent += 1
        except Exception:
            failed += 1

    bot.send_message(
        message.chat.id,
        f"✅ Рассылка завершена\nОтправлено: {sent}\nНе доставлено: {failed}"
    )


@bot.message_handler(commands=['addpoints'])
def adding(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(types.KeyboardButton(team))

    msg = bot.send_message(message.chat.id, "Выбери команду:", reply_markup=markup)
    bot.register_next_step_handler(msg, select_team_for_points)


def select_team_for_points(message):
    if message.from_user.id != ADMIN_ID:
        return
    if message.text not in teams:
        bot.send_message(message.chat.id, "Выбери команду кнопкой.")
        return

    admin_data[message.from_user.id] = message.text
    msg = bot.send_message(
        message.chat.id,
        "Введи количество очков:",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, enter_points_amount)


def enter_points_amount(message):
    if message.from_user.id != ADMIN_ID:
        return
    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Введи число.")
        return

    points_to_add = int(message.text)
    team_name = admin_data.get(message.from_user.id)

    try:
        cell = teams_sheet.find(team_name, in_column=1)
        row = cell.row

        current = teams_sheet.cell(row, 2).value
        current_points = int(current) if current and str(current).isdigit() else 0
        new_points = current_points + points_to_add

        teams_sheet.update_cell(row, 2, new_points)

        bot.send_message(
            message.chat.id,
            f"Команда <b>{team_name}</b> получила <b>{points_to_add}</b> очков!\n"
            f"Теперь у неё: <b>{new_points}</b> очков",
            parse_mode="HTML"
        )
    except Exception as e:
        print("ADD POINTS ERROR:", e)
        bot.send_message(message.chat.id, "ОШИБКА")


@bot.message_handler(commands=["check"])
def check_start(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "❌ У тебя нет прав.")
        return

    msg = bot.send_message(message.chat.id, "Введи номер чекпоинта (число):")
    bot.register_next_step_handler(msg, check_enter_checkpoint)


def check_enter_checkpoint(message):
    if message.from_user.id != ADMIN_ID:
        return

    if not message.text.isdigit():
        msg = bot.send_message(message.chat.id, "Введи номер чекпоинта ЦИФРОЙ:")
        bot.register_next_step_handler(msg, check_enter_checkpoint)
        return

    checkpoint = int(message.text)
    admin_data[message.from_user.id] = {"checkpoint": checkpoint}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for team in teams:
        markup.add(types.KeyboardButton(team))

    msg = bot.send_message(message.chat.id, "Выбери команду:", reply_markup=markup)
    bot.register_next_step_handler(msg, check_choose_team)


def check_choose_team(message):
    if message.from_user.id != ADMIN_ID:
        return

    if message.text not in teams:
        bot.send_message(message.chat.id, "Выбери команду.")
        return

    team_name = message.text
    checkpoint = admin_data.get(message.from_user.id, {}).get("checkpoint")

    if checkpoint is None:
        bot.send_message(message.chat.id, "Чекпоинт не задан")
        return

    try:
        checkpoint_ids = checkpoints_sheet.col_values(1)
        checkpoint_str = str(checkpoint)

        if checkpoint_str not in checkpoint_ids:
            bot.send_message(
                message.chat.id,
                "Чекпоинта нет в таблице.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        row = checkpoint_ids.index(checkpoint_str) + 1
        headers = checkpoints_sheet.row_values(1)

        if team_name not in headers:
            bot.send_message(
                message.chat.id,
                "Команда не найдена в заголовках таблицы.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        col = headers.index(team_name) + 1
        current = checkpoints_sheet.cell(row, col).value

        if current == "1":
            bot.send_message(
                message.chat.id,
                "Команда уже отмечена на этом чекпоинте.",
                reply_markup=types.ReplyKeyboardRemove()
            )
            return

        checkpoints_sheet.update_cell(row, col, 1)
        bot.send_message(
            message.chat.id,
            f"Отметил: <b>{team_name}</b> на чекпоинте <b>{checkpoint}</b>",
            parse_mode="HTML",
            reply_markup=types.ReplyKeyboardRemove()
        )
    except Exception as e:
        print("CHECKPOINT ERROR:", e)
        bot.send_message(message.chat.id, "ОШИБКА", reply_markup=types.ReplyKeyboardRemove())


@bot.message_handler(func=lambda message: message.text == "Статистика")
def show_teams(message):
    try:
        points_and_teams = []

        for i in range(2, 10):
            row = teams_sheet.row_values(i)
            if len(row) >= 3:
                team_name = row[0]
                points = int(row[1]) if row[1] and str(row[1]).isdigit() else 0
                life = int(row[2]) if row[2] and str(row[2]).isdigit() else 0
                points_and_teams.append([team_name, points, life])

        points_and_teams.sort(key=lambda x: -x[1])

        medals = ["🥇", "🥈", "🥉"]
        text = "🏆 <b>Таблица лидеров</b>\n\n"

        for index, (team, points, life) in enumerate(points_and_teams):
            place = index + 1
            if index < 3:
                medal = medals[index]
                text += f"{medal} <b>{place} место</b> - {team} | {points} очков | {life} здоровья\n"
            else:
                text += f"{place} место - {team} | {points} очков | {life} здоровья\n"

        bot.send_message(message.chat.id, text, parse_mode="HTML")
    except Exception as e:
        print("STATISTICS ERROR:", e)
        bot.send_message(
            message.chat.id,
            "К огромному сожалению вы израсходовали количество запросов. пожалуйста повторите запрос через 30 секунд <3"
        )


@bot.message_handler(func=lambda message: message.text == "Потратить очки заражения")
def infect_button(message):
    if deny_if_dead(message):
        return

    user_id = message.from_user.id
    team = get_user_team(user_id)

    if not team:
        bot.send_message(message.chat.id, "Ты не зарегистрирован. Нажми «Регистрация».")
        return

    user_sessions[user_id] = {"attacker_team": team}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for t in teams:
        if t != team:
            markup.add(types.KeyboardButton(t))

    msg = bot.send_message(message.chat.id, "Выбери команду-цель:", reply_markup=markup)
    bot.register_next_step_handler(msg, infect_choose_target)


def infect_choose_target(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        bot.send_message(message.chat.id, "Сессия сброшена. Начни заново.")
        return

    attacker_team = session["attacker_team"]
    target_team = message.text

    if target_team not in teams or target_team == attacker_team:
        bot.send_message(message.chat.id, "Выбери команду-цель кнопкой.")
        return

    session["target_team"] = target_team
    attacker_points, attacker_life = read_points_and_life(attacker_team)

    msg = bot.send_message(
        message.chat.id,
        f"У вашей команды <b>{attacker_points}</b> очков заражения.\n"
        f"Сколько потратить, чтобы снять жизни у <b>{target_team}</b>?",
        parse_mode="HTML",
        reply_markup=types.ReplyKeyboardRemove()
    )
    bot.register_next_step_handler(msg, infect_enter_amount)


def get_user_team(user_id):
    ids = users_sheet.col_values(1)
    teams_col = users_sheet.col_values(4)
    uid = str(user_id)

    for i in range(1, len(ids)):
        if ids[i] == uid:
            return teams_col[i] if i < len(teams_col) else None

    return None


def get_team_row_in_sheet2(team_name):
    cell = teams_sheet.find(team_name, in_column=1)
    return cell.row


def get_team_life(team_name):
    row = get_team_row_in_sheet2(team_name)
    life = teams_sheet.cell(row, 3).value
    return int(life) if life and str(life).isdigit() else 0


def read_points_and_life(team_name):
    row = get_team_row_in_sheet2(team_name)

    pts = teams_sheet.cell(row, 2).value
    life = teams_sheet.cell(row, 3).value

    pts_i = int(pts) if pts and str(pts).isdigit() else 0
    life_i = int(life) if life and str(life).isdigit() else 0

    return pts_i, life_i


def write_points_and_life(team_name, points, life):
    row = get_team_row_in_sheet2(team_name)
    teams_sheet.update_cell(row, 2, points)
    teams_sheet.update_cell(row, 3, life)


def infect_enter_amount(message):
    user_id = message.from_user.id
    session = user_sessions.get(user_id)

    if not session:
        bot.send_message(message.chat.id, "Сессия сброшена. Начни заново")
        return

    if not message.text.isdigit():
        bot.send_message(message.chat.id, "Введи число")
        return

    amount = int(message.text)

    if amount <= 0:
        bot.send_message(message.chat.id, "Нужно положительное число")
        return

    attacker_team = session["attacker_team"]
    target_team = session["target_team"]

    try:
        attacker_points, attacker_life = read_points_and_life(attacker_team)
        target_points, target_life = read_points_and_life(target_team)

        if attacker_points < amount:
            bot.send_message(
                message.chat.id,
                f"Недостаточно очков. У вас: <b>{attacker_points}</b>",
                parse_mode="HTML"
            )
            return

        if target_life <= 0:
            bot.send_message(message.chat.id, "У цели уже 0 жизней.")
            return

        new_attacker_points = attacker_points - amount
        new_target_life = max(0, target_life - amount)

        write_points_and_life(attacker_team, new_attacker_points, attacker_life)
        write_points_and_life(target_team, target_points, new_target_life)

        bot.send_message(
            message.chat.id,
            f"<b>{attacker_team}</b> потратила <b>{amount}</b> очков заражения на <b>{target_team}</b>\n"
            f"Очки вашей команды теперь: <b>{new_attacker_points}</b>\n"
            f"Жизни команды {target_team} теперь: <b>{new_target_life}</b>",
            parse_mode="HTML"
        )

    except Exception as e:
        print("INFECT ERROR:", e)
        bot.send_message(message.chat.id, "ОШИБКА при атаке.")
    finally:
        buttons(message)
        user_sessions.pop(user_id, None)


def deny_if_dead(message):
    team = get_user_team(message.from_user.id)

    if not team:
        bot.send_message(message.chat.id, "Ты не зарегистрирован.")
        return True

    life = get_team_life(team)

    if life <= 0:
        bot.send_message(
            message.chat.id,
            "💀 <b>Твоя команда мертва.</b>\nИгра для вас окончена.\n",
            parse_mode="HTML"
        )
        return True

    return False


bot.polling(none_stop=True)
