import twitter
import os
import os.path
import nsb_twitter




configPath = '/home/hatten/.config/cotn/'

t = nsb_twitter.twit(configPath + 'twitter/')

print(t.userTweetCount("necro_score_bot"))
rank = [0,0,0,0,0,0,0,0,0,0]
deathless = 0
speedrun = 0
score = 0
hits = [0]*30
for i in t.timeline("necro_score_bot"):
    if 'RT' in i['text']:
        continue
    elif 'Deathless' in i['text']:
        #for i in i['text'].split():
            #if i.isdigit():
                #rank[int(i)-1] += 1
        deathless += 1
    elif 'Speed' in i['text']:
        speedrun += 1
    else:
        score += 1
    hits[int(i['created_at'].split()[2])-1] += 1


print("DL:", deathless, "spd:", speedrun, "hc:", score, "sum:", deathless+speedrun+score)
print(hits)
