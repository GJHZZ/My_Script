# -*- config: utf8 -*-
# author: Jun
# update: 2020 07 31

import os
import time
import requests
import json
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

class FinishQuestion(object):

    def __init__(self, config_info, logger):
        self.logger = logger
        self.url = config_info['config']['url']
        self.token = config_info['config']['token']
        self.finish_dict = config_info
        self.class_dict = {
            'chniese': {
                '1': 131,
                '2': 132,
                '3': 157,
                '4': 158,
                '5': 183,
                '6': 184,
            },
            'math': {
                '1': 133,
                '2': 134,
                '3': 159,
                '4': 160,
                '5': 185,
                '6': 186,
            },
            'english': {
                '1': 135,
                '2': 136,
                '3': 161,
                '4': 162,
                '5': 187,
                '6': 188,
            },
            'science': {
                '1': 248,
                '2': 138,
                '3': 163,
                '4': 164,
                '5': 189,
                '6': 190,
            },
            'policy': {
                '1': 139,
                '2': 140,
                '3': 165,
                '4': 166,
                '5': 191,
                '6': 192,
            },
            'theory': {
                '1': 141,
                '2': 142,
                '3': 167,
                '4': 168,
                '5': 193,
                '6': 194,
            },
            'psychological': {
                '1': 143,
                '2': 144,
                '3': 169,
                '4': 170,
                '5': 195,
                '6': 196,
            },
            'management': {
                '1': 145,
                '2': 146,
                '3': 171,
                '4': 172,
                '5': 197,
                '6': 198,
            },
        }
        self.finish_info = {
            'class': 0,
            'finish_num': 0,
            'error_num': 0
        }
    
    def finish_class(self):
        test_list = []

        for i in self.finish_dict:
            if i == 'config':
                continue
            for j in self.finish_dict[i]:
                if self.finish_dict[i][j][0] == 1:
                    self.finish_info['class'] = self.class_dict[i][j]
                    self.finish_info['finish_num'] = self.finish_dict[i][j][1]
                    test_list.append(self.finish_info['class'])
                    self.logger('\n========== class start ==========')
                    self.logger('Finish : %s\n' % self.finish_info['finish_num'])
                    result = self.finish_test()
                    self.logger('\nTeacher : %s' % result['Teacher'])
                    self.logger('Class : %s' % result['Class'])
                    self.logger('Score : %s' % result['Score'])
                    self.logger('========== class finished =========\n')

        #             print(self.finish_info)
        # print(test_list)
        # for count in range(len(test_list) -1):
        #     for times in range(len(test_list) - count - 1):
        #         if test_list[times] > test_list[times + 1]:
        #             test_list[times], test_list[times + 1] = test_list[times + 1], test_list[times]
        # print(test_list)
    
    def finish_test(self):
        url = "https://%s/tps/api/question/questionList" % self.url
        headers = {
            "token": self.token,
            "Content-Type": "application/json;charset=UTF-8"
        }
        chose = ""
        haveAnswer = 0
        questionId = ""
        questionTypeId = 1
        questionTypeName = "单选题"
        resultsId = ""
        rightStatus = ""
        useTime = 0
        isend = 0
        score = 0
        while True:

            data = {
                "examinationId": self.finish_info['class'],
                "type": 1,
                "haveAnswer": haveAnswer,
                "questionId": questionId,
                "provinces": "",
                "city": "",
                "county": "",
                "resultsId": resultsId,
                "isend": isend,
                "score": score,
                "useTime": useTime,
                "rightStatus": rightStatus,
                "chose": chose,
                "questionTypeId": questionTypeId,
                "questionTypeName": questionTypeName
            }
            response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode(), verify=False)
            if isend == 1:
                break
            haveAnswer = 1
            resultsId = response.json()['data']['resultsId']
            id_index = response.json()['data']['questionIndex']
            questionId = response.json()['data']['idList'][id_index]
            questionTypeId = response.json()['data']['questionList'][0]['questionTypeId']
            questionTypeName = response.json()['data']['questionList'][0]['questionTypeName']
            if int(response.json()['data']['isLast']) == 1:
                isend = 1
            right_chose = ''
            error_chose = ''
            if int(questionTypeId) == 1 or int(questionTypeId) == 3:
                right_chose = response.json()['data']['questionList'][0]['rightList'][0]['questionKeyId']
                for key_info in response.json()['data']['questionList'][0]['keyList']:
                    if key_info['id'] != right_chose:
                        error_chose = key_info['id']
                        break
            
            if int(questionTypeId) == 2:
                for key_info in response.json()['data']['questionList'][0]['rightList']:
                    if right_chose == '':
                        right_chose = key_info['id']
                    else:
                        right_chose = "%s,%s" % (right_chose, key_info['id'])
                
                if len(response.json()['data']['questionList'][0]['rightList']) == 1:
                    for key_info in response.json()['data']['questionList'][0]['keyList']:
                        if error_chose == '':
                            error_chose = key_info['id']
                        else:
                            error_chose = "%s,%s" % (error_chose, key_info['id'])
                else:
                    error_chose = response.json()['data']['questionList'][0]['keyList'][0]['id']

            if int(questionTypeId) == 4:
                right_chose = response.json()['data']['questionList'][0]['rightList'][0]['rightContent']
                error_chose = '@@@'
                

            if self.finish_info['finish_num'] == 0:
                score = 0
                useTime = int(response.json()['data']['useTime']) + 5
                rightStatus = 0
                chose = error_chose
                self.logger('Question: %s == Type: %s == Result: Error' % (id_index + 1, questionTypeName))
            else:
                score = 5
                useTime = int(response.json()['data']['useTime']) + 5
                rightStatus = 1
                chose = right_chose
                self.finish_info['finish_num'] = self.finish_info['finish_num'] - 1
                self.logger('Question: %s == Type: %s == Result: Right' % (id_index + 1, questionTypeName))
        
        url = "https://%s/tps/api/question/practiceReport" % self.url
        data = {
            "resultsId": "%s" % response.json()['data']['resultsId']
        }
        response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode(), verify=False)
        result_info = {
            'Teacher': response.json()['data']['username'],
            'Class': response.json()['data']['name'],
            'Score': response.json()['data']['results']
        }
        return result_info

class Tools(object):

    def __init__(self, path):
        self.path = path
        self.ini_obj = {}
        try:
            os.remove('%s/run_log.txt' % self.path)
        except:
            pass

    def read_ini(self):
        self.ini_obj = {}
        with open('%s/config.ini' % self.path, 'r', encoding='UTF-8') as f:
            ini_info = f.readlines()

        for i in ini_info:
            ini_line = i.replace('\n', '')
            if ';' in ini_line or '#' in ini_line:
                continue

            if '[' in ini_line and ']' in ini_line:
                title = ini_line.replace('[', '').replace(']', '')
                self.ini_obj[title] = {}
                continue

            if '=' in ini_line:
                key = ini_line.replace(' ', '').split('=')[0]
                value = ini_line.replace(' ', '').split('=')[1]
                if title in self.ini_obj:
                    self.ini_obj[title][key] = value
        return

    def format_info(self):
        for i in self.ini_obj:
            if i == 'config':
                continue
            for j in self.ini_obj[i]:
                self.ini_obj[i][j] = self.ini_obj[i][j].split(',')
                self.ini_obj[i][j][0] = int(self.ini_obj[i][j][0])
                self.ini_obj[i][j][1] = int(self.ini_obj[i][j][1])
        return

    def run_log(self, log):
        print(log)
        with open('%s/run_log.txt' % self.path, 'a+', encoding='UTF-8') as f:
            f.write("%s\n" % log)


def main():
    path = os.path.dirname(os.path.abspath(__file__))
    if 'config.ini' in os.listdir(path):
        pass
    else:
        print('[ERROR] Config file not exist!')
        return

    try:
        tools = Tools(path)
        tools.read_ini()
        tools.format_info()
    except Exception as e:
        print('[ERROR] Config file error!')
        print('%s' % e)
        return

    try:
        test = FinishQuestion(tools.ini_obj, tools.run_log)
        test.finish_class()
    except Exception as e:
        print('%s' % e)
        return

main()
os.system('pause')