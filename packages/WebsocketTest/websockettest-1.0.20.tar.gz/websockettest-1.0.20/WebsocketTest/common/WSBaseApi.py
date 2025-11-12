import websockets
from WebsocketTest.common.utils import *
import hashlib
import hmac,time
from urllib.parse import urlparse,urlencode
from WebsocketTest.common.utils import *
from wsgiref.handlers import format_date_time
from time import mktime
class WSBaseApi:
    def __init__(self, **kwargs):
        self.request = {}
        self.response = {}
        for key, value in kwargs.items():
            setattr(self, key, value)
    def generate_Aipass_auth_headers(self,method="GET"):
        """为Aipass链路生成授权头"""
        # 解析 URL
        parsed_url = urlparse(self.url)
        url_host = parsed_url.netloc  # 获取 host (例如 "hu-sds.sp.volkswagen-anhui.com")
        url_path  = parsed_url.path    # 获取 path (例如 "/mos/iflytek/spark/api/v2/autoCar")
        # 查找第一个/v的位置
        v_pos = url_path.find('/v')
        _path = url_path[v_pos:] if v_pos != -1 else url_path
        date = format_date_time(mktime(datetime.now().timetuple()))
        authorization_headers = f"host: {url_host}\ndate: {date}\n{method} {_path} HTTP/1.1"
        signature_sha = hmac.new(self.apiSecret.encode('utf-8'), authorization_headers.encode('utf-8'),
                                digestmod=hashlib.sha256).digest()
        authorization_signature = encode_base64(signature_sha,input_encoding='bytes')
        authorization = f'api_key="{self.apiKey}", algorithm="hmac-sha256", headers="host date request-line", signature="{authorization_signature}"'
        return {
                "host": url_host,
                "date": date,
                "authorization": encode_base64(authorization),
                "appid": self.appId
                # ,"stubbing": "true"

            }

    def generate_WebsokectWebApi_auth_headers(self):
        """为3.5架构生成参数"""
        auth_parm = {
                "auth_id": self.auth_id,
                "data_type": "audio" if self.audio_enabled else "text",
                "scene": self.scene,
                "attach_params": json.dumps(self.attach_params, ensure_ascii=False),
                "userparams": encode_base64(self.UserParams)
             }
        # 如果不是音频模式，添加text_query字段
        if not self.audio_enabled:
            auth_parm["text_query"] = "tpp"
        param_json = json.dumps(auth_parm, ensure_ascii=False)
        param_base64 = encode_base64(param_json)
        cur_time = int(time.time())
        check_sum_pre = self.apiKey + str(cur_time) + param_base64
        checksum = hashlib.md5(check_sum_pre.encode("utf-8")).hexdigest()
        return {
                "appid": self.appId,
                "checksum": checksum,
                "param": param_base64,
                "curtime": str(cur_time),
                "signtype": "md5"
            }
    
    def assemble_ws_auth_url(self, chain=None):
        params = {
            '4.5': self.generate_Aipass_auth_headers,
            '4.0': self.generate_Aipass_auth_headers
        }.get(chain, self.generate_WebsokectWebApi_auth_headers)()
        # logger.info(urlencode(params))
        return f"{self.url}?{urlencode(params)}"

    async def handle_Aipass(self, ws):
        async def parse_frame(frame_data):
            """快速解析帧数据的协程"""
            try:
                return json.loads(base64.b64decode(frame_data["text"].encode()).decode())
            except Exception as e:
                logger.debug(f"帧解析跳过: {str(e)}")
                return None
        while True:
            try:
                result = await asyncio.wait_for(ws.recv(), timeout=50)
                print(result)
                msg = json.loads(result)
                # 快速失败检查
                if msg["header"]["code"] != 0:
                    logger.error(f"服务端错误: {msg['header']['message']}")
                    break

                # 使用walrus运算符简化payload检查
                if not (payload := msg.get("payload")):
                    continue
                if "iat" in payload:
                    iat_text = await parse_frame(payload["iat"])
                    logger.info(f"收到识别帧：{iat_text}")

                semantic = None
                # 使用位掩码快速检查帧类型
                if "stream_tpp" in payload: #4.0架构，接入的是其他大模型（字节doubao）
                    if (semantic := await parse_frame(payload["stream_tpp"])) and (answer := semantic["intent"].get("answer")):
                        self.answer_text += answer["text"]
                elif "tpp" in payload:   #4.0架构，接入的是其他大模型（字节doubao），大模型pk后传统语义落域
                    semantic = await parse_frame(payload["tpp"])
                    self.response = semantic
                    break
                elif "cbm_semantic" in payload:  # 4.5架构，接入的是星火大模型（spark45）,zone 4.0架构接入的是讯飞交互大模型(sparknew)
                    semantic = await parse_frame(payload["cbm_semantic"])
                    self.response = semantic
                    break


                # 最终结果处理
                if msg["header"].get("status") == 2:
                    if semantic and (answer := semantic["intent"].get("answer")):
                        answer["text"] = self.answer_text
                    self.response = semantic
                    break

            except asyncio.TimeoutError:
                logger.warning("接收超时，重试中...")
                continue  # 根据业务决定是否break
            except json.JSONDecodeError:
                logger.error("消息格式异常，终止连接")
                break
            except Exception as e:
                logger.error(f"处理错误: {e}")
                break

    async def WebSocketApi(self, extra_headers=None, chain=None, **kwargs):
        async with websockets.connect(self.url, extra_headers=extra_headers, **kwargs) as ws:
            if self.request:
                await ws.send(json.dumps(self.request, ensure_ascii=False)) #保留原始字符（如中文）
            if chain == "4.5" or chain == "4.0":
                await self.handle_Aipass(ws) 
            else:  # 3.5架构
                await self.handle_WebsokectWebApi(ws)
    @exception_decorator
    def run(self):
        self.request = self.generate_request()
        # WebSocket连接与消息发送
        asyncio.run(self.WebSocketApi())