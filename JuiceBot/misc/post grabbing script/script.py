import praw

reddit = praw.Reddit(client_id='gZbPvEUcPPHepw',
                     client_secret='JmzpEnSH-3z17wnYdRVMuUrekfM',
                     user_agent='Discord bot by /u/xxjuiceboxxx',
                     username='DCJuiceBot',
                     password='AwMiNoclan4f4')

file = open('insults.txt', 'w', encoding = 'utf-8')
subreddit=reddit.subreddit('insults')
posts=subreddit.top(limit=500)
for i, post in enumerate(posts):
    result=post.title+' '+post.selftext+'\n'
    if ('\n' not in post.selftext):
        file.write(result)
    print (str(i)+' ')
file.close()
print('done')

with open('insults.txt', encoding = 'utf-8') as infile, open('output.txt', 'w', encoding = 'utf-8') as outfile:
    for line in infile:
        if not line.strip(): continue  # skip the empty line
        outfile.write(line)  # non-empty line. Write it to output
