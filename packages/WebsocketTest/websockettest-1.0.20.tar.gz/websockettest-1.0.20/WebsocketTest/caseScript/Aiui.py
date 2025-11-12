from WebsocketTest.common.WSBaseApi import *
from pathlib import Path
class ApiTestRunner(WSBaseApi):
    # 类常量
    _DEFAULT_USER_PARAMS = {"clean_history": "on", "skip": "skip"}
    _DEFAULT_DEBUG_PARAMS = {
        "clean_history": "off", "extra": "false", "nwpt": "0", 
        "debugx": "true", "debug": "true"
    }
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 只需要初始化基本属性
        self.random_id = generate_random_string()
        self.auth_id = get_auth_id()
        # 确保scene属性存在后再使用
        self.is_main = "main" in getattr(self, 'scene', '')
        self.answer_text = ""
        self.UserParams = json.dumps(self._DEFAULT_USER_PARAMS)
        self.user_params = json.dumps(self._DEFAULT_DEBUG_PARAMS)
        self.pers_param = json.dumps({"appid": self.appId, "uid": self.random_id})
        self.asr_text_bytes = json.dumps({"intent": {"text": self.text}}).encode("utf-8")

    @property
    def text_path(self):
        """文件路径（延迟初始化）"""
        if not hasattr(self, '_text_path'):
            self._setup_file_path()
        return self._text_path

    @property
    def asr_text_encode(self):
        """编码文本（延迟初始化）"""
        if not hasattr(self, '_asr_text_encode'):
            self._setup_text_encoding()
        return self._asr_text_encode

    @property
    def iat_params(self):
        """语音识别参数（延迟初始化）"""
        if not hasattr(self, '_iat_params'):
            self._iat_params = self._build_iat_params()
        return self._iat_params

    @property
    def nlp_params(self):
        """NLP参数（延迟初始化）"""
        if not hasattr(self, '_nlp_params'):
            self._nlp_params = self._build_nlp_params()
        return self._nlp_params

    @property
    def attach_params(self):
        """附加参数（延迟初始化）"""
        if not hasattr(self, '_attach_params'):
            self._attach_params = self._build_attach_params()
        return self._attach_params

    def _setup_file_path(self):
        """设置文件路径的实际逻辑"""
        base_dir = Path.cwd().resolve().joinpath("data/audio", f"{self.text}")
        pcm_path = base_dir.with_suffix(".pcm")
        self._text_path = pcm_path if pcm_path.exists() else base_dir.with_suffix(".wav")

    def _setup_text_encoding(self):
        """设置文本编码的实际逻辑"""
        if self.is_main:
            self._asr_text_encode = encode_base64(self.asr_text_bytes, input_encoding='bytes')
        else:
            self._asr_text_encode = encode_base64(self.text)

    def _build_iat_params(self):
        """构建语音识别参数"""
        return {
            "language": self.language,
            "domain": self.domain,
            "accent": self.accent,
            "eos": "600",
            "evl": "0",
            "isFar": self.isFar,
            "svl": "50",
            "ufsa": "1",
            "vgap": "400"
        }

    def _build_nlp_params(self):
        """构建NLP参数"""
        return {
            "aiui45_intv_mode": 2,
            "aqua_route": self.project,
            "sparkEnv": getattr(self, 'sparkEnv', None),
            "devid": self.deviceId,
            "city": "合肥市",
            "user_defined_params": {},
            "weather_airquality": "true",
            "deviceId": self.deviceId,
            "userId": self.userId,
            "asp_did": self.asp_did,
            "vWtoken": self.token,
            "car_identity": self.car_identity,
            "theme": "standard",
            "vin": self.vin,
            "interactive_mode": "fullDuplex",
            "did": self.did
        }

    def _build_attach_params(self):
        """构建附加参数"""
        return {
            "trs_params": json.dumps({}, ensure_ascii=False),
            "iat_params": json.dumps(self.iat_params, ensure_ascii=False),
            "nlp_params": json.dumps(self.nlp_params, ensure_ascii=False)
        }
    
    def cbm_semantic_text(self):        
        semantic_text = {
            "userId": self.userId,
            "UserParams": encode_base64(self.UserParams),
            "attachparams": json.dumps(self.attach_params, ensure_ascii=False),
            "auth_id": self.auth_id,
            "close_delay": "100",
            "dwa": "wpgs",
            "fsa_car": "poi收藏|列表|退出熟路|导航",
            "iat_user_data": json.dumps({
                "sceneInfo": {},
                "recHotWords": "poi收藏|列表|退出熟路|导航"
            }),
            "interact_mode": "continuous",
            "lat": "39.904172",
            "lng": "116.407417",
            "pers_param": self.pers_param,
            "result_level": "complete",
            "scene": self.scene,
            "user_data": "",
            "debugx": "true",
            "debug": "true"
        }
        return encode_base64(json.dumps(semantic_text, ensure_ascii=False))
    
    async def handle_WebsokectWebApi(self, ws):
        """3.5架构处理链，接入闲聊大模型（适用于svw/gp sop2/sop3/vwa等）"""     
        while True:
            try:
                # 接收消息
                raw_msg = await ws.recv()
                msg = json.loads(raw_msg)
                # print(msg)
                # 处理不同action类型
                action = msg.get('action')
                if action == "started":
                    if self.audio_enabled:
                        await send_file_chunks(self.text_path, ws)
                    else:
                        await ws.send(self.asr_text_bytes)     
                    await ws.send(bytes("--end--".encode("utf-8")))
                elif action == "result":
                    data = msg.get('data', {})
                    sub_type = data.get('sub')
                    if sub_type == "stream_tpp":
                        try:
                            content = json.loads(data['content']) #content 是一个 JSON 字符串，需要解析为字典
                            if (answer := content.get("intent", {}).get("answer")):
                                self.answer_text += answer.get("text", "")
                                if answer.get("status") == 2 or data.get("is_last"):
                                    if self.answer_text:
                                        answer["text"] = self.answer_text
                                    self.response = content
                                    return
                            elif data.get("is_last"):
                                self.response = content
                                return
                        except (json.JSONDecodeError, KeyError) as e:
                            logger.warning(f"stream_tpp数据解析异常: {e}")
                    elif sub_type == "tpp":
                        try:
                            self.response = json.loads(data['content']) #content 是一个 JSON 字符串，需要解析为字典
                            return
                        except json.JSONDecodeError as e:
                            logger.error(f"tpp数据解析失败: {e}")        
            except json.JSONDecodeError as e:
                logger.error(f"消息JSON解析失败: {e} | 原始数据: {raw_msg[:100]}...")
                break
            except Exception as e:
                logger.error(f"未处理的异常: {type(e).__name__}: {e}", exc_info=True)
                break    
    
    def generate_request(self,chain=None):
        request = {}
        if chain in ("4.0", "4.5"):
            """根据文本创建请求数据"""
            # 基础数据结构
            request = {
                "header": {
                    "app_id": self.appId,
                    "uid": self.random_id,
                    "status": 3,
                    "stmid": "1",
                    "scene": self.scene,
                    "schema_name": self.schema_name,
                    "pers_param": self.pers_param
                },
                "parameter": {
                    "user": {"user_data": "","user_params":encode_base64(self.user_params)},
                    "nlp": 
                        {"sub_scene": getattr(self,"subScene",None),
                            "nlp": {
                                "compress": "raw",
                                "encoding": "utf8",
                                "format": "json"
                            }
                    }
                },
                "payload": {}
            }
            # 处理4.5链路spark场景
            if "spark" in self.scene:
                request["payload"]["cbm_semantic"] = {
                    "compress": "raw",
                    "encoding": "utf8",
                    "format": "plain",
                    "status": 3,
                    "text": self.cbm_semantic_text()
                }
            
            # 处理音频或文本数据
            if self.audio_enabled:
                request["payload"]["audio"] = {
                    "encoding": "raw",
                    "sample_rate": 24000,
                    "channels": 1,
                    "bit_depth": 16,
                    "frame_size": 0,
                    "status": 2,
                    "audio": get_audio(self.text_path)
                }
            else:
                if self.is_main:
                    request["header"]["text_query"] = "tpp"             
                request["payload"]["text"] = {
                    "encoding": "utf8",
                    "compress": "raw",
                    "format": "plain",
                    "status": 3,
                    "text":  self.asr_text_encode
                }
        return request  

    @exception_decorator
    def run(self):
        version = self.service.split("_")[1]
        self.url = self.assemble_ws_auth_url(version)
        self.request = self.generate_request(version)
        extra_headers = {'Authorization': self.token, "Origin": "https://wsapi.xfyun.cn"}
        # WebSocket连接与消息发送
        asyncio.run(self.WebSocketApi(
            extra_headers,
            version,
            subprotocols=["chat"]
            )
        )