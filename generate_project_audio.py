import httpx
import asyncio
import os

async def generate_piece(name, text):
    print(f"Generating {name}...")
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post(
                "http://127.0.0.1:8001/generate",
                json={"text": text, "language": "en"},
                timeout=300.0
            )
            if resp.status_code == 200:
                data = resp.json()
                print(f"Success for {name}: {data['audio_url']}")
                return data['audio_url']
            else:
                print(f"Error for {name}: {resp.status_code}")
        except Exception as e:
            print(f"Exception for {name}: {e}")
    return None

async def main():
    scripts = {
        "greeting": "Well, hello there. Welcome to this little corner of the digital highway. We're lookin' at somethin' a bit different today... a bridge between the past and the wires of the future. Glad you could make it.",
        "chatbot": "The brain of this operation... they call it a Chatbot, but I like to think of it as a ghost in the machine. It's powered by LangGraph and RAG, searchin' through pages of my life, my songs, and my thoughts to find an answer that's blowin' in the wind. It ain't just code, it's a conversation across time.",
        "3d_model": "And then there's this... digital reflection. A MetaHuman rig livin' in Unreal Engine. They're usin' NVIDIA Audio2Face to make these lips move to my voice, and Pixel Streaming to bring it right to your screen. It's like lookin' in a mirror from another dimension.",
        "gallery": "Step into the Dylan Lens Gallery. It's a place where time slows down. An AI looks at your modern world through LLaVA, and Stable Diffusion paints it over with the dust and grain of the 1960s. It's about seein' things not as they are, but as they were meant to be remembered."
    }
    
    results = {}
    for name, text in scripts.items():
        url = await generate_piece(name, text)
        results[name] = url
    
    print("\nFinal Results:")
    for name, url in results.items():
        print(f"{name}: {url}")

if __name__ == "__main__":
    asyncio.run(main())
