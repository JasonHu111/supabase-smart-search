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
      const payload = await req.json()
      const { content, id } = payload.record
      
      if (!content) {
        return Response.json(
          { ok: false, error: 'No content provided' },
          { status: 400, headers: corsHeaders }
        )
      }
      
      console.log(`🔄 Generating embedding for id ${id}`)
      
      const embedding = await model.run(content, {
        mean_pool: true,
        normalize: true,
      })
      
      const supabaseUrl = Deno.env.get('SUPABASE_URL')!
      const supabaseKey = Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')!
      const supabase = createClient(supabaseUrl, supabaseKey)
      
      const { error } = await supabase
        .from('embeddings')
        .update({ embedding: JSON.stringify(embedding) })
        .eq('id', id)
      
      if (error) {
        console.error('Database error:', error.message)
        return Response.json(
          { ok: false, error: error.message },
          { status: 500, headers: corsHeaders }
        )
      }
      
      console.log(`✅ Generated embedding for id ${id}`)
      return Response.json(
        { ok: true, id },
        { headers: corsHeaders }
      )
      
    } catch (error) {
      console.error('Error:', error)
      return Response.json(
        { ok: false, error: String(error) },
        { status: 500, headers: corsHeaders }
      )
    }
  },
}