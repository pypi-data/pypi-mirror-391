from urllib.parse import quote_plus 
from WebsocketTest.common.WSBaseApi import *

class ApiTestRunner(WSBaseApi):
    def __init__(self, **kwargs):
        self.random_id = generate_random_string()
        self.UserParams = json.dumps({"clean_history":"on","skip":"skip"})
        super().__init__(**kwargs)
        self.answer_text = ""
    def generate_request(self):
        """准备请求参数"""  
        return {
            "header": {
                "appid": self.appId,
                "scene": self.scene,
                "sid": self.random_id, # 奥迪sid为空时，不会自生成
                "uid": self.random_id,
                "usrid": ""
            },
            "parameter": {
                "custom": {
                    "custom_data": {
                        "SessionParams": {
                            "isLog": "true",
                            "app_id": "",
                            "attachparams": {
                                "iat_params": {
                                    "compress": "raw",
                                    "da": "0",
                                    "domain": "aiui-automotiveknife",
                                    "dwa": "wpgs",
                                    "encoding": "utf8",
                                    "eos": "600",
                                    "format": "json",
                                    "isFar": "0",
                                    "opt": "2",
                                    "ufsa": "1",
                                    "vgap": "200",
                                    "accent": self.accent,
                                    "language": self.language
                                },
                                "nlp_params": {
                                    "llmEnv": "test",
                                    "ovs_cluster": "AUDI" if self.project == "audi" else "",
                                    "city": "合肥",
                                    "compress": "raw",
                                    "encoding": "utf8",
                                    "format": "json",
                                    "devid": "",
                                    "news": {
                                        "pageNo": 1,
                                        "pageSize": 20
                                    },
                                    "flight": {
                                        "pageNo": 1,
                                        "pageSize": 20
                                    },
                                    "ovs_version": {
                                        "weather": "3.5"
                                    },
                                    "user_defined_params": {},
                                    "weather_airquality": "true",
                                    "mapU": {
                                        "pageNo": 1,
                                        "pageSize": 20
                                    },
                                    "deviceId": self.deviceId,
                                    "userId": self.userId,
                                    "asp_did": self.asp_did,
                                    "vWtoken": self.token,
                                    "car_identity": self.car_identity,
                                    "theme": "standard",
                                    "vin": self.vin,
                                    "interactive_mode": "fullDuplex",
                                    "did": self.did,
                                    "smarthome": {
                                        "jd": {
                                            "newSession": "true",
                                            "sessionId": "123456789",
                                            "userId": self.userId
                                        }
                                    },
                                    "train": {
                                        "pageNo": 1,
                                        "pageSize": 20
                                    }
                                },
                                "tts_params": {
                                    "bit_depth": "16",
                                    "channels": "1",
                                    "encoding": "speex-wb",
                                    "frame_size": "0",
                                    "sample_rate": "16000"
                                }
                            },
                            "aue": "speex-wb",
                            "bit_depth": "16",
                            "channels": "1",
                            "city_pd": "",
                            "client_ip": "112.132.223.243",
                            "dtype": "text",
                            "frame_size": "0",
                            "msc.lat": "31.837463",
                            "msc.lng": "117.17",
                            "pers_param":  {
                                            "appid": self.appId,
                                            "car_custom": "",
                                            "uid": self.random_id
                                        },
                            "sample_rate": "16000",
                            "scene": self.scene,
                            "stmid": "0",
                            "uid": self.random_id,
                            "debug": self.debug,
                            "debugx": self.debugx,
                            "category": self.category
                        },
                        "UserParams": encode_base64(self.UserParams),
                        "UserData": quote_plus(self.UserData)
                    }
                }
            },
            "payload": {
                "text": {
                    "compress": "raw",
                    "encoding": "utf8",
                    "format": "plain",
                    "plainText": self.plainText,
                    "status": 3
                }
            }
        }
    async def handle_WebsokectWebApi(self, ws):
        """
        处理3.5架构逻辑：
        """
        while True:
            _msg = await ws.recv()
            # print(_msg)
            try:
                msg = json.loads(_msg)
                code = safe_get(msg, ["header","code"])
                if code != 0:
                    logger.error(f'请求错误: {code}, {msg}')
                    break
                else:
                    answer = safe_get(msg, ["payload","results","text","intent","answer"])
                    answerText = safe_get(answer, ["text"])
                    if answerText:
                        self.answer_text += answerText
                    if msg['header']['status']=="2" or msg['header']['status']=="3":  # 返回结果接收完成
                        if self.answer_text:
                            answer["text"] = self.answer_text     
                        self.response = msg
                        return
            except Exception as e:
                logger.error(f"error in handle_WebsokectWebApi :{e}")
                break
 
    
