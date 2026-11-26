
import numpy as np

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import os


# =====================================================
# BACKEND: RADAR RAW DATA PROCESSING
# =====================================================

def process_radar_data(PATH, DIA, HORA, NBLOCKS):

    # -------------------------------------------------
    # 1. TIME CONFIGURATION
    # -------------------------------------------------

    fecha_hora = f"{DIA} {HORA}"

    fecha_utc = datetime.strptime(
        fecha_hora,
        '%d/%m/%Y %H:%M:%S'
    ).replace(tzinfo=timezone.utc)

    utc_defined = int(fecha_utc.timestamp())

    # Add 5 hours (original logic)
    lt_defined = utc_defined + 18000

    # -------------------------------------------------
    # 2. RADAR PARAMETERS
    # -------------------------------------------------

    nprofiles = 128
    nsamp = 800
    nreceivers = 2
    osamp = 4
    navg = 5

    # -------------------------------------------------
    # 3. GET FILES
    # -------------------------------------------------

    dirr = PATH

    filepath = os.listdir(dirr)

    filepath = sorted(filepath)

    # Original file selection
    filepath = [filepath[135]]

    # -------------------------------------------------
    # 4. INITIALIZATION
    # -------------------------------------------------

    blockcount = 0

    fileread = True

    processed_data = []

    # -------------------------------------------------
    # 5. READ FILES
    # -------------------------------------------------

    for file1 in filepath:

        print(file1)

        if fileread == True and file1[-1] == 'r':

            inputfile = open(
                os.path.join(dirr, file1),
                "rb"
            )

            fsize = os.stat(
                os.path.join(dirr, file1)
            ).st_size

            # Number of blocks
            nblocks = NBLOCKS

            # -----------------------------------------
            # BLOCK LOOP
            # -----------------------------------------

            for k in range(nblocks):

                if k == 0:

                    blockcount = blockcount + 1

                    print('blockcount', blockcount)

                    # ---------------------------------
                    # FIRST BLOCK: LONG HEADER
                    # ---------------------------------

                    nSize = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    version = np.fromfile(
                        inputfile, np.int16, 1, ""
                    )

                    dataBlock = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    utc = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    miliSecond = np.fromfile(
                        inputfile, np.int16, 1, ""
                    )

                    timeZone = np.fromfile(
                        inputfile, np.int16, 1, ""
                    )

                    dstFlag = np.fromfile(
                        inputfile, np.int16, 1, ""
                    )

                    errorCount = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    # First long header

                    size1LongHeader = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    if size1LongHeader.size == 0:
                        break

                    nSamples = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )[0]

                    nProfiles = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )[0]

                    nChannels = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )[0]

                    tmpSkip1 = np.fromfile(
                        inputfile,
                        np.int32,
                        int(size1LongHeader[0]/4)-3-1,
                        ""
                    )

                    # Second long header

                    size2LongHeader = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    tmpSkip2 = np.fromfile(
                        inputfile,
                        np.int32,
                        int(size2LongHeader[0]/4)-1,
                        ""
                    )

                    # Third long header

                    size3LongHeader = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    n2 = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    sizeBlock = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    tmpSkip3 = np.fromfile(
                        inputfile,
                        np.int32,
                        int(size3LongHeader[0]/4)-2-1,
                        ""
                    )

                # -------------------------------------
                # FOLLOWING BLOCKS: SHORT HEADER
                # -------------------------------------

                else:

                    blockcount = blockcount + 1

                    print('blockcount', blockcount)

                    nSize = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    version = np.fromfile(
                        inputfile, np.int16, 1, ""
                    )

                    dataBlock = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    utc = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                    miliSecond = np.fromfile(
                        inputfile, np.int16, 1, ""
                    )

                    timeZone = np.fromfile(
                        inputfile, np.int16, 1, ""
                    )

                    dstFlag = np.fromfile(
                        inputfile, np.int16, 1, ""
                    )

                    errorCount = np.fromfile(
                        inputfile, np.int32, 1, ""
                    )

                # -------------------------------------
                # UTC TIME
                # -------------------------------------

                if utc.size == 0:

                    print("End of file")

                    break

                utc_time = datetime.fromtimestamp(
                    utc[0],
                    timezone.utc
                )

                peru_time = utc_time.astimezone(
                    ZoneInfo("America/Lima")
                )

                print("UTC:", utc_time)

                print("Perú:", peru_time)

                # -------------------------------------
                # READ BLOCK DATA
                # -------------------------------------

                blockdata = np.fromfile(
                    inputfile,
                    np.int16,
                    2*nSamples*nProfiles*nChannels,
                    ""
                )

                # -------------------------------------
                # TIME CONDITION
                # -------------------------------------

                if utc[0] - lt_defined >= 0:

                    print("Pass")

                    # ---------------------------------
                    # I/Q CONVERSION
                    # ---------------------------------

                    r = blockdata[0::2]

                    i = blockdata[1::2]

                    complex_samp = r + 1j*i

                    channelList = np.arange(
                        0,
                        nChannels,
                        1
                    )

                    # ---------------------------------
                    # CHANNEL SEPARATION
                    # ---------------------------------

                    complex_samp1 = complex_samp[0::nChannels]

                    complex_samp2 = complex_samp[1::nChannels]

                    # ---------------------------------
                    # RESHAPE CHANNELS
                    # ---------------------------------

                    tempsamp1 = np.reshape(
                        complex_samp1,
                        (nProfiles, nSamples)
                    )

                    tempsamp2 = np.reshape(
                        complex_samp2,
                        (nProfiles, nSamples)
                    )

                    # ---------------------------------
                    # MULTICHANNEL ARRAY
                    # ---------------------------------

                    temp = np.stack(
                        [
                            tempsamp1,
                            tempsamp2
                        ],
                        axis=0
                    )

                    print("temp.shape:", temp.shape)

                    # ---------------------------------
                    # SAVE PROCESSED BLOCK
                    # ---------------------------------

                    processed_data.append(temp)

            inputfile.close()

    # -------------------------------------------------
    # 6. RETURN DATA TO TKINTER
    # -------------------------------------------------

    print("\nProcessing finished!")

    print("Total processed blocks:", len(processed_data))

    return processed_data
