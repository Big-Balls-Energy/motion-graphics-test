"""Preprocesa el video fuente para la edición: cuadros, cortes entre tomas, cara por cuadro y matte de la persona por cuadro.

Uso (desde agente-universidad/): python3 tools/preprocesar.py fuente/video_original.mp4 <trabajo> <modelos>
  <trabajo>/src/f_00000.jpg…  cuadros del video (JPEG q2)
  <trabajo>/mat/m_00000.png…  matte de la persona (PNG gris+alfa: alfa = persona), para recortarla y poner gráficos detrás
  tools/analisis.json         cortes entre tomas y caja de la cara por cuadro (x, y, ancho, alto, confianza)
Modelos (se descargan si faltan): YuNet (detector de caras de OpenCV Zoo) y Robust Video Matting (MobileNetV3, ONNX)."""
import json, os, subprocess, sys, urllib.request
from multiprocessing import Pool
import numpy as np, cv2
from PIL import Image

SRC, WORK, MOD = sys.argv[1:4]
YUNET = 'https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models/face_detection_yunet/face_detection_yunet_2023mar.onnx'
RVM = 'https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx'
os.makedirs(MOD, exist_ok=True)
for url, name in ((YUNET, 'yunet.onnx'), (RVM, 'rvm.onnx')):
    if not os.path.exists(f'{MOD}/{name}') or os.path.getsize(f'{MOD}/{name}') < 100000: urllib.request.urlretrieve(url, f'{MOD}/{name}')
for d in ('src', 'mat'): os.makedirs(f'{WORK}/{d}', exist_ok=True)
if not os.path.exists(f'{WORK}/src/f_00000.jpg'):
    subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', SRC, '-q:v', '2', '-start_number', '0', f'{WORK}/src/f_%05d.jpg'], check=True)
N = len([f for f in os.listdir(f'{WORK}/src') if f.endswith('.jpg')])

# cortes entre tomas: salto grande y aislado de la diferencia media entre cuadros consecutivos (en miniatura);
# los manotazos rápidos también dan saltos, pero no aislados (sus vecinos también cambian)
small = [cv2.resize(cv2.imread(f'{WORK}/src/f_{i:05d}.jpg', cv2.IMREAD_GRAYSCALE), (54, 96), interpolation=cv2.INTER_AREA).astype(np.float32) for i in range(N)]
d = [0.0] + [float(np.abs(small[i] - small[i - 1]).mean()) for i in range(1, N)]
CUTS = [i for i in range(1, N) if d[i] > 20 and d[i] > 2.5 * max(d[i - 1], d[i + 1] if i + 1 < N else 0)]
SHOTS = list(zip([0] + CUTS, CUTS + [N]))

def work(shots):
    import onnxruntime as ort
    so = ort.SessionOptions(); so.intra_op_num_threads = 1; so.inter_op_num_threads = 1
    sess = ort.InferenceSession(f'{MOD}/rvm.onnx', so, providers=['CPUExecutionProvider'])
    det = cv2.FaceDetectorYN.create(f'{MOD}/yunet.onnx', '', (540, 960), 0.6)
    faces = {}
    for a, b in shots:
        rec = [np.zeros((1, 1, 1, 1), np.float32)] * 4   # el modelo es recurrente: se reinicia en cada toma
        for i in range(a, b):
            img = cv2.imread(f'{WORK}/src/f_{i:05d}.jpg')
            _, f = det.detect(cv2.resize(img, (540, 960), interpolation=cv2.INTER_AREA))
            if f is not None and len(f):
                k = int(np.argmax(f[:, 2] * f[:, 3])); faces[i] = [round(float(v) * 2, 1) for v in f[k, :4]] + [round(float(f[k, 14]), 3)]
            src = (img[:, :, ::-1].astype(np.float32) / 255).transpose(2, 0, 1)[None]
            _, pha, *rec = sess.run(None, {'src': src, 'r1i': rec[0], 'r2i': rec[1], 'r3i': rec[2], 'r4i': rec[3], 'downsample_ratio': np.array([0.25], np.float32)})
            a8 = (np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8)
            Image.fromarray(np.dstack([np.zeros_like(a8), a8]), 'LA').save(f'{WORK}/mat/m_{i:05d}.png', optimize=False, compress_level=6)   # gris + alfa
    return faces

if __name__ == '__main__':
    groups = [[] for _ in range(4)]; load = [0] * 4
    for s in sorted(SHOTS, key=lambda s: s[0] - s[1]):   # reparte las tomas en 4 procesos con carga pareja
        k = int(np.argmin(load)); groups[k].append(s); load[k] += s[1] - s[0]
    faces = {}
    with Pool(4) as pool:
        for r in pool.map(work, groups): faces.update(r)
    out = {'fps': 30, 'frames': N, 'cuts': CUTS, 'shots': SHOTS, 'diff': [round(x, 2) for x in d],
           'faces': {str(i): faces.get(i) for i in range(N)}}
    json.dump(out, open('tools/analisis.json', 'w'))
    print('cuadros', N, 'cortes', CUTS, 'caras detectadas', sum(v is not None for v in faces.values()))
