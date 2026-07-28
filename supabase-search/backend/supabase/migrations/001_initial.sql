
create extension if not exists vector with schema extensions;


create table embeddings (
  id bigint primary key generated always as identity,
  content text not null,
  embedding extensions.vector (384),
  created_at timestamptz default now()
);

alter table embeddings enable row level security;
create index on embeddings using hnsw (embedding vector_ip_ops);


create or replace function query_embeddings(
  query_vec extensions.vector(384),
  match_threshold float default 0.3
)
returns table(
  id bigint,
  content text,
  created_at timestamptz
)
language plpgsql
as $$
begin
  return query
  select 
    e.id,
    e.content,
    e.created_at
  from embeddings e
  where e.embedding <#> query_vec < -match_threshold
  order by e.embedding <#> query_vec;
end;
$$;


create policy "Allow public read" 
  on embeddings for select 
  using (true);

create policy "Allow service role insert" 
  on embeddings for insert 
  with check (true);

create policy "Allow service role update" 
  on embeddings for update 
  using (true);