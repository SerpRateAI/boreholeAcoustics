# this script downloads data from iris using the urls generated in the urls file
# it downloads data at 40 streams at a time noted by -P 40 for xargs
# you can increase or decrease the number of streams assuming you have enough
# bandwidth
# you need to replace 'username' and 'password' with whatever your username
# and password are
# you also need to replace the target location of '/datadirectory/' with
# whatever target location you want your data to go in
# files will be named after the url request that is taken from the urls file
# for example : 
#'queryauth?net=7F&sta=B07&cha=GH2&starttime=2019-01-01&endtime=2021-01-01&format=miniseed&nodata=404'
cat urls | xargs -n 1 -P 40 wget -P /datadirectory/ --user username --password password
