import time
import logging
import threading

from .arcui import ArcUI

logger = logging.getLogger(__name__)

def main():
    arcui = ArcUI(sensitivity=0.25)
    arcui_bi = arcui.add_page("bipolar")
    arcui_uni = arcui.add_page("unipolar")
    arcui_ang = arcui.add_page("angular")
    arcui_reel = arcui.add_page("reel")
    arcui_reel.sensitivity = 0.1

    @arcui.handler
    def _(event):
        print("Handler: ring = %d, position = %f, delta = %f" % (event.ring.index, event.position, event.delta))

    @arcui_bi.handler
    def _(event):
        print("Bipolar handler: ring = %d, position = %f, delta = %f" % (event.ring.index, event.position, event.delta))

    @arcui_uni.handler
    def _(event):
        print("Unipolar handler: ring = %d, position = %f, delta = %f" % (event.ring.index, event.position, event.delta))

    @arcui_ang.handler
    def _(event):
        print("Angular handler: ring = %d, position = %f, delta = %f" % (event.ring.index, event.position, event.delta))

    def runloop():
        while True:
            time.sleep(0.05)
            for ring in arcui_reel.rings:
                ring.position += 1
                ring.draw()
    thread = threading.Thread(target=runloop, daemon=True)
    thread.start()

    while True:
        try:
            page_index = input("Enter page number [0123]$ ")
            print(page_index)
            page_index = int(page_index.strip())
            arcui.set_current_page(page_index)
        except Exception as e:
            print("Exiting...")
            print(e)
            break

main()