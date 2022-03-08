# -*- coding:UTF-8 -*-
# Created by Shing at 2020/1/18

import sys, os
import logging
import json
from urllib.parse import urlencode
import time
import urllib3

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from baseApi import base64StrFromImage
from rect import Rect
from b_exception import ApiError

_http_pool = urllib3.PoolManager(maxsize=50, timeout=5.0, retries=urllib3.Retry(5))


class BaiduML:

    @classmethod
    def recognizeVehicleType(cls, imagePath, is_excessive=False):
        '''识别车型、车在图中的位置(但主体识别，识别最大目标）'''
        try:
            url = 'https://aip.baidubce.com/rest/2.0/image-classify/v1/car'
            encoded_args = urlencode({'access_token': TokenManager.getToken(ImageToken.__name__, is_excessive)})
            url = url + '?' + encoded_args
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            fields = {'image': base64StrFromImage(imagePath)}
            r = _http_pool.request('POST', url, headers=headers, fields=fields)
            data = json.loads(r.data.decode('utf-8'))
            logging.info(imagePath + '识别车型信息结果：' + str(data))
            if 'error_code' in list(data.keys()) and int(data['error_code']) == 17:
                if not TokenManager.hasAccountForToken(ImageToken.__name__):
                    return None
                return cls.recognizeVehicleType(imagePath, True)
            if r.status == 200:
                if 'error_code' in list(data.keys()) or 'result' not in list(data.keys()):
                    # logging.info(data)
                    return None
                if 'result' not in list(data.keys()) or len(data['result']) == 0:
                    return None
                data['result'] = sorted(list(filter(lambda x: float(x['score']) > 0.18, data['result'])),
                                        key=lambda x: x['score'], reverse=True)
                return data
            else:
                logging.warning(r.status + str(data))
                return None
        except Exception as e:
            logging.exception(e)

    @classmethod
    def recognizeVehiclePlate(cls, imagePath, is_excessive=False):
        '''识别车牌'''
        try:
            url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/license_plate'
            encoded_args = urlencode({'access_token': TokenManager.getToken(OcrToken.__name__, is_excessive)})
            url = url + '?' + encoded_args
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            fields = {'image': base64StrFromImage(imagePath)}
            r = _http_pool.request('POST', url, headers=headers, fields=fields)
            data = json.loads(r.data.decode('utf-8'))
            logging.info(imagePath + "识别车牌号结果：" + str(data))
            if 'error_code' in list(data.keys()) and int(data['error_code']) == 17:
                if not TokenManager.hasAccountForToken(OcrToken.__name__):
                    return None
                return cls.recognizeVehiclePlate(imagePath, True)
            if r.status == 200:
                if 'error_code' in list(data.keys()):
                    # logging.info(data)
                    return None
                return data['words_result']['number']
            else:
                logging.warning(r.status + str(data))
                return None
        except Exception as e:
            logging.exception(e)

    @classmethod
    def recognize_vehicle_plate_v2(cls, imagePath, is_excessive=False, multi_detect=True):
        '''
        识别车牌
        返回列表[(车牌:str,置信度:float,位置:Rect)]
        '''
        try:
            url = 'https://aip.baidubce.com/rest/2.0/ocr/v1/license_plate'
            encoded_args = urlencode({'access_token': TokenManager.getToken(OcrToken.__name__, is_excessive)})
            url = url + '?' + encoded_args
            headers = {'Content-type': 'application/x-www-form-urlencoded'}
            fields = {'image': base64StrFromImage(imagePath), 'multi_detect': 'true' if multi_detect else 'false'}
            r = _http_pool.request('POST', url, headers=headers, fields=fields)
            data = json.loads(r.data.decode('utf-8'))
            logging.info(imagePath + "识别车牌号结果：" + str(data))
            if 'error_code' in data:
                if int(data['error_code']) == 17:
                    if TokenManager.hasAccountForToken(OcrToken.__name__):
                        return cls.recognizeVehiclePlate(imagePath, True)
                if int(data['error_code']) == 282103:
                    logging.info(f'{imagePath}，没有识别车牌：{data}')
                    return []
                raise ApiError('baidu', data['error_code'], data['error_msg'])
            if r.status == 200:
                def vertices_to_rect(vertices):
                    top, left, right, bottom = (
                        min(point['y'] for point in vertices),
                        min(point['x'] for point in vertices),
                        max(point['x'] for point in vertices),
                        max(point['y'] for point in vertices)
                    )
                    return Rect(top, left, right - left, bottom - top)

                results = data['words_result'] if multi_detect else [data['words_result']]
                return [
                    (
                        result['number'],
                        # 比较粗犷的计算方式
                        100 * sum(result['probability']) / len(result['probability']),
                        vertices_to_rect(result['vertexes_location'])
                    )
                    for result in results
                ]
        except Exception as e:
            logging.exception('百度车牌识别报错！')
            raise e


class Account:
    def __init__(self, clientId, clientSecret):
        self.clientId = clientId
        self.clientSecret = clientSecret


class Token:
    '''百度api token对象, 基础类

    '''
    accounts = [
        Account('6GVTzNZH11F9wZyLGVoVPS2e', 'PlNMRSu6q9l5UpgAZ8ioNCazNcHroO9c'),
        Account('6eALMdf94jhQ8XThMBHkSiHi', 'GSSTaMMeHCsCYgnK6zD1FgnyhvA12Wk4'),
    ]
    current_account_index = 0

    def __init__(self, token, expire):
        self.token = token
        self.expire = str(expire)

    def isExpired(self):
        if self.expire is None or len(self.expire) == 0:
            return True
        if int(self.expire) - time.time() <= 0:
            return True
        return False


class OcrToken(Token):
    '''文字识别api token'''
    pass


class ImageToken(Token):
    '''图片识别api token'''
    pass


class PersonBodyToken(Token):
    '''人体分析api token'''
    pass


class TokenManager:
    '''token 管理工具'''
    # tokenDir = '/mnt/d/mj/doc/jnx/baidu_ml_token'
    tokenDir = os.path.join(os.path.expanduser('~'), 'baidu_ml_token')
    if os.path.exists(tokenDir) is False:
        os.makedirs(tokenDir)

    @classmethod
    def getToken(cls, token_class_name, is_excessive=False):
        tokenpath = os.path.join(cls.tokenDir, token_class_name)
        if is_excessive:
            if not cls.hasAccountForToken(token_class_name):
                raise Exception(token_class_name, '没有可用的账号了')
            cls.changeTokenAccount(token_class_name)
            if os.path.exists(tokenpath):
                os.remove(tokenpath)
        if not os.path.exists(tokenpath):
            with open(tokenpath, 'x+'):
                pass
        with open(tokenpath, 'w+') as f:
            contents = f.read()
            if contents and not 'none'.__eq__(contents.lower()):
                token_dict = json.loads(contents)
                token_obj = eval(token_class_name)(**token_dict)
                if token_obj.isExpired():
                    token_obj = cls.queryTokenWith(token_class_name)
                    f.write(json.dumps(token_obj.__dict__))
                return token_obj.token
            else:
                token_obj = cls.queryTokenWith(token_class_name)
                f.write(json.dumps(token_obj.__dict__))
                return token_obj.token

    @classmethod
    def changeTokenAccount(cls, token_class_name):
        token_class = eval(token_class_name)

        if token_class.current_account_index < len(token_class.accounts) - 1:
            token_class.current_account_index += 1

    @classmethod
    def hasAccountForToken(cls, token_class_name):
        token_class = eval(token_class_name)

        return token_class.current_account_index < len(token_class.accounts) - 1

    @classmethod
    def queryTokenWith(cls, token_class_name):
        token_class = eval(token_class_name)

        account = token_class.accounts[token_class.current_account_index]
        data = cls.queryToken(account.clientId, account.clientSecret)
        return token_class(data['access_token'], int(data['expires_in']))

    @classmethod
    def queryToken(cls, clientId='RVnVGfL6Y8H4GwGG6F7UIbaz', clientSecret='k2rT1hzDhw233X4bpqbbZeDmmgcsTAWa'):
        url = 'https://aip.baidubce.com/oauth/2.0/token'
        params = {'grant_type': 'client_credentials',
                  'client_id': clientId,
                  'client_secret': clientSecret}
        r = _http_pool.request('POST', url, fields=params)
        if r.status == 200:
            data = json.loads(r.data.decode('utf-8'))
            if list(data.keys()).__contains__('error'):
                logging.warning(r)
                return None
            else:
                return data
        else:
            logging.warning(r)
            return None


if __name__ == '__main__':
    image_path = '/mnt/d/20200219/425733-4/2020-02-25-15-45-50.jpg'
    # print(BaiduML.recognize_vehicle_attr(image_path))
    print(BaiduML.recognize_vehicle_plate_v2(image_path))
    # print(TokenManager.queryToken())
