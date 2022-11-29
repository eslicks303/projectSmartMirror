# sm_app.py
# ----- Smart Mirror GUI Application -----
from __future__ import print_function

import platform
import PySimpleGUI as sg
import datetime
import time
import calendar
import os
import io
import ast
import re

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from pytube import YouTube

import PySimpleGUI as sg
import vlc

from pathlib import Path

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from PIL import Image
import cloudscraper

title = ''
streams = None
counter = 0


class GUI():
    def __init__(self):
        file = load_json('data.js')
        # variables
        scale = 0.75
        use_layout = int(file['layout'])
        fullscreen = True
        resolutionX, resolutionY = sg.Window.get_screen_size()
        plat = platform.system()
        print("Initializing Smart Mirror App for " + plat)
        
        debug = False
        
        if debug == True:
            scale = 0.5
            fullscreen = False
            resolutionX = int(1080 * scale)
            resolutionY = int(1920 * scale)
        
        sg.theme("Black")

        # declare all fonts (platforms have different formats)
        # Fonts for Windows
        if plat == "Windows":
            font_Med_1 = ("Roboto Medium", int(72 * scale)) # Time
            font_Med_2 = ("Roboto Medium", int(60 * scale)) # Temp

            font_Thin_1 = ("Roboto Thin Italic", int(36 * scale)) # Date & Weather
            font_Thin_2 = ("Roboto Thin Italic", int(72 * scale)) # Welcome Message
            font_Thin_3 = ("Roboto Thin Italic", int(24 * scale)) # List Titles
            font_Thin_4 = ("Roboto Thin Italic", int(18 * scale)) # Sub-list Items

            font_Reg = ("Roboto Regular", int(24 * scale)) # Location Name

            font_Light = ("Roboto Light", int(18 * scale)) # List Items
        # Fonts for Linux (RaspberryPi in this case)  
        elif plat == "Linux":
            font_Med_1 = ("Roboto Medium", int(72 * scale)) # Time
            font_Med_2 = ("Roboto Medium", int(60 * scale)) # Temp

            font_Thin_1 = ("Roboto Thin", int(36 * scale)) # Date & Weather
            font_Thin_2 = ("Roboto Thin", int(72 * scale)) # Welcome Message
            font_Thin_3 = ("Roboto Thin", int(24 * scale)) # List Titles
            font_Thin_4 = ("Roboto Thin", int(18 * scale)) # Sub-list Items

            font_Reg = ("Roboto", int(24 * scale)) # Location Name

            font_Light = ("Roboto Light", int(18 * scale)) # List Items

        # window elements

        time = [
            [sg.Text("Loading...", font=font_Med_1, key='-TIME-')],
            [sg.Text("Loading...", font=font_Thin_1, key='-DATE-')],
        ]

        weather = [
            [sg.Text("---°F", font=font_Med_2, key='-TEMP-')],
            [sg.Text("Loading...", font=font_Thin_1, key='-CONDITION-')],
            [sg.Text("Loading...", font=font_Reg, key='-LOCATION-')],
        ]
        
        cal_time = [
            [sg.Text("-----", font=font_Light, k='-CAL_TIME-')],
        ]
        
        cal_event = [
            [sg.Text("-----", font=font_Light, k='-CAL_EV-')],
        ]

        calendar = [
            [sg.Text("Upcoming Events", font=font_Thin_3)],
            [sg.HorizontalSeparator()],
            
            [sg.Column(cal_time, vertical_alignment='top'),
             sg.VerticalSeparator(),
             sg.Column(cal_event, vertical_alignment='top')],
        ]

        big_box = [
            [
            sg.Image('', size=(300, 170), key='-VID_OUT-')
            ]
        ]

        message = [
            [
                sg.Text("Welcome back :)", font=font_Thin_2, justification='center', k='-MSG-'),
            ]
        ]

        timer = [
            [sg.Text("Current Timers", font=font_Thin_3)],
            [sg.HorizontalSeparator()],
            [sg.Text("No timers to display!", font=font_Light, k='-TIMER-')],
        ]

        song = [
            [sg.Text("Nothing is playing", font=font_Light, k='-SONG-')]
        ]
        
        artist = [
            [sg.Text("", font=font_Thin_4, k='-ARTIST-')]
        ]
        
        artwork = [
            [sg.Image(k='-ART-')]
        ]
        
        music = [
            [sg.Text("What's Playing", font=font_Thin_3)],
            [sg.HorizontalSeparator()],
            
            [sg.Column(artwork, vertical_alignment='top'),
             sg.Column(song + artist, vertical_alignment='top')],
        ]

        spacer = [[]]

        # ----- Layout Conditionals -----
        if use_layout == 0:
            layout = [
                [sg.Column(time, vertical_alignment='top', justification='right')],
                
                [sg.Column(weather, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),
                sg.Column(calendar, vertical_alignment='top', justification='right', k='-R1-')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(timer, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),
                sg.Column(music, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 1:
            layout = [
                [sg.Column(time, vertical_alignment='top', justification='right')],
                
                [sg.Column(weather, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),
                sg.Column(music, vertical_alignment='top', justification='right', k='-R1-')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(timer, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),
                sg.Column(calendar, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 2:
            layout = [
                [sg.Column(time, vertical_alignment='top', justification='right')],
                
                [sg.Column(timer, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),
                sg.Column(music, vertical_alignment='top', justification='right', k='-R1-')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(weather, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),
                sg.Column(calendar, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 3:
            layout = [
                [sg.Column(time, vertical_alignment='top', justification='right')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(timer, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),
                sg.Column(music, vertical_alignment='top', justification='right', k='-R1-')],
                
                [sg.Column(weather, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),
                sg.Column(calendar, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 4:
            layout = [
                [sg.Column(time, vertical_alignment='top', justification='right')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(timer, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),
                sg.Column(weather, vertical_alignment='top', justification='right', k='-R1-')],
                
                [sg.Column(music, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),         
                sg.Column(calendar, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 5:
            layout = [
                [sg.Column(time, vertical_alignment='top', justification='right')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(weather, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),         
                sg.Column(music, vertical_alignment='top', justification='right', k='-R1-')],
                
                [sg.Column(calendar, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),         
                sg.Column(timer, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 6:
            layout = [
                [sg.Column(timer, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),         
                sg.Column(music, vertical_alignment='top', justification='right', k='-R1-')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                        
                [sg.Column(weather, vertical_alignment='top', justification='left')],
                
                [sg.Column(calendar, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),         
                sg.Column(time, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 7:
            layout = [
                [sg.Column(weather, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),         
                sg.Column(calendar, vertical_alignment='top', justification='right', k='-R1-')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                        
                [sg.Column(timer, vertical_alignment='top', justification='left')],
                
                [sg.Column(music, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),         
                sg.Column(time, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 8:
            layout = [
                [sg.Column(music, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),         
                sg.Column(weather, vertical_alignment='top', justification='right', k='-R1-')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                        
                [sg.Column(timer, vertical_alignment='top', justification='left')],
                
                [sg.Column(calendar, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),         
                sg.Column(time, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 9:
            layout = [
                [sg.Column(music, vertical_alignment='top', justification='center')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(timer, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),         
                sg.Column(weather, vertical_alignment='top', justification='right', k='-R1-')],     
                
                [sg.Column(calendar, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),         
                sg.Column(time, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 10:
            layout = [
                [sg.Column(timer, vertical_alignment='top', justification='center')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(music, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),         
                sg.Column(weather, vertical_alignment='top', justification='right', k='-R1-')],     
                
                [sg.Column(calendar, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),         
                sg.Column(time, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 11:
            layout = [
                [sg.Column(timer, vertical_alignment='top', justification='center')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(music, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),         
                sg.Column(calendar, vertical_alignment='top', justification='right', k='-R1-')],     
                
                [sg.Column(time, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),         
                sg.Column(weather, vertical_alignment='top', justification='right', k='-R2-')],
            ]
        elif use_layout == 12:
            layout = [
                [sg.Column(time, vertical_alignment='top', justification='left', k='-L1-'),
                sg.Column(spacer, justification='center', k='-SP1-'),         
                sg.Column(weather, vertical_alignment='top', justification='right')],
                
                [sg.Column(calendar, vertical_alignment='top', justification='left')],
                
                [sg.Column(big_box, vertical_alignment='center', justification='center', k='-C-')],       
                [sg.Column(message, vertical_alignment='center', justification='center', k='-M-')],
                
                [sg.Column(timer, vertical_alignment='top', justification='left', k='-L2-'),
                sg.Column(spacer, justification='center', k='-SP2-'),         
                sg.Column(music, vertical_alignment='top', justification='right', k='-R2-')],
            ]

        # Create window: remove title bar, and maximize (fullscreen)
        self.window = sg.Window(
            "Project Smart Mirror", 
            layout, 
            no_titlebar=fullscreen,
            location=(0,0), 
            size=(resolutionX, resolutionY)
        ).Finalize()


        self.window['-C-'].expand(True, True, True)
        self.window['-SP1-'].expand(True, True, False)
        self.window['-SP2-'].expand(True, True, False)
        self.window['-VID_OUT-'].expand(True, True)

        if fullscreen == True:
            self.window.Maximize()
            
def load_json(file):
    with open(file) as js_file:
        file = js_file.read()
        js_parse = file[file.find('{'): file.rfind('}')+1]
        data = ast.literal_eval(js_parse)
        
        return data

def update_date(gui):
    today = datetime.date.today()
    gui.window['-DATE-'].update(
        calendar.day_name[today.weekday()] + ", " + 
        calendar.month_name[int(today.strftime("%m"))] + " " +
        today.strftime("%d")
    )
    
def update_time(gui):
    blink = ":"
    am_pm = "AM"
    time = datetime.datetime.now()
    hour = int(time.strftime("%H"))
    minute = time.strftime("%M")
    second = int(time.strftime("%S"))
    
    if hour >= 12:
        am_pm = "PM"
    elif hour < 12:
        am_pm = "AM"
        
    if hour > 12:
        hour -= 12
    if hour == 0:
        hour = 12
        
    if (second % 2) == 0:
        blink = "  "
    else:
        blink = ":"

    gui.window['-TIME-'].update(
        str(hour) +
        blink +
        minute + " " +
        am_pm
    )
    
def update_message(gui, prev, msg_flag):
    # Remove welcome after ~5 seconds
    now = datetime.datetime.now().timestamp()
    if ((now - prev) > 4.5) and (msg_flag == True):
        msg_flag = False
        gui.window["-MSG-"].update("")
        print("Closing welcome message")
    return msg_flag
        
def update_weather_file(data):
    zip = data['zip']
    if platform.system() != "Windows":
        os.system("weather " + zip + " > currentWeather.txt")
    with open('currentWeather.txt') as txt:
        lines = txt.readlines()  

    for i in range(len(lines)):
        x = re.split("Temperature: ", lines[i])
        if len(x) > 1:
            x2 = re.split("\s", x[1])
            temperature = str(x2[0])
        
        y = re.split("conditions: ", lines[i])
        if len(y) > 1: 
            y2 = re.split("\n", str(y[1]))
            condition = str(y2[0])
    
    weather = {
        "temperature": temperature,
        "condition": condition
    }
    
    return weather
    
def update_weather_gui(gui, data, weather):
    location = data['city']
    gui.window["-TEMP-"].update(weather["temperature"] + "°F")
    gui.window["-CONDITION-"].update(weather["condition"])
    gui.window["-LOCATION-"].update(location)

def update_calendar(gui, data):
    print("Pulling events from user's calendar...")
    
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']  
    
    """
    Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    try:
        service = build('calendar', 'v3', credentials=creds)

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        print('Getting the upcoming 10 events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            print('No upcoming events found.')
            return

        # Grabs the start and name of the next 10 events
        gui.window["-CAL_TIME-"].update("")
        gui.window["-CAL_EV-"].update("")
        flag = 0
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            
            temp_t = gui.window["-CAL_TIME-"]
            temp_e = gui.window["-CAL_EV-"]
            
            hour = int(start[11:13])
            minute = start[14:16]
            am_pm = "AM"
            
            if hour >= 12:
                am_pm = "PM"
            elif hour < 12:
                am_pm = "AM"
        
            if hour > 12:
                hour -= 12
            if hour == 0:
                hour = 12
            
            if flag == 0:
                gui.window["-CAL_TIME-"].update(
                    calendar.month_abbr[int(start[5:7])] + " " + 
                    start[8:10] + ", " +
                    str(hour) + ":" + minute + " " + am_pm)
                gui.window["-CAL_EV-"].update(event['summary'])
                flag = 1
            else:
                gui.window["-CAL_TIME-"].update(temp_t.get() + "\n" +
                    calendar.month_abbr[int(start[5:7])] + " " + 
                    start[8:10] + ", " +
                    str(hour) + ":" + minute + " " + am_pm)
                gui.window["-CAL_EV-"].update(temp_e.get() + "\n" + event['summary'])

    except HttpError as error:
        print('An error occurred: %s' % error)
    

def update_timers(gui):
    
    gui.window['-TIMER-'].update("")
    temp = gui.window['-TIMER-']
    for i in range(len(tog_vals)):
        if tog_vals[i] == "true":
            if h_count[i] < 10:
                h_temp = "0" + str(h_count[i])
            else:
                h_temp = str(h_count[i])

            if m_count[i] < 10:
                m_temp = "0" + str(m_count[i])
            else:
                m_temp = str(m_count[i])

            if s_count[i] < 10:
                s_temp = "0" + str(s_count[i])
            else:
                s_temp = str(s_count[i])
            gui.window['-TIMER-'].update(temp.get() + str(h_temp) + ":" + str(m_temp) + ":" + str(s_temp) + "\n")
    # update timer 0        
    s_count[0] -= 1
    if s_count[0] == -1 and (m_count[0] > 0 or h_count[0] > 0):
        s_count[0] = 59
        m_count[0] -= 1
        if m_count[0] == -1 and h_count[0] > 0:
            m_count[0] = 59
            h_count[0] -= 1
            if h_count[0] == -1:
                h_count[0] = 0
        elif m_count[0] == -1 and h_count[0] <= 0:
            m_count[0] = 0
    elif s_count[0] == -1 and m_count[0] <= 0:
        s_count[0] = 0
    # update time 1    
    s_count[1] -= 1
    if s_count[1] == -1 and (m_count[1] > 0 or h_count[1] > 0):
        s_count[1] = 59
        m_count[1] -= 1
        if m_count[1] == -1 and h_count[1] > 0:
            m_count[1] = 59
            h_count[1] -= 1
            if h_count[1] == -1:
                h_count[1] = 0
        elif m_count[1] == -1 and h_count[1] <= 0:
            m_count[1] = 0
    elif s_count[1] == -1 and m_count[1] <= 0:
        s_count[1] = 0
    # update timer 2    
    s_count[2] -= 1
    if s_count[2] == -1 and (m_count[2] > 0 or h_count[2] > 0):
        s_count[2] = 59
        m_count[2] -= 1
        if m_count[2] == -1 and h_count[2] > 0:
            m_count[2] = 59
            h_count[2] -= 1
            if h_count[2] == -1:
                h_count[2] = 0
        elif m_count[2] == -1 and h_count[2] <= 0:
            m_count[2] = 0
    elif s_count[2] == -1 and m_count[2] <= 0:
        s_count[2] = 0        

def update_music(gui):
    SPOTIPY_CLIENT_ID='11c23d64e28948ee9afd18eb4f8a31c3'
    SPOTIPY_CLIENT_SECRET='57d720ac8a0d4ee7b2f213d6bf6b6755'
    SPOTIPY_REDIRECT_URI='http://google.com/'
    scope = "user-read-playback-state,user-modify-playback-state"
    
    oauth_object = SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=scope)
    
    token_dict = oauth_object.get_access_token()
    token = token_dict['access_token']
    
    sp = spotipy.Spotify(auth=token)
    
    results = sp.currently_playing()

    if str(results) != "None":
        if results["is_playing"] == True:
            artist = results["item"]["album"]["artists"][0]["name"]
            song = results["item"]["name"]
            url = results["item"]["album"]["images"][2]["url"]
            
            jpg_data = (
                cloudscraper.create_scraper(
                    browser={"browser": "firefox", "platform": "windows", "mobile": False}
                )
                .get(url)
                .content
            )
            
            pil_image = Image.open(io.BytesIO(jpg_data))
            png_bio = io.BytesIO()
            pil_image.save(png_bio, format="PNG")
            png_data = png_bio.getvalue()        
            
            gui.window["-SONG-"].update(song)
            gui.window["-ARTIST-"].update(artist)
            gui.window["-ART-"].update(png_data)
        else:
            gui.window["-SONG-"].update("Nothing is playing")
            gui.window["-ARTIST-"].update("")
            gui.window["-ART-"].update("")
    else:
        gui.window["-SONG-"].update("Nothing is playing")
        gui.window["-ARTIST-"].update("")
        gui.window["-ART-"].update("")

def download_video(stream):
    global done, title, streams, counter
    counter = 0
    stream.download()
    
def video_player(URL, action, media_list, list_player, player):

    # Check to see if file exists already
    video_file = Path(str(YouTube(URL).title) + ".mp4")
    if video_file.is_file():
        pass
    else:
        # ----- clean dir -----
        directory = "./"

        files_in_directory = os.listdir(directory)
        filtered_files = [file for file in files_in_directory if file.endswith(".mp4")]

        for file in filtered_files:
            path_to_file = os.path.join(directory, file)
            os.remove(path_to_file)
            
        # ----- download -----
        stream = get_quality(URL)
        download_video(stream)
        
    # ----- load -----
    media_list.add_media("./")
    list_player.set_media_list(media_list)
        
    # The possible values from the MSP will be:
    #   "play"
    #   "stop"
    #   "pause"
    #   "unpause"


    if action == "play\n" and player.is_playing() != True:       
        list_player.next()
        list_player.play()
    
    elif action == "pause\n" and player.is_playing():
        list_player.pause()

    elif action == "unpause\n" and player.is_playing() != True:
        list_player.pause()
        
    elif action == "stop\n":
        list_player.stop()

    
def get_quality(url):
    global title
    yt = YouTube(url)
    streams = yt.streams.filter(progressive=True).all()
    title = yt.title
    # layout = [[sg.T('Choose streams')]] # GUI DEBUG FOR PICKING STREAMS
    # for i, s in enumerate(streams):
    #     layout += [[sg.CB(str(s), k=i)]]

    # layout += [[sg.Ok(), sg.Cancel()]]
    # event, values = sg.Window('Choose Stream', layout).read(close=True)
    # choices = [k for k in values if values[k]]
    # if not choices:
    #     sg.popup_error('Must choose stream')
    #     exit()
    return streams[len(streams) - 1]      # Return the first choice made  

def pull_data():
    if platform.system() != "Windows":
        os.system("python pull.py")

def main():
    
    gui = GUI()
    print("Finished Initializing")
    welcome_timer = datetime.datetime.now().timestamp()
    flag = 0
    msg_flag = True
    done_flag = False
    
    init_data = load_json('data.js')
    hours_mem = init_data["hours"]
    minutes_mem = init_data["minutes"]
    seconds_mem = init_data["seconds"]
    tog_mem = init_data["toggles"]
    
    global h_count
    global m_count
    global s_count
    global tog_vals
    
    h_count = hours_mem
    m_count = minutes_mem
    s_count = seconds_mem
    tog_vals = tog_mem
    
    # create player
    inst = vlc.Instance()
    list_player = inst.media_list_player_new()
    media_list = inst.media_list_new([])
    list_player.set_media_list(media_list)
    player = list_player.get_media_player()
    if platform.system().startswith('Linux'):
        player.set_xwindow(gui.window['-VID_OUT-'].Widget.winfo_id())
    else:
        player.set_hwnd(gui.window['-VID_OUT-'].Widget.winfo_id())
    
    # event loop
    while True:
        event, values = gui.window.read(timeout=500)
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        
        
        else:
            MSP_OUTPUT = open("MSP_OUTPUT.txt", 'r')
            action = MSP_OUTPUT.read()
            pull_data()
            data = load_json('data.js')
            URL = data['URL']
            msg_flag = update_message(gui, welcome_timer, msg_flag)
            update_time(gui)
            update_date(gui)
            weather = update_weather_file(data)
            update_weather_gui(gui, data, weather)
            now = datetime.datetime.now()
            if ((int(now.strftime("%M")) % 5) == 0 and (int(now.strftime("%S")) < 1.25)) or flag == 0:
                update_calendar(gui, data)
                flag = 1
            update_music(gui)
            if done_flag == True:
                video_player(URL, action, media_list, list_player, player)
            done_flag = True
            # check if the timers have been changed in data.js
            
            # # timer 0
            # if (h_count[0]    != data["hours"][0]   or
            #     m_count[0]  != data["minutes"][0]   or
            #     s_count[0]  != data["seconds"][0]   or
            #     tog_vals[0]      != data["toggles"][0]):
            #     print(seconds_mem[0])
            #     print(data["seconds"][0])
            #     # update timer to relect changes in data.js
            #     hours_mem[0]    = data["hours"][0]
            #     minutes_mem[0]  = data["minutes"][0]
            #     seconds_mem[0]  = data["seconds"][0]
            #     tog_mem[0]      = data["toggles"][0]
                
            #     h_count[0] = hours_mem[0]
            #     m_count[0] = minutes_mem[0]
            #     s_count[0] = seconds_mem[0]
            #     tog_vals[0] = tog_mem[0]
                
            # # timer 1
            # if (hours_mem[1]    != data["hours"][1]     or
            #     minutes_mem[1]  != data["minutes"][1]   or
            #     seconds_mem[1]  != data["seconds"][1]   or
            #     tog_mem[1]      != data["toggles"][1]):
                
            #     # update timer to relect changes in data.js
            #     hours_mem[1]    = data["hours"][1]
            #     minutes_mem[1]  = data["minutes"][1]
            #     seconds_mem[1]  = data["seconds"][1]
            #     tog_mem[1]      = data["toggles"][1]
                
            #     h_count[1] = hours_mem[1]
            #     m_count[1] = minutes_mem[1]
            #     s_count[1] = seconds_mem[1]
            #     tog_vals[1] = tog_mem[1] 
                               
            # # timer 2
            # if (hours_mem[2]    != data["hours"][2]     or
            #     minutes_mem[2]  != data["minutes"][2]   or
            #     seconds_mem[2]  != data["seconds"][2]   or
            #     tog_mem[2]      != data["toggles"][2]):
                
            #     # update timer to relect changes in data.js
            #     hours_mem[2]    = data["hours"][2]
            #     minutes_mem[2]  = data["minutes"][2]
            #     seconds_mem[2]  = data["seconds"][2]
            #     tog_mem[2]      = data["toggles"][2]
                
            #     h_count[2] = hours_mem[2]
            #     m_count[2] = minutes_mem[2]
            #     s_count[2] = seconds_mem[2]
            #     tog_vals[2] = tog_mem[2]

            update_timers(gui)



    gui.window.close()
    # Clean up downloaded videos
    directory = "./"

    files_in_directory = os.listdir(directory)
    filtered_files = [file for file in files_in_directory if file.endswith(".mp4")]

    for file in filtered_files:

        path_to_file = os.path.join(directory, file)

        os.remove(path_to_file)
    print("Closed")
    
if __name__ == '__main__':
    main()
