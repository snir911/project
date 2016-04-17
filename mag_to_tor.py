import shutil
import tempfile
import sys
import libtorrent as lt
from time import sleep

def magnet2torrent(magnet):
    tempdir = tempfile.mkdtemp()
    ses = lt.session()
    params = {
        'save_path': tempdir,
        'storage_mode': lt.storage_mode_t(2),
        'paused': False,
        'auto_managed': True,
        'duplicate_is_error': True,
        'flag_merge_resume_trackers': True
    }
    handle = lt.add_magnet_uri(ses, magnet, params)

    print("Downloading Metadata (this may take a while)")
    while (not handle.has_metadata()):
        try:
            sleep(1)
        except KeyboardInterrupt:
            print("Aborting...")
            ses.pause()
            print("Cleanup dir " + tempdir)
            shutil.rmtree(tempdir)
            sys.exit(0)
    ses.pause()
    shutil.rmtree(tempdir)
    print("Done")
    
    torinfo = handle.get_torrent_info()
    torfile = lt.create_torrent(torinfo)
    torcontent = lt.bencode(torfile.generate())
    return torcontent
