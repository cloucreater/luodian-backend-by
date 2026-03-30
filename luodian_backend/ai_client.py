import httpx
from config import settings

class AIClient:
    def __init__(self):
        self.provider = settings.AI_PROVIDER

    async def chat(self, message: str, history: list = None) -> str:
        if self.provider == 'openai':
            return await self._openai_chat(message, history)
        elif self.provider == 'zhipu':
            return await self._zhipu_chat(message, history)
        elif self.provider == 'local':
            return await self._local_chat(message, history)
        else:
            return self._mock_reply(message)

    async def _openai_chat(self, message: str, history: list = None) -> str:
        url = f'{settings.OPENAI_BASE_URL}/chat/completions'
        headers = {'Authorization': f'Bearer {settings.OPENAI_API_KEY}', 'Content-Type': 'application/json'}
        messages = [{'role': 'system', 'content': '你是一个螺钿文化专家，回答关于螺钿的历史、技艺、传承等问题。'}]
        if history:
            messages.extend(history[-5:])
        messages.append({'role': 'user', 'content': message})
        payload = {'model': 'gpt-3.5-turbo', 'messages': messages, 'temperature': 0.7}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, headers=headers, timeout=30)
            data = resp.json()
            return data['choices'][0]['message']['content']

    async def _zhipu_chat(self, message: str, history: list = None) -> str:
        return '智谱 AI 接口待接入'

    async def _local_chat(self, message: str, history: list = None) -> str:
        url = settings.LOCAL_MODEL_URL
        payload = {'prompt': message, 'history': history or []}
        async with httpx.AsyncClient() as client:
            resp = await client.post(url, json=payload, timeout=60)
            data = resp.json()
            return data.get('response', '')

    def _mock_reply(self, message: str) -> str:
        keywords = {
            '起源': '螺钿技艺起源于商周时期，考古发现表明当时已有贝壳装饰的漆器。',
            '点螺': '点螺是螺钿工艺中最精细的技法，将贝壳磨至极薄，切割成细小的点状拼贴。',
            '材料': '螺钿主要使用夜光螺、鲍鱼壳、珍珠贝、砗磲等贝壳材料。',
        }
        for kw, reply in keywords.items():
            if kw in message:
                return reply
        return '关于螺钿的问题，你可以查看知识库或继续问我。'

ai_client = AIClient()
