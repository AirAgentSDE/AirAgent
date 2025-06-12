from airsim_wrapper import *
from openai import OpenAI



# 载入VLM模型
vlm_client = OpenAI(
    base_url = 'http://localhost:11434/v1',
    api_key='ollama', # required, but unused
)


# 连接到AirSim客户端
client = airsim.MultirotorClient()

# 读取图像
rgb_image = get_image()

# 转成base64格式的png图片
base64_image = cv2_to_base64(rgb_image, ".png")  # png或 '.jpg'

# 视觉理解
completion = vlm_client.chat.completions.create(
        model="qwen2.5vl:32b",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"}
                    },
                    {"type": "text", "text": "你有三台无人机可以调动，它们支持起飞，降落，飞到某处，检测目标等动作。请生成一个高层次(high-level)计划，让无人机完成风力发电机巡检。"}
                ]
            }
        ]
    )
print(completion.choices[0].message.content)
