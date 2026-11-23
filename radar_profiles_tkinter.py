import os
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import tkinter as tk


def convertTime(date, hour):
    fecha_hora = f"{date} {hour}"
    fecha_utc = datetime.strptime(fecha_hora, "%d/%m/%Y %H:%M:%S").replace(
        tzinfo=timezone.utc
    )
    return int(fecha_utc.timestamp())


def iter_valid_blocks(variable_path, variable_fecha, variable_hora, num_bloques, num_file):
    """Genera bloques válidos (temp, utc_timestamp, block_idx) de forma perezosa."""
    utc_defined = convertTime(variable_fecha, variable_hora)
    lt_defined = utc_defined + 18000

    dirr = variable_path
    filepath = sorted(os.listdir(dirr))

    # Misma selección de archivo que tenías; si quieres recorrer más archivos, ajusta aquí
    filepath = [filepath[num_file]]

    blockcount = 0

    for file1 in filepath:
        print("Archivo:", file1)
        if not file1.endswith("r"):
            continue

        with open(os.path.join(dirr, file1), "rb") as inputfile:
            for k in range(num_bloques):
                blockcount += 1
                print("blockcount:", blockcount)

                if k == 0:
                    nSize = np.fromfile(inputfile, np.int32, 1, "")
                    version = np.fromfile(inputfile, np.int16, 1, "")
                    dataBlock = np.fromfile(inputfile, np.int32, 1, "")
                    utc = np.fromfile(inputfile, np.int32, 1, "")
                    miliSecond = np.fromfile(inputfile, np.int16, 1, "")
                    timeZone = np.fromfile(inputfile, np.int16, 1, "")
                    dstFlag = np.fromfile(inputfile, np.int16, 1, "")
                    errorCount = np.fromfile(inputfile, np.int32, 1, "")

                    size1LongHeader = np.fromfile(inputfile, np.int32, 1, "")
                    nSamples = np.fromfile(inputfile, np.int32, 1, "")[0]
                    nProfiles = np.fromfile(inputfile, np.int32, 1, "")[0]
                    nChannels = np.fromfile(inputfile, np.int32, 1, "")[0]
                    tmpSkip1 = np.fromfile(
                        inputfile, np.int32, int(size1LongHeader[0] / 4) - 3 - 1, ""
                    )

                    size2LongHeader = np.fromfile(inputfile, np.int32, 1, "")
                    tmpSkip2 = np.fromfile(
                        inputfile, np.int32, int(size2LongHeader[0] / 4) - 1, ""
                    )

                    size3LongHeader = np.fromfile(inputfile, np.int32, 1, "")
                    n2 = np.fromfile(inputfile, np.int32, 1, "")
                    sizeBlock = np.fromfile(inputfile, np.int32, 1, "")
                    tmpSkip3 = np.fromfile(
                        inputfile, np.int32, int(size3LongHeader[0] / 4) - 2 - 1, ""
                    )
                else:
                    nSize = np.fromfile(inputfile, np.int32, 1, "")
                    version = np.fromfile(inputfile, np.int16, 1, "")
                    dataBlock = np.fromfile(inputfile, np.int32, 1, "")
                    utc = np.fromfile(inputfile, np.int32, 1, "")
                    miliSecond = np.fromfile(inputfile, np.int16, 1, "")
                    timeZone = np.fromfile(inputfile, np.int16, 1, "")
                    dstFlag = np.fromfile(inputfile, np.int16, 1, "")
                    errorCount = np.fromfile(inputfile, np.int32, 1, "")

                if utc.size > 0:
                    utc_time = datetime.fromtimestamp(utc[0], timezone.utc)
                    peru_time = utc_time.astimezone(ZoneInfo("America/Lima"))
                    print("UTC:", utc_time)
                    print("Perú:", peru_time)

                blockdata = np.fromfile(
                    inputfile, np.int16, 2 * nSamples * nProfiles * nChannels, ""
                )

                # Si el archivo se cortó antes de completar el bloque, detenemos este archivo
                expected_len = 2 * nSamples * nProfiles * nChannels
                if blockdata.size < expected_len:
                    print("Bloque incompleto, fin de lectura para este archivo.")
                    break

                if utc.size > 0 and (utc[0] - lt_defined) >= 0:
                    print("Pass -> Bloque válido:", blockcount)
                    r = blockdata[0::2]
                    i = blockdata[1::2]
                    complex_samp = r + 1j * i
                    #print('complex_samp.shape',complex_samp.shape)
                    #Normalization

                    #magnitude = np.abs(complex_samp)
                    #mag_max = np.max(magnitude)
                    
                    #if mag_max > 0:
                    #    mag_norm = complex_samp / mag_max  # Values in [0.0, 1.0]
                    #else:
                    #    mag_norm = np.zeros_like(magnitude, dtype=np.float64)

                    #complex_samp = mag_norm

                    complex_samp1 = complex_samp[0::nChannels]
                    complex_samp2 = complex_samp[1::nChannels]

                    tempsamp1 = np.reshape(complex_samp1, (nProfiles, nSamples))
                    tempsamp2 = np.reshape(complex_samp2, (nProfiles, nSamples))



                    temp = np.stack([tempsamp1, tempsamp2], axis=0)
                    #print('temp.shape', temp.shape)

                    mag = np.abs(temp)
                    mag_max_per_profile = np.max(mag, axis=-1, keepdims=True)

                    temp_norm = np.zeros_like(temp, dtype=np.complex128)
                    valid = mag_max_per_profile > 0

                    # Broadcasting automático a lo largo de nHeights
                    max_broadcast = np.broadcast_to(mag_max_per_profile, temp.shape)
                    valid_broadcast = np.broadcast_to(valid, temp.shape)

                    temp_norm[valid_broadcast] = temp[valid_broadcast] / max_broadcast[valid_broadcast]

                    temp = temp_norm


                    yield {
                        "temp": temp,
                        "nProfiles": nProfiles,
                        "nSamples": nSamples,
                        "blockcount": blockcount,
                        "peru_time": peru_time,
                    }


def run_continuous_viewer(
    variable_path, variable_fecha, variable_hora, num_bloques, num_file
):
    block_gen = iter_valid_blocks(
        variable_path, variable_fecha, variable_hora, num_bloques, num_file
    )

    current_block = None
    current_profile = -1
    finished_all = False

    def load_next_block():
        nonlocal current_block, current_profile, finished_all
        try:
            current_block = next(block_gen)
            current_profile = 0
            return True
        except StopIteration:
            finished_all = True
            current_block = None
            return False

    # Una sola ventana principal para toda la sesión
    root = tk.Tk()
    root.title("Radar profiles - Continuous Viewer")

    info_label = tk.Label(
        root, text="Presiona 'Next profile' para iniciar", font=("Arial", 10)
    )
    info_label.pack(pady=(6, 0))

    fig = Figure(figsize=(9, 5), dpi=100)
    ax = fig.add_subplot(111)

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

    def render_current_profile():
        temp = current_block["temp"]
        n_profiles = current_block["nProfiles"]
        n_samples = current_block["nSamples"]
        blockcount = current_block["blockcount"]
        peru_time = current_block["peru_time"]

        t = np.arange(n_samples)
        ax.clear()
        ax.plot(t, np.real(temp[0, current_profile, :]), label="Real")
        ax.plot(t, np.imag(temp[0, current_profile, :]), label="Imaginary")

        ax.set_title(
            f"Bloque {blockcount} ({peru_time.strftime('%H:%M:%S')} PE) | "
            f"Perfil {current_profile + 1}/{n_profiles}"
        )
        ax.set_xlabel("Samples")
        ax.set_ylabel("Amplitude")
        #ax.set_xlim([xmin, xmax])
        ax.set_ylim([-1, 1])
        ax.legend()
        ax.grid()

        fig.tight_layout()
        canvas.draw()
        info_label.config(
            text=f"Bloque {blockcount} — Perfil {current_profile + 1} de {n_profiles}"
        )

    def show_next_profile():
        nonlocal current_profile

        if finished_all:
            return

        # Primer clic o avance normal dentro del bloque actual
        if current_block is None:
            if not load_next_block():
                ax.clear()
                ax.set_title("No hay más bloques disponibles")
                canvas.draw()
                next_button.config(state=tk.DISABLED, text="No more blocks")
                info_label.config(text="Fin de bloques. Cierra la ventana para salir.")
                return
        else:
            current_profile += 1
            # Si se acabó el bloque actual, saltamos automáticamente al siguiente bloque
            if current_profile >= current_block["nProfiles"]:
                if not load_next_block():
                    ax.clear()
                    ax.set_title("Todos los bloques y perfiles completados")
                    canvas.draw()
                    next_button.config(state=tk.DISABLED, text="Completed")
                    info_label.config(
                        text="Fin de todos los bloques. Cierra la ventana para salir."
                    )
                    return

        print(
            f"Mostrando Bloque {current_block['blockcount']} - "
            f"Perfil {current_profile + 1}/{current_block['nProfiles']}"
        )
        render_current_profile()

    def on_close():
        root.quit()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)

    next_button = tk.Button(
        root,
        text="Next profile",
        command=show_next_profile,
        font=("Arial", 12),
    )
    next_button.pack(pady=8)

    # Opcional: mostrar el perfil 1 del primer bloque automáticamente al abrir
    show_next_profile()

    root.mainloop()


if __name__ == "__main__":
    #VARIABLE_PATH = "/media/cportilla/HDD/mnt/share-1/Faraday/main_radar/rawdata/d2026230/"
    
    VARIABLE_PATH = '/media/cportilla/HDD/DAVID-OP/data-sevag/7/d2021301/'
    #VARIABLE_FECHA = "18/08/2026"
    VARIABLE_FECHA = '28/10/2021'
    VARIABLE_HORA = "00:00:00"
    #VARIABLE_NUMERO_DE_BLOQUES = 214
    VARIABLE_NUMERO_DE_BLOQUES = 50
    VARIABLE_NUMERO_DE_FILE = 1

    run_continuous_viewer(
        VARIABLE_PATH,
        VARIABLE_FECHA,
        VARIABLE_HORA,
        VARIABLE_NUMERO_DE_BLOQUES,
        VARIABLE_NUMERO_DE_FILE
    )