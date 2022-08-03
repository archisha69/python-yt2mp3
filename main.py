import os
import sys
import pip
import tarfile
import zipfile
import requests
import threading

from tkinter import *
from tkinter.ttk import *
from tkinter import messagebox

try:
    from youtube_dl import YoutubeDL
    from youtube_search import YoutubeSearch
except ImportError:
    if hasattr(pip, "main"):
        pip.main("install", "youtube-dl")
        pip.main("install", "youtube-search")
    else:
        pip._internal.main("install", "youtube-dl")
        pip._internal.main("install", "youtube-dl")
    from youtube_dl import YoutubeDL
    from youtube_search import YoutubeSearch

ydl_opts = {
    'format': 'bestaudio/best',
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    'noplaylist':'True'
}

def downloadFile(url):
    local_filename = url.split('/')[-1]
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(local_filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192): 
                f.write(chunk)
    return local_filename

def dlThread(window, objVideo:dict):
    try:
        with YoutubeDL(ydl_opts) as ydl: ydl.download([f"http://youtube.com{objVideo['url_suffix']}"])
        os.rename(objVideo["title"] + "-" + objVideo["url_suffix"].replace("/watch?v=", "") + ".mp3", objVideo["title"] + ".mp3")
    except Exception as e:
        window.destroy()
        _type, value, traceback = sys.exc_info()
        messagebox.showerror(title="Error", message=f"{e.__name__} while downloading audio")
        raise Exception(value)
    window.destroy()
    messagebox.showinfo(title="info", message="download complete")
    exit(0)

if __name__ == "__main__":
    e = os.system("ffmpeg" + " > nul" if os.name == "nt" else " > /dev/null")
    e1 = os.system("./ffmpeg" + " > nul" if os.name == "nt" else  "> /dev/null")
    if e != 0 and e1 != 0:
        f = downloadFile("https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip" if os.name == "nt" else "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-linux64-gpl.tar.xz")
        if f.endswith(".zip"):
            with zipfile.ZipFile(f"./{f}") as zipref: zipref.extractall(".")
        else:
            with tarfile.TarFile(f"./{f}") as tarref: tarref.extractall(".")
    window = Tk()
    window.title("youtube to mp3 downloader")
    window.geometry("350x50")
    lbl = Label(window, text="search query")
    lbl.grid(column=0, row=0)
    txt = Entry(window, width=10)
    txt.grid(column=1, row=0)

    def clicked():
        global p
        p = txt.get()
        window.destroy()

    btn = Button(window, text="Submit", command=clicked)
    btn.grid(column=2, row=0)
    window.mainloop()
    del window

    window = Tk()
    window.title("youtube to mp3 downloader")
    results = YoutubeSearch(p, max_results=5).to_dict()
    m = []
    for i in range(5): m.append(len(results[i]["title"]))
    window.geometry(f"{str(int(7.4 * max(len(results[i]['title']) for i in range(5))))}x150")
    sel = IntVar()
    for i in range(1, 6): globals()[f"rad{i}"] = Radiobutton(window, text=results[i-1]["title"], value=i, variable=sel)

    def radioClicked():
        s = sel.get()

        if s == 0: messagebox.showerror(title="Error", message="Please select an option")
        else:
            window.destroy()
            root = Tk()
            root.geometry("300x60")
            root.title("Downloading, please wait...")
            root.grid()
            pb = Progressbar(root, orient='horizontal', mode='indeterminate', length=280)
            pb.grid(column=0, row=0, columnspan=2, padx=10, pady=20)
            pb.start()
            t = threading.Thread(target=dlThread, args=(root, results[s-1],))
            t.start()
            root.mainloop()
    
    btn = Button(window, text="Submit", command=radioClicked)
    for i in range(1, 6): globals()[f"rad{i}"].grid(column=0, row=i-1)
    btn.grid(column=0, row=5)
    window.mainloop()
