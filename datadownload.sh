cat urls | xargs -n 1 -P 40 wget -P /datadirectory/ --user username --password password
