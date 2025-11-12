import numpy
from cwinpy.signal import HeterodynedCWSimulator
import matplotlib.pyplot as plt
from cwinpy.parfile import PulsarParameters
from cwinpy.info import HW_INJ_BASE_PATH


parfile = HW_INJ_BASE_PATH + "/O3/hw_inj/PULSAR03.par"
ephem = PulsarParameters(parfile)

ref_freq = 52.5
ref_epoch = None # 1020912039 # ephem["PEPOCH"]

dt = 0.1

t0 = 1382158336 + 270 * 86400 # GPS of 2023-10-24T04:52:35.000
t_end = t0 + 10 * 86400 # GPS of 2023-11-24T22:07:15.000

det = "L1"

t = numpy.arange(t0, t_end, dt)

phase = HeterodynedCWSimulator(
    det=det, times=t, usetempo2=False, ref_freq=ref_freq, ref_epoch=ref_epoch,
)

phase_evolution = phase.phase_evolution(newpar=ephem)

phase_fft = numpy.fft.fftshift(numpy.fft.fft(numpy.exp(-1j * 2 * numpy.pi * phase_evolution)))

fft_freqs = numpy.fft.fftshift(numpy.fft.fftfreq(len(phase_fft), numpy.diff(t)[0]))

plt.plot(fft_freqs + 2 * phase.hetpar["F0"], numpy.square(numpy.abs(phase_fft)))
plt.axvline(2 * ephem["F0"], color="k", ls="--")
plt.yscale("log")

plt.xlabel("Frequency [Hz]")
plt.ylabel("Squared abs(fft)")
plt.show()