-- Aktien-Ampel: Datenbank für Login, Journale und Vorschläge.
-- Einmal im Supabase SQL Editor ausführen (New query, alles einfügen, Run).
-- Kann ohne Schaden mehrmals ausgeführt werden.

-- ---------- Tabellen ----------
create table if not exists public.profile (
  id uuid primary key references auth.users(id) on delete cascade,
  name text not null default '' check (char_length(name) <= 40),
  rolle text not null default 'mitglied' check (rolle in ('admin', 'mitglied')),
  erstellt timestamptz not null default now()
);

-- Ein Journal pro Person (Käufe, Verkäufe, Dividenden als JSON)
create table if not exists public.journale (
  user_id uuid primary key default auth.uid() references public.profile(id) on delete cascade,
  daten jsonb not null default '{}'::jsonb,
  geaendert timestamptz not null default now()
);

create table if not exists public.vorschlaege (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null default auth.uid() references public.profile(id) on delete cascade,
  symbol text not null check (char_length(symbol) between 1 and 60),
  name text not null default '' check (char_length(name) <= 120),
  notiz text not null default '' check (char_length(notiz) <= 300),
  status text not null default 'offen' check (status in ('offen', 'angenommen', 'abgelehnt')),
  erstellt timestamptz not null default now(),
  entschieden timestamptz
);

-- ---------- Hilfsfunktionen ----------
create or replace function public.ist_admin() returns boolean
language sql stable security definer set search_path = public
as $$ select exists (select 1 from public.profile where id = auth.uid() and rolle = 'admin') $$;

-- Neuer Benutzer bekommt ein Profil. Der allererste wird Admin (Pascal), alle weiteren Mitglieder.
create or replace function public.neues_profil() returns trigger
language plpgsql security definer set search_path = public
as $$
begin
  insert into public.profile (id, name, rolle)
  values (
    new.id,
    coalesce(nullif(new.raw_user_meta_data ->> 'name', ''), initcap(split_part(split_part(new.email, '@', 1), '.', 1))),
    case when exists (select 1 from public.profile where rolle = 'admin') then 'mitglied' else 'admin' end
  )
  on conflict (id) do nothing;
  return new;
end $$;

drop trigger if exists bei_neuem_benutzer on auth.users;
create trigger bei_neuem_benutzer after insert on auth.users
  for each row execute function public.neues_profil();

-- Falls schon Benutzer angelegt wurden: Profile nachtragen, der älteste wird Admin
insert into public.profile (id, name)
  select u.id, initcap(split_part(split_part(u.email, '@', 1), '.', 1)) from auth.users u
  on conflict (id) do nothing;
update public.profile set rolle = 'admin'
  where id = (select p.id from public.profile p join auth.users u on u.id = p.id order by u.created_at limit 1)
    and not exists (select 1 from public.profile where rolle = 'admin');

-- Kleiner Ping, damit das Gratis-Projekt nicht pausiert (wird von GitHub 2x pro Woche aufgerufen)
create or replace function public.ping() returns text language sql stable as $$ select 'ok'::text $$;

revoke all on function public.neues_profil() from public, anon, authenticated;
revoke all on function public.ist_admin() from public, anon;
grant execute on function public.ist_admin() to authenticated;
grant execute on function public.ping() to anon, authenticated;

-- ---------- Regeln (Row Level Security): jeder sieht nur, was er darf ----------
alter table public.profile enable row level security;
alter table public.journale enable row level security;
alter table public.vorschlaege enable row level security;

drop policy if exists "Profile sehen" on public.profile;
create policy "Profile sehen" on public.profile for select to authenticated using (true);
drop policy if exists "Eigenen Namen ändern" on public.profile;
create policy "Eigenen Namen ändern" on public.profile for update to authenticated
  using (id = auth.uid()) with check (id = auth.uid());

drop policy if exists "Nur eigenes Journal" on public.journale;
create policy "Nur eigenes Journal" on public.journale for all to authenticated
  using (user_id = auth.uid()) with check (user_id = auth.uid());

drop policy if exists "Vorschläge sehen" on public.vorschlaege;
create policy "Vorschläge sehen" on public.vorschlaege for select to authenticated
  using (user_id = auth.uid() or public.ist_admin());
drop policy if exists "Vorschlag machen" on public.vorschlaege;
create policy "Vorschlag machen" on public.vorschlaege for insert to authenticated
  with check (user_id = auth.uid() and status = 'offen');
drop policy if exists "Vorschlag entscheiden" on public.vorschlaege;
create policy "Vorschlag entscheiden" on public.vorschlaege for update to authenticated
  using (public.ist_admin()) with check (public.ist_admin());
drop policy if exists "Vorschlag zurückziehen" on public.vorschlaege;
create policy "Vorschlag zurückziehen" on public.vorschlaege for delete to authenticated
  using ((user_id = auth.uid() and status = 'offen') or public.ist_admin());

-- ---------- Rechte: nur angemeldete Personen, nichts für Unbekannte ----------
revoke all on public.profile, public.journale, public.vorschlaege from anon;
grant select on public.profile to authenticated;
grant update (name) on public.profile to authenticated;
grant select, insert, update, delete on public.journale to authenticated;
grant select, insert, delete on public.vorschlaege to authenticated;
grant update (status, entschieden) on public.vorschlaege to authenticated;

-- Kontrolle: zeigt alle Profile mit Rolle
select p.name, p.rolle, u.email from public.profile p join auth.users u on u.id = p.id order by u.created_at;
