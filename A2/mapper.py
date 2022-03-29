#! /usr/bin/python
import sys
import json
import re
#jsonData1 = '{"a":1,"b":2,"c":3,"d":4,"e":5}';
#jsonData = '{"created_at":"Tue May 13 11:38:51 +0000 2014","id":466180771209048064,"id_str":"466180771209048064","text":"hon hen det han den h\u00e4r dagen \u00e4r ju helt v\u00e4rdel\u00f6s","source":"web","truncated":false,"in_reply_to_status_id":null,"in_reply_to_status_id_str":null,"in_reply_to_user_id":null,"in_reply_to_user_id_str":null,"in_reply_to_screen_name":null,"user":{"id":474758865,"id_str":"474758865","name":"lisa k\u00f6rner \u2020","screen_name":"liisuus","location":"","url":"http:\/\/www.liisuus.blogg.se","description":"skrattar. gr\u00e5ter. andas. lever \/ 18, sweden","protected":false,"followers_count":202,"friends_count":490,"listed_count":0,"created_at":"Thu Jan 26 09:45:04 +0000 2012","favourites_count":12170,"utc_offset":7200,"time_zone":"Stockholm","geo_enabled":true,"verified":false,"statuses_count":11019,"lang":"sv","contributors_enabled":false,"is_translator":false,"is_translation_enabled":false,"profile_background_color":"ACDED6","profile_background_image_url":"http:\/\/pbs.twimg.com\/profile_background_images\/755654800\/6b2ee5b3801cee3dc292d95f607bb87c.png","profile_background_image_url_https":"https:\/\/pbs.twimg.com\/profile_background_images\/755654800\/6b2ee5b3801cee3dc292d95f607bb87c.png","profile_background_tile":true,"profile_image_url":"http:\/\/pbs.twimg.com\/profile_images\/463784356876529664\/za9TZvZI_normal.jpeg","profile_image_url_https":"https:\/\/pbs.twimg.com\/profile_images\/463784356876529664\/za9TZvZI_normal.jpeg","profile_banner_url":"https:\/\/pbs.twimg.com\/profile_banners\/474758865\/1399639962","profile_link_color":"333333","profile_sidebar_border_color":"EEEEEE","profile_sidebar_fill_color":"F6F6F6","profile_text_color":"038543","profile_use_background_image":true,"default_profile":false,"default_profile_image":false,"following":null,"follow_request_sent":null,"notifications":null},"geo":null,"coordinates":null,"place":null,"contributors":null,"retweet_count":0,"favorite_count":0,"entities":{"hashtags":[],"symbols":[],"urls":[],"user_mentions":[]},"favorited":false,"retweeted":false,"filter_level":"medium","lang":"sv"}';
for jsonData in sys.stdin:
 if  jsonData[0] == '{' :
    print ("%s\t%s" % ('tweets', 1)); 
    tweet = json.loads(jsonData);
    #print("Success!\n");
    if "retweeted_status" in tweet:
        #print("This is a retweeted tweet.\n");
        pass;
    else:
        #print("This is a unique tweeted tweet.\n");
        #print(tweet["text"]);
        print ("%s\t%s" % ('uniquetweets', 1));
        line = tweet["text"];
        line = line.strip();
        match1=re.search(r'\bhan\b',line,re.I);
        if match1:
            print ("%s\t%s" % ('han', 1));
        match2=re.search(r'\bhon\b',line,re.I);
        if match2:
            print ("%s\t%s" % ('hon', 1));
        match3=re.search(r'\bden\b',line,re.I);
        if match3:
            print ("%s\t%s" % ('den', 1));
        match4=re.search(r'\bdet\b',line,re.I);
        if match4:
            print ("%s\t%s" % ('det', 1));
        match5=re.search(r'\bdenna\b',line,re.I);
        if match5:
            print ("%s\t%s" % ('denna', 1));
        match6=re.search(r'\bdenne\b',line,re.I);
        if match6:
            print ("%s\t%s" % ('denne', 1));
        match7=re.search(r'\bhen\b',line,re.I);
        if match7:
            print ("%s\t%s" % ('hen', 1));
        
else:
    pass;
