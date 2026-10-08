import importlib, sys, traceback
mods = sys.argv[1:]
for m in mods:
    try:
        mod = importlib.import_module("collectors." + m)
        items = mod.fetch()
        nb = sum(1 for i in items if i.is_new)
        nd = sum(1 for i in items if (i.released_at or i.uploaded_at))
        print(f"OK   {m:28s} {len(items):4d}건  is_new={nb}  dated={nd}")
    except Exception as e:
        print(f"FAIL {m:28s} {type(e).__name__}: {str(e)[:200]}")
    sys.stdout.flush()
