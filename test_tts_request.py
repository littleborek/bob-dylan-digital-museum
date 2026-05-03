import httpx
import asyncio

async def generate():
    text = "Well, hello there. They told me I had to step out of the shadows for a minute and talk about this... digital twin of mine. You know, they put me in a machine, tried to capture the wind, tried to catch a ghost. What you're looking at ain't exactly me, but it ain't a lie neither. Berk and Eray, they built this portal. They took my words, fed them to an algorithm, and now... here I am, talking to you from a world made of code and light. We got a gallery in here, where an AI looks at photographs and reimagines them through the dust of the 1960s, using something they call Stable Diffusion. And my face... well, they hooked it up to MetaHuman and NVIDIA Audio2Face, making these digital lips move to the rhythm of my voice. It is a strange new world, man. They call it a project... I just call it another road. So, knock on the door, ask a question, and let's see what the machine has to say."
    
    print("Sending request...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                "http://127.0.0.1:8001/generate",
                json={"text": text, "language": "en"},
                timeout=300.0
            )
            print(resp.status_code)
            print(resp.json())
        except Exception as e:
            print("Error:", e)

if __name__ == "__main__":
    asyncio.run(generate())
