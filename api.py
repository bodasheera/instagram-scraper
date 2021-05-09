import requests
import json
import re


search_user = 'https://www.instagram.com/'
search_user_next_graph = 'https://www.instagram.com/graphql/query/?query_hash=42323d64886122307be10013ad2dcc44&variables={vars}'
search_hashtag = 'https://www.instagram.com/explore/tags/{tag}/?__a=1'
search_hashtag_next_graph = 'https://www.instagram.com/explore/tags/{tag}/?__a=1&max_id={max_id}'
graphql_query = 'https://www.instagram.com/graphql/query'
post_data = 'https://www.instagram.com/p/{shortcode}/?__a=1'


proxies = {
         'http': 'Enter Proxy here',
         'https': 'Enter Proxy here'
}


def get_user_profile(username: str):
    url = search_user + username
    
    resp = requests.get(url, proxies=proxies, verify=False)
    match = re.search(r'window\._sharedData = (.*);</script>', resp.text)
    if match is not None:
        resp_json = json.loads(match.group(1))
        entry_data = resp_json.get('entry_data')
        post_or_profile_page = list(entry_data.values())[0] if entry_data is not None else None
        if post_or_profile_page is None:
            print("window._sharedData does not contain required keys.")
        if 'graphql' not in post_or_profile_page[0]:
            match = re.search(r'window\.__additionalDataLoaded\([^{​​​​​​​​]+{​​​​​​​​"graphql":({​​​​​​​​.*}​​​​​​​​)}​​​​​​​​\);</script>',resp.text)
            if match is not None:
                post_or_profile_page[0]['graphql'] = json.loads(match.group(1))
        return post_or_profile_page[0]['graphql']['user']

def get_user_data(parameters: dict):
    """ Get the user data details from username
        Args:
            parameters (dict): The username and next id of the person who posted the instagram post
        Returns:
            Response : Response object of GET request
    """
    vars = {'id': parameters['user_id'] , 'first': 12 , 'after': parameters['next_id']}
    if parameters['next_id'] == '':
        return get_user_profile(parameters['name'])

    elif parameters['next_id'] != '':
        url = search_user_next_graph.replace('{vars}',json.dumps(vars))
       
        response = requests.get(url, proxies=proxies, verify=False)

        response = json.loads(response.text)
        return response['data']['user']

def get_posts_by_hashtag(parameters: dict):

    """ Get list of instagram posts by hashtag search
         Args:
            parameters (dict): The parameters to pass to the GET request
        Returns:
            Response : Response object of GET request
    """
    if parameters['next_id'] == '':
        url = search_hashtag.replace('{tag}', parameters['name'])

    elif parameters['next_id'] != '':
        url = search_hashtag_next_graph.replace('{tag}', parameters['name']).replace('{max_id}',parameters['next_id'])

    response = requests.get(url, proxies=proxies, verify=False)
    posts_graph = json.loads(response.text)
    return posts_graph['graphql']['hashtag']

def get_comments_replies(parameters: dict):
    query_hash= '97b41c52301f77ce508f55e66d17620e'
        # if threaded_comments_available == True else 'f0986789a5c5d17c2400faebf16efd0d'
    variables = json.dumps(parameters)
    params = {
        'query_hash': query_hash,
        'variables': variables
    }
    return requests.get(graphql_query,params=params, proxies=proxies, verify=False)

def get_post_comment_details(shortcode):
    """  Get the Post Details of a particular post
        Args:
            shortcode (string): The shortcode id of the post
        Returns:
            Response : Response object of GET request
    """
    post_url = post_data.replace('{shortcode}', shortcode)
    return requests.get(post_url, proxies=proxies, verify=False)


# API -> Top Posts 
# id 