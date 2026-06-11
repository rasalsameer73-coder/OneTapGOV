-- Run as a database owner after replacing the role password through a secret manager.
-- The API should connect through Supabase's transaction pooler, not the direct host.
create role onetapgov_api login noinherit;
grant usage on schema public to onetapgov_api;
grant select, insert, update, delete on all tables in schema public to onetapgov_api;
grant usage, select on all sequences in schema public to onetapgov_api;
alter default privileges in schema public
  grant select, insert, update, delete on tables to onetapgov_api;
alter default privileges in schema public
  grant usage, select on sequences to onetapgov_api;

-- Keep migrations on a separate owner credential. Do not grant CREATE or DROP
-- to the runtime role. Supabase Auth JWTs are verified by the API and exchanged
-- for short-lived OneTapGOV access/refresh tokens.

