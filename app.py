from unittest.loader import VALID_MODULE_NAME
import os
import wx
import wx.xrc
from pytube import YouTube
import moviepy.editor as mp
from urllib.parse import urlparse
import datetime
import tempfile
from slugify import slugify

vid_url = ""
yt = None
video_title = ""

class AppFrame ( wx.Frame ):
    def __init__( self, parent ):
        wx.Frame.__init__ ( self, parent, id = wx.ID_ANY, title = u"PYT SoundRipper", pos = wx.DefaultPosition, size = wx.Size( 600,312 ), style = wx.CAPTION|wx.CLOSE_BOX|wx.MINIMIZE|wx.MINIMIZE_BOX|wx.TAB_TRAVERSAL )

        self.InitUI()
        self.Centre() 
        self.Show()

    def InitUI(self):
        self.SetSizeHints( wx.Size( 600,200 ), wx.Size( 600,200 ) )

        main_fgsizer = wx.FlexGridSizer( 3, 2, 0, 0 )
        main_fgsizer.SetFlexibleDirection( wx.BOTH )
        main_fgsizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        self.url_field = wx.TextCtrl( self, wx.ID_ANY,  u"Enter URL", wx.DefaultPosition, wx.DefaultSize, style=wx.TE_PROCESS_ENTER )
        self.url_field.SetMinSize( wx.Size( 400,-1 ) )
        self.url_field.Bind(wx.EVT_TEXT_ENTER, self.InfoClick)

        main_fgsizer.Add( self.url_field, 0, wx.ALL, 5 )

        self.info_button = wx.Button( self, wx.ID_ANY, u"Get Info", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.info_button.SetMinSize( wx.Size( 120,-1 ) )
        self.info_button.Bind(wx.EVT_BUTTON, self.InfoClick)

        main_fgsizer.Add( self.info_button, 0, wx.ALL, 5 )

        infobox_sizer = wx.FlexGridSizer( 0, 2, 0, 0 )
        infobox_sizer.SetFlexibleDirection( wx.BOTH )
        infobox_sizer.SetNonFlexibleGrowMode( wx.FLEX_GROWMODE_SPECIFIED )

        infobox_sizer.SetMinSize( wx.Size( 400,100 ) )
        self.tit_lbl = wx.StaticText( self, wx.ID_ANY, u"Title: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.tit_lbl.Wrap( -1 )

        infobox_sizer.Add( self.tit_lbl, 0, wx.ALL, 5 )

        self.vid_title = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.vid_title.Wrap( -1 )

        infobox_sizer.Add( self.vid_title, 0, wx.ALL, 5 )

        self.len_lbl = wx.StaticText( self, wx.ID_ANY, u"Length: ", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.len_lbl.Wrap( -1 )

        infobox_sizer.Add( self.len_lbl, 0, wx.ALL, 5 )

        self.vid_len = wx.StaticText( self, wx.ID_ANY, wx.EmptyString, wx.DefaultPosition, wx.DefaultSize, 0 )
        self.vid_len.Wrap( -1 )

        infobox_sizer.Add( self.vid_len, 0, wx.ALL, 5 )


        main_fgsizer.Add( infobox_sizer, 1, wx.EXPAND, 5 )

        self.save_button = wx.Button( self, wx.ID_ANY, u"Save", wx.DefaultPosition, wx.DefaultSize, 0 )
        self.save_button.SetMinSize( wx.Size( 120,-1 ) )
        self.save_button.Disable()
        self.save_button.Bind(wx.EVT_BUTTON, self.SaveClick)

        main_fgsizer.Add( self.save_button, 0, wx.ALL, 5 )


        self.SetSizer( main_fgsizer )
        self.Layout()

        self.Centre( wx.BOTH )

    def ErrorPop(self, msg):
        dial = wx.MessageDialog(self, msg, "Error", wx.OK|wx.STAY_ON_TOP|wx.CENTRE|wx.ICON_ERROR)
        dial.ShowModal()

    def InfoClick(self, event):
        global yt
        global video_title
        vid_url = self.url_field.GetValue()
        if uri_validator(vid_url) == False:
            msg = "Sorry, that is not a valid URL! (Be sure to include the \"https://\" prefix!)"
            self.ErrorPop(msg)
        elif "youtube" not in vid_url:
            msg = "Sorry, that's not a YouTube URL! This only works with YouTube."
            self.ErrorPop(msg)
        elif "playlist" in vid_url:
            msg = "Sorry, you can't save an entire playlist at once!"
            self.ErrorPop(msg)
        else:
            yt = YouTube(vid_url)
            video_title = yt.title
            if len(yt.title) > 42:
                short_title = yt.title[:41] + "..."
                self.vid_title.SetLabel(short_title)
            else:
                self.vid_title.SetLabel(yt.title)
            self.vid_len.SetLabel(str(datetime.timedelta(seconds=yt.length)))
            self.save_button.Enable(True)

    def SaveClick(self, event):
        self.default_save_dir = get_download_folder()
        dl_exists = os.path.exists(self.default_save_dir)
        if dl_exists == False:
            os.makedirs(self.default_save_dir)
        try:
            temp_audio = (yt.streams.filter(only_audio=True).first().download(output_path = tempfile.gettempdir()))
            default_file = slugify(video_title) + ".wav"
            audio = mp.AudioFileClip(temp_audio)
            audio.write_audiofile(os.path.join(self.default_save_dir, default_file))
            self.save_button.Disable()
        except IOError:
            msg = "Cannot save current data in file '%s'." % self.default_save_dir
            self.ErrorPop(msg)

    def __del__( self ):
        pass

if os.name == 'nt':
    import ctypes
    from ctypes import windll, wintypes
    from uuid import UUID

    # ctypes GUID copied from MSDN sample code
    class GUID(ctypes.Structure):
        _fields_ = [
            ("Data1", wintypes.DWORD),
            ("Data2", wintypes.WORD),
            ("Data3", wintypes.WORD),
            ("Data4", wintypes.BYTE * 8)
        ] 

        def __init__(self, uuidstr):
            uuid = UUID(uuidstr)
            ctypes.Structure.__init__(self)
            self.Data1, self.Data2, self.Data3, \
                self.Data4[0], self.Data4[1], rest = uuid.fields
            for i in range(2, 8):
                self.Data4[i] = rest>>(8-i-1)*8 & 0xff

    SHGetKnownFolderPath = windll.shell32.SHGetKnownFolderPath
    SHGetKnownFolderPath.argtypes = [
        ctypes.POINTER(GUID), wintypes.DWORD,
        wintypes.HANDLE, ctypes.POINTER(ctypes.c_wchar_p)
    ]

    def _get_known_folder_path(uuidstr):
        pathptr = ctypes.c_wchar_p()
        guid = GUID(uuidstr)
        if SHGetKnownFolderPath(ctypes.byref(guid), 0, 0, ctypes.byref(pathptr)):
            raise ctypes.WinError()
        return pathptr.value

    FOLDERID_Download = '{374DE290-123F-4565-9164-39C4925E467B}'

    def get_download_folder():
        return _get_known_folder_path(FOLDERID_Download)
else:
    def get_download_folder():
        home = os.path.expanduser("~")
        return os.path.join(home, "Downloads")

def uri_validator(x):
    try:
        result = urlparse(x)
        return all([result.scheme, result.netloc])
    except:
        return False
        
app = wx.App() 
AppFrame(None) 
app.MainLoop()