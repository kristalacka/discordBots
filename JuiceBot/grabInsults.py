import praw

reddit = praw.Reddit(client_id='<ID>',
                     client_secret='<Secret>',
                     user_agent='<UA>',
                     username='<UN>',
                     password='<pass>')

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
