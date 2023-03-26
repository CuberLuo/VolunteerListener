import os.path
import random
import threading
import time
import traceback

import requests
import sys
from agents import user_agents
from utils.cryptUtil import md5encrypt
from utils.mailUtil import mail
from utils.timeUtil import isDuringThatTime
from configs import configParser

info_params = {
    "pageSize": 5,
    "pageIndex": 1,
    "organizationType": 1
}

random_headers = {
    'User-Agent': random.choice(user_agents.pc() + user_agents.mobile())
}

# 多线程中的可重入锁
lock = threading.RLock()


def CreateListenerThread(activitiesText, logText, organizationType):
    while True:
        t = time.strftime('%Y-%m-%d, %H:%M:%S', time.localtime(time.time()))
        # 两个线程共享info_params,使用RLock保证线程安全
        lock.acquire()
        try:
            info_params['organizationType'] = organizationType
            response = requests.get(
                url='https://www.api.volunteer.zjut.edu.cn/api/frontend/activity/list',
                params=info_params,
                headers=random_headers
            )
            response.encoding = 'utf-8'
            jsonData = response.json()
            if 'data' in jsonData:
                data = response.json()['data']
                # 读取已存在的活动信息
                with open(activitiesText, 'r', encoding='utf-8') as f:
                    content = f.read()
                    beforeMd5 = md5encrypt(content)
                createTime_list = []
                recruitTime_list = []
                activityDetails_list = []
                for data_item in data:
                    # 招募校区包含campus
                    # 非定向或定向代码包含orientationId
                    if campus in data_item['ccampus'] and \
                            (data_item['orientationId'] == '' or orientationId in data_item['orientationId']):
                        createTime_list.append(data_item['createTime'])
                        activityDetails_list.append(data_item['activityDetails'])
                        if 'timingRecruitTime' in data_item:
                            recruitTime_list.append(data_item['timingRecruitTime'])
                        else:
                            recruitTime_list.append('null')

                # 将第一条活动信息写入文件
                if activityDetails_list:  # activityDetails_list不为空时进行后续操作
                    with open(activitiesText, 'w', encoding='utf-8') as f:
                        f.write(activityDetails_list[0])

                    afterMd5 = md5encrypt(activityDetails_list[0])
                    print(f'{activitiesText}->beforeMd5:{beforeMd5}  afterMd5:{afterMd5}')
                    if beforeMd5 == afterMd5:
                        log_info = t + f' {activitiesText} no update'
                        print(log_info)
                        with open(logText, 'a', encoding='utf-8') as f:
                            f.write(log_info + '\n')
                    else:
                        organizationType_info = '<p>&lt;校级活动&gt;</p>' if organizationType == 1 else '<p>&lt;院级活动&gt;</p>'
                        createTime_info = f"<p>&lt;活动创建时间{createTime_list[0]}&gt;</p>"
                        recruitTime_info = f"<p>&lt;活动开始招募时间{recruitTime_list[0]}&gt;</p>"
                        activity_info = activityDetails_list[0]
                        mail_content = organizationType_info + createTime_info + recruitTime_info + activity_info

                        if mail(mail_content, sender, auth_code, receiver):
                            mail_info = t + f" type{organizationType}邮件发送成功 receiver={receiver}"
                        else:
                            mail_info = t + f" type{organizationType}邮件发送失败 receiver={receiver}"
                        print(mail_info)
                        with open(logText, 'a', encoding='utf-8') as f:
                            f.write(mail_info + '\n')
                else:
                    print(f"There is no information that meets the requirements in type{organizationType}")
        except Exception:
            traceback.print_exc()

        lock.release()
        if isDuringThatTime("5:00", "23:30"):
            time.sleep(30)  # 每30s请求一次
        else:
            time.sleep(60 * 60)  # 每1h请求一次


def main():
    threading.Thread(target=CreateListenerThread, args=(type1Text, log1Text, 1)).start()
    threading.Thread(target=CreateListenerThread, args=(type2Text, log2Text, 2)).start()


def checkFile(file_name):
    if not os.path.exists(file_name):
        file = open(file_name, "w", encoding='utf-8')
        file.close()


def checkDir(dir_name):
    if not os.path.exists(dir_name):
        os.makedirs(dir_name)


def init_dir_and_file():
    checkDir(receiver_data_dirname)
    checkFile(type1Text)
    checkFile(type2Text)
    checkFile(log1Text)
    checkFile(log2Text)


if __name__ == '__main__':
    sender = configParser.getConfig('config', 'mail_data', 'sender')  # 发件人邮箱账号
    auth_code = configParser.getConfig('config', 'mail_data', 'auth_code')  # 发件人邮箱授权码
    if len(sys.argv) == 4:
        receiver = sys.argv[1]  # 收件人邮箱
        campus = sys.argv[2]  # 校区
        orientationId = sys.argv[3]  # 学院id
        print(f"信息初始化成功!\n收件人邮箱:{receiver}\n校区:{campus}\n定向代码:{orientationId}")
        receiver_data_dirname = f'./receiver_data/{receiver}'
        type1Text = f'{receiver_data_dirname}/{receiver}_activities_type1.txt'
        type2Text = f'{receiver_data_dirname}/{receiver}_activities_type2.txt'
        log1Text = f'{receiver_data_dirname}/{receiver}_log1.txt'
        log2Text = f'{receiver_data_dirname}/{receiver}_log2.txt'
        init_dir_and_file()
        main()
    else:
        print("无效参数!")
