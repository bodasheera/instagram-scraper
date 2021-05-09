import json
import  api as api
import modules as md
from datetime import datetime
import datetime as dt
import pandas as pd

def get_posts_hashtags(type,name,year):
    print(f"Get Posts for {type} : {name} \n\n")
    parameters = {
        'user_id': '',
        'name': name,
        'next_id': ''
    }
    graph_index = 0
    max_posts = 100
    current_total = 0
    total_posts = 0
    posts_graph = ""
    posts_edges = ""
    page_info = ""
    while True:
        print(f"Graph {graph_index} in the cluster")

        
        posts_graph = api.get_posts_by_hashtag(parameters)
      

        if posts_graph == {}:
            f = open("log.txt", "a")
            f.write(f"No {type} available for {name} ")
            f.close()
            return 0


        if graph_index == 0:
            
            top_post_edges = posts_graph['edge_hashtag_to_top_posts']['edges']
            md.save_postdata_fromgraph(top_post_edges, type, is_top_posts=True)
            total_posts = posts_graph['edge_hashtag_to_media']['count']
            
            print(f"Total posts available for the {type} {name} : {total_posts}")

        
        posts_edges = posts_graph['edge_hashtag_to_media']['edges']
      

        if year != None:
            temp_edges = []
            wrong_year_count = 0
            for edge in posts_edges:
                timestamp = dt.datetime.fromtimestamp(edge['node']['taken_at_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                if timestamp < year:
                    wrong_year_count +=1
                elif timestamp > year:
                    temp_edges.append(edge)

            if wrong_year_count == len(posts_edges):
                break
            else:
                md.save_postdata_fromgraph(temp_edges, type)
        else:
            md.save_postdata_fromgraph(posts_edges, type)

        
        page_info = posts_graph['edge_hashtag_to_media']['page_info']
       

        parameters['next_id'], if_last_item = md.check_graph_next_node(page_info)
        graph_index = graph_index + 1

        if if_last_item:
            break

        if max_posts != -1:
            current_total = current_total + len(posts_edges)
            if current_total >= max_posts:
                with open(md.get_output_directory(type,name) + 'nextid.json', 'w') as outfile:
                    json.dump(parameters['next_id'], outfile)
                break

    all_posts_df = pd.DataFrame(md.get_all_posts())

    print(f"Total posts collected for {type} {name} : {all_posts_df.shape[0]}")

    output_directory = md.get_output_directory(type,name)
    all_posts_df.to_csv(output_directory + "raw_posts.csv",index=False,encoding="utf-8-sig")

    if type == "hashtag":
        top_posts_df = pd.DataFrame(md.get_top_posts())
        top_posts_df.to_csv(output_directory + "raw_top_posts.csv", index=False, encoding="utf-8-sig")

    return all_posts_df.shape[0]

def get_posts_username(type,name,year):
    print(f"Get Posts for {type} : {name} \n\n")
    parameters = {
        'user_id': '',
        'name': name,
        'next_id': ''
    }
    graph_index = 0
    max_posts = -1
    current_total = 0
    total_posts = 0
    posts_graph = ""
    posts_edges = ""
    page_info = ""
    while True:
        print(f"Graph {graph_index} in the cluster")

       
        posts_graph = api.get_user_data(parameters)


        if posts_graph == {}:
            f = open("log.txt", "a")
            f.write(f"No {type} available for {name} ")
            f.close()
            return 0

        
        if not parameters['user_id']:
            parameters['user_id'] = md.save_user_meta_data(posts_graph,type,name)

        if graph_index == 0:
           
            
            total_posts = posts_graph['edge_owner_to_timeline_media']['count']

            print(f"Total posts available for the {type} {name} : {total_posts}")

       
        posts_edges = posts_graph['edge_owner_to_timeline_media']['edges']


        if year != None:
            temp_edges = []
            wrong_year_count = 0
            for edge in posts_edges:
                timestamp = dt.datetime.fromtimestamp(edge['node']['taken_at_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
                timestamp = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
                if timestamp < year:
                    wrong_year_count +=1
                elif timestamp > year:
                    temp_edges.append(edge)

            if wrong_year_count == len(posts_edges):
                break
            else:
                md.save_postdata_fromgraph(temp_edges, type)
        else:
            md.save_postdata_fromgraph(posts_edges, type)

        
        page_info = posts_graph['edge_owner_to_timeline_media']['page_info']

        parameters['next_id'], if_last_item = md.check_graph_next_node(page_info)
        graph_index = graph_index + 1

        if if_last_item:
            break

        if max_posts != -1:
            current_total = current_total + len(posts_edges)
            if current_total >= max_posts:
                with open(md.get_output_directory(type,name) + 'nextid.json', 'w') as outfile:
                    json.dump(parameters['next_id'], outfile)
                break

    all_posts_df = pd.DataFrame(md.get_all_posts())

    print(f"Total posts collected for {type} {name} : {all_posts_df.shape[0]}")

    output_directory = md.get_output_directory(type,name)
    all_posts_df.to_csv(output_directory + "raw_posts.csv",index=False,encoding="utf-8-sig")

    return all_posts_df.shape[0]

def get_comments_replies(type,name):
    datadict = {}
    print(f"Get Full post details , comments and replies for {type} {name}\n\n")
    output_directory = md.get_output_directory(type,name)
    file = output_directory + "raw_posts.csv"
    posts_df = pd.read_csv(file)
    posts_df = md.get_full_posts_comments(posts_df,type)

    if type == "hashtag":
        file = output_directory + "raw_top_posts.csv"
        top_posts_df = pd.read_csv(file)
        top_posts_df = md.get_full_posts_comments(top_posts_df, type)

    all_comments_df = pd.DataFrame(md.get_all_comments())
    all_replies_df = pd.DataFrame(md.get_all_comments_replies())
    all_tagged_users_df = pd.DataFrame(md.get_all_tagged_users())

    posts_df.to_csv(output_directory + 'All_Posts.csv', index=False, encoding='utf-8-sig')
    all_tagged_users_df.to_csv(output_directory + 'All_Tagged_Users.csv', index=False, encoding='utf-8-sig')
    all_comments_df.to_csv(output_directory + 'All_Comments.csv', index=False, encoding='utf-8-sig')
    all_replies_df.to_csv(output_directory + 'All_Replies.csv', index=False, encoding='utf-8-sig')

    datadict = {
        "Posts": posts_df,
        "Comments": all_comments_df,
        "Replies": all_replies_df,
        "Tagged_Users": all_tagged_users_df
    }

    if type == "hashtag":
        all_users_df = pd.DataFrame(md.get_all_users())
        datadict['All Users'] = all_users_df
        datadict['Top Posts'] = top_posts_df
        all_users_df.to_csv(output_directory + 'All_Users.csv', index=False, encoding='utf-8-sig')
        top_posts_df.to_csv(output_directory + 'Top_Posts.csv', index=False, encoding='utf-8-sig')


# data = get_posts_hashtags('hashtag','pepsi', None)

data = get_posts_username('username','thenameisyash',None)
get_comments_replies('username', 'thenameisyash')


# Hashtag
# 1. Top/Hot Posts -> Most impressions 
# 2. All Posts 
# Faster to scrape . only comment count is available .

# Basic Details 
# Profile 