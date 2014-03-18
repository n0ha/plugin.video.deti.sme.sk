# coding=utf-8
import sys
import urllib
import urlparse
import urllib2
import xbmcgui
import xbmcplugin
import CommonFunctions

common = CommonFunctions
common.plugin = "deti.sme.sk xbmc plugin 0.0.1"

deti_sme_sk_url = 'http://deti.sme.sk/content/new/?children_category=age'
parse_video_url = 'http://deti.sme.sk/show/video_id/?print=1'

base_url = sys.argv[0]
addon_handle = int(sys.argv[1])
args = urlparse.parse_qs(sys.argv[2][1:])

xbmcplugin.setContent(addon_handle, 'movies')


def build_url(query):
    return base_url + '?' + urllib.urlencode(query)


def add_top_folder_item(age, foldername):
    url = build_url({'mode': 'content', 'age': age})
    li = xbmcgui.ListItem(foldername, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)

def add_content_folder_item(content, age, foldername):
    url = build_url({"mode": "folder", "content": content, "age": age})
    li = xbmcgui.ListItem(foldername, iconImage='DefaultFolder.png')
    xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li, isFolder=True)


def get_deti_url(content, age):
    return deti_sme_sk_url.replace("content", content).replace("age", age)

mode = args.get('mode', None)

# toplevel folder
if mode is None:
    add_top_folder_item('-1', u"pre všetky deti")
    add_top_folder_item('1', u"pre najmenšie deti (0-3 rokov)")
    add_top_folder_item('2', u"pre škôlkárov (4-6 rokov)")
    add_top_folder_item('3', u"pre školákov (7-10 rokov)")
    add_top_folder_item('4', u"pre násťročných (11 rokov a viac)")
    xbmcplugin.endOfDirectory(addon_handle)

elif mode[0] == 'content':
    age = args["age"][0]
    add_content_folder_item("video", age, u"Krátke videá")
    add_content_folder_item("rozpravky", age, u"Rozprávky")
    add_content_folder_item("pesnicky", age, u"Pesničky")
    xbmcplugin.endOfDirectory(addon_handle)

# category folder
elif mode[0] == 'folder':
    age = args["age"][0]
    content = args["content"][0]

    url = get_deti_url(content, age)

    print "url to get: " + url

    request = urllib2.Request(url)
    con = urllib2.urlopen(request)
    inputdata = con.read()
    con.close()
    inputdata = inputdata.decode("windows-1250")

    #if result["status"] == 200:
    print(url + " fetched OK")

    # parsing page
    div_wrap = common.parseDOM(inputdata, "div", attrs={"id": "c-wrap"})
    entries = common.parseDOM(div_wrap, "div", attrs={"class": "entry"}, ret="id")

    print "entries length: " + str(len(entries))

    # show entries as videos
    for entry in entries:
        entry_dom = common.parseDOM(div_wrap, "div", attrs={"id": entry})

        # scrape title and image from the html
        title = common.parseDOM(entry_dom, "a", ret="title")[0]
        image_src = common.parseDOM(entry_dom, "img", attrs={"class": "entry_img"}, ret="src")[0]

        code = entry.replace("entry_", "")

        url = build_url({"mode": "video", "video_id": code})
        li = xbmcgui.ListItem(title, iconImage='DefaultVideo.png', thumbnailImage=image_src)
        li.setInfo(type="Video", infoLabels={"Title": title})
        li.setProperty("IsPlayable", "true")
        xbmcplugin.addDirectoryItem(handle=addon_handle, url=url, listitem=li)

    xbmcplugin.endOfDirectory(addon_handle)

# video
elif mode[0] == 'video':
    video_id = args['video_id'][0]
    print("video_id = " + str(video_id))

    # scrape youtube url
    video_url = parse_video_url.replace("video_id", video_id)
    request = urllib2.Request(video_url)
    con = urllib2.urlopen(request)
    inputdata = con.read()
    con.close()

    inputdata = inputdata.decode("windows-1250")
    print("inputdata = " + repr(inputdata))

    video_youtube_code = common.parseDOM(inputdata, "article_kod")[0]
    print("video_youtube_code = " + str(video_youtube_code))

    if video_youtube_code is not None:
        youtube_plugin_url = "plugin://plugin.video.youtube/?path=/root/video&action=play_video&videoid=" + video_youtube_code
        print("youtube_plugin_url = " + youtube_plugin_url)

        li = xbmcgui.ListItem(path=youtube_plugin_url)
        li.setProperty('IsPlayable', 'true')
        xbmcplugin.setResolvedUrl(addon_handle, True, li)
    else:
        print "No code"