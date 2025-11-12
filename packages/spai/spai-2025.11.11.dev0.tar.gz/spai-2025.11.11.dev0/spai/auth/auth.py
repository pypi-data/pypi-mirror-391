import time
import webbrowser

from ..errors import LoginError, AuthTimeOut
from ..repos import APIRepo, AuthRepo


def auth(max_t=60, interval=2):
    api_repo, repo = APIRepo(), AuthRepo()
    user = repo.load_creds()
    if user:
        return user
    response = api_repo.login()
    if response.status_code != 200:
        raise LoginError()
    data = response.json()
    opened = webbrowser.open(data['login_url'])
    if not opened:
        print(f"Please open this URL manually:\n{data['login_url']}")
    
    authenticated = False
    t0 = time.time()
    while not authenticated and time.time() - t0 < max_t:
        response = api_repo.token(data['state'])
        token_data = response.json()
        if response.status_code == 200:
            print("Authenticated!")
            print("- Id Token: {}...".format(token_data["id_token"][:10]))

            creds_path = repo.save_creds(token_data)
            print("Saved credentials to: ", creds_path)

            current_user = repo.decode_token(token_data)
            authenticated = True
            current_user["id_token"] = token_data["id_token"]
            return current_user
        else:
            time.sleep(interval)
    if not authenticated:
        raise AuthTimeOut()


# auth decorator
def with_auth(func):
    def wrapper(*args, **kwargs):
        user = auth()
        return func(*args, **kwargs, user=user)

    return wrapper
