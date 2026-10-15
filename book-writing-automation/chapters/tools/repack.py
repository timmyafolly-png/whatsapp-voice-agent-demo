import sys, zipfile, shutil, os

def repack(path):
    src = zipfile.ZipFile(path, 'r')
    names = [n for n in src.namelist() if not n.endswith('/')]
    ct = '[Content_Types].xml'
    if ct not in names:
        raise SystemExit('no [Content_Types].xml in ' + path)
    ordered = [ct] + [n for n in names if n != ct]
    tmp = path + '.tmp'
    with zipfile.ZipFile(tmp, 'w', zipfile.ZIP_DEFLATED) as out:
        for n in ordered:
            info = src.getinfo(n)
            data = src.read(n)
            zi = zipfile.ZipInfo(n, date_time=info.date_time)
            zi.compress_type = zipfile.ZIP_DEFLATED
            zi.external_attr = 0o600 << 16
            out.writestr(zi, data)
    src.close()
    os.replace(tmp, path)
    z = zipfile.ZipFile(path)
    assert z.namelist()[0] == ct, z.namelist()[0]
    assert z.testzip() is None
    print('repacked', os.path.basename(path), '->', len(z.namelist()), 'entries, first =', z.namelist()[0])

for p in sys.argv[1:]:
    repack(p)
