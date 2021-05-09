import api as api

import re
import json
import datetime as dt
import time
from tqdm import tqdm
import pandas as pd

import os
from datetime import datetime

output_directory = './Datasets/'

excluded_user_keys = [
                        'blocked_by_viewer','restricted_by_viewer','country_block','edge_mutual_followed_by',
                        'edge_media_collections','edge_felix_video_timeline','edge_owner_to_timeline_media',
                        'edge_saved_meset_output_directorydia','requested_by_viewer','profile_pic_url','has_requested_viewer',
                     ]

top_posts = []
all_posts = []
all_comments = []
all_comments_replies = []
all_tagged_users = []
all_users = []

def get_output_directory(type,name):
    """Get output directory for saving scrapped data
        Returns:
                string : returns a output directory
    """
    return output_directory + type + "_" + name + "_"

def save_postdata_fromgraph(posts_edges,type,is_top_posts=False):
    """Save all posts from Hashtag/Username Graph Api - Typically each Hashtag Graph will have 65-70 posts
         Args:
            posts_edges (List(dict)): The partial posts data from the Graph Api
            type (str): The type of data to be scraped username or hashtag
            top_posts (bool) : If top posts , only applicable for hashtag type
    """
    global top_posts
    for edge in tqdm(posts_edges):
        is_post_present = len(edge['node']['edge_media_to_caption']['edges'])
        if is_post_present:
            post = get_post(edge,type)
            if is_top_posts is False:
                all_posts.append(post)
            elif is_top_posts is True:
                top_posts.append(post)



def get_post(edge: dict,type):
    """Filter and returns all important posts data parameters
         Args:
            edge (dict): The edge of a posts graph where each edge represents a post
         Returns:
            dict : The partial meta data associated with the post
    """
    post_node = edge['node']

    caption = post_node['edge_media_to_caption']['edges'][0]['node']['text']
    hashtags = get_caption_hashtags(caption)
    timestamp = dt.datetime.fromtimestamp(post_node['taken_at_timestamp']).strftime('%Y-%m-%d %H:%M:%S')
    shortcode = get_shortcode_post(edge)
    comments = int(post_node['edge_media_to_comment']['count'])
    post_id = post_node['id']

    if type == "hashtag":
        likes = int(post_node['edge_liked_by']['count'])
    elif type == "username":
        likes = int(post_node['edge_media_preview_like']['count'])

    # post_graph_data = get_comments_replies(shortcode, comments, post_id)
    # get_user_meta_data(post_graph_data['owner']['username'])

    post = {
        'post_id': post_id,
        'user_id': edge['node']['owner']['id'],
        'short_code': shortcode,
        'caption': caption,
        'hashtags': hashtags,
        'image': post_node['thumbnail_src'],
        'comments': comments,
        'likes':  likes,
        'mentions': get_caption_mentions(caption),
        'accessibility': post_node['accessibility_caption'] if type == "hashtag" else "",
        'timestamp': timestamp,
    }
    return post

def get_shortcode_post(edge: str):
    """Media shortcode. URL of the post is instagram.com/p/<shortcode>/.
        Args:
            edge (dict): The edge of a posts graph where each edge represents a post
        Returns:
            str: shortcode id of the post
    """
    return edge['node']['shortcode'] if 'shortcode' in edge['node'] else edge['node']['code']


def get_caption_hashtags(caption: str):
    """List of all lowercased hashtags (without preceeding #) that occur in the Post's caption.
         Args:
            caption (string): The caption posted by the user
        Returns:
            List[str]: List of hashtags are present , Empty list otherwise.
    """
    if not caption:
        return []
    hash_tags = re.compile(r'(?i)(?<=\#)\w+', re.UNICODE)
    return ['#' + hashtag for hashtag in hash_tags.findall(caption)]


def get_caption_mentions(caption: str):
    """List of all lowercased profiles that are mentioned in the Post's caption, without preceeding @.
        Args:
            caption (string): The caption posted by the user
        Returns:
            List[str]: List of strings if mentions are present , Empty list otherwise.
    """
    if not caption:
        return []

    mention_regex = re.compile(r"(?:@)(\w(?:(?:\w|(?:\.(?!\.))){0,28}(?:\w))?)")
    return re.findall(mention_regex,caption)



def check_graph_next_node(page_info: dict):
    """List of all lowercased hashtags (without preceeding #) that occur in the Post's caption.
         Args:
            page_info (dict): The page info for the graph
         Return:
            string : The next_id pointing to a new graph
            string : True if last graph for the hashtag else False
    """
    if_last_item = False
    next_id = ''

    if page_info['has_next_page'] is True:
        next_id = page_info['end_cursor']
    elif page_info['has_next_page'] is False:
        if_last_item = True

    return next_id, if_last_item



def get_all_posts():
    """Get all posts associated with a hashtag
        Returns:
            List (dict): returns a list of dictionary
    """
    return all_posts

    
    
def get_top_posts():
    """Get all top posts for a hashtag
            Returns:
                List (dict): returns a list of dictionary
        """
    return top_posts


def save_user_meta_data(user_graph,type,name):
    """Saves the user profile details and returns user id
         Args:
            user_graph (dict): The username of a Instagram User
         Returns:
            dict : The userid
    """

    user_meta_data = {k: v for (k, v) in user_graph.items() if k not in excluded_user_keys}
    output_directory = get_output_directory(type,name)
    with open(output_directory + 'metadata.json', 'w') as outfile:
        json.dump(user_meta_data, outfile)
    return user_meta_data['id']

def save_users_hashtag(user_graph):
    user_meta_data = {k: v for (k, v) in user_graph.items() if k not in excluded_user_keys}
    return user_meta_data


def save_post_tagged_user_data(tagged_dataset,post_id):
    global all_tagged_users
    """Save users who were tagged in the post
        Args:
             tagged_dataset (List(dict)): The list of all the tagged users
    """
    users = [user_dict['node']['user'] for user_dict in tagged_dataset]
    for user in users:
        user["postid"] = post_id
    all_tagged_users = all_tagged_users + users


def add_user_details_hashtag(username):
    parameters = {
        'user_id': '',
        'next_id': '',
        'name': username
    }
    try:
        graph = api.get_user_data(parameters)
        # graph = json.loads(response.text)
        # graph = graph['graphql']['user']
        user = save_users_hashtag(graph)
        if user not in all_users:
            all_users.append(user)
    except:
        print("Error for username")
        # api.ip_rotation()
        # response = api.get_user_data(parameters)
        graph = api.get_user_data(parameters)
        if isinstance(graph,dict):
            print(graph)
            # graph = graph['graphql']['user']
            user = save_users_hashtag(graph)
            all_users.append(user)
        print(f"Error finding data for {username}")


def save_replies(comment_data,post_id):
    """All replies to the comments of the post are saved in all_comments_replies list
         Args:
            comment_data (dict): The comment data which has all replies
    """
    try:
        for thread_comment in comment_data['edge_threaded_comments']['edges']:
            reply_data = thread_comment['node']

            all_comments_replies.append({
                'comment_id': comment_data['id'],
                'reply_id': reply_data['id'],
                'user_id': reply_data['owner']['id'],
                'username': reply_data['owner']['username'],
                'reply': reply_data['text'],
                'profile_pic': reply_data['owner']['profile_pic_url'],
                'is_verified': reply_data['owner']['is_verified'],
                'likes': reply_data['edge_liked_by']['count'],
                'timestamp': dt.datetime.fromtimestamp(reply_data['created_at']).strftime('%Y-%m-%d %H:%M:%S')
            })
    except:
        print(f"Failed to get comments for post id {post_id} and comment_id {comment_data['id']}")


def update_post_details(posts_df, index, post_graph):
    """Update post details and add data from Post Shortcode Graph Api
         Args:
            posts_df (DataFrame): The partial post data got from the Hashtag Graph
            index (int): The current iterator index while looping posts_df Dataframe
            post_graph (dict): The full post details data
    """
    posts_df.loc[posts_df.index[index], 'username'] = post_graph['owner']['username']
    posts_df.loc[posts_df.index[index], 'full_name'] = post_graph['owner']['full_name']
    posts_df.loc[posts_df.index[index], 'is_verified'] = post_graph['owner']['is_verified']
    posts_df.loc[posts_df.index[index], 'is_private'] = post_graph['owner']['is_private']
    posts_df.loc[posts_df.index[index], 'profile_pic_url'] = post_graph['owner']['profile_pic_url']
    posts_df.loc[posts_df.index[index], 'total_posts'] = post_graph['owner']['edge_owner_to_timeline_media']['count']

    posts_df.loc[posts_df.index[index], 'location'] = post_graph['location']['name'] if post_graph['location'] else ''
    posts_df.loc[posts_df.index[index], 'tagged_users_count'] = len(post_graph['edge_media_to_tagged_user']['edges'])
    posts_df.loc[posts_df.index[index], 'is_ad'] = post_graph['is_ad']
    posts_df.loc[posts_df.index[index], 'comments_disabled'] = post_graph['comments_disabled']

    posts_df.loc[posts_df.index[index], 'is_video'] = post_graph['is_video']
    posts_df.loc[posts_df.index[index], 'video_url'] = post_graph['video_url'] if 'video_url' in post_graph.keys() else ''
    posts_df.loc[posts_df.index[index], 'video_view_count'] = post_graph['video_view_count'] if 'video_view_count' in post_graph.keys() else ''
    posts_df.loc[posts_df.index[index], 'video_duration'] = post_graph['video_duration'] if 'video_duration' in post_graph.keys() else ''

    if len(post_graph['edge_media_to_tagged_user']['edges']) > 0:
        save_post_tagged_user_data(post_graph['edge_media_to_tagged_user']['edges'],post_graph['id'])

def get_comments(comment_edges,threaded_comments_available,post_id):
    """Get all the to comments associated with a post . Calls replies function to get replies
         Args:
            comment_edges (str): The comments edges in comments graph
            threaded_comments_available (boolean): True if there are replies to the comments, otherwise False
            post_id (str) : unique post id
    """
    try:
        for edge in comment_edges:
            comment_data = edge['node']
            all_comments.append({
                'post_id': post_id,
                'comment_id': comment_data['id'],
                'user_id': comment_data['owner']['id'],
                'username': comment_data['owner']['username'],
                'comment': comment_data['text'],
                'replies': comment_data['edge_threaded_comments']['count'],
                'profile_pic': comment_data['owner']['profile_pic_url'],
                'is_verified': comment_data['owner']['is_verified'],
                'likes': comment_data['edge_liked_by']['count'],
                'timestamp': dt.datetime.fromtimestamp(comment_data['created_at']).strftime('%Y-%m-%dt %H:%M:%S')
            })

            if threaded_comments_available:
                save_replies(comment_data,post_id)
    except:
        print(f"Failed to get comments for post id {post_id}")

def get_comments_replies(shortcode, post_id,comments):
    """Gets all the comments and replies to the comments associated with a post
         Args:
            shortcode (str): The shortcode of the post
            post_id (str) : The id of the post
        Returns:
            dict : The post graph data

    """
    params = {'shortcode': shortcode, 'first': 50}
    max_comments = 500
    found_comments_count = 0

    while True:
        response = api.get_post_comment_details(shortcode)
        try:
            post_details_data = json.loads(response.text)['graphql']['shortcode_media']
        except:
            print(f"Error for post data {post_id}")
            post_details_data = ""
            break

        if comments == 0:
            break
        elif comments < 50:
            try:
                comment_edges = post_details_data['edge_media_to_parent_comment']['edges']
                threaded_comments_available = True
                # answers_count = sum([edge['node']['edge_threaded_comments']['count'] for edge in comment_edges])
                get_comments(comment_edges, threaded_comments_available, post_id)
                break
            except:
                print(f"Error getting comment edges ")
        else:
            try:
                response = api.get_comments_replies(params)
                post_graph_data = json.loads(response.text)['data']['shortcode_media']
            except:
                print("Error")
                time.sleep(320)
                # api.ip_rotation()
                # api.instagram_login()
                response = api.get_comments_replies(params)
                post_graph_data = json.loads(response.text)
                if isinstance(post_graph_data, dict):
                    post_graph_data = post_graph_data['data']['shortcode_media']
                else:
                    break
            try:
                comment_edges = post_graph_data['edge_media_to_parent_comment']['edges']
                # answers_count = sum([edge['node']['edge_threaded_comments']['count'] for edge in comment_edges])
                threaded_comments_available = True
            except KeyError:
                comment_edges = post_graph_data['edge_media_to_comment']['edges']
                # answers_count = 0
                threaded_comments_available = False

            if len(comment_edges) > 500:
                print(f"comments are : {len(comment_edges)}")
            found_comments_count = found_comments_count + len(comment_edges)

            get_comments(comment_edges, threaded_comments_available, post_id)


            page_info = post_graph_data['edge_media_to_parent_comment']['page_info']

            # if found_comments_count >= max_comments:
            #     difference = max_comments - found_comments_count
            #     get_comments(comment_edges[:difference + 1], threaded_comments_available, post_id)
            #     break


            if page_info['has_next_page'] is True:
                params['post_id'] = post_id
                params['after'] = page_info['end_cursor']
            elif page_info['has_next_page'] is False:
                break

    return post_details_data

def get_full_posts_comments(posts_df,type):
    posts_df = posts_df.head(10)
    for index,post in tqdm(enumerate(posts_df.itertuples())):

        post_graph = get_comments_replies(post.short_code, post.post_id,post.comments)
        if isinstance(post_graph, str) and post_graph == "":
            continue
        else:
            update_post_details(posts_df,index,post_graph)
            if type == "hashtag":
                add_user_details_hashtag(posts_df.loc[index]['username'])
    return posts_df

def get_all_comments():
    """Get all comments of the post
        Returns:
            List (dict): returns a list of dictionary
    """
    return all_comments


def get_all_comments_replies():
    """Get all replies to the comments
        Returns:
            List (dict): returns a list of dictionary
    """
    return all_comments_replies


def get_all_tagged_users():
    """Get all users who where tagged in the post
        Returns:
            List (dict): returns a list of dictionary
    """
    return all_tagged_users


def get_all_users():
    """Get all users who posted a Post on Instagram
            Returns:
                List (dict): returns a list of dictionary
        """
    return all_users