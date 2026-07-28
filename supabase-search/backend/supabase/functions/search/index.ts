import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const model = new Supabase.ai.Session('gte-small')

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
  'Access-Control-Allow-Headers': 'Content-Type, Authorization',
}

export default {
  fetch: async (req: Request) => {
    if (req.method === 'OPTIONS') {
      return new Response(null, { status: 204, headers: corsHeaders })
    }

    try {
      const { search, threshold = 0.3, limit = 5 } = await req.json()
      
      if (!search || search.trim() === '') {
        return Response.json(
          { error: '请提供搜索词！' },
          { status: 400, headers: corsHeaders }
        )
      }
      
      console.log(`🔍 Searching for: "${search}"`)
      
      const embedding = await model.run(search.trim(), {
        mean_pool: true,
        normalize: true,
      })
      
      const supabaseUrl = Deno.env.get('SUPABASE_URL')!
      const supabaseKey = Deno.env.get('SUPABASE_ANON_KEY')!
      const supabase = createClient(supabaseUrl, supabaseKey)
      
      const { data: result, error } = await supabase
        .rpc('query_embeddings', {
          query_vec: embedding,
          match_threshold: threshold,
        })
        .select('id, content, created_at')
        .limit(limit)
      
      if (error) {
        console.error('RPC error:', error.message)
        return Response.json(
          { error: error.message },
          { status: 500, headers: corsHeaders }
        )
      }
      
      return Response.json(
        {
          search,
          threshold,
          count: result?.length || 0,
          results: result || [],
        },
        { headers: corsHeaders }
      )
      
    } catch (error) {
      console.error('Search error:', error)
      return Response.json(
        { error: String(error) },
        { status: 500, headers: corsHeaders }
      )
    }
  },
}