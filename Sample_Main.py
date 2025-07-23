# import os
from dotenv import load_dotenv
import os
dotenv_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=dotenv_path)

print("GROQ_API_KEY:", os.getenv("GROQ_API_KEY"))
print("HF_TOKEN:", os.getenv("HF_TOKEN"))
