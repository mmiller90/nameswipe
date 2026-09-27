-- NameSwipe database setup
-- Run once in Supabase: SQL Editor -> New query -> paste all of this -> Run.
-- Safe to run again; it won't duplicate anything.

-- 1. Tables ------------------------------------------------------------------
-- People who swipe (Michael, Rebecca, and anyone added later in the app)
create table if not exists public.app_users (
  id         text primary key,
  name       text not null unique,
  created_at timestamptz not null default now()
);

-- One row per person per name they have swiped: keep = 1, not keep = 0
create table if not exists public.decisions (
  user_id    text not null references public.app_users(id) on delete cascade,
  gender     text not null check (gender in ('boy', 'girl')),
  name       text not null,
  keep       smallint not null check (keep in (0, 1)),
  updated_at timestamptz not null default now(),
  primary key (user_id, gender, name)
);

insert into public.app_users (id, name)
values ('michael', 'Michael'), ('rebecca', 'Rebecca')
on conflict do nothing;

-- Keep updated_at current when someone changes their mind
create or replace function public.touch_updated_at()
returns trigger language plpgsql set search_path = '' as $$
begin
  new.updated_at = now();
  return new;
end $$;

drop trigger if exists decisions_touch on public.decisions;
create trigger decisions_touch before update on public.decisions
for each row execute function public.touch_updated_at();

-- 2. Security: only someone signed in with the family password gets in -------
alter table public.app_users enable row level security;
alter table public.decisions enable row level security;

drop policy if exists "family reads users"       on public.app_users;
drop policy if exists "family adds users"        on public.app_users;
drop policy if exists "family reads decisions"   on public.decisions;
drop policy if exists "family adds decisions"    on public.decisions;
drop policy if exists "family changes decisions" on public.decisions;
drop policy if exists "family undoes decisions"  on public.decisions;

create policy "family reads users"       on public.app_users for select to authenticated using (true);
create policy "family adds users"        on public.app_users for insert to authenticated with check (true);
create policy "family reads decisions"   on public.decisions for select to authenticated using (true);
create policy "family adds decisions"    on public.decisions for insert to authenticated with check (true);
create policy "family changes decisions" on public.decisions for update to authenticated using (true) with check (true);
create policy "family undoes decisions"  on public.decisions for delete to authenticated using (true);

revoke all on public.app_users, public.decisions from anon;
grant select, insert on public.app_users to authenticated;
grant select, insert, update, delete on public.decisions to authenticated;

-- 3. Matches: names BOTH Michael and Rebecca kept ------------------------------
create or replace view public.matches with (security_invoker = on) as
select gender, name
from public.decisions
where keep = 1 and user_id in ('michael', 'rebecca')
group by gender, name
having count(*) = 2;

revoke all on public.matches from anon;
grant select on public.matches to authenticated;
