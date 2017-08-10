# # -*- coding: utf-8 -*-
# #------------------------------------------------------------------
                                                        
#--------------------------------------------------------------------
# License: GPL (http://www.gnu.org/licenses/gpl-3.0.html)
#
# Author: PJD
#   
#
#  Big thanks to Whufclee and Vulcan for their patience and help
#------------------------------------------------------------

import os           # access operating system commands
import xbmc         # the base xbmc functions, pretty much every add-on is going to need at least one function from here
import xbmcaddon    # pull addon specific information such as settings, id, fanart etc.
import xbmcplugin   # contains functions required for creating directory structure style add-ons (plugins)

# The following are often used, we are not using them in this particular file so they are commented out

# import re           # allows use of regex commands, if you're intending on scraping you'll need this
# import xbmcgui      # gui based functions, contains things like creating dialog pop-up windows

from koding import Add_Dir, Find_In_Text, Open_URL, OK_Dialog
from koding import Open_Settings, Play_Video, Run, Text_File
from koding import *

#debug        = Addon_Setting(setting='debug')        Debug tunred off Line 45,46 also to enable
addon_id     = xbmcaddon.Addon().getAddonInfo('id')
home         = xbmc.translatePath('special://home')

# Our master XML we want to load up
main_xml     = 'https://raw.githubusercontent.com/alfreddempsey3/repository.rage/master/plugin.video.musicaddon/addon.xml'
# Alternatively you could set a local XML but online obviously means less add-on updates to push
# main_xml     = os.path.join(home,'addons',addon_id,'resources','video.xml')

#----------------------------------------------------------------
@route(mode='start')
def Start():
    Main_Menu(main_xml)
    Refresh()
#----------------------------------------------------------------
@route(mode='main_menu',args=['url'])
def Main_Menu(url=main_xml):

 # If debug mode is enabled show the koding tutorials
 #    if debug == 'true':
 #        Add_Dir ( '[COLOR=lime]Koding Tutorials[/COLOR]', '', "tutorials", True, '', '', '' )
 #     else:
 #        Add_Dir ( '[COLOR=lime]Enable debug mode for some cool dev tools![/COLOR]', '', "koding_settings", False, '', '', '' )

# An optional example title/message, however in our example we're going to do one via our online xml so we've commented this out
    # my_message= "{'title' : 'Support & Suggestions', 'msg' : \"If you come across any online content you'd like to get added please use the support thread at noobsandnerds.com and I'll be happy to look into it for you.\"}"
    # Add_Dir(
    #     name="Support/Suggestions", url=my_message, mode="simple_dialog", folder=False,
    #     icon="https://cdn2.iconfinder.com/data/icons/picons-basic-2/57/basic2-087_info-512.png")

# Read the contents of our file into memory
    if url.startswith('http'):
        contents  = Open_URL(url)
    else:
        contents  = Text_File(url,'r')

# Split the contents up into sections - we're finding every instance of <item> and </item> and everything inbetween
    raw_links = Find_In_Text(content=contents, start='<item>', end=r'</item>')

# Now loop through each of those matches and pull out the relevant data
    for item in raw_links:
        title  = Find_In_Text(content=item, start='<title>', end=r'</title>')
        title  = title[0] if (title!=None) else 'Unknown Video'
        thumb  = Find_In_Text(content=item, start='<thumbnail>', end=r'</thumbnail>')
        thumb  = thumb[0] if (thumb!=None) else ''
        fanart = Find_In_Text(content=item, start='<thumbnail>', end=r'</thumbnail>')
        fanart = fanart[0] if (fanart!=None) else ''

# If this contains sublinks grab all of them
        if not '<sublink>' in item:
            links  = Find_In_Text(content=item, start='<link>', end=r'</link>')

# Otherwise just grab the link tag
        else:
            links  = Find_In_Text(content=item, start='<sublink>', end=r'</sublink>')

# If it's an xml file then we set the link to the xml path rather than a list of links
        if links[0].endswith('.xml') or links[0]=='none' or links[0] == '' or links[0].startswith('msg~'):
            links = links[0]

        dolog('Data type: '+Data_Type(links))

    # If link is none we presume it's a folder
        if links == 'none' or links == '':
            Add_Dir( name=title, url='', mode='', folder=False, icon=thumb, fanart=fanart )

    # If link is a string it's either another menu or a message
        elif Data_Type(links)=='str':

        # If it's a message clean up the string and load up the simple_dialog function
            if links.startswith('msg~'):
                links = links.replace('msg~','')
                Add_Dir( name=title, url="{%s}"%links, mode='simple_dialog', folder=False, icon=thumb, fanart=fanart )

        # Otherwise we presume it's a menu
            else:
                Add_Dir( name=title, url=links, mode='main_menu', folder=True, icon=thumb, fanart=fanart )

    # Otherwise send through our list of links to the Play_Link function
        else:
            Add_Dir( name=title, url="{'url':%s}"%links, mode='play_link', folder=False, icon=thumb, fanart=fanart )
#----------------------------------------------------------------
# Simple function to check playback, it will return true or false if playback successful
@route(mode='play_link',args=['url'])
def Play_Link(url):
# If only one item in the list we try and play automatically
    if len(url)==1:
        if not Play_Video(url[0]):
            OK_Dialog( 'PLAYBACK FAILED','This stream is currently offline.' )

# If more than one link then we give a choice of which link to play
    elif len(url)>1:
        link_list   = []
        counter     = 1
        for item in url:
            link_list.append( 'Link '+str(counter) )
            counter += 1
        choice = Select_Dialog( 'CHOOSE STREAM', link_list )
        if choice >= 0:
            if not Play_Video( url[choice] ):
                OK_Dialog( 'PLAYBACK FAILED','This stream is currently offline.' )
                Play_Link(url)
#----------------------------------------------------------------
# A basic OK Dialog
@route(mode='koding_settings')
def Koding_Settings():
    Open_Settings()
#----------------------------------------------------------------
# A basic OK Dialog
@route(mode='simple_dialog', args=['title','msg'])
def Simple_Dialog(title,msg):
    OK_Dialog(title, msg)
#----------------------------------------------------------------
if __name__ == "__main__":
    Run(default='start')
    xbmcplugin.endOfDirectory(int(sys.argv[1]))
