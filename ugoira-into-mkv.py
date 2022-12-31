from pathlib import Path
from zipfile import ZipFile
import tempfile
import json
import subprocess
folder=Path(__file__).parent.absolute()
ugoiras=folder.rglob('*.ugoira')
for i in ugoiras:
    _mkv=Path(str(i).replace('.ugoira','.mkv'))
    if _mkv.exists():
        print('exists.')
        continue
    with tempfile.TemporaryDirectory() as tmpf:
        _tmpf=Path(tmpf)
        ZipFile(i.absolute()).extractall(tmpf)
        _json=json.load(open(_tmpf/'animation.json'))
        _frames=_json['frames']
        _names=[j['file'] for j in _frames]
        _times=[j['delay'] for j in _frames]
        _paths=[_tmpf/j for j in _names]
        _trailing=_paths[0] if _paths[0].stat().st_size<_paths[-1].stat().st_size else _paths[-1]
        _paths.append(_trailing)
        _concat='\n'.join([r"file {p}".format(p=str(j).replace('\\','\\\\').replace(' ','\\ ')) for j in _paths])
        _ms=0;_timestamps=['# timestamp format v2','0']
        for j in _times:
            _ms+=j
            _timestamps.append(str(_ms))
        _concatfile=_tmpf/'concat'
        _mkv1=_tmpf/'tmp.mkv'
        _timestampfile=_tmpf/'timestamps'
        with open(_concatfile,'w',encoding='utf-8') as _o:
            _o.write(_concat)
        with open(_timestampfile,'w') as _o:
            _o.write('\n'.join(_timestamps))
        _run=subprocess.run(f'ffmpeg -safe 0 -loglevel error -f concat -i "{_concatfile}" -c:v copy "{_mkv1}"',shell=True)
        if _run.returncode==0:
            _run2=subprocess.run(f'mkvmerge -o "{_mkv}" --no-global-tags --no-track-tags --compression 0:zlib --timestamps 0:"{_timestampfile}" {_mkv1}',shell=True)
        if _run2.returncode==0:
            pass
        else:
            _mkv.unlink(missing_ok=True)
input('Press Enter to leave.')