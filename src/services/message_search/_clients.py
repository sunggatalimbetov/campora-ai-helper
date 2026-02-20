from openai import OpenAI
from supabase import Client, create_client

from src.config.settings import OPENAI_API_KEY, SUPABASE_SERVICE_KEY, SUPABASE_URL

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
client_oa: OpenAI = OpenAI(api_key=OPENAI_API_KEY)
