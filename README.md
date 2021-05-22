# Instagram Scraper

## Types of data scraping available

1. By Hashtag -> Top Posts , All Posts, Comments and replies for posts 
2. By Username -> All Posts, Comments and replies for posts 

#### Note: You can also get information such as if its verified profile , ad post , if video , video url , video duration . video views , HD image of post images 

## How to run code

1. create a virtual environment and install the libraries from requirement.txt file
2. Create a empty folder called "Datasets" . The data will get saved in that folder .
3. Add a proxy in the api.py to run the code . Please note that the code is designed to scrape unlimited data without any rate limit restrictions so we are not logging in as a user and we will be using proxy to change IP addresses continuosly so that we won't get blocked . So this code will not work without a proxy.
4. You can modify the code to run without proxy . But then you will not be able to scrape posts by username or get advanced user details for any posts which you scrape by hastags ( unless you login )
5. I have tested the code with luminati proxy and it is fine 

## How to scrape data 

1. Create a new python file add following code to scrape by hashtags

```python 
import instagram as insta

count = get_posts_hashtags('hashtag','pepsi', None) 
# type of data to scrape => hashtag 
# hastag to scrape => pepsi 
# start year to scrape => None , you can add python timestamp
# This will scrape top posts , all posts without comments and replies 
# comment below line get_comments_replies() before running code 

get_comments_replies('hashtag', 'pepsi')
# comment above line get_posts_hashtags() before running code  The code is not pipeline so you need to run by commenting it .
# You will get comments and replies for all posts hashtags amd top posts hastags . You will also get user bio details 

```

2. Create a new python file add following code to scrape by posts

```python 
import instagram as insta

count = get_posts_username('username','thenameisyash',None)
# type of data to scrape => username 
# user to scrape => thenameisyash 
# start year to scrape => None , you can add python timestamp
# This will scrape user posts without comments and replies 
# comment below line get_comments_replies() before running code 

get_comments_replies('hashtag', 'pepsi')
# comment above line get_posts_username() before running code  The code is not pipeline so you need to run by commenting it .
# You will get comments and replies for posts by user 

```

Please feel free to optimize the code and contribute to the code by sending a pull request . 

