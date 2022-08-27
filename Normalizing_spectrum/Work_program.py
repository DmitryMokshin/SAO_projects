import warnings
from specutils import Spectrum1D
from astropy import units as u
from specutils.fitting import fit_continuum
import numpy as np


def init_region_header(header_file):
    return np.linspace(header_file['CRVAL1'],
                       header_file['CDELT1'] * (header_file['NAXIS1'] - 1) + header_file['CRVAL1'],
                       header_file['NAXIS1'])


def approximation_of_the_continuum(data_fits, model_aproximation):
    """Апроксимация континуума"""
    x = init_region_header(data_fits.header)
    y = data_fits.data

    spectrum = Spectrum1D(flux=y * u.Jy, spectral_axis=x * u.AA)

    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        fitted_continuum = fit_continuum(spectrum, model=model_aproximation)

    y_continuum_fitted = np.array(fitted_continuum(x * u.AA))

    return y_continuum_fitted, fitted_continuum


def clear_frame(frame_to_clear):
    for widget in frame_to_clear.winfo_children():
        widget.destroy()
    frame_to_clear.pack_forget()


if __name__ == '__main__':
    import tkinter

    from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
    from matplotlib.figure import Figure

    import numpy as np

    root = tkinter.Tk()
    root.wm_title("Embedding in Tk")

    fig = Figure(figsize=(5, 4), dpi=100)
    t = np.arange(0, 3, .01)
    ax = fig.add_subplot()
    line, = ax.plot(t, 2 * np.sin(2 * np.pi * t))
    ax.set_xlabel("time [s]")
    ax.set_ylabel("f(t)")

    canvas = FigureCanvasTkAgg(fig, master=root)  # A tk.DrawingArea.
    canvas.draw()

    # pack_toolbar=False will make it easier to use a layout manager later on.
    toolbar = NavigationToolbar2Tk(canvas, root, pack_toolbar=False)
    toolbar.update()

    # canvas.mpl_connect(
    #     "key_press_event", lambda event: print(f"you pressed {event.key}"))
    # canvas.mpl_connect("key_press_event", key_press_handler)

    button_quit = tkinter.Button(master=root, text="Quit", command=root.quit)


    def update_frequency(new_val):
        # retrieve frequency
        f = float(new_val)

        # update data
        y = 2 * np.sin(2 * np.pi * f * t)
        line.set_data(t, y)

        # required to update canvas and attached toolbar!
        canvas.draw()


    slider_update = tkinter.Scale(root, from_=0, to=100, orient=tkinter.HORIZONTAL,
                                  command=update_frequency, label="Frequency [Hz]")

    # Packing order is important. Widgets are processed sequentially and if there
    # is no space left, because the window is too small, they are not displayed.
    # The canvas is rather flexible in its size, so we pack it last which makes
    # sure the UI controls are displayed as long as possible.
    button_quit.pack(side=tkinter.BOTTOM)
    slider_update.pack(side=tkinter.BOTTOM)
    toolbar.pack(side=tkinter.BOTTOM, fill=tkinter.X)
    canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

    tkinter.mainloop()
