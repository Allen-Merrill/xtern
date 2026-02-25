from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
from pathlib import Path

# Load .env from parent directory
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=str(env_path))

app = FastAPI(
    title='Supply Chain PO Automation',
    description='Multi-Agent Purchase Order System Backend',
    version='0.1.0'
)

# Allow frontend to call backend (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:3000', 'https://*.vercel.app'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

@app.get('/health')
def health_check():
    return {
        'status': 'ok',
        'service': 'supply-chain-po-backend',
        'supabase_configured': bool(os.getenv('SUPABASE_SERVICE_ROLE_KEY')),
        'openrouter_configured': bool(os.getenv('OPENROUTER_API_KEY')),
    }

@app.get('/test-supabase')
async def test_supabase():
    """Verify Supabase connection works."""
    try:
        from supabase import create_client
        client = create_client(
            os.getenv('NEXT_PUBLIC_SUPABASE_URL'),
            os.getenv('SUPABASE_SERVICE_ROLE_KEY')
        )
        # Try to query a table (will return empty before seeding)
        result = client.table('products').select('*').limit(1).execute()
        return {'status': 'connected', 'sample_data': result.data}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

@app.get('/test-openrouter')
async def test_openrouter():
    """Verify OpenRouter LLM connection works."""
    try:
        from langchain_openai import ChatOpenAI
        llm = ChatOpenAI(
            model='meta-llama/llama-3.1-8b-instruct:free',
            openai_api_key=os.getenv('OPENROUTER_API_KEY'),
            openai_api_base='https://openrouter.ai/api/v1',
            max_tokens=50,
            default_headers={
                'HTTP-Referer': 'http://localhost:3000',
                'X-Title': 'Supply Chain PO Automation'
            }
        )
        response = llm.invoke('Say hello in one word.')
        return {'status': 'connected', 'response': response.content}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}
    
@app.get('/data-summary')
async def data_summary():
    """Return counts of all seeded tables."""
    from supabase import create_client
    client = create_client(
        os.getenv('NEXT_PUBLIC_SUPABASE_URL'),
        os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    )
    tables = ['products', 'suppliers', 'supplier_products',
             'forecasts', 'inventory', 'container_specs',
             'supplier_scoring_weights']
    counts = {}
    for table in tables:
        result = client.table(table).select('*', count='exact').execute()
        counts[table] = result.count
    return {'status': 'ok', 'counts': counts}


# Should return:
# {"status":"ok","counts":{"products":60,"suppliers":6,
#   "supplier_products":195,"forecasts":720,"inventory":60,
#   "container_specs":2,"supplier_scoring_weights":4}}