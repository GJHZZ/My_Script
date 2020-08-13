# -*- config: utf8 -*-
# author: Jun
# update: 2020 07 31

import os
import sys
import time
import requests
import json
import urllib3
import traceback
import configparser
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class FinishQuestion(object):

    def __init__(self, config_info, logger):
        self.logger = logger
        self.url = config_info['config']['url']
        self.headers = {
            "token": config_info['config']['token'],
            "Content-Type": "application/json;charset=UTF-8"
        }
        self.config_info = config_info
        self.class_type = {
            '1': '教育政策',
            '2': '教育理论',
            '3': '儿童心理',
            '4': '班级管理',
            '5': '教学改进',
            '6': '传统文化',
            '7': '艺术美育',
            '12': '人文科技',
            '8': '小学语文',
            '9': '小学数学',
            '10': '小学英语',
            '11': '小学科学',
        }
        self.test_type = {
            '1': {
                'level': '1',
                'type': '0'
            },
            '2': {
                'level': '1',
                'type': '1'
            },
            '3': {
                'level': '2',
                'type': '0'
            },
            '4': {
                'level': '2',
                'type': '1'
            },
            '5': {
                'level': '3',
                'type': '0'
            },
            '6': {
                'level': '3',
                'type': '1'
            },
        }
        self.status = 0
    
    def start_class(self):
        url = 'https://%s/tps/api/user/mySpace' % self.url
        data = {}
        myspace_info = requests.post(
            url, 
            headers=self.headers, 
            data=json.dumps(data, ensure_ascii=False).encode(), 
            verify=False
        ).json()['data']

        if str(myspace_info['perfect']) == '1':
            pass
        else:
            self.logger('* user info not complite!')
            return

        url = 'https://%s/tps/api/index/dimensionNameList' % self.url
        data = {
            "county": "",
            "city": "",
            "provinces": ""
        }
        myclass_info = requests.post(
            url, 
            headers=self.headers, 
            data=json.dumps(data, ensure_ascii=False).encode(), 
            verify=False
        ).json()['data']

        myclass_list = []
        for class_id in myclass_info:
            myclass_list.append(str(class_id['dimensionId']))

        for class_id in self.config_info:
            if class_id == 'config':
                continue
            
            test_args = {}
            test_args['class_id'] = class_id
            test_args['class_name'] = self.class_type[class_id]

            if class_id in ['5', '6', '7', '11', '12']:
                self.logger('')
                self.logger('')
                self.logger(' === Class : %s' % test_args['class_name'])
                self.logger('* Class unavailable!')
                continue

            if class_id not in myclass_list:
                self.logger('')
                self.logger('')
                print(myclass_list)
                self.logger(' === Class : %s' % test_args['class_name'])
                self.logger('* Have not class!')
                continue
            
            for test_id in self.config_info[class_id]:
                url = 'http://%s/tps/api/index/courseList' % self.url
                data = {
                    "provinces":"null",
                    "dimensionId":"%s" % test_args['class_id'],
                    "city":"null",
                    "county":"null",
                    "dimension":"%s" % test_args['class_name']
                }
                class_info = requests.post(
                    url, 
                    headers=self.headers, 
                    data=json.dumps(data, ensure_ascii=False).encode(), 
                    verify=False
                ).json()['data']
                self.logger('')
                self.logger('')
                self.logger(' === Class : %s' % test_args['class_name'])
                if len(class_info['courseList']) == 0 or 'courseList' not in class_info:
                    self.logger('* Have not test!')
                    break

                test_args['test_id'] = test_id
                test_args['test_level'] = self.test_type[test_id]['level']
                test_args['test_type'] = self.test_type[test_id]['type']
                test_args['test_num'] = int(self.config_info[class_id][test_id])
                self.logger(' === Class level : %s' % test_args['test_level'])
                self.logger(' === Class type : %s' % test_args['test_type'])

                if test_args['test_level'] == '1' and test_args['test_type'] == '0':
                    test_args['paper_id'] = class_info['courseList'][int(test_args['test_level']) - 1]['paperId']
                else:
                    if test_args['test_type'] == '0':
                        if str(class_info['courseList'][int(test_args['test_level']) - 2]['courseDto']['testStatus']) == '1':
                            test_args['paper_id'] = class_info['courseList'][int(test_args['test_level']) - 1]['paperId']
                        else:
                            self.logger('* Before test not pass!')
                            break
                    
                    if test_args['test_type'] == '1':
                        if str(class_info['courseList'][int(test_args['test_level']) - 1]['testStatus']) == '1':
                            test_args['paper_id'] = class_info['courseList'][int(test_args['test_level']) - 1]['courseDto']['paperId']
                        else:
                            self.logger('* Before test not pass!')
                            break
                
                if str(class_info['messageType']) == '1':
                    pass
                else:
                    if test_args['test_type'] == '0' and int(class_info['practiceFrequency']) > 0:
                        pass
                    elif test_args['test_type'] == '1' and int(class_info['evaluationFrequency']) > 0:
                        pass
                    else:
                        url = 'http://%s/tps/api/question/getConsumeCoin' % self.url
                        data = {
                            "dimensionId": "%s" % test_args['class_id'],
                            "level": "%s" % test_args['test_level'],
                            "type": "%s" % test_args['test_type']
                        }
                        check_cion = requests.post(
                            url, 
                            headers=self.headers, 
                            data=json.dumps(data, ensure_ascii=False).encode(), 
                            verify=False
                        ).json()['data']
                        if str(check_cion) == '1':
                            pass
                        else:
                            self.logger('* Cion not enough!')
                            break
                
                self.logger(' === Start test ========')
                result = self.start_test(**test_args)
                if result['Status'] == 0:
                    for info in result:
                        self.logger(' %s : %s' % (info, result[info]))
                self.logger(' === Complite ==========')
                self.logger('')
                self.logger('')

    
    def start_test(self, *args, **kwargs):
        url = 'https://%s/tps/api/question/examDescription' % self.url
        data = {
            "examinationId": "%s" % kwargs['paper_id']
        }

        requests.post(
            url,
            headers=self.headers,
            data=json.dumps(data, ensure_ascii=False).encode(),
            verify=False
        )

        url = "https://%s/tps/api/question/questionList" % self.url
        data = {
            "examinationId": int(kwargs['paper_id']),
            "type": 1,
            "haveAnswer": 0,
            "questionId": "",
            "provinces": "",
            "city": "",
            "county": "",
            "resultsId": "",
            "isend": 0,
            "score": 0,
            "useTime": 0,
            "rightStatus": "",
            "chose": "",
            "questionTypeId": "",
            "questionTypeName": ""
        }
        while True:
            response = requests.post(
                url, 
                headers=self.headers, 
                data=json.dumps(data, ensure_ascii=False).encode(), 
                verify=False
            )

            if data['isend'] == 1:
                break

            data['haveAnswer'] = 1
            try:
                data['resultsId'] = response.json()['data']['resultsId']
                id_index = response.json()['data']['questionIndex']
                data['questionId'] = response.json()['data']['idList'][id_index]
                data['questionTypeId'] = response.json()['data']['questionList'][0]['questionTypeId']
                data['questionTypeName'] = response.json()['data']['questionList'][0]['questionTypeName']
                data['score'] = int(response.json()['data']['questionList'][0]['score'])
            except:
                for i in self.headers:
                    print('[HEADER]%s == %s' % (i, self.headers[i]))
                for i in data:
                    print('[DATA] %s == %s' % (i, data[i]))
                try:
                    print(response.json())
                except:
                    print(response.text)
                return {'Status': 1}

            if int(response.json()['data']['isLast']) == 1:
                data['isend'] = 1
            right_chose = ''
            error_chose = ''
            if int(data['questionTypeId']) == 1 or int(data['questionTypeId']) == 3:
                right_chose = response.json()['data']['questionList'][0]['rightList'][0]['questionKeyId']
                for key_info in response.json()['data']['questionList'][0]['keyList']:
                    if key_info['id'] != right_chose:
                        error_chose = key_info['id']
                        break
            
            if int(data['questionTypeId']) == 2:
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

            if int(data['questionTypeId']) == 4:
                right_chose = response.json()['data']['questionList'][0]['rightList'][0]['rightContent']
                error_chose = '@@@'

            if kwargs['test_num'] == 0:
                data['score'] = 0
                data['useTime'] = int(response.json()['data']['useTime']) + 5
                data['rightStatus'] = 0
                data['chose'] = error_chose
                self.logger(' Question: %s == Type: %s == Result: Error' % (id_index + 1, data['questionTypeName']))
            else:
                data['useTime'] = int(response.json()['data']['useTime']) + 5
                data['rightStatus'] = 1
                data['chose'] = right_chose
                kwargs['test_num'] = kwargs['test_num'] - 1
                self.logger(' Question: %s == Type: %s == Result: Right' % (id_index + 1, data['questionTypeName']))
        
        url = "https://%s/tps/api/question/practiceReport" % self.url
        data = {
            "resultsId": "%s" % response.json()['data']['resultsId']
        }
        response = requests.post(
            url, 
            headers=self.headers, 
            data=json.dumps(data, ensure_ascii=False).encode(), 
            verify=False
        )
        result_info = {
            'Status' : 0,
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
        config = configparser.ConfigParser()
        config.read('%s/config.ini' % self.path, encoding='utf8')
        for title in config:
            if title == 'DEFAULT':
                continue
            self.ini_obj[title] = {}
            for key in config[title]:
                self.ini_obj[title][key] = config[title][key]
            
            if title == 'config':
                continue

            for key in self.ini_obj[title]:
                self.ini_obj[title][key] = int(self.ini_obj[title][key])
        return

    def run_log(self, log):
        if '*' in log:
            log = log.replace('*', '[ERROR]')
        else:
            log = '[INFO]' + log
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
        test = FinishQuestion(tools.ini_obj, tools.run_log)
        test.start_class()
    except:
        print('[ERROR] ============================')
        for i in traceback.format_exc().split('\n'):
            print('[INFO] %s' % i)
        print('[ERROR] ============================')
        return


if __name__ == "__main__":
    main()