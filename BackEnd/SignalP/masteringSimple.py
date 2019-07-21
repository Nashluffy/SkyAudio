from pysndfx import AudioEffectsChain

fx = (
    AudioEffectsChain()
    .equalizer(10000, 1, 3)
    .equalizer(20, 1, -10)
    .limiter(3)
    .normalize()
    .compand(0.2, 1, 2.0, -20, -20, -20)
)
inf = 'sd1audiotest.wav'
outf = 'masteringSimple.wav'
fx(inf, outf)