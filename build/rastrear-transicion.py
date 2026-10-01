import cv2, numpy as np, json, os, sys
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
S = os.path.join(R, 'build', 'rastreo')  # salida: track.json y cuadros de control
cap = cv2.VideoCapture(os.path.join(R, 'assets', 'transicion.mp4'))
fps = cap.get(cv2.CAP_PROP_FPS)
W, H = 1280, 720
frames = []
while True:
    ok, f = cap.read()
    if not ok: break
    frames.append(cv2.resize(f, (W, H), interpolation=cv2.INTER_AREA))
print('frames', len(frames), 'fps', fps)

A = np.array([0.494 * W, 0.969 * H])   # punto del suelo donde pisan Siderax y la moto
k = 1.0
out = [(0.0, A[0] / W, A[1] / H, k, 0)]
prev = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)
os.makedirs(os.path.join(S, 'trk'), exist_ok=True)
for i in range(1, len(frames)):
    cur = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)
    hw = max(0.16 * W * k, 60); hh = max(0.12 * H * k, 40)
    x0, x1 = int(max(0, A[0] - hw)), int(min(W, A[0] + hw))
    y0, y1 = int(max(0, A[1] - hh * 1.6)), int(min(H, A[1] + hh * 0.6))
    mask = np.zeros_like(prev); mask[y0:y1, x0:x1] = 255
    p0 = cv2.goodFeaturesToTrack(prev, 400, 0.005, 4, mask=mask, blockSize=5)
    n = 0
    if p0 is not None and len(p0) >= 8:
        p1, st, err = cv2.calcOpticalFlowPyrLK(prev, cur, p0, None, winSize=(21, 21), maxLevel=4)
        good = st.ravel() == 1
        a, b = p0[good].reshape(-1, 2), p1[good].reshape(-1, 2)
        # verificación hacia atrás
        if len(a) >= 8:
            back, st2, _ = cv2.calcOpticalFlowPyrLK(cur, prev, b.reshape(-1, 1, 2), None, winSize=(21, 21), maxLevel=4)
            fb = np.linalg.norm(back.reshape(-1, 2) - a, axis=1) < 1.0
            a, b = a[fb], b[fb]
        if len(a) >= 8:
            M, inl = cv2.estimateAffinePartial2D(a, b, method=cv2.RANSAC, ransacReprojThreshold=1.5, maxIters=5000)
            if M is not None:
                n = int(inl.sum())
                s = float(np.hypot(M[0, 0], M[1, 0]))
                A = M @ np.array([A[0], A[1], 1.0])
                k *= s
    out.append((i / fps, A[0] / W, A[1] / H, k, n))
    if i % 12 == 0 or i == len(frames) - 1:
        vis = frames[i].copy()
        cv2.circle(vis, (int(A[0]), int(A[1])), 6, (0, 0, 255), -1)
        cv2.line(vis, (int(A[0]), int(A[1])), (int(A[0]), int(A[1] - 0.5 * H * k)), (0, 255, 255), 2)
        cv2.imwrite(os.path.join(S, 'trk', f'{i:03d}.jpg'), cv2.resize(vis, (480, 270)))
    prev = cur
for t, x, y, kk, n in out[::6]:
    print(f'{t:5.2f}  x={x:.4f} y={y:.4f} k={kk:.4f} n={n}')
json.dump(out, open(os.path.join(S, 'track.json'), 'w'))
