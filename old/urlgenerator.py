url = 'https://service.iris.edu/fdsnws/dataselect/1/queryauth?net=7F&sta={station}&cha={channel}&starttime=2019-01-01&endtime=2021-01-01&format=miniseed&nodata=404'

with open('urls', 'w') as f:
    f.writelines([url.format(station=s, channel=c)+'\n' for s, c in zip(stations, channels)])
    f.close()
