
import barc4beams as b4b
std_beam_1 = b4b.read_beam('./std_beam_1.h5')
stats_1 = b4b.get_statistics(std_beam_1, verbose=True)
caustic = b4b.compute_caustic(std_beam_1, start=5, finish=7)


# bm.plot_beam(std_beam_1, plot_type='size')
# b4b.plot_caustic(caustic, top_stat='std', plot=False)
b4b.plot_beam(std_beam_1, mode='scatter', plot=False, aspect_ratio=True, envelope=True, bin_method=0)
# b4b.plot_beam(std_beam_1, mode='histo', plot=False, aspect_ratio=True, envelope=True)

# b4b.plot_energy(std_beam_1, plot=False)
# b4b.plot_energy_vs_intensity(std_beam_1, mode="hist", envelope=True, plot=False)
# b4b.plot_energy_vs_intensity(std_beam_1, mode="scatter", envelope=True, plot=False)
# b4b.plot_divergence(std_beam_1, mode='scatter', plot=False, aspect_ratio=False)
# b4b.plot_phase_space(std_beam_1, mode='scatter', plot=False, aspect_ratio=False)
b4b.plot()