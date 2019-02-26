import json

res = {
        "id": 115844517,
        "first_name": "Татьяна",
        "last_name": "Смирнова",
        "sex": 1,
        "nickname": "",
        "maiden_name": "",
        "domain": "id115844517",
        "screen_name": "id115844517",
        "bdate": "1.4",
        "city": {
            "id": 1,
            "title": "Москва"
        },
        "country": {
            "id": 1,
            "title": "Россия"
        },
        "photo_50": "https://pp.userapi.com/c824204/v824204220/13933a/G1-CXO-kGmM.jpg?ava=1",
        "photo_100": "https://pp.userapi.com/c824204/v824204220/139339/8a62-zYPNOI.jpg?ava=1",
        "photo_200": "https://pp.userapi.com/c824204/v824204220/139337/uy6s23WAjiI.jpg?ava=1",
        "photo_max": "https://pp.userapi.com/c824204/v824204220/139337/uy6s23WAjiI.jpg?ava=1",
        "photo_200_orig": "https://pp.userapi.com/c824204/v824204220/139337/uy6s23WAjiI.jpg?ava=1",
        "photo_400_orig": "https://pp.userapi.com/c824204/v824204220/139338/pJd2I5ow5to.jpg?ava=1",
        "photo_max_orig": "https://pp.userapi.com/c824204/v824204220/139338/pJd2I5ow5to.jpg?ava=1",
        "photo_id": "115844517_456249039",
        "has_photo": 1,
        "has_mobile": 1,
        "is_friend": 0,
        "friend_status": 0,
        "online": 0,
        "wall_comments": 1,
        "can_post": 0,
        "can_see_all_posts": 0,
        "can_see_audio": 1,
        "can_write_private_message": 0,
        "can_send_friend_request": 1,
        "mobile_phone": "8-960-532-55-05",
        "home_phone": "**-**-**",
        "skype": "tanysha_smirnova",
        "site": "http://**",
        "status": "",
        "last_seen": {
            "time": 1551196409,
            "platform": 2
        },
        "crop_photo": {
            "photo": {
                "id": 456249039,
                "album_id": -6,
                "owner_id": 115844517,
                "photo_75": "https://pp.userapi.com/c824204/v824204220/13932c/dQdtyza1PSE.jpg",
                "photo_130": "https://pp.userapi.com/c824204/v824204220/13932d/Htm-AZX-8mQ.jpg",
                "photo_604": "https://pp.userapi.com/c824204/v824204220/13932e/FyULri9Rn5M.jpg",
                "photo_807": "https://pp.userapi.com/c824204/v824204220/13932f/ufcFLohCu-A.jpg",
                "photo_1280": "https://pp.userapi.com/c824204/v824204220/139330/b5Ta55R4jR8.jpg",
                "photo_2560": "https://pp.userapi.com/c824204/v824204220/139331/KX8AHLWmJUM.jpg",
                "width": 1500,
                "height": 2000,
                "text": "",
                "date": 1525894555,
                "post_id": 4087
            },
            "crop": {
                "x": 0.0,
                "y": 6.3,
                "x2": 100.0,
                "y2": 81.3
            },
            "rect": {
                "x": 0.0,
                "y": 0.0,
                "x2": 100.0,
                "y2": 100.0
            }
        },
        "verified": 0,
        "followers_count": 530,
        "blacklisted": 0,
        "blacklisted_by_me": 0,
        "is_favorite": 0,
        "is_hidden_from_feed": 0,
        "common_count": 5,
        "occupation": {
            "type": "work",
            "name": "Тренировки"
        }
    }


for key in res:
    try:
        print(res[key+'_vk'])
        pass
    except:
        print(False)
        pass
    