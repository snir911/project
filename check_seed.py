import libtorrent as lt
from time import sleep
from mag_to_tor import magnet2torrent
ip_table2 = []
def checkseed(ip_table2):
    from optparse import OptionParser

    parser = OptionParser()

    parser.add_option('-p', '--port',
        type='int', help='set listening port')

    parser.add_option('-d', '--max-download-rate',
        type='float', help='the maximum download rate given in kB/s. 0 means infinite.')

    parser.add_option('-u', '--max-upload-rate',
        type='float', help='the maximum upload rate given in kB/s. 0 means infinite.')

    parser.add_option('-s', '--save-path',
        type='string', help='the path where the downloaded file/folder should be placed.')

    parser.add_option('-a', '--allocation-mode',
        type='string', help='sets mode used for allocating the downloaded files on disk. Possible options are [full | compact]')

    parser.add_option('-r', '--proxy-host',
        type='string', help='sets HTTP proxy host and port (separated by \':\')')

    parser.set_defaults(
        port=6881
      , max_download_rate=0
      , max_upload_rate=0
      , save_path='.'
      , allocation_mode='compact'
      , proxy_host=''
    )

    (options, args) = parser.parse_args()

    if options.port < 0 or options.port > 65525:
        options.port = 6881

    options.max_upload_rate *= 1000
    options.max_download_rate *= 1000

    if options.max_upload_rate <= 0:
        options.max_upload_rate = -1
    if options.max_download_rate <= 0:
        options.max_download_rate = -1

    compact_allocation = options.allocation_mode == 'compact'

    settings = lt.session_settings()
    settings.user_agent = 'python_client/' + lt.version

    ses = lt.session()
    ses.set_download_rate_limit(int(options.max_download_rate))
    ses.set_upload_rate_limit(int(options.max_upload_rate))
    ses.listen_on(options.port, options.port + 10)
    ses.set_settings(settings)
    ses.set_alert_mask(0xfffffff)
    
    if options.proxy_host != '':
        ps = lt.proxy_settings()
        ps.type = lt.proxy_type.http
        ps.hostname = options.proxy_host.split(':')[0]
        ps.port = int(options.proxy_host.split(':')[1])
        ses.set_proxy(ps)
        
    magnet=raw_input("Please enter magnet link ")
    rawdata = magnet2torrent(magnet)
    di=lt.bdecode(rawdata)
    info = lt.torrent_info(di)
    
    atp = {}
    atp["save_path"] = options.save_path
    atp["storage_mode"] = lt.storage_mode_t.storage_mode_sparse
    atp["paused"] = False
    atp["auto_managed"] = True
    atp["duplicate_is_error"] = True
    handles = []
    
    print('Adding \'%s\'...' % info.name())
    atp["ti"] = info

    h = ses.add_torrent(atp)
    handles.append(h)
    torrent_inf=h.get_torrent_info()
    trackers = torrent_inf.trackers() 
    x=1
    i=0
    while(x==1):
        peers=h.get_peer_info()
        for p in peers:
            if p.ip not in ip_table2:
                if p.flags & lt.peer_info.seed : #this peer is a seed
                    ip_table2.append(p.ip)
                    i=i+1 
                    print i
                    if i>3:
                        x=0   
                    
    for el in ip_table2:
        print el   