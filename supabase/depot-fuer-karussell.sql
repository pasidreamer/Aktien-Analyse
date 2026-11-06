-- Aktien-Ampel: Welche Aktien hält Pascal gerade? (für «Offenlegung: Ich halte diese Aktie» im Karussell)
-- Einmal im Supabase SQL Editor ausführen (New query, alles einfügen, Run). Kann mehrmals ausgeführt werden.
--
-- Gibt nur die Kürzel zurück, die im Journal des Admins (Pascal) mit Bestand > 0 stehen.
-- Keine Stückzahlen, keine Beträge, keine anderen Nutzer. Aufrufbar nur mit dem geheimen Schlüssel,
-- der unten erzeugt wird und als GitHub-Secret DEPOT_SCHLUESSEL hinterlegt wird.

create extension if not exists pgcrypto;

-- Geheimnisse: keine Regeln (Policies) = über die App nicht lesbar, nur hier im SQL Editor
create table if not exists public.geheimnisse (
  name text primary key,
  wert text not null
);
alter table public.geheimnisse enable row level security;
revoke all on public.geheimnisse from anon, authenticated;

-- Schlüssel nur beim ersten Mal erzeugen
insert into public.geheimnisse (name, wert)
  values ('depot_lesen', encode(gen_random_bytes(24), 'hex'))
  on conflict (name) do nothing;

create or replace function public.admin_depot_ticker(schluessel text) returns text[]
language plpgsql stable security definer set search_path = public
as $$
declare d jsonb;
begin
  if not exists (select 1 from public.geheimnisse where name = 'depot_lesen' and wert = schluessel) then
    raise exception 'nicht erlaubt';
  end if;
  select j.daten into d
    from public.journale j join public.profile p on p.id = j.user_id
    where p.rolle = 'admin'
    order by j.geaendert desc limit 1;
  return array(
    select upper(t ->> 'ticker')
      from jsonb_array_elements(coalesce(d -> 'tx', '[]'::jsonb)) t
      where t ->> 'typ' in ('kauf', 'verkauf') and coalesce(t ->> 'ticker', '') <> ''
      group by upper(t ->> 'ticker')
      having sum(case when t ->> 'typ' = 'kauf' then (t ->> 'stueck')::numeric
                      else -(t ->> 'stueck')::numeric end) > 0.0000001
      order by 1
  );
end $$;

revoke all on function public.admin_depot_ticker(text) from public;
grant execute on function public.admin_depot_ticker(text) to anon, authenticated;

-- Zum Schluss den Schlüssel anzeigen: diesen Wert als GitHub-Secret DEPOT_SCHLUESSEL eintragen
select wert as "DEPOT_SCHLUESSEL (kopieren)" from public.geheimnisse where name = 'depot_lesen';
