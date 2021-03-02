import requests
import json
import random
import string

CONFIG_PATH = r"bot.config"
API_URL = "http://127.0.0.1:8000/"
POST = {"content": "hello"}


def get_auth_header(token):
    return {'Authorization': 'Token {}'.format(token)}


def read_config(path=CONFIG_PATH):
    """
    reads the bot config (JSON)
    :param path: string, path to config file
    :return: dict containing configuration
    """
    with open(path, 'rb') as f:
        conf = json.load(f)
    return conf


def signup_users(n):
    """
    signs up a given ammoun of users
    :param n: number of users to signup
    :return: dict of username to JWT token
    """
    users = {}
    counter = 0
    while len(users.keys()) < n:
        username = "user{}".format(counter)
        email = "user{}@gmail.com".format(counter)
        password = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(10))
        signup = {"username": username, "email": email, "password": password, "confirm_password": password}
        res = requests.post(API_URL + "register/", json=signup)
        if res.status_code == 201:
            auth = {"username": username, "password": password}
            res = requests.post(API_URL+"api-token-auth/", json=auth)
            users[username] = res.json()['token']
        counter += 1
    return users


def create_posts(users, max_posts):
    """
    creates a random amount of posts per user, up to max_posts
    :param users: user dict
    :param max_posts: int, maximum amount of posts per user
    :return: None
    """
    for username in users.iterkeys():
        user_posts = random.randint(0, max_posts)
        header = get_auth_header(users[username])
        for i in xrange(user_posts):
            requests.post(API_URL+"posts/", json=POST, headers=header)


def find_next_user(users, max_likes):
    """
    finds nex user that will like posts
    :return: username, number of likes
    """
    # authenticating with random user
    header = get_auth_header(users.values()[0])
    user_list = requests.get(API_URL+"users/", headers=header).json()
    username = None
    posts = None
    likes = None
    for u in user_list:
        if len(u['posts']) > posts and len(u['liked_posts']) < max_likes and u['username'] in users.keys():
            username = u['username']
            posts = len(u['posts'])
            likes = len(u['liked_posts'])
    return username, likes


def continue_liking(token):
    """
    looks for a post with zero likes
    :return: Bool, False if no posts with zero likes, True otherwise
    """
    header = get_auth_header(token)
    post_list = requests.get(API_URL + "posts/", headers=header).json()
    for post in post_list:
        if not post['likes']:
            return True
    return False


def get_users_with_zero_likes(token):
    """
    :param token: auth token
    :return: a list of usernames who have at least one post with zero likes
    """
    header = get_auth_header(token)
    post_list = requests.get(API_URL + "posts/", headers=header).json()
    unliked_users = []
    for post in post_list:
        if not post['likes'] and post['creator'] not in unliked_users:
            unliked_users.append(post['creator'])
    return unliked_users


def like_posts(users, max_likes):
    """
    nex user to like is the user who has most posts and has not reached max likes
    user likes until he reaches max likes
    user can only like post from users who have at least one post with zero likes
    bot stops when there are no posts with zero likes
    :param users: user dict
    :return: None
    """
    username, likes = find_next_user(users, max_likes)
    while username:
        header = get_auth_header(users[username])
        posts = requests.get(API_URL+"posts/", headers=header).json()
        user_id = get_user_id(username, users[username])
        unliked_users = get_users_with_zero_likes(users[username])
        for post in posts:
            if post['creator'] != user_id and user_id not in post['likes'] and post['creator'] in unliked_users:
                res = requests.post(API_URL+'like/', json={"post_id": post['post_id']}, headers=header)
                if res.status_code == 201:
                    likes += 1
                    if not continue_liking(users.values()[0]):
                        return
            if likes == max_likes:
                break
        username, likes = find_next_user(users, max_likes)


def get_user_id(username, token):
    """
    finds user id by user name
    :param username: srting
    :param token: string, JWT
    :return: int, user_id
    """
    header = get_auth_header(token)
    user_list = requests.get(API_URL+"users/", headers=header).json()
    for u in user_list:
        if u['username'] == username:
            return u['id']
    return


def main():
    conf = read_config()
    # testing connection
    try:
        r = requests.get(API_URL)
        status = r.status_code
    except requests.ConnectionError:
        status = 0
    if status == 200:
        users = signup_users(conf['number_of_users'])
        create_posts(users, conf['max_user_posts'])
        like_posts(users, conf['max_user_likes'])
        print("All done!")

    else:
        print("Could not establish connection to API, quitting.")


if __name__ == "__main__":
    main()