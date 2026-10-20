# Builds the Shikimori/MyAnimeList ↔ TMDB map for anime.js from Fribb/anime-lists.
# Output: anime-map/m/NN.json  (MAL id → [kind, tmdb id, season])   kind: "t" — TV, "m" — movie
#         anime-map/t/NN.json  ("t123" / "m123" → [[MAL id, season], ...])
# NN = id % 100. Season is the TVDB one: it is numbered like trackers number seasons.
import json, os, sys, urllib.request

SRC = 'https://raw.githubusercontent.com/Fribb/anime-lists/master/anime-list-full.json'
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'anime-map')
SHARDS = 100


def main():
    data = json.load(urllib.request.urlopen(SRC, timeout=120)) if len(sys.argv) < 2 else json.load(open(sys.argv[1], encoding='utf-8'))
    fwd = [dict() for _ in range(SHARDS)]
    rev = [dict() for _ in range(SHARDS)]
    count = 0
    for x in data:
        mal = x.get('mal_id')
        tm = x.get('themoviedb_id')
        if not mal or not isinstance(tm, dict):
            continue
        first = lambda v: v[0] if isinstance(v, list) else v
        if tm.get('tv'):
            kind, tid = 't', int(first(tm['tv']))
            season = int((x.get('season') or {}).get('tvdb') or 0)
        elif tm.get('movie'):
            kind, tid, season = 'm', int(first(tm['movie'])), 0
        else:
            continue
        fwd[mal % SHARDS][str(mal)] = [kind, tid, season]
        rev[tid % SHARDS].setdefault(kind + str(tid), []).append([mal, season])
        count += 1
    for sub, shards in (('m', fwd), ('t', rev)):
        os.makedirs(os.path.join(OUT, sub), exist_ok=True)
        for i, part in enumerate(shards):
            with open(os.path.join(OUT, sub, '%02d.json' % i), 'w', encoding='utf-8') as f:
                json.dump(part, f, separators=(',', ':'), sort_keys=True)
    print('entries', count)


if __name__ == '__main__':
    main()
